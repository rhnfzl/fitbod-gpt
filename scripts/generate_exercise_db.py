#!/usr/bin/env python3
"""
Generate exercise-database.json from the Fitbod2HevyConverter EXERCISE_MAPPING.

Applies pattern-based heuristics to auto-classify each exercise by equipment,
primary/secondary muscles, movement pattern, compound vs isolation, difficulty,
category, and various flags.

Usage:
    python generate_exercise_db.py
"""

import json
import os
import re
from datetime import date
from typing import Any

# ---------------------------------------------------------------------------
# Source data: Fitbod name -> Hevy name (219 exercises)
# ---------------------------------------------------------------------------
EXERCISE_MAPPING: dict[str, str] = {
    "Ab Crunch Machine": "Crunch (Machine)",
    "Air Squats": "Squat (Bodyweight)",
    "Arnold Dumbbell Press": "Arnold Press (Dumbbell)",
    "Assisted Chin Up": "Chin Up (Assisted)",
    "Assisted Dip": "Triceps Dip",
    "Assisted Neutral Grip Pull Up": "Pull Up (Assisted)",
    "Assisted Pull Up": "Pull Up (Assisted)",
    "Assisted Wide Grip Pull Up": "Pull Up (Assisted)",
    "Australian Pull Up": "Inverted Row",
    "Back Extensions": "Back Extension",
    "Back Squat": "Squat (Barbell)",
    "Backward Arm Circle": "Backward Arm Circle",
    "Barbell Bench Press": "Bench Press (Barbell)",
    "Barbell Curl": "Bicep Curl (Barbell)",
    "Barbell Hip Thrust": "Hip Thrust (Barbell)",
    "Barbell Incline Bench Press": "Incline Bench Press (Barbell)",
    "Barbell Lunge": "Lunge (Barbell)",
    "Barbell Shoulder Press": "Overhead Press (Barbell)",
    "Barbell Shrug": "Shrug (Barbell)",
    "Bench Dip": "Bench Dip",
    "Bench T-Spine Stretch": "Bench T-Spine Stretch",
    "Bent Over Barbell Row": "Bent Over Row (Barbell)",
    "Bicycle Crunch": "Bicycle Crunch",
    "Bird Dog": "Bird Dog",
    "Bodyweight Bulgarian Split Squat": "Bulgarian Split Squat",
    "Burpee": "Burpee",
    "Cable Bicep Curl": "Bicep Curl (Cable)",
    "Cable Crossover Fly": "Cable Fly Crossovers",
    "Cable Crunch": "Cable Crunch",
    "Cable Face Pull": "Face Pull",
    "Cable Hip Abduction": "Hip Abduction (Cable)",
    "Cable Hip Adduction": "Hip Adduction (Cable)",
    "Cable Lateral Raise": "Lateral Raise (Cable)",
    "Cable One Arm Tricep Side Extension": "Triceps Extension (Cable)",
    "Cable One Arm Underhand Tricep Extension": "Triceps Extension (Cable)",
    "Cable Rear Delt Fly": "Reverse Fly (Cable)",
    "Cable Rope Overhead Triceps Extension": "Triceps Rope Pushdown",
    "Cable Rope Tricep Extension": "Triceps Rope Pushdown",
    "Cable Row": "Seated Row (Cable)",
    "Cable Tricep Pushdown": "Triceps Pushdown",
    "Cable Underhand Tricep Pushdown": "Triceps Pushdown",
    "Calf Press": "Calf Press (Machine)",
    "Cat Cow": "Cat Cow",
    "Chest Expansion": "Chest Expansion",
    "Chin Up": "Chin Up",
    "Close-Grip Bench Press": "Bench Press - Close Grip (Barbell)",
    "Cross Body Hammer Curls": "Cross Body Hammer Curl (Dumbbell)",
    "Crunches": "Crunch",
    "Cycling": "Cycling",
    "Cycling - Stationary": "Stationary Bike",
    "Dead Bug": "Dead Bug",
    "Dead Hang": "Dead Hang",
    "Deadlift": "Deadlift (Barbell)",
    "Deadlift to Calf Raise": "Deadlift (Barbell)",
    "Decline Crunch": "Decline Crunch",
    "Decline Push Up": "Decline Push Up",
    "Decline Russian Twists": "Russian Twist",
    "Dip": "Dip",
    "Diverging Seated Row": "Seated Row (Machine)",
    "Dumbbell Back Fly": "Reverse Fly (Dumbbell)",
    "Dumbbell Bench Press": "Bench Press (Dumbbell)",
    "Dumbbell Bicep Curl": "Bicep Curl (Dumbbell)",
    "Dumbbell Decline Bench Press": "Decline Bench Press (Dumbbell)",
    "Dumbbell Fly": "Chest Fly (Dumbbell)",
    "Dumbbell Front Raise": "Front Raise (Dumbbell)",
    "Dumbbell Goblet Squat": "Goblet Squat",
    "Dumbbell Incline Bench Press": "Incline Bench Press (Dumbbell)",
    "Dumbbell Incline Fly": "Incline Chest Fly (Dumbbell)",
    "Dumbbell Kickbacks": "Triceps Kickback (Dumbbell)",
    "Dumbbell Lateral Raise": "Lateral Raise (Dumbbell)",
    "Dumbbell Lunge": "Lunge (Dumbbell)",
    "Dumbbell Pullover": "Pullover (Dumbbell)",
    "Dumbbell Rear Delt Raise": "Reverse Fly (Dumbbell)",
    "Dumbbell Romanian Deadlift": "Romanian Deadlift (Dumbbell)",
    "Dumbbell Row": "Dumbbell Row",
    "Dumbbell Shoulder Press": "Shoulder Press (Dumbbell)",
    "Dumbbell Shoulder Raise": "Lateral Raise (Dumbbell)",
    "Dumbbell Shrug": "Shrug (Dumbbell)",
    "Dumbbell Skullcrusher": "Skullcrusher (Dumbbell)",
    "Dumbbell Squat": "Squat (Dumbbell)",
    "Dumbbell Squat To Shoulder Press": "Thruster (Dumbbell)",
    "Dumbbell Superman": "Superman",
    "Dumbbell Tricep Extension": "Triceps Extension (Dumbbell)",
    "Dumbbell Upright Row": "Upright Row (Dumbbell)",
    "Dumbbell Walking Lunge": "Lunge (Dumbbell)",
    "EZ-Bar Curl": "Bicep Curl (EZ Bar)",
    "EZ-Bar Overhead Tricep Extension": "Triceps Extension (Barbell)",
    "EZ-Bar Reverse Grip Curl": "Reverse Curl",
    "Elliptical": "Elliptical Trainer",
    "Face Down Plate Neck Resistance": "Neck Extension",
    "Farmer's Walk": "Farmer's Walk",
    "Forward Arm Circle": "Forward Arm Circle",
    "Forward Lunge with Twist": "Lunge",
    "Front Squat": "Front Squat",
    "Glute Kickback Machine": "Glute Kickback (Machine)",
    "Good Morning": "Good Morning (Barbell)",
    "Hack Squat": "Hack Squat (Machine)",
    "Hammer Curls": "Hammer Curl (Dumbbell)",
    "Hammerstrength Chest Press": "Chest Press (Machine)",
    "Hammerstrength Decline Chest Press": "Decline Bench Press (Machine)",
    "Hammerstrength Incline Chest Press": "Incline Chest Press (Machine)",
    "Hammerstrength Iso Row": "Iso-Lateral Row (Machine)",
    "Hammerstrength Shoulder Press": "Seated Shoulder Press (Machine)",
    "Hanging Knee Raise": "Hanging Knee Raise",
    "Hanging Leg Raise": "Hanging Leg Raise",
    "Hiking": "Hiking",
    "Hip Thrust": "Hip Thrust (Barbell)",
    "Incline Back Extension": "Back Extension",
    "Incline Dumbbell Curl": "Incline Bicep Curl (Dumbbell)",
    "Incline Dumbbell Row": "Incline Row (Dumbbell)",
    "Incline EZ-Bar Curl": "Incline Bicep Curl (EZ Bar)",
    "Incline Hammer Curl": "Incline Hammer Curl (Dumbbell)",
    "Inverted Row": "Inverted Row",
    "Kettlebell Single Arm Farmer Walk": "Farmer's Walk",
    "Kettlebell Swing": "Kettlebell Swing",
    "Kettlebell Swing American": "Kettlebell Swing",
    "Knee Up": "Knee Raise Parallel Bars",
    "Lat Pulldown": "Lat Pulldown (Cable)",
    "Leg Curl": "Seated Leg Curl (Machine)",
    "Leg Extension": "Leg Extension (Machine)",
    "Leg Press": "Leg Press (Machine)",
    "Leg Pull-In": "Leg Pull In",
    "Leg Raise": "Leg Raise",
    "Leg Swing": "Leg Swing",
    "Lunge": "Lunge",
    "Lunge Twist": "Lunge",
    "Lying Hamstrings Curl": "Lying Leg Curl (Machine)",
    "Machine Bench Press": "Chest Press (Machine)",
    "Machine Bicep Curl": "Bicep Curl (Machine)",
    "Machine Fly": "Chest Fly (Machine)",
    "Machine Hip Abductor": "Hip Abduction (Machine)",
    "Machine Hip Adductor": "Hip Adduction (Machine)",
    "Machine Leg Press": "Leg Press (Machine)",
    "Machine Overhead Press": "Seated Shoulder Press (Machine)",
    "Machine Preacher Curl": "Preacher Curl (Machine)",
    "Machine Rear Delt Fly": "Reverse Fly (Machine)",
    "Machine Reverse Fly": "Reverse Fly (Machine)",
    "Machine Row": "Seated Row (Machine)",
    "Machine Shoulder Press": "Seated Shoulder Press (Machine)",
    "Machine Tricep Dip": "Triceps Dip",
    "Machine Tricep Extension": "Triceps Extension (Machine)",
    "Medicine Ball Russian Twist": "Russian Twist",
    "Palms-Down Dumbbell Wrist Curl": "Wrist Curl (Dumbbell)",
    "Palms-Up Dumbbell Wrist Curl": "Wrist Curl (Dumbbell)",
    "Pendlay Row": "Pendlay Row (Barbell)",
    "Plank": "Plank",
    "Plank Shoulder Taps": "Plank",
    "Preacher Curl": "Preacher Curl (EZ Bar)",
    "Pull Up": "Pull Up",
    "Push Press": "Push Press",
    "Push Up": "Push Up",
    "PVC Around the World": "PVC Around the World",
    "Reverse Barbell Curl": "Reverse Curl (Barbell)",
    "Reverse Crunch": "Reverse Crunch",
    "Reverse Dumbbell Curl": "Reverse Curl (Dumbbell)",
    "Romanian Deadlift": "Romanian Deadlift (Barbell)",
    "Rowing": "Rowing Machine",
    "Running": "Running",
    "Running - Treadmill": "Treadmill",
    "Russian Twist": "Russian Twist",
    "Scapular Pull Up": "Scapular Pull-ups",
    "Scissor Crossover Kick": "Scissor Kicks",
    "Scissor Kick": "Scissor Kicks",
    "Seated Back Extension": "Back Extension (Machine)",
    "Seated Cable Row": "Seated Row (Cable)",
    "Seated Dumbbell Curl": "Bicep Curl (Dumbbell)",
    "Seated Figure Four": "Seated Figure Four",
    "Seated Leg Curl": "Seated Leg Curl (Machine)",
    "Seated Machine Calf Press": "Seated Calf Raise",
    "Seated Tricep Press": "Overhead Triceps Extension (Machine)",
    "Side Bridge": "Side Plank",
    "Single Arm Cable Bicep Curl": "Bicep Curl (Cable)",
    "Single Arm Dumbbell Tricep Extension": "Triceps Extension (Dumbbell)",
    "Single Arm Landmine Press": "Landmine Press",
    "Single Leg Cable Kickback": "Single Leg Cable Kickback",
    "Single Leg Glute Bridge": "Single Leg Glute Bridge",
    "Single Leg Leg Extension": "Leg Extension (Machine)",
    "Single Leg Overhead Kettlebell Hold": "Single Leg Overhead Kettlebell Hold",
    "Single Leg Straight Forward Bend": "Single Leg Straight Forward Bend",
    "Sit Up": "Sit Up",
    "Skullcrusher": "Skullcrusher (Barbell)",
    "Sled Push": "Sled Push",
    "Smith Machine Bench Press": "Bench Press (Smith Machine)",
    "Smith Machine Calf Raise": "Standing Calf Raise (Smith Machine)",
    "Smith Machine Incline Bench Press": "Incline Bench Press (Smith Machine)",
    "Smith Machine Squat": "Squat (Smith Machine)",
    "Spider Curls": "Spider Curl (Dumbbell)",
    "Stability Ball Hip Bridge": "Stability Ball Hip Bridge",
    "Stair Stepper": "Stair Machine",
    "Standing Leg Side Hold": "Standing Calf Raise",
    "Standing Machine Calf Press": "Standing Calf Raise",
    "Step Up": "Step Up",
    "Stiff-Legged Barbell Good Morning": "Good Morning (Barbell)",
    "Superman": "Superman",
    "Superman Hold": "Superman",
    "Superman with Scaption": "Superman",
    "T-Bar Row": "T Bar Row",
    "Toe Touchers": "Toe Touchers",
    "Tricep Extension": "Triceps Extension (Dumbbell)",
    "Tricep Push Up": "Diamond Push Up",
    "Tricep Stretch": "Tricep Stretch",
    "Upright Row": "Upright Row (Barbell)",
    "V-Bar Pulldown": "Lat Pulldown (Cable)",
    "Vertical Knee Raise": "Vertical Knee Raise",
    "Walking": "Walking",
    "Walkout to Push Up": "Walkout to Push Up",
    "Wide Grip Lat Pulldown": "Lat Pulldown (Cable)",
    "Zottman Curl": "Zottman Curl (Dumbbell)",
    "Zottman Preacher Curl": "Zottman Preacher Curl (Dumbbell)",
}


