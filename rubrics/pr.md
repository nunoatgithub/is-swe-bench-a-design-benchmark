You rate the engineering and design effort of a fix, as described by the pull request that made it. You see only the PR title and body (the author's own description of the change).

Score (integer 0-3) = the engineering/design effort the fix required:
- 0: mechanical fix, obvious (typo, wrong condition or constant, missing check, one-line change).
- 1: small localized change. The desired behavior is clear, but the code needed some thought (a few lines in one place, a simple edge case).
- 2: required real choices: how to shape a parameter/API, which edge cases to cover, how to keep existing behavior compatible, or changes in a few places that must stay consistent.
- 3: required design work: several viable approaches with tradeoffs, a new abstraction or semantics, or coordinated changes across modules/layers.

Rate the fix itself, not how hard the bug was to find. Judge only from the title and body; do not guess at code you cannot see.

If the title and body do not give enough information to judge the effort (for example the body is empty or only says "Fixes #1234" and the title is too generic), set "insufficient_info": true and "score": null. Do not guess. A PR whose body is short but whose title clearly describes a small change can still be scored.

Output one JSON object per line (JSONL), one line per instance, exactly:
{"instance_id": "...", "score": 0|1|2|3|null, "insufficient_info": true|false, "confidence": 0.0-1.0, "reason": "<one sentence>"}
