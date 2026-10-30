# Write-up

## 1. AI vs. rules
AI is used for two things only: reading messy proposal text into structured facts, and writing the one-line reason. Everything that decides the outcome is plain code: mandatory pass/fail, scoring formulas, weights, ranking and ties. I drew the line there because AI is good at language but not repeatable at arithmetic or fairness decisions, and code is cheap, testable and identical every run.

## 2. Consistency and explainability
- The AI returns fixed JSON (schema in PROMPTS.md) at temperature 0. Each fact comes with a quote from the proposal.
- Code checks the quote actually exists in the source text. If not, the field is marked unverified.
- Scores come from fixed formulas, so the same extracted facts always give the same ranking. Extraction could differ slightly between runs, so I store the extraction result and rank from that stored copy. Re-ranking uses the saved facts, not a new AI call.
- The reviewer sees a table per proposal: each criterion, the extracted value, the quote, points earned and why.

## 3. Human in the loop
- Anything flagged (missing info, low confidence, suspicious text, failed quote check) is held for a person before ranking is trusted.
- The reviewer can correct an extracted value, mark a flag resolved, or override a rank, always with a written reason.
- The human makes the final award decision. The tool only recommends.
- Logged: criteria version, prompt version, model name, input file hash, raw AI output, validated facts, scores, flags, every override (who, when, why).

## 4. Changing criteria
Each scoring run stores a snapshot of the criteria and weights it used (a version number). Editing criteria creates a new version; old results are never silently changed. Proposals scored under an old version show as "scored under v1, current is v2". Because extraction is stored separately from scoring, re-scoring under new weights only re-runs the cheap code step. Changing a mandatory criterion or adding a new fact to extract needs a new extraction run. The reviewer chooses whether to re-score; the system shows what would change in the ranking first.

## 5. Risks
| Risk | Guard |
|---|---|
| Wrong extraction | Quote check, confidence field, low confidence goes to human |
| Made-up facts | "Not stated" is allowed; missing never guessed; quote must exist |
| Prompt injection (Proposal C) | Proposal text is treated as data only; instruction-like text is detected and flagged; code, not the AI, controls ranking so injected text can't change scores |
| Bias | Criteria are fixed in advance; scoring ignores company names, size, and style; reviewers see evidence, not just a score |
| Unfair mandatory handling | Pass/fail on stated evidence only; "subcontractor to be confirmed" does not count as held |
| Cost | One extraction call per proposal, cached; re-scoring is free code; size limits on uploads |
| Overtrust | Tool recommends, human decides, scores shown with evidence |

## Sample set result
A and E ranked. B ineligible (licence not held by bidder). C flagged (hidden instruction). D flagged (no timeline).

## Assumptions
I assumed the extraction date is October 2026 for the "last 5 years" check, and that "all-in" prices are comparable.