# ---------------------------------------------------------------------------
# Classification helpers
# ---------------------------------------------------------------------------

def _lower(name: str) -> str:
    return name.lower()


# ---- Equipment detection ----

def detect_equipment(fitbod: str) -> str:
    """Return an equipment tag from the Fitbod exercise name."""
    fl = _lower(fitbod)

    if "smith machine" in fl:
        return "smith_machine"
    if "hammerstrength" in fl:
        return "machine"
    if fl.startswith("machine ") or "machine" in fl.split():
        return "machine"
    if "cable" in fl:
        return "cable"
    if "barbell" in fl:
        return "barbell"
    if "dumbbell" in fl:
        return "dumbbell"
    if "landmine" in fl or "t-bar" in fl:
        return "barbell"
    if (
        "hammer curl" in fl
        or "cross body hammer" in fl
        or "spider curl" in fl
        or "zottman" in fl
        or fl == "tricep extension"
    ):
        return "dumbbell"
    if "ez-bar" in fl or "ez bar" in fl:
        return "ez_bar"
    if "kettlebell" in fl:
        return "kettlebell"
    if "medicine ball" in fl:
        return "medicine_ball"
    if "stability ball" in fl:
        return "stability_ball"
    if "sled" in fl:
        return "sled"
    if "pvc" in fl:
        return "other"
    if "plate" in fl:
        return "plate"

    # Exercises whose Fitbod name doesn't hint at equipment but aren't bodyweight
    machine_keywords = [
        "leg press", "leg curl", "leg extension", "hack squat",
        "calf press", "ab crunch machine", "glute kickback machine",
        "diverging seated row", "lat pulldown", "v-bar pulldown",
        "wide grip lat pulldown", "hamstrings curl",
    ]
    for kw in machine_keywords:
        if kw in fl:
            return "machine"

    barbell_keywords = [
        "deadlift", "back squat", "front squat", "bench press",
        "pendlay row", "bent over", "good morning", "romanian deadlift",
        "skullcrusher", "close-grip bench", "hip thrust",
        "push press", "upright row",
    ]
    for kw in barbell_keywords:
        if kw in fl:
            # Some of these also appear in dumbbell variants; dumbbell check
            # already ran above so if we are here, it means no "dumbbell" in name.
            return "barbell"

    # Preacher curl (no modifier) typically uses EZ bar
    if fl == "preacher curl":
        return "ez_bar"

    # Bodyweight / no equipment
    return "bodyweight"


