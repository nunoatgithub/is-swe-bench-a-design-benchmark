"""The 0-3 engineering-effort scale, shared by every backend that is not a Claude Code subagent.

Keep in sync with rubrics/issue.md, which carries the same anchors as prose for the subagents.
"""

INSTRUCTIONS = (
    "How much engineering and design effort does a correct fix for this GitHub issue require? "
    "Rate the fix itself, not how hard it is to find the bug."
)

LEVELS = [
    "Mechanical fix, obvious from the issue (typo, wrong condition or constant, missing check, one-line change)",
    "Small localized change; the desired behavior is clear but the code needs some thought",
    "Requires real choices: how to shape a parameter or API, which edge cases to cover, "
    "how to keep existing behavior compatible, or consistent changes in a few places",
    "Requires design work: several viable approaches with tradeoffs, a new abstraction or semantics, "
    "or coordinated changes across modules or layers",
]
