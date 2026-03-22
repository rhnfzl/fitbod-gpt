# FitbodGPT Report Format Parsing Reference

This document describes how to parse Fitbod workout report data. Reports can arrive in one of four formats: GPT, JSON, YAML, or Markdown. Detect the format first, then parse accordingly.

---

## Format Detection

Use the opening characters of the content to determine the format:

```python
def detect_format(content):
    content = content.strip()
    if content.startswith('date_range:'):
        return 'gpt'
    if content.startswith('{'):
        return 'json'
    if content.startswith('report_type:') or content.startswith('---'):
        return 'yaml'
    if content.startswith('# Workout'):
        return 'markdown'
    return 'unknown'
```

---

## Key Fields Reference

Before diving into formats, understand the core fields that appear across all of them.

| Field | Description |
|---|---|
| **working_sets** | Number of non-warmup sets. This is the primary metric for volume analysis. |
| **warmup_sets** | Warmup sets. **IGNORE these for all analysis.** |
| **volume** | weight x reps (working sets only), expressed in kg\*reps or lbs\*reps. |
| **max_weight** | Heaviest weight used for that exercise in the period. |
| **is_cardio** | Boolean. Cardio exercises have duration/distance instead of weight/reps. |
| **trend** | Percentage change over the report period. Positive means improving. |
| **total_workout_time** | Combined cardio + strength duration for the period (in minutes). |
| **total_distance** | Distance covered during cardio exercises. Unit depends on unit system. |

### Unit System

Always check the `unit_system` (JSON/YAML) or `unit` (GPT format) field:

- **metric**: Weight in kg, distance in km.
- **imperial**: Weight in lbs, distance in miles.

---

## 1. GPT Format (Preferred)

The most token-efficient format. Starts with `date_range:` metadata. Data is TSV-based and organized into named sections.

### Structure

```
date_range: 2024-01-01 to 2024-03-15
weeks: 11
sessions: 33
unit: metric
exercises: 24

## weekly_summary
week	sessions	strength_min	cardio_min	volume_kg	reps	distance_km
2024-01-01	3	145	30	12450	342	5.2

## exercise_stats
exercise	sessions	working_sets	total_reps	max_kg	avg_kg	total_volume	trend
Barbell Bench Press	22	66	528	80.0	65.5	34584	+5.2%

## muscle_volume
muscle	weekly_avg_sets	trend
chest	14	+2.1%

## recent_sessions
date	exercises
2024-03-14	Barbell Bench Press:3x8@75kg,Dumbbell Incline Press:3x10@30kg
```

### Header

The lines before the first `## ` section are key-value metadata pairs separated by `:`.

### Sections

Each `## section_name` line starts a new TSV section. The first line after the section heading is the column header row; subsequent lines are data rows.

- **weekly_summary** -- One row per week with session counts, time breakdowns, volume, reps, and distance.
- **exercise_stats** -- One row per exercise with aggregated stats across the report period.
- **muscle_volume** -- One row per muscle group with average weekly sets and trend.
- **recent_sessions** -- One row per recent workout date with a compact exercise notation (`Name:SetsxReps@Weight`).

### Parsing

```python
import csv


def parse_gpt_format(text):
    """Parse the GPT TSV format into a header dict and sections dict."""
    sections = {}
    current = None
    lines = text.strip().split('\n')
    header = {}

    for line in lines:
        if line.startswith('## '):
            current = line[3:].strip().split(' ')[0]
            sections[current] = []
            continue
        if current is None and ':' in line:
            key, val = line.split(':', 1)
            header[key.strip()] = val.strip()
        elif current and line.strip():
            sections[current].append(line)

    # Parse each section as TSV
    for key in sections:
        reader = csv.DictReader(sections[key], delimiter='\t')
        sections[key] = list(reader)

    return header, sections
```

#### Example Usage