# ---- Cardio / mobility detection ----

CARDIO_EXERCISES: set[str] = {
    "cycling", "cycling - stationary", "elliptical", "hiking",
    "rowing", "running", "running - treadmill", "stair stepper",
    "walking",
}

MOBILITY_EXERCISES: set[str] = {
    "backward arm circle", "forward arm circle", "bench t-spine stretch",
    "bird dog", "cat cow", "chest expansion", "dead bug", "dead hang",
    "leg swing", "pvc around the world", "seated figure four",
    "single leg straight forward bend", "tricep stretch",
    "single leg overhead kettlebell hold",
}


# ---- Muscle group mapping ----

# Each rule: (pattern_in_lower_name, primary_muscles, secondary_muscles)
# Order matters: first match wins. More specific patterns first.
MUSCLE_RULES: list[tuple[str, list[str], list[str]]] = [
    # --- Core / Abs ---
    ("crunch", ["abs"], []),
    ("sit up", ["abs"], ["hip_flexors"]),
    ("russian twist", ["obliques", "abs"], []),
    ("plank", ["abs", "obliques"], []),
    ("side bridge", ["obliques", "abs"], []),
    ("hanging knee raise", ["abs", "hip_flexors"], []),
    ("hanging leg raise", ["abs", "hip_flexors"], []),
    ("vertical knee raise", ["abs", "hip_flexors"], []),
    ("knee up", ["abs", "hip_flexors"], []),
    ("leg raise", ["abs", "hip_flexors"], []),
    ("leg pull-in", ["abs", "hip_flexors"], []),
    ("scissor", ["abs", "hip_flexors"], []),
    ("toe toucher", ["abs"], []),
    ("reverse crunch", ["abs"], []),

    # --- Back ---
    ("deadlift to calf raise", ["hamstrings", "glutes", "lower_back"], ["traps", "calves"]),
    ("romanian deadlift", ["hamstrings", "glutes", "lower_back"], ["traps"]),
    ("deadlift", ["hamstrings", "glutes", "lower_back"], ["traps", "quads", "forearms"]),
    ("good morning", ["hamstrings", "lower_back", "glutes"], []),
    ("back extension", ["lower_back", "glutes"], ["hamstrings"]),
    ("superman", ["lower_back", "glutes"], ["hamstrings"]),
    ("t-bar row", ["lats", "upper_back"], ["biceps", "rear_delts"]),
    ("pendlay row", ["lats", "upper_back"], ["biceps", "rear_delts", "lower_back"]),
    ("bent over", ["lats", "upper_back"], ["biceps", "rear_delts", "lower_back"]),
    ("inverted row", ["lats", "upper_back"], ["biceps", "rear_delts"]),
    ("australian pull up", ["lats", "upper_back"], ["biceps", "rear_delts"]),
    ("incline dumbbell row", ["lats", "upper_back"], ["biceps", "rear_delts"]),
    ("dumbbell row", ["lats", "upper_back"], ["biceps", "rear_delts"]),
    ("cable row", ["lats", "upper_back"], ["biceps", "rear_delts"]),
    ("seated cable row", ["lats", "upper_back"], ["biceps", "rear_delts"]),
    ("diverging seated row", ["lats", "upper_back"], ["biceps", "rear_delts"]),
    ("machine row", ["lats", "upper_back"], ["biceps", "rear_delts"]),
    ("hammerstrength iso row", ["lats", "upper_back"], ["biceps", "rear_delts"]),
    ("lat pulldown", ["lats"], ["biceps", "upper_back"]),
    ("v-bar pulldown", ["lats"], ["biceps", "upper_back"]),
    ("wide grip lat pulldown", ["lats"], ["biceps", "upper_back"]),
    ("chin up", ["lats", "biceps"], ["upper_back"]),
    ("pull up", ["lats", "upper_back"], ["biceps"]),
    ("scapular pull up", ["upper_back", "lats"], []),
    ("pullover", ["lats", "chest"], ["triceps"]),

    # --- Chest ---
    ("cable crossover fly", ["chest"], ["front_delts"]),
    ("cable fly", ["chest"], ["front_delts"]),
    ("machine fly", ["chest"], ["front_delts"]),
    ("dumbbell fly", ["chest"], ["front_delts"]),
    ("incline fly", ["upper_chest"], ["front_delts"]),
    ("hammerstrength decline chest press", ["lower_chest", "chest"], ["triceps", "front_delts"]),
    ("hammerstrength incline chest press", ["upper_chest", "chest"], ["triceps", "front_delts"]),
    ("hammerstrength chest press", ["chest"], ["triceps", "front_delts"]),
    ("decline bench press", ["lower_chest", "chest"], ["triceps", "front_delts"]),
    ("incline bench press", ["upper_chest", "chest"], ["triceps", "front_delts"]),
    ("close-grip bench press", ["triceps", "chest"], ["front_delts"]),
    ("bench press", ["chest"], ["triceps", "front_delts"]),
    ("chest press", ["chest"], ["triceps", "front_delts"]),
    ("walkout to push up", ["chest", "abs"], ["triceps", "front_delts"]),
    ("diamond push up", ["triceps", "chest"], ["front_delts"]),
    ("tricep push up", ["triceps", "chest"], ["front_delts"]),
    ("decline push up", ["upper_chest", "chest"], ["triceps", "front_delts"]),
    ("push up", ["chest"], ["triceps", "front_delts"]),
    ("landmine press", ["upper_chest", "front_delts"], ["triceps"]),

    # --- Mixed / athletic compounds ---
    ("squat to shoulder press", ["quads", "glutes", "front_delts"], ["triceps", "hamstrings"]),

    # --- Shoulders ---
    ("arnold", ["front_delts", "side_delts"], ["triceps"]),
    ("shoulder press", ["front_delts", "side_delts"], ["triceps"]),
    ("overhead press", ["front_delts", "side_delts"], ["triceps"]),
    ("push press", ["front_delts", "side_delts"], ["triceps", "quads"]),
    ("lateral raise", ["side_delts"], []),
    ("shoulder raise", ["side_delts"], []),
    ("front raise", ["front_delts"], []),
    ("face pull", ["rear_delts", "upper_back"], []),
    ("rear delt", ["rear_delts"], []),
    ("reverse fly", ["rear_delts"], ["upper_back"]),
    ("dumbbell back fly", ["rear_delts"], ["upper_back"]),
    ("upright row", ["side_delts", "traps"], ["biceps"]),
    ("shrug", ["traps"], []),
    ("neck", ["neck"], []),

    # --- Legs / hips that would otherwise match generic arm rules ---
    ("glute kickback", ["glutes"], ["hamstrings"]),
    ("cable kickback", ["glutes"], ["hamstrings"]),
    ("leg curl", ["hamstrings"], []),
    ("hamstrings curl", ["hamstrings"], []),
    ("wrist curl", ["forearms"], []),

    # --- Arms: Biceps ---
    ("zottman preacher curl", ["biceps", "forearms"], []),
    ("spider curl", ["biceps"], ["forearms"]),
    ("preacher curl", ["biceps"], ["forearms"]),
    ("hammer curl", ["biceps", "forearms"], []),
    ("cross body hammer", ["biceps", "forearms"], []),
    ("zottman curl", ["biceps", "forearms"], []),
    ("reverse.*curl", ["forearms", "biceps"], []),
    ("curl", ["biceps"], ["forearms"]),

    # --- Arms: Triceps ---
    ("bench dip", ["triceps"], ["chest", "front_delts"]),
    ("skullcrusher", ["triceps"], []),
    ("triceps? extension", ["triceps"], []),
    ("triceps? pushdown", ["triceps"], []),
    ("triceps? rope", ["triceps"], []),
    ("triceps? push", ["triceps"], []),
    ("triceps? press", ["triceps"], []),
    ("tricep", ["triceps"], []),
    ("kickback", ["triceps"], []),
    ("dip", ["triceps", "chest"], ["front_delts"]),

    # --- Legs ---
    ("hip thrust", ["glutes", "hamstrings"], []),
    ("glute bridge", ["glutes", "hamstrings"], []),
    ("hip abduction", ["glutes"], []),
    ("hip abductor", ["glutes"], []),
    ("hip adduction", ["adductors"], []),
    ("hip adductor", ["adductors"], []),
    ("hack squat", ["quads", "glutes"], ["hamstrings"]),
    ("front squat", ["quads", "glutes"], ["hamstrings", "abs"]),
    ("goblet squat", ["quads", "glutes"], ["hamstrings"]),
    ("bulgarian split squat", ["quads", "glutes"], ["hamstrings"]),
    ("squat", ["quads", "glutes"], ["hamstrings"]),
    ("lunge", ["quads", "glutes"], ["hamstrings"]),
    ("step up", ["quads", "glutes"], ["hamstrings"]),
    ("leg press", ["quads", "glutes"], ["hamstrings"]),
    ("leg extension", ["quads"], []),
    ("calf press", ["calves"], []),
    ("calf raise", ["calves"], []),
    ("standing leg side hold", ["calves"], []),

    # --- Carries ---
    ("farmer", ["forearms", "traps"], ["abs"]),
    ("sled push", ["quads", "glutes"], ["calves", "hamstrings"]),

    # --- Cardio ---
    ("cycling", ["quads", "hamstrings"], ["calves"]),
    ("stationary", ["quads", "hamstrings"], ["calves"]),
    ("elliptical", ["quads", "hamstrings"], ["glutes"]),
    ("hiking", ["quads", "glutes"], ["calves", "hamstrings"]),
    ("rowing", ["lats", "upper_back"], ["biceps", "quads"]),
    ("running", ["quads", "hamstrings"], ["calves", "glutes"]),
    ("treadmill", ["quads", "hamstrings"], ["calves", "glutes"]),
    ("stair", ["quads", "glutes"], ["calves"]),
    ("walking", ["quads", "glutes"], ["calves"]),
    ("burpee", ["quads", "chest"], ["triceps", "abs", "front_delts"]),
    ("kettlebell swing", ["glutes", "hamstrings"], ["lower_back", "abs", "front_delts"]),

    # --- Mobility / stability (catch-all) ---
    ("t-spine", ["upper_back", "shoulders"], []),
    ("arm circle", ["shoulders"], []),
    ("cat cow", ["lower_back", "abs"], []),
    ("chest expansion", ["chest", "shoulders"], []),
    ("bird dog", ["abs", "lower_back"], ["glutes"]),
    ("dead bug", ["abs"], []),
    ("dead hang", ["forearms", "lats"], []),
    ("leg swing", ["hip_flexors"], []),
    ("pvc around the world", ["shoulders"], []),
    ("seated figure four", ["glutes", "hip_flexors"], []),
    ("single leg straight forward bend", ["hamstrings"], []),
    ("tricep stretch", ["triceps"], []),
    ("stability ball hip bridge", ["glutes", "hamstrings"], ["abs"]),
    ("single leg overhead kettlebell hold", ["shoulders", "abs"], []),
]


