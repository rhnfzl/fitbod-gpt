# FitbodGPT - Claude Code Instructions

## Project Overview
Custom GPT for ChatGPT that analyzes Fitbod workout data and recommends personalized workouts. No backend — this repo contains GPT configuration files, knowledge files, and a spec.

## Key Decisions
- GPT model: GPT-5.4 (as of March 2026)
- No Fitbod API — read-only (analyze data → recommend workouts)
- Code Interpreter enabled for data parsing
- Exercise DB has 209 exercises but is NOT exhaustive — GPT infers unknown exercises

## File Roles
- `gpt/instructions.md` — The system prompt, pasted into the GPT builder. ~6000 chars, max ~8000.
- `knowledge/*.json|.md` — Uploaded to GPT as knowledge files. Referenced via RAG.
- `scripts/generate_exercise_db.py` — Regenerates exercise-database.json from Fitbod2HevyConverter data.
- `spec/SPEC.md` — Complete specification. Source of truth for all design decisions.

## Related Repos
- fitbod-report (`/Users/rehan-8v/8vance/portfolio/fitbod-report`) — has `generate_gpt_report()` and `exercise_db.py`
- Fitbod2HevyConverter (`/Users/rehan-8v/8vance/portfolio/Fitbod2HevyConverter`) — source of exercise mappings

## When Modifying
- If adding exercises: update both `knowledge/exercise-database.json` AND `fitbod-report/src/data/exercise_db.py`
- If changing the GPT format: update both `generate_gpt_report()` in fitbod-report AND `knowledge/report-format-guide.md`
- Keep `gpt/instructions.md` under 8000 characters
