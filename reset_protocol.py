from __future__ import annotations

PROTOCOL = {
    "Morning Routine": [
        "Wake up at consistent time",
        "Hydrate (500 ml water)",
        "10 minutes of mobility or stretching",
        "Protein-first breakfast",
    ],
    "Morning Skincare": [
        "Gentle cleanser",
        "Vitamin C serum",
        "Moisturizer",
        "SPF 30+ sunscreen",
    ],
    "Daytime Habits": [
        "Hit daily step target",
        "Balanced lunch (protein + fiber)",
        "2 hydration check-ins",
        "Limit sugary snacks",
    ],
    "Evening Routine": [
        "Training session or walk",
        "Protein-focused dinner",
        "Prep tomorrow's priorities",
        "Cut caffeine 8+ hours before bed",
    ],
    "Night Skincare": [
        "Cleanser",
        "Treatment (retinoid or active)",
        "Moisturizer",
    ],
    "Bedtime": [
        "No screens 30 minutes before sleep",
        "Light stretch or breathing (5 minutes)",
        "Set alarm and sleep window",
    ],
    "Weekly Checkpoint": [
        "Review 7-day completion trend",
        "Adjust calorie target if needed",
        "Plan workouts and groceries",
        "Set one focus habit for next week",
    ],
}


def all_items_count() -> int:
    return sum(len(items) for items in PROTOCOL.values())