def detect_muscles(fitbod: str) -> tuple[list[str], list[str]]:
    """Return (primary_muscles, secondary_muscles) for the Fitbod exercise name."""
    fl = _lower(fitbod)
    for pattern, primary, secondary in MUSCLE_RULES:
        if re.search(pattern, fl):
            return list(primary), list(secondary)
    # Fallback
    return ["full_body"], []


# ---- Movement pattern ----

MOVEMENT_PATTERN_RULES: list[tuple[str, str]] = [
    # Horizontal push
    ("bench press", "horizontal_push"),
    ("chest press", "horizontal_push"),
    ("walkout to push up", "horizontal_push"),
    ("diamond push up", "horizontal_push"),
    ("tricep push up", "horizontal_push"),
    ("decline push up", "horizontal_push"),
    ("push up", "horizontal_push"),
    ("fly", "horizontal_push"),  # chest fly is a push accessory
    ("landmine press", "horizontal_push"),

    # Horizontal pull
    ("row", "horizontal_pull"),
    ("inverted row", "horizontal_pull"),
    ("australian pull up", "horizontal_pull"),
    ("face pull", "horizontal_pull"),

    # Vertical push
    ("shoulder press", "vertical_push"),
    ("overhead press", "vertical_push"),
    ("arnold", "vertical_push"),
    ("push press", "vertical_push"),
    ("squat to shoulder press", "vertical_push"),
    ("lateral raise", "isolation_push"),
    ("shoulder raise", "isolation_push"),
    ("front raise", "isolation_push"),

    # Vertical pull
    ("pull up", "vertical_pull"),
    ("chin up", "vertical_pull"),
    ("lat pulldown", "vertical_pull"),
    ("v-bar pulldown", "vertical_pull"),
    ("pullover", "vertical_pull"),

    # Hip hinge
    ("deadlift", "hip_hinge"),
    ("romanian deadlift", "hip_hinge"),
    ("good morning", "hip_hinge"),
    ("hip thrust", "hip_hinge"),
    ("glute bridge", "hip_hinge"),
    ("kettlebell swing", "hip_hinge"),
    ("back extension", "hip_hinge"),
    ("superman", "hip_hinge"),
    ("glute kickback", "hip_hinge"),
    ("cable kickback", "hip_hinge"),

    # Lunge (before squat so "bulgarian split squat" matches lunge first)
    ("bulgarian split squat", "lunge"),
    ("lunge", "lunge"),
    ("step up", "lunge"),

    # Squat
    ("squat", "squat"),
    ("leg press", "squat"),
    ("hack squat", "squat"),

    # Isolation push
    ("bench dip", "isolation_push"),
    ("dip", "isolation_push"),
    ("tricep stretch", "mobility"),
    ("tricep press", "isolation_push"),
    ("tricep", "isolation_push"),
    ("extension", "isolation_push"),
    ("pushdown", "isolation_push"),
    ("skullcrusher", "isolation_push"),
    ("kickback", "isolation_push"),
    ("tricep rope", "isolation_push"),
    ("leg extension", "isolation_push"),
    ("calf press", "isolation_push"),
    ("calf raise", "isolation_push"),
    ("hip abduction", "isolation_push"),
    ("hip abductor", "isolation_push"),
    ("shrug", "isolation_push"),
    ("sled push", "isolation_push"),

    # Isolation pull
    ("hammer curl", "isolation_pull"),
    ("zottman preacher curl", "isolation_pull"),
    ("reverse fly", "isolation_pull"),
    ("rear delt", "isolation_pull"),
    ("dumbbell back fly", "isolation_pull"),
    ("leg curl", "isolation_pull"),
    ("hamstrings curl", "isolation_pull"),
    ("hip adduction", "isolation_pull"),
    ("hip adductor", "isolation_pull"),
    ("wrist curl", "isolation_pull"),
    ("curl", "isolation_pull"),
    ("neck", "isolation_pull"),

    # Core
    ("crunch", "core"),
    ("sit up", "core"),
    ("russian twist", "core"),
    ("plank", "core"),
    ("side bridge", "core"),
    ("hanging knee raise", "core"),
    ("hanging leg raise", "core"),
    ("vertical knee raise", "core"),
    ("knee up", "core"),
    ("leg raise", "core"),
    ("leg pull-in", "core"),
    ("scissor", "core"),
    ("toe toucher", "core"),
    ("reverse crunch", "core"),
    ("bird dog", "core"),
    ("dead bug", "core"),

    # Locomotion / cardio
    ("cycling", "locomotion"),
    ("stationary", "locomotion"),
    ("elliptical", "locomotion"),
    ("hiking", "locomotion"),
    ("rowing", "locomotion"),
    ("running", "locomotion"),
    ("treadmill", "locomotion"),
    ("stair", "locomotion"),
    ("walking", "locomotion"),
    ("burpee", "locomotion"),

    # Carry
    ("farmer", "carry"),

    # Mobility
    ("arm circle", "mobility"),
    ("cat cow", "mobility"),
    ("chest expansion", "mobility"),
    ("dead hang", "mobility"),
    ("leg swing", "mobility"),
    ("pvc around the world", "mobility"),
    ("seated figure four", "mobility"),
    ("single leg straight forward bend", "mobility"),
    ("tricep stretch", "mobility"),
    ("bench t-spine stretch", "mobility"),
    ("stability ball hip bridge", "mobility"),
    ("single leg overhead kettlebell hold", "mobility"),
    ("standing leg side hold", "mobility"),
    ("scapular pull up", "mobility"),
]