```python
header, sections = parse_gpt_format(content)

# Access metadata
date_range = header['date_range']       # "2024-01-01 to 2024-03-15"
unit = header['unit']                    # "metric"

# Iterate weekly summaries
for week in sections['weekly_summary']:
    print(week['week'], week['volume_kg'])

# Find top exercises by volume
exercises = sections['exercise_stats']
exercises.sort(key=lambda e: float(e['total_volume']), reverse=True)
for ex in exercises[:5]:
    print(ex['exercise'], ex['total_volume'], ex['trend'])

# Parse recent session exercise notation
import re

def parse_session_exercises(compact_str):
    """Parse 'Bench Press:3x8@75kg,Curls:3x10@15kg' into structured data."""
    results = []
    for item in compact_str.split(','):
        match = re.match(r'(.+?):(\d+)x(\d+)@([\d.]+)(\w+)', item.strip())
        if match:
            results.append({
                'name': match.group(1),
                'sets': int(match.group(2)),
                'reps': int(match.group(3)),
                'weight': float(match.group(4)),
                'unit': match.group(5),
            })
    return results
```

---

## 2. JSON Format

Starts with `{`. This is the most detailed format with full per-set data available in the "detailed" variant.

### Top-Level Structure

```json
{
  "report_type": "weekly",
  "grouping_mode": "calendar",
  "unit_system": "metric",
  "format": "summary",
  "periods": [],
  "overall": {}
}
```

| Field | Values | Description |
|---|---|---|
| `report_type` | `daily`, `weekly`, `monthly`, `quarterly`, `half-yearly`, `yearly` | The period type for grouping. |
| `grouping_mode` | `calendar`, `rolling` | Whether periods align to calendar boundaries or roll from the start date. |
| `unit_system` | `metric`, `imperial` | Weight and distance units. |
| `format` | `summary`, `detailed` | Summary omits per-set data; detailed includes it. |

### Period Object

Each element in `periods[]`:

```json
{
  "date": "2024-01-01",
  "day_of_week": "Monday",
  "end_date": "2024-01-07",
  "period": "Week 1",
  "exercises": [],
  "stats": {
    "total_workout_time": 175,
    "strength_time": 145,
    "cardio_time": 30,
    "total_distance": 5.2,
    "total_reps": 342,
    "total_volume": 12450
  }
}
```

- `end_date` and `period` are optional (present for multi-day report types).
- `day_of_week` is present for daily reports.

### Exercise Object

Each element in a period's `exercises[]`:

```json
{
  "name": "Barbell Bench Press",
  "working_sets": 3,
  "warmup_sets": 1,
  "total_reps": 24,
  "max_weight": 80.0,
  "weight_unit": "kg",
  "total_volume": 1920,
  "is_cardio": false,
  "sets": [
    {"weight": 80.0, "reps": 8, "type": "working"},
    {"weight": 75.0, "reps": 8, "type": "working"},
    {"weight": 75.0, "reps": 8, "type": "working"}
  ]
}
```

- `sets[]` is only present when `format` is `"detailed"`.
- Each set has `weight`, `reps`, and `type` (`"working"` or `"warmup"`).
- Cardio exercises (`is_cardio: true`) may have `duration` and `distance` fields instead of `weight`/`reps`.

### Overall Object

Aggregated stats across all periods:

```json
{
  "date_range": {"start": "2024-01-01", "end": "2024-03-15"},
  "total_sessions": 33,
  "total_workout_time": 5775,
  "total_volume": 410400,
  "total_reps": 11286,
  "total_distance": 57.2,
  "averages": {
    "sessions_per_week": 3.0,
    "volume_per_session": 12436,
    "reps_per_session": 342,
    "workout_time_per_session": 175
  }
}
```

### Parsing

