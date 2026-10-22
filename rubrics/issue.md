You rate GitHub issues from SWE-bench by how much engineering and design effort a correct fix requires. Judge only from the issue text (problem_statement); do not try to look up the real fix.

Score (integer 0-3) = the engineering/design effort of the fix:
- 0: mechanical fix, obvious from the issue (typo, wrong condition or constant, missing check, one-line change).
- 1: small localized change. The desired behavior is clear, but the code needs some thought (a few lines in one place, a simple edge case).
- 2: requires real choices: how to shape a parameter/API, which edge cases to cover, how to keep existing behavior compatible, or changes in a few places that must stay consistent.
- 3: requires design work: several viable approaches with tradeoffs, a new abstraction or semantics, or coordinated changes across modules/layers.

Rate the fix itself, not how hard it is to find the bug. A long hard-to-diagnose bug with a one-line fix is a 0 or 1. If the issue itself proposes a concrete fix, rate the effort a correct fix needs, not the proposal's length.

Output one JSON object per line (JSONL), one line per instance, exactly:
{"instance_id": "...", "score": 0|1|2|3, "confidence": 0.0-1.0, "reason": "<one sentence>"}