def detect_movement_pattern(fitbod: str) -> str:
    fl = _lower(fitbod)
    for pattern, mp in MOVEMENT_PATTERN_RULES:
        if pattern in fl:
            return mp
    return "other"


# ---- Compound vs isolation ----

COMPOUND_PATTERNS: list[str] = [
    "bench press", "chest press", "push up", "decline push up", "diamond push up",
    "walkout to push up", "landmine press",
    "row", "inverted row", "australian pull up",
    "shoulder press", "overhead press", "arnold", "push press",
    "pull up", "chin up", "lat pulldown", "v-bar pulldown",
    "squat", "leg press", "hack squat", "lunge", "step up",
    "bulgarian split squat",
    "deadlift", "romanian deadlift", "good morning",
    "hip thrust", "glute bridge",
    "dip", "burpee", "kettlebell swing",
    "upright row", "pullover", "sled push",
    "farmer",
]


def detect_compound(fitbod: str) -> bool:
    fl = _lower(fitbod)
    for p in COMPOUND_PATTERNS:
        if p in fl:
            return True
    return False


# ---- Difficulty ----

def detect_difficulty(fitbod: str, equipment: str, is_compound: bool) -> str:
    fl = _lower(fitbod)

    # Advanced exercises
    advanced_kw = [
        "push press", "front squat", "pendlay row",
        "hack squat", "scapular pull up", "walkout to push up",
    ]
    for kw in advanced_kw:
        if kw in fl:
            return "advanced"

    # Bodyweight compounds requiring good strength
    if fl in ("pull up", "chin up", "dip"):
        return "intermediate"

    # Assisted exercises are beginner-friendly
    if "assisted" in fl:
        return "beginner"

    # Machine and bodyweight basics are beginner-friendly
    if equipment in ("machine", "bodyweight"):
        if is_compound and equipment == "bodyweight" and fl not in CARDIO_EXERCISES and fl not in MOBILITY_EXERCISES:
            return "intermediate"
        return "beginner"

    # Free weights are generally intermediate
    if equipment in ("barbell", "dumbbell", "ez_bar", "kettlebell", "smith_machine"):
        return "intermediate"

    return "beginner"