```python
import json


def parse_json_format(content):
    data = json.loads(content)

    unit = data.get('unit_system', 'metric')
    report_type = data.get('report_type', 'weekly')

    for period in data.get('periods', []):
        date = period['date']
        stats = period.get('stats', {})
        volume = stats.get('total_volume', 0)

        for exercise in period.get('exercises', []):
            name = exercise['name']
            working = exercise.get('working_sets', 0)
            max_w = exercise.get('max_weight', 0)
            is_cardio = exercise.get('is_cardio', False)

            # Access per-set data if available (detailed format)
            for s in exercise.get('sets', []):
                if s.get('type') == 'working':
                    print(f"  {s['weight']} x {s['reps']}")

    overall = data.get('overall', {})
    averages = overall.get('averages', {})
    return data
```

---

## 3. YAML Format

Starts with `report_type:` or `---`. The structure is identical to JSON.

### Example

```yaml
report_type: weekly
grouping_mode: calendar
unit_system: metric
format: summary
periods:
  - date: "2024-01-01"
    end_date: "2024-01-07"
    period: "Week 1"
    exercises:
      - name: Barbell Bench Press
        working_sets: 3
        warmup_sets: 1
        total_reps: 24
        max_weight: 80.0
        weight_unit: kg
        total_volume: 1920
        is_cardio: false
    stats:
      total_workout_time: 175
      strength_time: 145
      cardio_time: 30
      total_distance: 5.2
      total_reps: 342
      total_volume: 12450
overall:
  date_range:
    start: "2024-01-01"
    end: "2024-03-15"
  total_sessions: 33
  total_volume: 410400
  averages:
    sessions_per_week: 3.0
    volume_per_session: 12436
```

### Parsing

```python
import yaml


def parse_yaml_format(content):
    data = yaml.safe_load(content)

    # Same structure as JSON -- iterate identically
    for period in data.get('periods', []):
        for exercise in period.get('exercises', []):
            name = exercise['name']
            volume = exercise.get('total_volume', 0)
            print(f"{name}: {volume}")

    return data
```

---

## 4. Markdown Format

Starts with `# Workout Summary Report`. Human-readable but requires regex parsing to extract structured data.

### Structure

```markdown
# Workout Summary Report

**Report Type:** Weekly
**Date Range:** 2024-01-01 to 2024-03-15
**Unit System:** Metric

## Week: 2024-01-01 to 2024-01-07

### Volume by Exercise
- Barbell Bench Press: 1920.00 kg*reps (3 working sets, 1 warmup sets, max 80.0 kg)
- Dumbbell Incline Press: 900.00 kg*reps (3 working sets, 0 warmup sets, max 30.0 kg)

### Distance by Exercise
- Treadmill Running: 5.20 km

### Summary Statistics
- Total Volume: 12450.00 kg*reps
- Total Reps: 342
- Total Distance: 5.20 km
- Total Workout Time: 175 min
- Strength Time: 145 min
- Cardio Time: 30 min
```

### Parsing

