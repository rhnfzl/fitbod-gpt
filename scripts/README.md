# Scripts

## generate_exercise_db.py

Generates the `knowledge/exercise-database.json` file used by FitbodGPT as a knowledge file.

**Important**: The current `exercise-database.json` (v2.0) contains ~1,089 exercises — 209 core exercises from this script's `EXERCISE_MAPPING` plus ~880 additional exercises merged from the Fitbod website. Running this script will overwrite that with only the 209 core exercises. Use `--force` if that's intentional.

### What it does

1. Takes the built-in `EXERCISE_MAPPING` dictionary (Fitbod exercise names mapped to common alternative names)
2. Applies pattern-based rules to classify each exercise:
   - **Equipment**: barbell, dumbbell, cable, machine, kettlebell, smith machine, bodyweight, etc.
   - **Primary/secondary muscles**: chest, back, quads, hamstrings, biceps, triceps, etc.
   - **Movement pattern**: horizontal push, vertical pull, squat, hip hinge, core, etc.
   - **Compound vs isolation**: multi-joint or single-joint
   - **Difficulty**: beginner, intermediate, advanced
   - **Category**: strength, cardio, mobility, plyometric
   - **Flags**: bodyweight, unilateral
3. Outputs `knowledge/exercise-database.json` with all classifications

### How to run

```bash
cd scripts
python generate_exercise_db.py --force
```

### When to run

- After adding new exercises to the `EXERCISE_MAPPING` dictionary inside the script
- After changing classification rules
- You do not need to run this regularly. Only run it when updating the core exercise list.

### Adding new exercises

1. Add the Fitbod exercise name and its common alternative name to `EXERCISE_MAPPING` at the top of the script
2. The classification rules will auto-assign muscle groups, equipment, and patterns based on name matching
3. Run the script with `--force` to regenerate the JSON
4. Review the output to verify the new exercises were classified correctly
5. Also update `exercise_db.py` in the [fitbod-report](https://github.com/rhnfzl/fitbod-report) repo (`src/data/exercise_db.py`) so the GPT report format can compute muscle volumes for the new exercises

### Output format

```json
{
  "version": "2.0",
  "generated": "2026-03-23",
  "exercises": [
    {
      "fitbod_name": "Barbell Bench Press",
      "alternative_names": ["Bench Press (Barbell)"],
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
  "equipment_types": ["barbell", ...],
  "categories": ["strength", ...]
}
```
