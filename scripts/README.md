# Scripts

## generate_exercise_db.py

Generates the `knowledge/exercise-database.json` file used by FitbodGPT as a knowledge file. It classifies all 209 known Fitbod exercises by muscle groups, equipment, movement patterns, and other attributes.

### What it does

1. Takes the built-in `EXERCISE_MAPPING` dictionary (Fitbod exercise names mapped to Hevy exercise names)
2. Applies pattern-based rules to classify each exercise:
   - **Equipment**: barbell, dumbbell, cable, machine, kettlebell, smith machine, bodyweight, etc.
   - **Primary/secondary muscles**: chest, back, quads, hamstrings, biceps, triceps, etc.
   - **Movement pattern**: horizontal push, vertical pull, squat, hip hinge, core, etc.
   - **Compound vs isolation**: multi-joint or single-joint
   - **Difficulty**: beginner, intermediate, advanced
   - **Category**: strength, cardio, mobility
   - **Flags**: bodyweight, unilateral
3. Outputs `knowledge/exercise-database.json` with all classifications

### How to run

```bash
cd scripts
python generate_exercise_db.py
```

Output goes to `../knowledge/exercise-database.json`. The script prints a summary showing equipment, category, and movement pattern breakdowns.

### When to run

- After adding new exercises to the `EXERCISE_MAPPING` dictionary inside the script
- After changing classification rules
- You do not need to run this regularly. Only run it when updating the exercise list.

### Adding new exercises

1. Add the Fitbod exercise name and its Hevy equivalent to `EXERCISE_MAPPING` at the top of the script
2. The classification rules will auto-assign muscle groups, equipment, and patterns based on name matching
3. Run the script to regenerate the JSON
4. Review the output to verify the new exercises were classified correctly
5. Also update `exercise_db.py` in the [fitbod-report](https://github.com/rhnfzl/fitbod-report) repo (`src/data/exercise_db.py`) so the GPT report format can compute muscle volumes for the new exercises

### Classification rules

The script uses keyword matching on exercise names. For example:

- "Bench Press" in the name -> chest as primary muscle, horizontal push pattern
- "Barbell" in the name -> barbell equipment
- "Curl" in the name -> biceps as primary muscle, isolation pull pattern
- "Squat" in the name -> quads/glutes as primary, squat pattern

Rules are applied in priority order, so more specific patterns (like "Bulgarian Split Squat") match before generic ones (like "Squat"). If no rule matches, the exercise gets a fallback classification that you should review and correct.

### Output format

```json
{
  "version": "1.0",
  "generated": "2026-03-22",
  "source": "...",
  "exercises": [
    {
      "fitbod_name": "Barbell Bench Press",
      "hevy_name": "Bench Press (Barbell)",
      "equipment": "barbell",
      "primary_muscles": ["chest"],
      "secondary_muscles": ["front_delts", "triceps"],
      "movement_pattern": "horizontal_push",
      "is_compound": true,
      "difficulty": "intermediate",
      "category": "strength",
      "is_bodyweight": false,
      "is_unilateral": false
    }
  ],
  "muscle_groups": ["chest", "back", ...],
  "movement_patterns": ["horizontal_push", ...],
  "equipment_types": ["barbell", ...]
}
```
