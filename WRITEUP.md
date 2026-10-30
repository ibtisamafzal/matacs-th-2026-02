# Write-up

## 1. AI vs. rules
AI is used for two things only: reading messy proposal text into structured facts, and writing the one-line reason. Everything that decides the outcome is plain code: mandatory pass/fail, scoring formulas, weights, ranking and ties. I drew the line there because AI is good with language but not repeatable at arithmetic or fairness decisions, while code is cheap, testable and identical on every run.

## 2. Consistency and explainability
- The AI returns fixed JSON (schema in PROMPTS.md) at temperature 0. Each fact comes with a quote from the proposal.
- Code checks that the quote really exists in the source text. If not, the field is marked low confidence.
- Scores come from fixed formulas, so the same extracted facts always give the same ranking. Extraction itself could vary slightly between runs, so I store the extraction result and rank from that stored copy. Re-ranking never makes a new AI call.
- The reviewer sees a table per proposal: each criterion, the extracted value, the quote, the points earned and why.

## 3. Human in the loop
- Anything flagged (missing information, low confidence, suspicious text, over budget or over 16 weeks) is held for a person before the ranking is trusted.
- The reviewer can correct an extracted value, resolve a flag, or override a rank. A written reason is required.
- The human makes the final award decision. The tool only recommends.
- Logged: criteria version, prompt version, model name, input file hash, raw AI output, validated facts, scores, flags, and every override (who, when, why).

## 4. Changing criteria
Each scoring run stores a snapshot of the criteria and weights it used (a version number). Editing criteria creates a new version; old results are never silently changed. Proposals scored under an old version show as "scored under v1, current is v2". Because extraction is stored separately from scoring, re-scoring under new weights only re-runs the cheap code step. Changing a mandatory criterion or adding a new fact to extract needs a new extraction run. The reviewer chooses whether to re-score, and the system first shows how the ranking would change.

## 5. Risks
| Risk | Guard |
|---|---|
| Wrong extraction | Quote check, confidence field; low confidence goes to a human |
| Made-up facts | "Not stated" is allowed and missing is never guessed; quotes must exist in the source |
| Prompt injection (Proposal C) | Proposal text is treated as data only; instruction-like text is detected and flagged; code, not the AI, controls ranking so injected text cannot change scores |
| Bias | Criteria fixed in advance; scoring ignores company name, size and writing style; reviewers see evidence, not just a score |
| Mandatory criteria applied unfairly | Pass/fail on stated evidence only; "subcontractor to be confirmed" does not count as held |
| Cost | One extraction call per proposal, cached; re-scoring is free code; upload size limits |
| Overtrust | Tool recommends, human decides; scores always shown with evidence |

## Sample set result
A and E are ranked. B is ineligible (licence not held by the bidder). C is flagged (hidden instruction, and a vague "since 2020" install count). D is flagged (no timeline, so the 16-week limit cannot be verified).

## Assumptions
"Last 5 years" is counted from October 2026. Prices are all-in and comparable. Price and timeline are scored relative to the best eligible bid.
