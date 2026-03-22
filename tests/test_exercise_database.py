"""Regression tests for generated GPT knowledge files.

These tests validate the knowledge files that get uploaded to ChatGPT.
They are self-contained and do not require the fitbod-report repo.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXERCISE_DB_PATH = ROOT / "knowledge" / "exercise-database.json"
FORMAT_GUIDE_TXT_PATH = ROOT / "knowledge" / "report-format-guide.txt"


def _load_exercises():
    data = json.loads(EXERCISE_DB_PATH.read_text())
    return {entry["fitbod_name"]: entry for entry in data["exercises"]}


def test_regression_exercise_classifications():
    exercises = _load_exercises()

    assert exercises["Leg Curl"]["primary_muscles"] == ["hamstrings"]
    assert exercises["Lying Hamstrings Curl"]["primary_muscles"] == ["hamstrings"]
    assert exercises["Seated Leg Curl"]["primary_muscles"] == ["hamstrings"]
    assert exercises["Glute Kickback Machine"]["primary_muscles"] == ["glutes"]
    assert exercises["Single Leg Cable Kickback"]["primary_muscles"] == ["glutes"]
    assert exercises["Bench Dip"]["primary_muscles"] == ["triceps"]

    assert exercises["Cross Body Hammer Curls"]["equipment"] == "dumbbell"
    assert exercises["Hammer Curls"]["equipment"] == "dumbbell"
    assert exercises["Single Arm Landmine Press"]["equipment"] == "barbell"
    assert exercises["T-Bar Row"]["equipment"] == "barbell"


def test_format_guide_covers_all_five_formats():
    """The .txt file uploaded to ChatGPT must document all 5 input formats."""
    guide = FORMAT_GUIDE_TXT_PATH.read_text()

    # All five format detection rules present
    assert 'Starts with "date_range:"' in guide
    assert 'Starts with "{"' in guide
    assert 'Starts with "report_type:"' in guide
    assert 'Starts with "# Workout"' in guide
    assert 'Starts with "Date,Exercise,Reps"' in guide

    # Key sections present
    assert "TSV FORMAT" in guide or "1. TSV" in guide
    assert "JSON FORMAT" in guide or "2. JSON" in guide
    assert "YAML FORMAT" in guide or "3. YAML" in guide
    assert "MARKDOWN FORMAT" in guide or "4. Markdown" in guide.upper()
    assert "RAW FITBOD CSV" in guide

    # Core fields documented
    assert "working_sets" in guide
    assert "warmup_sets" in guide
    assert "is_cardio" in guide
    assert "isWarmup" in guide  # raw CSV column


def test_exercise_db_structure():
    """Exercise DB JSON has the expected top-level keys and exercise shape."""
    data = json.loads(EXERCISE_DB_PATH.read_text())

    assert "exercises" in data
    assert "muscle_groups" in data or "version" in data
    assert len(data["exercises"]) > 200

    ex = data["exercises"][0]
    for key in ["fitbod_name", "equipment", "primary_muscles", "movement_pattern", "is_compound", "category"]:
        assert key in ex, f"Missing key: {key}"
