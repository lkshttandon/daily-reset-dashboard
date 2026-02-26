from __future__ import annotations

PROTOCOL = {
    "Morning Routine": [
        "7:30 AM: Wake up, drink warm water, open curtains, no phone in bed",
        "7:45 AM: 5 min stretching, optional black coffee",
        "8:30-9:30 AM: Gym (strength + mobility, focus on form)",
        "Post-workout meal: Protein + moderate carbs (eggs, whey + oats, paneer + rice)",
    ],
    "Morning Skincare": [
        "Gentle cleanser",
        "Niacinamide serum",
        "Light moisturizer",
        "Sunscreen SPF 30+ (every day)",
    ],
    "Daytime Habits": [
        "Drink 2-3 liters of water",
        "10 min walk after lunch",
        "Deep work in first 90 minutes",
        "Keep evening routine calm after 6-8 PM",
        "Avoid late-night snacking",
    ],
    "Evening Routine": [
        "Dinner: Protein + veggies (moderate carbs if needed)",
        "Dim lights after 8:30 PM",
        "Avoid intense work or overthinking late at night",
    ],
    "Night Skincare": [
        "Retinol nights (2-3x/week): Cleanser -> Retinol -> Moisturizer",
        "Non-retinol nights: Cleanser -> Moisturizer only",
    ],
    "Bedtime": [
        "Brush teeth, wash face",
        "5 min journaling if thoughts are racing",
        "In bed by 12:30 AM",
        "Lights out before 1:00 AM",
    ],
    "Weekly Checkpoint": [
        "2 light cardio days",
        "1 full rest day",
        "Change pillowcase weekly",
        "Shower after gym sessions",
    ],
}


def all_items_count() -> int:
    return sum(len(items) for items in PROTOCOL.values())
