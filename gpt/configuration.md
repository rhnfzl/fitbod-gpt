# FitbodGPT - GPT Builder Configuration

## Basic Info

| Field | Value |
|-------|-------|
| **Name** | FitbodGPT |
| **Description** | Upload your Fitbod workout report and get personalized training analysis, imbalance detection, and science-backed workout plans. Strength-focused with cardio awareness. |
| **Recommended model** | GPT-5.4 Thinking if available; otherwise use the best current reasoning model exposed in the GPT builder |

## Capabilities

| Capability | Enabled | Rationale |
|------------|---------|-----------|
| Code Interpreter & Data Analysis | Yes | Required for parsing reports, computing metrics, generating plans |
| Web Search | No | All needed data comes from user's report and knowledge files |
| DALL-E Image Generation | No | Text-based recommendations only |
| Canvas | No | Not needed for this use case |

## Knowledge Files

Upload these 3 files from the `knowledge/` directory:

1. **exercise-database.json** (~35KB) — 209 Fitbod exercises with muscle groups, equipment, movement patterns
2. **training-principles.md** (~4KB) — Volume landmarks, progressive overload, splits, recovery science
3. **report-format-guide.md** (~5KB) — Parsing instructions for all 4 report formats (GPT/JSON/YAML/MD)

The `fitbod-report` app keeps GPT exports weekly by default for FitbodGPT so the coaching prompt and confidence tiers stay week-based.

## Conversation Starters

See `conversation-starters.md` for the 4 starters with rationale.

## Actions

None - Fitbod has no public API. FitbodGPT is read-only (analyze data → recommend workouts).

## Privacy & Safety

- FitbodGPT processes workout data (exercise names, weights, reps, dates). No PII beyond what the user voluntarily uploads.
- Knowledge files uploaded in the GPT builder remain attached to the GPT until you replace or delete them.
- Files users upload in chat and the chat itself follow ChatGPT's retention rules for their plan. Do not promise zero retention unless your workspace policy guarantees it.
- If publishing to GPT Store later: add a privacy policy URL and usage disclaimer about health/fitness advice not being medical advice.

## Setup Instructions

1. Go to [chatgpt.com/gpts](https://chatgpt.com/gpts)
2. Click **Create**
3. Open the configuration view for the GPT draft
4. Paste contents of `instructions.md` into the Instructions field
5. Upload the 3 knowledge files
6. Add the 4 conversation starters
7. Set the recommended model to GPT-5.4 Thinking if your workspace offers it
8. Enable Code Interpreter & Data Analysis and leave the other capabilities off unless you have a deliberate reason to expand scope
9. Keep this GPT private for initial testing
10. Test with sample reports, especially weekly GPT exports from `fitbod-report`
11. Iterate on instructions based on GPT behavior in Preview
12. When ready: share with a link or publish to the GPT Store
