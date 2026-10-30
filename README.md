# matacs-th-2026-02

**Name:** Muhammad Ibtisam Afzal
**Reference:** MATACS-TH-2026-02
**Time actually spent:** TODO: write your real total (for example "about 4 hours over 2 days")

## Summary
A design for an AI-assisted proposal triage tool. AI is used only to read messy proposal text into structured facts (with evidence quotes) and to write a one-line reason. All pass/fail checks, scoring and ranking are plain code, so results are repeatable. People review every flagged item and make the final award decision.

On the sample set, A and E are ranked, C and D are flagged for human review, and B is ineligible.

## How I used AI tools
I used Claude to help draft the process flow, the extraction prompt, the scoring rubric and a first version of the write-up and prototype. I then read, checked and edited the results myself and ran the prototype to confirm it reproduces `ranking.json`.
TODO: edit this paragraph so it describes what you actually did.

**Where I disagreed with or corrected the AI:**
TODO: write ONE real example in your own words (what the AI suggested, what you changed, and why).

## Files
- [WRITEUP.md](WRITEUP.md): answers to the five questions
- [PROMPTS.md](PROMPTS.md): extraction and reason prompts
- [ranking.json](ranking.json): expected ranking of proposals A to E
- [diagram/flow.png](diagram/flow.png): process flow (source: [diagram/flow.dot](diagram/flow.dot))
- [prototype/](prototype/): optional scripts

## Prototype (optional)
`prototype/score.py` applies the scoring rules to extracted facts and prints the ranking. It uses no AI and no API key.

```
cd prototype
python score.py
```

`prototype/extract.py` runs the extraction prompt on text files you place in `prototype/proposals/` (git-ignored). It needs an API key: copy `.env.example` to `.env` and fill it in. Limitation: its output uses the nested schema from PROMPTS.md, and `score.py` currently reads a flat format (`sample_facts.json`), so a mapping step between the two is not written yet.

## Assumptions
- "Last 5 years" is counted from October 2026.
- Proposal prices are all-in and comparable.
- A proposal with a hidden instruction is flagged for review, not rejected, and scored only on its genuine content.
