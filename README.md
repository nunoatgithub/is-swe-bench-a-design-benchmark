# How much engineering does SWE-bench Verified ask for?

SWE-bench Verified is the standard benchmark for coding agents: 500 real GitHub issues, each
paired with the pull request that fixed it. This project investigates **how much effort each fix
requires**, to see what kind of work the benchmark actually measures and how much actual design effort it entails.

Every task gets a score from 0 to 3, rated by language models from the issue text and,
independently, from the title and body of the PR that fixed it.

## Headline result

**SWE-bench Verified is almost entirely bug fixing.** About two thirds of the tasks are scored
0 or 1: a mechanical fix or a small localized change. The rest are mostly scored 2, which on
this scale means correctness and interface decisions (how to shape an API, which edge cases to
handle, how to stay compatible), not architecture. Only about 4% reach the top score, and
those are candidates for design work that this study did not verify. **Nothing here is
evidence that the benchmark contains a meaningful share of real design challenges.**

| Score | Meaning |
|---|---|
| **0** | Mechanical fix, obvious from the text (typo, wrong condition or constant, missing check, one-line change) |
| **1** | Small localized change; the desired behavior is clear but the code needs some thought |
| **2** | A fix with choices to make: how to shape a parameter or API, which edge cases to cover, how to keep behavior compatible, or consistent changes in a few places. These are correctness and interface decisions, not design in the architectural sense |
| **3** | The closest the scale gets to design: several viable approaches with tradeoffs, a new abstraction or semantics, or coordinated changes across modules or layers. Judged from text only and not verified, so a 3 may still be a large bug fix |

Number of tasks per score (out of 500; percentages are of 500):

| Score | Rated from the issue: Haiku | Rated from the issue: Sonnet | Rated from the PR: Haiku | Rated from the PR: Sonnet |
|---|---|---|---|---|
| **0** | 125 (25%) | 104 (21%) | 99 (20%) | 82 (16%) |
| **1** | 223 (45%) | 220 (44%) | 272 (54%) | 261 (52%) |
| **2** | 141 (28%) | 154 (31%) | 107 (21%) | 128 (26%) |
| **3** | 11 (2%) | 22 (4%) | 9 (2%) | 20 (4%) |
| Too thin to score | – | – | 13 | 9 |

All four columns tell the same story: 1 is the most common score, and 3 is rare. By Sonnet's
ratings, 65% of tasks are 0 or 1 when rated from the issue, and 70% of the scorable tasks are
0 or 1 when rated from the PR. Even the 2s (about 30%) are not design in the architectural
sense, so the share of design-heavy tasks is bounded by the 3s: roughly 2-4%, before any
validation.

### The level 3 tasks (the design-like ones)

Level 3 is the one that matches design work, so it is the number to watch. No more than
about 4% of tasks reach it in any single rating (Haiku 2%, Sonnet 4%, Jev under 1%). Counting
how many of the four Claude ratings (Haiku and Sonnet, from the issue and from the PR) give
a task a 3:

| Claude ratings at 3 (of 4) | Tasks |
|---|---|
| 4 | 2 |
| 3 | 8 |
| 2 | 8 |
| 1 | 14 |
| **At least one** | **32 (6% of 500)** |

Only 10 tasks have three or more of the four ratings at 3, and 2 have all four. These
are the tasks to read first if you want to examine the design-like cases; `analyze.py` lists
them in `results/level3.csv`. The 14 tasks that Sonnet rates 3 from both
the issue and the PR are spread over nine repositories, with Django the largest share (5).

### The high-confidence subset

Taking only the tasks where the issue-based and PR-based Sonnet scores agree gives a set of
**313 tasks** with a stable label:

| Score | Tasks | Share |
|---|---|---|
| 0 | 54 | 17% |
| 1 | 156 | 50% |
| 2 | 89 | 28% |
| 3 | 14 | 4% |

A stricter set, where all four ratings (Haiku and Sonnet, from the issue and from the PR)
agree, has **153 tasks**: 34 at 0, 86 at 1, 31 at 2 and 2 at 3. `analyze.py` writes the
per-task scores and both subset flags to `results/scores.csv`.

### What this does and does not show

