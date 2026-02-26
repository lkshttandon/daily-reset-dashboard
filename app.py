from __future__ import annotations

from datetime import date, datetime

import pandas as pd
import streamlit as st

from coach_local import generate_local_advice
from db import (
    completion_for_day,
    completion_history,
    current_streak,
    get_checks_for_day,
    get_metrics_for_day,
    get_setting,
    init_db,
    reset_day,
    set_setting,
    upsert_check,
    upsert_metrics,
)
from reset_protocol import PROTOCOL
from telegram_notifier import send_telegram_message

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


def _masked_token(token: str) -> str:
    if len(token) <= 8:
        return "*" * len(token)
    return f"{token[:4]}...{token[-4:]}"


def _build_default_reminder_text(day: str) -> str:
    stats = completion_for_day(day, PROTOCOL)
    return (
        f"Daily Reset reminder ({day})\n"
        f"Current progress: {stats['done']}/{stats['total']} ({stats['pct']:.1f}%).\n"
        "Open your dashboard and complete your next 3 non-negotiables."
    )


def _is_valid_hhmm(value: str) -> bool:
    if len(value) != 5 or value[2] != ":":
        return False
    left, right = value.split(":")
    if not (left.isdigit() and right.isdigit()):
        return False
    hour = int(left)
    minute = int(right)
    return 0 <= hour <= 23 and 0 <= minute <= 59


def _maybe_send_scheduled_reminder(day: str) -> None:
    enabled = get_setting("telegram_enabled", "0") == "1"
    token = get_setting("telegram_bot_token", "")
    chat_id = get_setting("telegram_chat_id", "")
    reminder_time = get_setting("telegram_reminder_time", "20:00")
    reminder_message = get_setting("telegram_reminder_message", "")

    if not enabled or not token or not chat_id:
        return

    now = datetime.now()
    now_hhmm = now.strftime("%H:%M")
    last_day_sent = get_setting("telegram_last_sent_day", "")
    if last_day_sent == day:
        return
    if now_hhmm < reminder_time:
        return

    message = reminder_message.strip() or _build_default_reminder_text(day)
    ok, detail = send_telegram_message(token, chat_id, message)
    if ok:
        set_setting("telegram_last_sent_day", day)
        set_setting("telegram_last_sent_at", now.strftime("%Y-%m-%d %H:%M:%S"))
        set_setting("telegram_last_error", "")
    else:
        set_setting("telegram_last_error", detail)


def render_reminders_tab(day: str) -> None:
    st.subheader("Reminders")
    st.caption("Configure Telegram notifications for iPhone and Android.")

    enabled_default = get_setting("telegram_enabled", "0") == "1"
    token_default = get_setting("telegram_bot_token", "")
    chat_id_default = get_setting("telegram_chat_id", "")
    time_default_str = get_setting("telegram_reminder_time", "20:00")
    msg_default = get_setting("telegram_reminder_message", "")
    last_sent = get_setting("telegram_last_sent_at", "")
    last_error = get_setting("telegram_last_error", "")

    with st.form("telegram_settings_form"):
        enabled = st.checkbox("Enable Telegram reminders", value=enabled_default)
        token = st.text_input("Bot token", value=token_default, type="password", placeholder="123456:ABCDEF...")
        chat_id = st.text_input("Chat ID", value=chat_id_default, placeholder="e.g. 123456789")
        reminder_time = st.text_input("Daily reminder time (24h HH:MM)", value=time_default_str, placeholder="20:00")
        reminder_message = st.text_area(
            "Reminder message (optional)",
            value=msg_default,
            placeholder="Leave blank to use default progress-based reminder.",
            height=80,
        )
        saved = st.form_submit_button("Save Reminder Settings", use_container_width=True)

    if saved:
        valid_time = _is_valid_hhmm(reminder_time.strip())
        if not valid_time:
            st.error("Reminder time must be in HH:MM format (24h), for example 20:00.")
        else:
            set_setting("telegram_enabled", "1" if enabled else "0")
            set_setting("telegram_bot_token", token.strip())
            set_setting("telegram_chat_id", chat_id.strip())
            set_setting("telegram_reminder_time", reminder_time.strip())
            set_setting("telegram_reminder_message", reminder_message.strip())
            st.success("Telegram reminder settings saved.")

    st.divider()
    st.markdown("**Current Status**")
    st.write(f"Enabled: {'Yes' if enabled_default else 'No'}")
    st.write(f"Bot token: {_masked_token(token_default) if token_default else 'Not set'}")
    st.write(f"Chat ID: {chat_id_default if chat_id_default else 'Not set'}")
    st.write(f"Reminder time: {time_default_str}")
    st.write(f"Last sent: {last_sent if last_sent else 'Never'}")
    if last_error:
        st.warning(f"Last send error: {last_error}")

    if st.button("Send Test Telegram Message", use_container_width=True):
        if not token_default or not chat_id_default:
            st.error("Set bot token and chat ID first, then save settings.")
        else:
            msg = f"Test from Daily Reset Dashboard ({day}). Telegram setup is working."
            ok, detail = send_telegram_message(token_default, chat_id_default, msg)
            if ok:
                set_setting("telegram_last_sent_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                set_setting("telegram_last_error", "")
                st.success("Test message sent.")
            else:
                set_setting("telegram_last_error", detail)
                st.error(f"Failed to send test message: {detail}")


def main() -> None:
    init_db()

    st.title("Daily Reset Dashboard")
    day = date.today().isoformat()
    st.caption(f"Tracking for {day}")
    _maybe_send_scheduled_reminder(day)

    tab_today, tab_insights, tab_coach, tab_reminders = st.tabs(["Today", "Insights", "Coach", "Reminders"])

    with tab_today:
        render_today_tab(day)

    with tab_insights:
        render_insights_tab()

    with tab_coach:
        render_coach_tab(day)

    with tab_reminders:
        render_reminders_tab(day)


if __name__ == "__main__":
    main()
