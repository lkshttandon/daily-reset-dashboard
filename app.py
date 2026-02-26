from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from coach_local import generate_local_advice
from db import (
    completion_for_day,
    completion_history,
    current_streak,
    get_checks_for_day,
    get_metrics_for_day,
    init_db,
    reset_day,
    upsert_check,
    upsert_metrics,
)
from reset_protocol import PROTOCOL

st.set_page_config(page_title="Daily Reset Dashboard", page_icon=":material/autorenew:", layout="centered")


def on_check_change(day: str, section: str, item: str, state_key: str) -> None:
    upsert_check(day=day, section=section, item=item, checked=bool(st.session_state[state_key]))


def on_metrics_change(day: str) -> None:
    upsert_metrics(
        day=day,
        sleep_hours=float(st.session_state["sleep_hours"]),
        energy=int(st.session_state["energy"]),
        time_available=int(st.session_state["time_available"]),
        notes=str(st.session_state["notes"]),
    )


def render_today_tab(day: str) -> None:
    st.subheader("Today")

    metrics = get_metrics_for_day(day) or {}

    col1, col2, col3 = st.columns(3)
    col1.number_input(
        "Sleep (hours)",
        min_value=0.0,
        max_value=16.0,
        value=float(metrics.get("sleep_hours", 7.5)),
        step=0.5,
        key="sleep_hours",
        on_change=on_metrics_change,
        args=(day,),
    )
    col2.slider(
        "Energy (1-10)",
        min_value=1,
        max_value=10,
        value=int(metrics.get("energy", 6)),
        key="energy",
        on_change=on_metrics_change,
        args=(day,),
    )
    col3.number_input(
        "Time Available (min)",
        min_value=0,
        max_value=300,
        value=int(metrics.get("time_available", 45)),
        step=5,
        key="time_available",
        on_change=on_metrics_change,
        args=(day,),
    )

    st.text_area(
        "Notes",
        value=str(metrics.get("notes", "")),
        key="notes",
        height=90,
        on_change=on_metrics_change,
        args=(day,),
        placeholder="What might block your consistency today?",
    )

    checks_for_day = get_checks_for_day(day)

    for section, items in PROTOCOL.items():
        with st.expander(section, expanded=section in ("Morning Routine", "Daytime Habits", "Evening Routine")):
            for idx, item in enumerate(items):
                key = f"check::{day}::{section}::{idx}"
                default = checks_for_day.get((section, item), False)
                if key not in st.session_state:
                    st.session_state[key] = default
                st.checkbox(
                    item,
                    key=key,
                    on_change=on_check_change,
                    args=(day, section, item, key),
                )

    stats = completion_for_day(day, PROTOCOL)
    done, total, pct = stats["done"], stats["total"], stats["pct"]

    st.divider()
    st.caption(f"Progress: {done}/{total} complete ({pct:.1f}%)")
    st.progress(float(pct) / 100.0)

    if st.button("Reset Today", type="secondary", use_container_width=True):
        reset_day(day)
        for k in [k for k in st.session_state.keys() if k.startswith(f"check::{day}::")]:
            del st.session_state[k]
        for mk in ["sleep_hours", "energy", "time_available", "notes"]:
            if mk in st.session_state:
                del st.session_state[mk]
        st.rerun()


def render_insights_tab() -> None:
    st.subheader("Insights")

    history_60 = completion_history(PROTOCOL, days=60)
    chart_df = history_60.copy()
    chart_df["day"] = pd.to_datetime(chart_df["day"])
    chart_df = chart_df.set_index("day")
    st.line_chart(chart_df[["pct"]], height=240)

    history_14 = completion_history(PROTOCOL, days=14)
    display_14 = history_14.copy()
    display_14["day"] = pd.to_datetime(display_14["day"]).dt.strftime("%Y-%m-%d")
    display_14 = display_14.rename(columns={"day": "Date", "done": "Done", "total": "Total", "pct": "Completion %"})

    st.dataframe(display_14, use_container_width=True, hide_index=True)

    streak = current_streak(PROTOCOL, threshold_pct=70.0)
    st.metric("Current Streak (>= 70%)", f"{streak} day(s)")


def render_coach_tab(day: str) -> None:
    st.subheader("Coach")
    st.caption("Actionable recommendations for fat loss + stable energy and muscle gain + performance.")

    today_stats = completion_for_day(day, PROTOCOL)
    today_metrics = get_metrics_for_day(day) or {
        "sleep_hours": 7.5,
        "energy": 6,
        "time_available": 45,
        "notes": "",
    }

    completion_pct = float(today_stats["pct"])
    sleep = float(today_metrics.get("sleep_hours") or 7)
    energy = int(today_metrics.get("energy") or 5)
    time_available = int(today_metrics.get("time_available") or 45)
    notes = str(today_metrics.get("notes") or "")

    advice = generate_local_advice(
        completion_pct=completion_pct,
        sleep=sleep,
        energy=energy,
        time_available=time_available,
        notes=notes,
    )
    st.markdown(advice)


def main() -> None:
    init_db()

    st.title("Daily Reset Dashboard")
    day = date.today().isoformat()
    st.caption(f"Tracking for {day}")

    tab_today, tab_insights, tab_coach = st.tabs(["Today", "Insights", "Coach"])

    with tab_today:
        render_today_tab(day)

    with tab_insights:
        render_insights_tab()

    with tab_coach:
        render_coach_tab(day)


if __name__ == "__main__":
    main()