This is evidence that the benchmark measures bug fixing: small, localized, well-specified
corrections. The 2s should not be read as design challenges. They are fixes with choices
about interfaces, edge cases and compatibility, which is correctness work, not design or
resource management. The 3s are the only tasks that could involve design, and they are about
4% of the benchmark, judged from text by models.

The score measures the *effort of the fix itself*. It says nothing about how hard the fix is
to *find* in a large codebase, or how much reading and testing it takes. Also, SWE-bench
Verified was deliberately filtered to well-specified, tractable issues, so a skew toward small
fixes is partly by design. See [Limitations](#limitations).

## How much do the raters agree?

Three raters scored the issue text: Claude Haiku, Claude Sonnet, and Jev (TypeSafe's scoring
model). A task counts as agreeing when both raters give the same 0-3 score.

| Pair (issue text) | Exactly equal | Within 1 point | Differ by 2+ |
|---|---|---|---|
| Haiku vs Sonnet | 68.8% | 99.2% | 4 of 500 |
| Jev vs Haiku | 62.4% | 99.4% | 3 of 500 |
| Jev vs Sonnet | 60.6% | 98.4% | 8 of 500 |
| Haiku vs Sonnet, rated from the PR | 67.8% | 100% | 0 of 481 |

The raters almost never contradict each other; they mostly disagree by one point at a boundary.

- **Sonnet rates slightly higher than Haiku**, mainly at the top end: 22 tasks at 3 against 11.
- **Jev squeezes scores toward 1.** It gives 1 to 353 of 500 tasks (71%) and rarely gives a 2
  or a 3 (64 and 2). Its probabilities are informative at the top: on the 39 tasks where its
  confidence is 0.85 or higher, it matches Sonnet 97% of the time. Below 0.85 its confidence
  tells you little.
- **Cost.** Jev bills about $0.042 per million input tokens and nothing for output. The whole
  500-task run used 466K input tokens, about $0.02. It returns no explanation, only
  probabilities.

## Issue text versus PR description

The PR description says what the author actually did, while the issue is written before the
fix. How well do the two agree?

| Model | Tasks scored from both | Exactly equal | Within 1 point | Differ by 2+ |
|---|---|---|---|---|
| Sonnet | 491 | 63.7% | 99.0% | 5 |
| Haiku | 487 | 53.4% | 95.9% | 20 |

Sonnet's agreement is the more reliable one; Haiku's is noisier. A PR is "too thin to score"
when its body is empty or only says "Fixes #1234" and its title says nothing useful. That
affected 9 tasks for Sonnet and 13 for Haiku.

When the sources differ it is almost always by one point. Sonnet's issue score (rows) against
its PR score (columns):

| Issue \ PR | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| **0** | 54 | 50 | 0 | 0 |
| **1** | 25 | 156 | 33 | 1 |
| **2** | 3 | 54 | 89 | 5 |
| **3** | 0 | 1 | 6 | 14 |

Issues that look like 0 often turn out to be 1 in the PR (50 cases), and issues scored 2
are often a 1 in the PR (54 cases), which may mean the PR shows a smaller change than the issue
suggested.

## Method

**Data.** The 500 tasks of
[`princeton-nlp/SWE-bench_Verified`](https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified).
The issue text is the dataset's `problem_statement`, which is what the benchmark's agent sees.
The PR title and body are fetched from the GitHub API (`fetch_prs.py`); the PR number is the
suffix of the `instance_id`. The agent never sees the PR text.

**Rating.** Each rater scores every task on the 0-3 scale from one source only:
- *Issue text*: [`rubrics/issue.md`](rubrics/issue.md). The rater judges the effort a correct
  fix would need.
- *PR title and body*: [`rubrics/pr.md`](rubrics/pr.md). Same scale, rated from the author's
  description, with an `insufficient_info` option instead of a guess.

Claude Haiku and Claude Sonnet ran as Claude Code subagents (model aliases `haiku` and `sonnet`,
default settings), each rating a chunk of tasks in parallel (25 per agent for Haiku, 50 for
Sonnet) and seeing nothing but the rubric and its chunk. The exact prompt is in
[`prompts/subagent.md`](prompts/subagent.md). Each rater returns a score, a confidence and a
one-sentence reason; the per-task outputs go to `raw/`.

Jev was queried through its HTTP API with a Score question whose four levels are the same
anchors ([`engeff/scale.py`](engeff/scale.py)). Its score is the probability-weighted mean of
the levels, rounded to the nearest integer; the unrounded value is kept in `raw/issue_jev.jsonl`.
The run used `jev-1.14.0`.

**Earlier attempt.** A first version of this analysis used a yes/no "design challenge" label
with category tags. It was dropped because the categories mixed difficulty with design effort
and the yes/no was too coarse. Only the 0-3 scale is reported here.

## Limitations

- **No human validation.** All scores are model judgments. The raters agree with each other,
  which shows consistency, not correctness; they could share the same blind spots.
- **Effort is judged from text, not code.** The raters never see the repository or the patch.
  Both models sometimes invent complexity or miss it. In a manual look at the four tasks where
  Haiku and Sonnet differed most, the issue described a small, clearly specified change in all
  four, and each model had over-rated one of them with a speculative reason.
- **The scale rates the fix, not the search.** Locating the right place in a large codebase,
  reading the surrounding code and checking the behavior are not scored.
- **Design appears only at level 3.** The scale rates the effort of the fix. Level 2 mixes
  interface and correctness decisions with a little real design, and the scale does not
  separately measure architecture or resource management. Conclusions about design should rest
  on the level 3 tasks alone, and those were not validated by a person.
- **A sample of one benchmark.** The results describe SWE-bench Verified only.
- **Single run.** Model outputs can vary between runs; I did not measure that.

## Reproducing

Requires Python 3.10+.

```bash
conda create -p ./.conda python=3.11 && conda activate ./.conda
pip install -r requirements.txt

# 1. PR titles and bodies (needs a GitHub token; no scopes required)
export GITHUB_TOKEN=...
python fetch_prs.py

# 2. Chunk the inputs for the Claude Code subagents
python prepare_chunks.py --source issues --size 25   # Haiku
python prepare_chunks.py --source issues --size 50   # Sonnet
python prepare_chunks.py --source prs --size 25
python prepare_chunks.py --source prs --size 50

# 3. Rate with Claude Code subagents: one agent per chunk, using prompts/subagent.md
#    (outputs go to raw/issue_{haiku,sonnet}/ and raw/pr_{haiku,sonnet}/)

# 4. Rate the issues with Jev (needs a TypeSafe API key)
export TYPESAFE_API_KEY=...
python run_jev.py --model jev-1.14.0

# 5. Build the results table and statistics
python analyze.py

python -m unittest discover -s tests -t .
```

Step 3 was done interactively in Claude Code; it is not a script. The ratings behind this
README are committed in `raw/` and the tables built from them in `results/`, so steps 1-4 can be
skipped and `analyze.py` run directly. A fresh rerun of the rating steps may differ slightly,
since model outputs vary.

## Repository layout

| Path | Contents |
|---|---|
| `results/scores.csv` | One row per task: all scores, Jev confidence, and the two agreement flags |
| `results/level3.csv` | The 32 tasks at least one Claude rating scores 3, ranked by how many agree |
| `results/stats.json` | Every number quoted in this README |
| `raw/` | Per-task outputs of each rater, including the reason text |
| `rubrics/` | The two rating rubrics |
| `prompts/subagent.md` | The prompt given to each subagent |
| `engeff/` | Shared code: the scale, data loading, the Jev client |
| `fetch_prs.py`, `prepare_chunks.py`, `run_jev.py`, `analyze.py` | The pipeline |
| `tests/` | Unit tests for the Jev client |

`results/scores.csv` columns: `instance_id`, `repo`, `issue_haiku`, `issue_sonnet`,
`issue_jev`, `issue_jev_confidence`, `pr_haiku`, `pr_sonnet` (empty when the PR was too thin to
score), `issue_pr_agree_sonnet`, `agree_all_four`.

The SWE-bench issue text and the GitHub PR text are not redistributed here; they are fetched
by the scripts. The files in `raw/` and `results/` contain only scores, confidences and
one-sentence reasons written by the raters.
