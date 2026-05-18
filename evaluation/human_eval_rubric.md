# Human Evaluation Rubric

Use a 1-5 score for each criterion.

## Task A - Review Simulation

| Criterion | 1 | 3 | 5 |
|---|---|---|---|
| Behavioural fidelity | Ignores persona/history | Uses a few user signals | Clearly reflects rating style, preferences, complaints, and context |
| Rating-review consistency | Review contradicts rating | Mostly aligned but uneven | Tone, praise, complaints, and rating match naturally |
| Tone realism | Robotic or exaggerated | Understandable but generic | Sounds like a plausible human review |
| Item specificity | Could apply to anything | Mentions one item detail | Uses concrete item, price, delivery, portion, spice, or location details |
| Nigerian contextual naturalness | Missing or gimmicky | Some local cues | Natural Nigerian context without forced slang |

Suggested Task A interpretation:

- `1`: unusable for judging behavioural modelling.
- `3`: acceptable baseline.
- `5`: strong competition-grade simulation.

## Task B - Recommendation

| Criterion | 1 | 3 | 5 |
|---|---|---|---|
| Contextual relevance | Ignores current need | Partly fits context | Strongly fits persona and current situation |
| Recommendation usefulness | Poor or repetitive list | Some useful items | Ranked list feels actionable and diverse |
| Explanation quality | Vague | Mentions broad reason | Explains score drivers and trade-offs clearly |
| Cold-start quality | Fails without history | Uses persona only | Handles persona, context, metadata, and Nigerian cues well |
| Cross-domain usefulness | Cannot recommend outside one category | Some cross-domain awareness | Cross-domain items are sensible when context supports them |
| Nigerian contextual fit | Generic global recommendations | Some local relevance | Uses price, delivery, portion, spice, location, and local examples naturally |

## Overall Notes

Reviewers should mark any obviously unsafe, offensive, or fabricated claim. Mild Nigerian English is acceptable when it improves realism, but excessive slang should reduce the tone realism score.