```python
import re


def parse_markdown_format(content):
    """Extract structured data from the Markdown report format."""
    result = {
        'metadata': {},
        'periods': [],
    }

    # Extract metadata
    for key in ['Report Type', 'Date Range', 'Unit System']:
        match = re.search(rf'\*\*{key}:\*\*\s*(.+)', content)
        if match:
            result['metadata'][key.lower().replace(' ', '_')] = match.group(1).strip()

    # Split into period sections
    period_pattern = re.compile(
        r'## (?:Week|Month|Day|Quarter|Year): (.+?)(?=\n## |\Z)',
        re.DOTALL
    )

    for period_match in period_pattern.finditer(content):
        period_text = period_match.group(0)
        period_header = period_match.group(1).strip()
        period_data = {'header': period_header, 'exercises': [], 'stats': {}}

        # Parse volume exercises
        volume_pattern = re.compile(
            r'- (.+?): ([\d.]+) (\w+\*?\w*)'
            r'(?: \((\d+) working sets, (\d+) warmup sets, max ([\d.]+) (\w+)\))?'
        )
        volume_section = re.search(
            r'### Volume by Exercise\n(.*?)(?=###|\Z)', period_text, re.DOTALL
        )
        if volume_section:
            for m in volume_pattern.finditer(volume_section.group(1)):
                exercise = {
                    'name': m.group(1),
                    'total_volume': float(m.group(2)),
                    'volume_unit': m.group(3),
                }
                if m.group(4) is not None:
                    exercise['working_sets'] = int(m.group(4))
                    exercise['warmup_sets'] = int(m.group(5))
                    exercise['max_weight'] = float(m.group(6))
                    exercise['weight_unit'] = m.group(7)
                period_data['exercises'].append(exercise)

        # Parse distance exercises
        distance_section = re.search(
            r'### Distance by Exercise\n(.*?)(?=###|\Z)', period_text, re.DOTALL
        )
        if distance_section:
            dist_pattern = re.compile(r'- (.+?): ([\d.]+) (\w+)')
            for m in dist_pattern.finditer(distance_section.group(1)):
                period_data['exercises'].append({
                    'name': m.group(1),
                    'distance': float(m.group(2)),
                    'distance_unit': m.group(3),
                    'is_cardio': True,
                })

        # Parse summary statistics
        stats_section = re.search(
            r'### Summary Statistics\n(.*?)(?=##|\Z)', period_text, re.DOTALL
        )
        if stats_section:
            stat_pattern = re.compile(r'- (.+?): ([\d.]+)\s*(\w*)')
            for m in stat_pattern.finditer(stats_section.group(1)):
                stat_name = m.group(1).strip().lower().replace(' ', '_')
                period_data['stats'][stat_name] = float(m.group(2))

        result['periods'].append(period_data)

    return result
```

---

## Unified Parsing Entrypoint

Combine detection and parsing into a single function:

```python
import json
import yaml
import csv
import re


def parse_fitbod_report(content):
    """Detect format and parse a Fitbod report into structured data."""
    fmt = detect_format(content)

    if fmt == 'gpt':
        header, sections = parse_gpt_format(content)
        return {'format': 'gpt', 'header': header, 'sections': sections}

    elif fmt == 'json':
        return {'format': 'json', 'data': json.loads(content)}

    elif fmt == 'yaml':
        return {'format': 'yaml', 'data': yaml.safe_load(content)}

    elif fmt == 'markdown':
        return {'format': 'markdown', 'data': parse_markdown_format(content)}

    else:
        raise ValueError(f"Unknown report format. Content starts with: {content[:50]!r}")
```

---

## Unknown Exercises

The exercise database covers ~209 common Fitbod exercises but is not exhaustive. The GPT report format may include an `## unknown_exercises` section listing exercises that were not found in the database:

```
## unknown_exercises
Cable Woodchop
Zercher Squat
TRX Row
```

When you encounter unknown exercises:
1. **Do NOT skip them** — infer muscle groups from the exercise name using your training knowledge
2. Include them in volume and analysis calculations using your inferred classification
3. Briefly note to the user which exercises you inferred, so they can correct if needed
4. You can still recommend these exercises in workout plans

---

## Edge Cases and Caveats

### Same-Timestamp Exports
Some Fitbod data has all exercises within a session sharing identical timestamps. In these cases, workout duration is estimated by the report generator rather than measured precisely.

### Weight Multiplier
The weight multiplier (for exercises like Dumbbell Curl where each arm holds a dumbbell) is already applied during report generation. Do **not** multiply weights again.

### Empty or Missing Fields
- Treat missing numeric fields as `0`.
- Treat missing text fields as empty string `""`.
- A missing `sets[]` array means the report is in summary mode -- per-set data is unavailable.

### Unit System
Always check the unit system before presenting numbers to the user:
- `metric` -- weight in **kg**, distance in **km**.
- `imperial` -- weight in **lbs**, distance in **miles**.

Volume units follow the weight unit: `kg*reps` or `lbs*reps`.

### Warmup Sets
Warmup sets are included in the data for completeness but must be **excluded** from all volume and analysis calculations. Only `working_sets` count toward training volume.
