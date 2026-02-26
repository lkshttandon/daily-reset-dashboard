from __future__ import annotations


def _has_keyword(notes: str, keyword: str) -> bool:
    return keyword.lower() in notes.lower()


def generate_local_advice(
    completion_pct: float,
    sleep: float,
    energy: int,
    time_available: int,
    notes: str,
) -> str:
    sore = _has_keyword(notes, "sore")
    busy = _has_keyword(notes, "busy")
    craving = _has_keyword(notes, "craving")

    short_on_time = time_available < 30
    low_energy = energy <= 4
    low_sleep = sleep < 6
    low_completion = completion_pct < 50

    food_options = [
        "Greek yogurt bowl (2% Greek yogurt, frozen berries, oats, chia) + 2 boiled eggs",
        "Rotisserie chicken wrap (whole wheat tortilla, bagged salad, hummus) + apple",
    ]
    if craving:
        food_options[1] = (
            "Protein snack swap: skyr or cottage cheese + banana + small handful of almonds"
        )

    if low_energy or low_sleep or sore:
        exercise = "Walk + mobility: 20-30 min brisk walk + 10 min hips/shoulders mobility."
    elif short_on_time or busy:
        exercise = (
            "Short gym circuit (20-25 min): 3 rounds - goblet squat x10, push-ups x8-12, row x10, plank 30s."
        )
    else:
        exercise = (
            "Gym full session (45-60 min): squat 3x5, bench 3x6-8, row 3x8-10, RDL 3x8, incline walk 10 min."
        )

    improvements: list[str] = []
    if low_completion:
        improvements.append("Pick only 3 non-negotiables today: hydration, protein at 2 meals, bedtime target.")
    if low_sleep:
        improvements.append("Shift bedtime 30 minutes earlier tonight and stop caffeine after lunch.")
    if low_energy:
        improvements.append("Front-load water + protein in the first 2 hours after waking.")
    if busy:
        improvements.append("Use a minimum viable day: one workout block, one protein prep, one evening reset.")
    if sore:
        improvements.append("Reduce training intensity by 20-30% and prioritize mobility and steps.")
    if craving:
        improvements.append("Pre-empt cravings with a protein snack before the usual trigger window.")

    if not improvements:
        improvements.append("Prep tomorrow's gym clothes and breakfast tonight to reduce friction.")
    improvements = improvements[:3]

    if low_energy or low_sleep or busy or short_on_time:
        fallback = (
            "12-15 min plan: 8 min brisk walk + 2 rounds of bodyweight squats x12, incline push-ups x10, plank 30s."
        )
    else:
        fallback = "15-20 min plan: incline treadmill walk 10 min + dumbbell circuit (squat/press/row) 2 rounds."

    markdown = (
        "### \\U0001F957 Food\n"
        f"- {food_options[0]}\n"
        f"- {food_options[1]}\n\n"
        "### \\U0001F3CB\uFE0F Exercise\n"
        f"{exercise}\n\n"
        "### \\U0001F527 Improvements\n"
        + "\n".join(f"- {item}" for item in improvements)
        + "\n\n"
        "### \\U0001F691 Fallback Plan\n"
        f"{fallback}"
    )

    return markdown