# ---- Category ----

def detect_category(fitbod: str) -> str:
    fl = _lower(fitbod)
    if fl in CARDIO_EXERCISES:
        return "cardio"
    if fl in MOBILITY_EXERCISES:
        return "mobility"
    return "strength"


# ---- Bodyweight flag ----

BODYWEIGHT_EXERCISES: set[str] = {
    "air squats", "australian pull up", "bicycle crunch", "bird dog",
    "bodyweight bulgarian split squat", "burpee", "chin up", "crunches",
    "dead bug", "dead hang", "decline crunch", "decline push up",
    "decline russian twists", "dip", "forward lunge with twist",
    "hanging knee raise", "hanging leg raise", "inverted row",
    "knee up", "leg pull-in", "leg raise", "lunge", "lunge twist",
    "medicine ball russian twist", "plank", "plank shoulder taps",
    "pull up", "push up", "reverse crunch", "russian twist",
    "scapular pull up", "scissor crossover kick", "scissor kick",
    "side bridge", "sit up", "step up", "superman", "superman hold",
    "superman with scaption", "toe touchers", "tricep push up",
    "vertical knee raise", "walkout to push up",
    "assisted chin up", "assisted dip", "assisted neutral grip pull up",
    "assisted pull up", "assisted wide grip pull up",
    # Mobility bodyweight
    "backward arm circle", "forward arm circle", "bench t-spine stretch",
    "cat cow", "chest expansion", "leg swing", "seated figure four",
    "single leg straight forward bend", "tricep stretch",
    # Bodyweight legs
    "single leg glute bridge",
}


