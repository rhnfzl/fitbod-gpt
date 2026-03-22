# FitbodGPT Specification

> Comprehensive specification document for FitbodGPT — a custom GPT inside ChatGPT that analyzes Fitbod workout data and provides personalized workout recommendations.

**Version**: 1.0
**Date**: 2026-03-22
**Status**: Draft

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [User Requirements](#3-user-requirements)
4. [GPT Configuration](#4-gpt-configuration)
5. [GPT System Instructions](#5-gpt-system-instructions)
6. [Knowledge Files](#6-knowledge-files)
7. [GPT-Optimized Report Format](#7-gpt-optimized-report-format)
8. [User Level Detection Algorithm](#8-user-level-detection-algorithm)
9. [Recommendation Engine](#9-recommendation-engine)
10. [User Flow](#10-user-flow)
11. [Edge Cases](#11-edge-cases)
12. [Fitbod-Report Modifications](#12-fitbod-report-modifications)
13. [File Structure](#13-file-structure)
14. [Future Roadmap](#14-future-roadmap)

---

## 1. Project Overview

- **Name**: FitbodGPT
- **What**: A custom GPT inside ChatGPT that analyzes Fitbod workout data and provides personalized workout recommendations.
- **Inspired by**: [Hevy GPT](https://github.com/hevyapp/hevy-gpt) — but read-only since Fitbod has no public API.
- **Model**: GPT-5.4 (current as of March 2026)
- **Distribution**: Start as a private GPT, publish to the GPT Store later.

### Repositories

Two repositories are involved:

| Repo | Purpose |
|------|---------|
| `fitbod-gpt` (new) | GPT configuration, knowledge files, spec, generation scripts |
| `fitbod-report` (modify) | Add GPT-optimized export format and "Copy for FitbodGPT" clipboard button to the existing Streamlit app |

---

## 2. Architecture

```
User's Fitbod App → Export CSV → fitbod-report (Streamlit) → GPT-optimized report
                                                                    ↓
                                              FitbodGPT (Custom GPT in ChatGPT)
                                                                    ↓
                                              Personalized workout plan + coaching
```

FitbodGPT is a **read-only** GPT. It has no Actions (API endpoints) because Fitbod does not expose a public API. All data flows in one direction: from the user's exported Fitbod data into the GPT via copy-paste or file upload.

The `fitbod-report` Streamlit app serves as the intermediary that transforms raw Fitbod CSV exports into a token-efficient, pre-aggregated report format that the GPT can parse and analyze.

---

## 3. User Requirements

The following requirements were gathered from user interviews. Each decision is numbered for traceability.

### 3.1 Input Formats

All 4 formats are supported with auto-detection:

| Format | Priority | Notes |
|--------|----------|-------|
| GPT (TSV-based) | Preferred | Token-efficient, pre-aggregated |
| JSON | Supported | Structured, verbose |
| YAML | Supported | Human-readable |
| Markdown | Supported | Copy-paste friendly |

The GPT auto-detects the input format upon upload/paste. The GPT-optimized TSV format is the recommended path for best results.

### 3.2 Output Style

Both coaching conversation and structured text plan:

1. Start with coaching questions (goals, equipment confirmation, preferences).
2. Output a structured workout plan after the conversation.

This hybrid approach ensures the GPT understands context before prescribing.

### 3.3 Science Depth

Adaptive to user level. The GPT auto-detects beginner/intermediate/advanced from training data and adjusts the depth and terminology of its explanations accordingly. See [Section 8](#8-user-level-detection-algorithm) for the detection algorithm.

### 3.4 Imbalance Correction

All 4 approaches are supported. The user chooses their preference:

1. **Gentle nudge** — mention imbalances with soft suggestions.
2. **Corrective programming** — actively modify the plan to address imbalances.
3. **Ask user** — present the imbalance data and let the user decide.
4. **Data-driven with explanation** — show the data, explain the science, recommend a fix.

### 3.5 Warmup Data

Warmups are **ignored** in analysis. Focus is on working sets only. The GPT-optimized report format excludes warmup sets by default.

### 3.6 Data Window

Tiered analysis with confidence warnings:

| Data Available | Confidence Level | Capabilities |
|----------------|------------------|--------------|
| < 4 weeks | Limited | Snapshot only. No trends. Basic recommendations with disclaimer. |
| 4-12 weeks | Moderate | Some trend detection. Moderate confidence in recommendations. |
| 12+ weeks | Strong | Full trend analysis. High confidence in recommendations. |

### 3.7 Cardio Scope

**Strength-focused with cardio awareness.** The GPT tracks cardio data when present but does not prescribe cardio programming. See [Section 5, Item 7](#57-cardio-handling) for handling details.

### 3.8 Onboarding

**Upload-first flow:**

1. Ask the user to upload or paste their Fitbod report.
2. Analyze the data.
3. Then ask about goals, preferences, and equipment.

This avoids asking premature questions before having data context.

### 3.9 Knowledge Files

Three knowledge files are bundled with the GPT:

1. **exercise-database.json** — 209 exercises with classifications.
2. **training-principles.md** — Training science reference material.
3. **report-format-guide.md** — Parsing instructions for all 4 input formats.

### 3.10 Equipment

Inferred from report data, confirmed with the user **once per session**. The GPT reads the equipment used in the user's exercises and presents its inference for confirmation before recommending exercises.

### 3.11 Split Style

The GPT offers **2-3 split choices** with trade-offs relative to the user's data (frequency, goals, available time). See [Section 9.2](#92-split-selection) for the full matrix.

### 3.12 Conversation Starters

Four action-oriented starters (see [Section 4](#4-gpt-configuration)).

### 3.13 Code Interpreter

**Enabled.** Used for programmatic data parsing, calculations, and analysis. This is critical for handling larger reports and computing derived metrics.

### 3.14 Exercise Database

Auto-generated from the 209 Fitbod exercise mappings in `Fitbod2HevyConverter.EXERCISE_MAPPING`, then reviewed. Generated by `scripts/generate_exercise_db.py`.

### 3.15 Clipboard

A "Copy for FitbodGPT" button is added to the `fitbod-report` Streamlit app, visible when the GPT output format is selected.

---

## 4. GPT Configuration

| Setting | Value |
|---------|-------|
| **Name** | FitbodGPT |
| **Description** | Upload your Fitbod workout report and get personalized training analysis, imbalance detection, and science-backed workout plans. |
| **Model** | GPT-5.4 |
| **Capabilities** | Code Interpreter only |
| **Disabled capabilities** | Web search, DALL-E, Canvas |
| **Actions** | None (no Fitbod API) |

### Knowledge Files

| File | Approximate Size | Purpose |
|------|-----------------|---------|
| `exercise-database.json` | ~35KB | 209 exercises with full classifications |
| `training-principles.md` | ~4KB | Volume landmarks, overload strategies, splits, recovery |
| `report-format-guide.md` | ~5KB | Format detection, parsing instructions, edge cases |

### Conversation Starters

1. "Upload my Fitbod report and analyze my training"
2. "Build me a workout plan for this week"
3. "What are my strength trends and progress?"
4. "Help me break through a training plateau"

---

## 5. GPT System Instructions

The system prompt is approximately 5,500 characters and contains 8 sections.

### 5.1 Identity and Persona

The GPT presents as an **evidence-based strength coach**. It is knowledgeable, encouraging, and grounded in data. It never fabricates data or makes claims unsupported by the user's report.

### 5.2 Onboarding Flow

Upload-first:

1. Greet the user and ask for their Fitbod report.
2. Parse and analyze the uploaded data.
3. Present a summary of findings.
4. Ask about goals, equipment confirmation, and preferences.

### 5.3 Data Confidence Tiers

The GPT qualifies all analysis with confidence based on data depth:

| Data Depth | Label | Behavior |
|------------|-------|----------|
| < 4 weeks | Limited | Snapshot analysis only. No trend detection. Recommendations carry a disclaimer. |
| 4-12 weeks | Moderate | Some trend detection. Moderate confidence. |
| 12+ weeks | Strong | Full trend analysis. High confidence. |

### 5.4 User Level Detection

A 7-axis weighted scoring system (0-100). See [Section 8](#8-user-level-detection-algorithm) for the full algorithm.

Score mapping:
- **0-33**: Beginner
- **34-66**: Intermediate
- **67-100**: Advanced

### 5.5 Analysis Pipeline

After parsing the report, the GPT runs through:

1. **Data validation** — confirm format, check for anomalies.
2. **Summary statistics** — sessions, frequency, volume, exercise variety.
3. **Trend detection** — weight progression, volume changes, frequency shifts.
4. **Muscle balance assessment** — compare volumes to MAV targets.
5. **Level detection** — compute the 7-axis score.
6. **Equipment inference** — extract equipment from exercise data.

### 5.6 Recommendation Engine

Covers imbalance handling, split selection, weight guidance, volume management, output format, and adaptive depth. See [Section 9](#9-recommendation-engine) for full details.

### 5.7 Cardio Handling

- Acknowledge cardio data when present.
- Report cardio minutes and frequency in summaries.
- Do **not** prescribe cardio programming.
- Note potential interference effects if cardio volume is high relative to strength training.
- If a user is cardio-only with no strength data, explain that the GPT is strength-focused and offer to help them start a strength program.

### 5.8 Rules

1. Never fabricate data — only reference what is in the user's report.
2. Cite specific time periods when discussing trends (e.g., "over the last 6 weeks").
3. Use Code Interpreter for parsing and calculations.
4. Do not prescribe specific weights for exercises the user has never performed.
5. Volume increases must not exceed 20% per week above the user's current level.
6. Always confirm equipment before recommending exercises.
7. Respect the user's chosen imbalance correction style.
8. If the user disagrees with their detected level, allow override.

---

## 6. Knowledge Files

### 6.1 exercise-database.json (~35KB)

Contains 209 exercises sourced from the `Fitbod2HevyConverter.EXERCISE_MAPPING`.

**Per-exercise schema:**

```json
{
  "fitbod_name": "Barbell Bench Press",
  "canonical_name": "Bench Press (Barbell)",
  "category": "Chest",
  "equipment": ["Barbell", "Flat Bench"],
  "primary_muscles": ["Pectoralis Major"],
  "secondary_muscles": ["Anterior Deltoid", "Triceps"],
  "movement_pattern": "Horizontal Push",
  "compound": true,
  "difficulty": "Intermediate",
  "bodyweight": false,
  "unilateral": false
}
```

**Reference lists included in the file:**

| Reference | Count | Purpose |
|-----------|-------|---------|
| Muscle groups | 24 | Canonical list for muscle volume tracking |
| Movement patterns | 14 | Categorization of exercises by movement type |
| Equipment types | 13 | Equipment inference and exercise filtering |

**Generation:** Auto-generated by `scripts/generate_exercise_db.py` from the Fitbod2HevyConverter source.

### 6.2 training-principles.md (~4KB)

Covers:

- **Volume landmarks per muscle group** — MEV (Minimum Effective Volume), MAV (Maximum Adaptive Volume), MRV (Maximum Recoverable Volume).
- **Progressive overload strategies by level** — weight increments, rep progression, set progression.
- **Rep range guidelines** — strength (1-5), hypertrophy (6-12), endurance (12+).
- **Common imbalances and corrections** — push/pull ratio, anterior/posterior chain, upper/lower split.
- **Split recommendations by frequency** — 2-6 days/week with pros and cons.
- **Recovery and deload protocols** — when to deload, deload strategies.
- **Cardio interference guidelines** — concurrent training considerations.
- **1RM estimation formulas** — Epley, Brzycki, and when to use each.

### 6.3 report-format-guide.md (~5KB)

Covers:

- **Format detection rules** — how to identify GPT, JSON, YAML, and Markdown formats.
- **Parsing instructions** — Python code snippets for parsing each of the 4 formats.
- **Key field definitions** — what each field means and its expected type/range.
- **Unified parsing entrypoint** — a single function that detects format and delegates.
- **Edge cases** — malformed input, missing fields, duplicate timestamps, large files.

---

## 7. GPT-Optimized Report Format

A TSV-based format designed for token efficiency. Approximately 4x smaller than equivalent JSON.

### 7.1 Format Structure

```
@fitbodgpt v1
date_range: 2024-01-01 to 2024-03-15
weeks: 11
sessions: 33
unit: metric
exercises: 24

## weekly_summary
week	sessions	strength_min	cardio_min	volume_kg	reps	distance_km

## exercise_stats
exercise	sessions	working_sets	total_reps	max_kg	avg_kg	total_volume	trend

## muscle_volume
muscle	weekly_avg_sets	trend

## recent_sessions
date	exercises (compact notation: Exercise:SxR@Weight)
```

### 7.2 Design Decisions

| Decision | Rationale |
|----------|-----------|
| TSV over JSON | ~4x token savings. Tab-separated values are natively parseable by Code Interpreter. |
| Pre-computed `muscle_volume` | Reduces Code Interpreter workload. The GPT can read muscle balance data without computing it from raw sets. |
| Pre-computed `trend` | Allows instant trend reporting without regression analysis on raw data. |
| Warmups excluded | Working sets only, per user requirement. Reduces noise in analysis. |
| Compact session notation | `Exercise:SxR@Weight` (e.g., `Bench Press:3x8@80`) minimizes tokens while preserving key information. |
| Header metadata | `@fitbodgpt v1` enables format detection. Metadata fields provide context without parsing. |

### 7.3 Sections

#### `weekly_summary`
One row per week. Provides a high-level overview of training load over time. Used for trend detection and frequency analysis.

#### `exercise_stats`
One row per exercise across the entire date range. Aggregated statistics for each exercise the user has performed. The `trend` field indicates weight progression direction.

#### `muscle_volume`
One row per muscle group. Pre-computed weekly average sets targeting each muscle group. The `trend` field indicates whether volume is increasing, stable, or decreasing.

#### `recent_sessions`
One row per session for the most recent sessions. Uses compact notation to fit maximum detail into minimum tokens. Used for examining recent programming and providing specific workout continuity.

---

## 8. User Level Detection Algorithm

A 7-axis weighted scoring system that produces a score from 0 to 100.

### 8.1 Axes

| Axis | Weight | Beginner (0) | Intermediate (50) | Advanced (100) |
|------|--------|-------------|-------------------|----------------|
| Exercise variety | 15% | < 6 unique exercises | 6-15 unique exercises | > 15 unique exercises |
| Training frequency | 15% | < 2x/week | 2-4x/week | > 4x/week |
| Compound lift count | 15% | 0-1 compound exercises | 2-4 compound exercises | 5+ compound exercises |
| Progressive overload evidence | 20% | < 20% of compounds trending up | 20-60% trending up | > 60% trending up |
| Volume per session | 15% | < 8 working sets | 8-16 working sets | > 16 working sets |
| Data depth | 10% | < 4 weeks | 4-26 weeks | > 26 weeks |
| Exercise sophistication | 10% | < 30% free weight or unilateral | 30-60% | > 60% |

### 8.2 Score Mapping

| Score Range | Level | Behavior |
|-------------|-------|----------|
| 0-33 | Beginner | Simpler language. Fewer exercise options. More explanation of fundamentals. Conservative volume. |
| 34-66 | Intermediate | Standard coaching language. Full exercise variety. Moderate volume guidance. |
| 67-100 | Advanced | Technical language welcomed. Advanced programming concepts. Higher volume tolerance. |

### 8.3 Override

If the user disagrees with the detected level, they can override it. The GPT adjusts all subsequent recommendations accordingly.

---

## 9. Recommendation Engine

### 9.1 Imbalance Detection

The GPT compares the user's muscle group volumes (from the `muscle_volume` section or computed from raw data) against MAV targets from `training-principles.md`.

**Checks performed:**

| Check | Target | Flagged When |
|-------|--------|-------------|
| Push:Pull ratio | 1:1 to 1:1.5 | Ratio falls outside range |
| Anterior:Posterior chain | Balanced | Significant anterior dominance |
| Upper:Lower split | At least 30% lower body | Lower body below 30% of total volume |
| Bilateral dominance | Mixed | > 80% bilateral exercises |

The imbalance correction style is determined by user preference (see [Section 3.4](#34-imbalance-correction)).

### 9.2 Split Selection

The GPT presents 2-3 options based on the user's training frequency with pros and cons for each:

| Frequency | Option 1 | Option 2 | Option 3 |
|-----------|----------|----------|----------|
| 2 days/week | Full Body x2 | — | — |
| 3 days/week | Full Body x3 | PPL | Upper-Lower-Full |
| 4 days/week | Upper/Lower x2 (default) | PPL + Arms | — |
| 5-6 days/week | PPL x2 | Arnold Split | — |

Each option includes trade-offs relative to the user's specific data (e.g., "Given your push/pull imbalance, PPL gives you a dedicated pull day to address this").

### 9.3 Exercise Selection Rules

1. **Only recommend exercises matching confirmed equipment.** If the user has no barbell access, never recommend barbell exercises.
2. **For exercises the user already performs:** Use historical data for weight guidance (e.g., "Your last Bench Press was 3x8@80kg, aim for 3x8@82.5kg").
3. **For new exercises:** Reference `exercise-database.json` for classification, but do **not** prescribe specific weights. Guide with RPE or relative intensity instead.
4. **Volume increases:** Maximum 20% per week above the user's current level.

### 9.4 Weight Guidance

- For known exercises: base recommendations on historical max/avg weights with progressive overload.
- For new exercises: provide RPE guidance (e.g., "RPE 7-8") rather than absolute weights.
- Never fabricate weight recommendations without data backing.

### 9.5 Output Format

After the coaching conversation concludes, the GPT outputs a structured workout plan:

```
## [Split Name] — Week [N]

### Day [N]: [Focus]

| Exercise | Sets x Reps | Weight Guidance | Rest | Notes |
|----------|-------------|-----------------|------|-------|
| ... | ... | ... | ... | ... |
```

### 9.6 Adaptive Depth

The depth of explanation adapts to the user's detected (or overridden) level:

| Level | Explanation Style |
|-------|-------------------|
| Beginner | Plain language. Explain "why" for each recommendation. Include form cues. |
| Intermediate | Standard coaching language. Explain key programming decisions. |
| Advanced | Technical terminology. Focus on periodization, volume management, and nuanced programming. |

---

## 10. User Flow

The end-to-end flow from data export to workout plan:

1. **Export**: User exports workout data as CSV from the Fitbod app.
2. **Upload to fitbod-report**: User uploads the CSV to the `fitbod-report` Streamlit app.
3. **Configure report**: User selects date range, period type, and "GPT" format.
4. **Copy or download**: User clicks "Copy for FitbodGPT" (clipboard) or downloads the report file.
5. **Open FitbodGPT**: User opens FitbodGPT in ChatGPT.
6. **Paste or upload report**: User pastes the report text or uploads the file.
7. **GPT parses and summarizes**: GPT parses the report, presents a summary, and asks to confirm equipment.
8. **User provides context**: User confirms equipment, states goals, and selects imbalance correction preference.
9. **GPT presents split options**: GPT offers 2-3 split choices with trade-offs specific to the user's data.
10. **User picks split**: User selects their preferred split.
11. **GPT generates plan**: GPT outputs a structured workout plan in table format.
12. **Ongoing coaching**: User can ask follow-up questions, request modifications, or discuss training topics.

---

## 11. Edge Cases

| Scenario | Handling |
|----------|----------|
| **Cardio-only user** (no strength data) | Skip level detection. Explain the GPT is strength-focused. Offer to help start a strength program. |
| **Bodyweight-only user** | Can be any level. Recommend progression via reps, tempo, and harder variations rather than added weight. |
| **Sparse data** (< 4 weeks) | Snapshot analysis only. No trend detection. Preliminary recommendations with disclaimer. |
| **Very sparse data** (< 2 weeks) | Basic exercise list and goals discussion only. No quantitative analysis. |
| **Extreme volume** (> 30 sets/session) | Flag as unusual. Ask if this reflects supersets, circuits, or actual straight-set volume. |
| **Same-timestamp exports** | Older Fitbod data may have identical timestamps for different sets. Duration estimates are unreliable in this case. Note this to the user. |
| **Large reports** (1 year+) | GPT format pre-aggregates, so size is manageable. For raw formats, Code Interpreter extracts summaries from the most relevant window. |
| **Unsupported format** | Ask the user to re-export using fitbod-report or paste in a recognized format. |
| **User disagrees with detected level** | Allow override. Adjust all subsequent recommendations accordingly. |

---

## 12. Fitbod-Report Modifications

Changes required in the `fitbod-report` repository to support the GPT export flow.

### 12.1 New File: `src/data/exercise_db.py`

- Python dictionary mapping exercise names to muscle groups.
- Serves as the shared source of truth with `exercise-database.json` in the `fitbod-gpt` repo.
- Used by `generate_gpt_report()` to compute the `muscle_volume` section.

### 12.2 Modified: `src/report/generator.py`

- Add `generate_gpt_report()` function.
- Follows the pattern of the existing `_build_structured_report()` (lines 983-1125).
- Outputs the compact TSV format with pre-computed analytics (weekly summary, exercise stats, muscle volume, recent sessions).
- Excludes warmup sets.

### 12.3 Modified: `app.py`

- Add `"gpt"` to the output format selector dropdown.
- Add a "Copy for FitbodGPT" clipboard button, visible when the "gpt" format is selected.
- Wire `generate_gpt_report()` into the report generation pipeline.

### 12.4 Modified: `tests/test_reports.py`

- Add test cases for GPT format output.
- Verify TSV parsing correctness.
- Verify section structure (all 4 sections present with correct headers).
- Verify warmup exclusion.

---

## 13. File Structure

```
fitbod-gpt/
├── README.md
├── CLAUDE.md
├── spec/
│   └── SPEC.md                    # This file
├── gpt/
│   ├── instructions.md            # GPT system prompt (~5500 chars)
│   ├── conversation-starters.md   # 4 starters with rationale
│   └── configuration.md           # GPT builder settings
├── knowledge/
│   ├── exercise-database.json     # 209 exercises with classifications
│   ├── training-principles.md     # Training science reference
│   └── report-format-guide.md     # Report format parsing guide
└── scripts/
    └── generate_exercise_db.py    # Generates exercise-database.json from Fitbod2HevyConverter
```

---

## 14. Future Roadmap

Listed in approximate priority order:

1. **GPT Store publishing** — Polish instructions, add a privacy policy, submit for OpenAI review.
2. **Fitbod API integration** — If Fitbod launches a public API, add Actions for direct data pull (similar to how Hevy GPT works with the Hevy API).
3. **Progress tracking** — If ChatGPT adds persistent memory per GPT, track user progress across sessions for longitudinal coaching.
4. **Visual reports** — Enable DALL-E for generating workout cards or progress charts.
5. **Multi-language support** — Expand system instructions for non-English users.
6. **Community exercise database** — Allow users to suggest new exercises not in the 209-exercise base set.
