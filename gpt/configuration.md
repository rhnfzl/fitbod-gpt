# FitbodGPT - GPT Builder Configuration

## Basic Info

| Field | Value |
|-------|-------|
| **Name** | FitbodGPT |
| **Description** | Upload your Fitbod workout report and get personalized training analysis, imbalance detection, and science-backed workout plans. Strength-focused with cardio awareness. |
| **Recommended model** | Use the best reasoning model available in the GPT builder at the time of setup |

## Capabilities

| Capability | Enabled | Rationale |
|------------|---------|-----------|
| Code Interpreter & Data Analysis | Yes | Required for parsing reports, computing metrics, generating plans |
| Web Search | No | All needed data comes from user's report and knowledge files |
| Image generation | No | Text-based recommendations only |
| Canvas | No | Not needed for this use case |

## Knowledge Files

Upload these 4 files from the `knowledge/` directory. Use `.txt` versions (not `.md`) for better RAG retrieval in ChatGPT:

1. **exercise-database.json** (~35KB) - 209 Fitbod exercises with muscle groups, equipment, movement patterns
2. **training-principles.txt** (~4KB) - Volume landmarks, progressive overload, splits, recovery science
3. **report-format-guide.txt** (~5KB) - Format descriptions for all 5 input types (TSV/JSON/YAML/Markdown/raw CSV)
4. **coaching-guidelines.txt** (~10KB) - User level detection, injury handling, recovery data interpretation, volume targets, split recommendations, deload protocols

The `.md` versions of some files are kept in the repo for GitHub readability but should not be uploaded to the GPT builder.

The `fitbod-report` app keeps GPT exports weekly by default for FitbodGPT so the coaching prompt and confidence tiers stay week-based.

## Conversation Starters

See `conversation-starters.md` for the 4 starters with rationale.

## Actions

None - Fitbod has no public API. FitbodGPT is read-only (analyze data → recommend workouts).

## Privacy & Safety

- FitbodGPT processes workout data (exercise names, weights, reps, dates). No PII beyond what the user voluntarily uploads.
- Knowledge files uploaded in the GPT builder remain attached to the GPT until you replace or delete them.
- Files users upload in chat and the chat itself follow ChatGPT's retention rules for their plan. Do not promise zero retention unless your workspace policy guarantees it.
- If publishing to GPT Store later: include a plain-language training disclaimer. A privacy policy URL becomes mandatory when you add custom actions that call external services.

## About / Publishing

- Add a profile image so the GPT is recognizable in links and in the Store.
- Pick the most accurate category available in the builder before publishing.
- If you want Store visibility, set up and verify your Builder Profile first.
- Use link-only sharing while you are validating behavior; switch to Store visibility only after prompt and report-flow testing is stable.
- The About page should stay aligned with the builder fields: name, description, capabilities, starter prompts, and Builder information.

## Setup Instructions

1. Go to [chatgpt.com/gpts](https://chatgpt.com/gpts)
2. Click **Create**
3. Open the configuration view for the GPT draft
4. Paste contents of `instructions.md` into the Instructions field
5. Upload the 3 knowledge files
6. Add the 4 conversation starters
7. Set the recommended model to the best reasoning model your workspace offers
8. Enable Code Interpreter & Data Analysis and leave the other capabilities off unless you have a deliberate reason to expand scope
9. Add a profile image and choose the best-fitting category in the About/configuration fields
10. Keep this GPT private for initial testing
11. Test with sample reports, especially weekly GPT exports from `fitbod-report`
12. Iterate on instructions based on GPT behavior in Preview
13. When ready: share with a link or publish to the GPT Store