def is_bodyweight(fitbod: str, equipment: str) -> bool:
    if _lower(fitbod) in {e.lower() for e in BODYWEIGHT_EXERCISES}:
        return True
    return equipment == "bodyweight" and _lower(fitbod) not in {
        "bench dip", "dumbbell superman",
    }


# ---- Unilateral flag ----

UNILATERAL_PATTERNS: list[str] = [
    "single arm", "single leg", "one arm",
    "cross body hammer", "dumbbell row",
    "kettlebell single arm",
]


def is_unilateral(fitbod: str) -> bool:
    fl = _lower(fitbod)
    for p in UNILATERAL_PATTERNS:
        if p in fl:
            return True
    # Walking lunges and Bulgarian split squats are unilateral
    if "walking lunge" in fl or "bulgarian split squat" in fl:
        return True
    return False


# ---------------------------------------------------------------------------
# Build a single exercise entry
# ---------------------------------------------------------------------------

def build_exercise(fitbod_name: str, hevy_name: str) -> dict[str, Any]:
    equipment = detect_equipment(fitbod_name)
    primary, secondary = detect_muscles(fitbod_name)
    movement = detect_movement_pattern(fitbod_name)
    compound = detect_compound(fitbod_name)
    category = detect_category(fitbod_name)
    difficulty = detect_difficulty(fitbod_name, equipment, compound)
    bw = is_bodyweight(fitbod_name, equipment)
    uni = is_unilateral(fitbod_name)

    return {
        "fitbod_name": fitbod_name,
        "hevy_name": hevy_name,
        "equipment": equipment,
        "primary_muscles": primary,
        "secondary_muscles": secondary,
        "movement_pattern": movement,
        "is_compound": compound,
        "difficulty": difficulty,
        "category": category,
        "is_bodyweight": bw,
        "is_unilateral": uni,
    }


