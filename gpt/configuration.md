# FitbodGPT — GPT Builder Configuration

## Basic Info

| Field | Value |
|-------|-------|
| **Name** | FitbodGPT |
| **Description** | Upload your Fitbod workout report and get personalized training analysis, imbalance detection, and science-backed workout plans. Strength-focused with cardio awareness. |
| **Model** | GPT-5.4 |

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

## Conversation Starters

See `conversation-starters.md` for the 4 starters with rationale.

## Actions

None — Fitbod has no public API. FitbodGPT is read-only (analyze data → recommend workouts).

## Privacy & Safety

- FitbodGPT processes workout data (exercise names, weights, reps, dates). No PII beyond what the user voluntarily uploads.
- The GPT does not store data between conversations.
- If publishing to GPT Store later: add a privacy policy URL and usage disclaimer about health/fitness advice not being medical advice.

## Setup Instructions

1. Go to https://chat.openai.com/gpts/editor
2. Click "Create a GPT"
3. Switch to "Configure" tab
4. Paste contents of `instructions.md` into the Instructions field
5. Upload the 3 knowledge files
6. Add the 4 conversation starters
7. Enable Code Interpreter, disable all other capabilities
8. Set to "Only me" for initial private testing
9. Test with sample reports (both small and large datasets)
10. Iterate on instructions based on GPT behavior
11. When ready: change to "Anyone with the link" or publish to GPT Store