# ---------------------------------------------------------------------------
# Reference lists
# ---------------------------------------------------------------------------

ALL_MUSCLE_GROUPS: list[str] = sorted({
    "abs", "obliques", "hip_flexors", "lower_back",
    "lats", "upper_back", "traps", "rear_delts",
    "chest", "upper_chest", "lower_chest",
    "front_delts", "side_delts", "shoulders",
    "biceps", "triceps", "forearms",
    "quads", "hamstrings", "glutes", "calves", "adductors",
    "neck", "full_body",
})

ALL_MOVEMENT_PATTERNS: list[str] = sorted({
    "horizontal_push", "horizontal_pull",
    "vertical_push", "vertical_pull",
    "hip_hinge", "squat", "lunge",
    "isolation_push", "isolation_pull",
    "core", "locomotion", "carry", "mobility", "other",
})

ALL_EQUIPMENT_TYPES: list[str] = sorted({
    "barbell", "dumbbell", "cable", "machine", "kettlebell",
    "smith_machine", "ez_bar", "bodyweight", "medicine_ball",
    "stability_ball", "sled", "plate", "other",
})


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    exercises = []
    for fitbod_name, hevy_name in sorted(EXERCISE_MAPPING.items()):
        exercises.append(build_exercise(fitbod_name, hevy_name))

    db = {
        "version": "1.0",
        "generated": str(date.today()),
        "source": f"Fitbod2HevyConverter EXERCISE_MAPPING ({len(EXERCISE_MAPPING)} exercises)",
        "exercises": exercises,
        "muscle_groups": ALL_MUSCLE_GROUPS,
        "movement_patterns": ALL_MOVEMENT_PATTERNS,
        "equipment_types": ALL_EQUIPMENT_TYPES,
    }

    output_path = os.path.join(os.path.dirname(__file__), "..", "knowledge", "exercise-database.json")
    output_path = os.path.normpath(output_path)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Wrote {len(exercises)} exercises to {output_path}")

    # Quick summary stats
    equipment_counts: dict[str, int] = {}
    category_counts: dict[str, int] = {}
    pattern_counts: dict[str, int] = {}
    for ex in exercises:
        equipment_counts[ex["equipment"]] = equipment_counts.get(ex["equipment"], 0) + 1
        category_counts[ex["category"]] = category_counts.get(ex["category"], 0) + 1
        pattern_counts[ex["movement_pattern"]] = pattern_counts.get(ex["movement_pattern"], 0) + 1

    print("\nEquipment breakdown:")
    for k, v in sorted(equipment_counts.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")

    print("\nCategory breakdown:")
    for k, v in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")

    print("\nMovement pattern breakdown:")
    for k, v in sorted(pattern_counts.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
