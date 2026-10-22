"""Build results/scores.csv and results/stats.json from the raw ratings in raw/.

    python analyze.py

Reads the issue-text ratings (raw/issue_*) and the PR title+body ratings (raw/pr_*),
joins them per instance, and computes every statistic quoted in the README.
"""
import csv
import json
import os
from collections import Counter

from datasets import load_dataset

from engeff import data

SCORES = range(4)

issue = {m: data.load_chunks(f"raw/issue_{m}") for m in ("haiku", "sonnet")}
issue["jev"] = data.load_results("raw/issue_jev.jsonl")
pr = {m: data.load_chunks(f"raw/pr_{m}") for m in ("haiku", "sonnet")}

ids = sorted(issue["sonnet"])
repo = {r["instance_id"]: r["repo"] for r in load_dataset("princeton-nlp/SWE-bench_Verified", split="test")}


def pr_score(m, i):
    r = pr[m][i]
    return None if r.get("insufficient_info") or r.get("score") is None else r["score"]


def dist(values):
    c = Counter(values)
    return {s: c.get(s, 0) for s in SCORES} | ({"n/a": c.get(None, 0)} if None in c else {})


def agreement(a, b):
    """a, b: {id: score or None}. Exact / within-1 agreement over ids where both are scored."""
    both = [i for i in a if a[i] is not None and b.get(i) is not None]
    d = [abs(a[i] - b[i]) for i in both]
    return {"n": len(both), "exact": sum(x == 0 for x in d) / len(both),
            "within_1": sum(x <= 1 for x in d) / len(both), "two_or_more": sum(x >= 2 for x in d)}


iss = {m: {i: issue[m][i]["score"] for i in ids} for m in issue}
prs = {m: {i: pr_score(m, i) for i in ids} for m in pr}

agree_sonnet = [i for i in ids if prs["sonnet"][i] is not None and iss["sonnet"][i] == prs["sonnet"][i]]
agree_all = [i for i in ids if None not in (prs["haiku"][i], prs["sonnet"][i])
             and len({iss["haiku"][i], iss["sonnet"][i], prs["haiku"][i], prs["sonnet"][i]}) == 1]

jev_hi = [i for i in ids if issue["jev"][i]["confidence"] >= 0.85]
confusion = [[sum(1 for i in ids if iss["sonnet"][i] == a and prs["sonnet"][i] == b) for b in SCORES] for a in SCORES]

stats = {
    "n": len(ids),
    "distribution": {
        "issue_haiku": dist(iss["haiku"].values()), "issue_sonnet": dist(iss["sonnet"].values()),
        "pr_haiku": dist(prs["haiku"].values()), "pr_sonnet": dist(prs["sonnet"].values()),
        "issue_jev": dist(iss["jev"].values()),
    },
    "agreed_set": {
        "sonnet_issue_equals_pr": {"n": len(agree_sonnet), "distribution": dist(iss["sonnet"][i] for i in agree_sonnet)},
        "all_four": {"n": len(agree_all), "distribution": dist(iss["sonnet"][i] for i in agree_all)},
    },
    "models_on_issues": {
        "haiku_vs_sonnet": agreement(iss["haiku"], iss["sonnet"]),
        "jev_vs_sonnet": agreement(iss["jev"], iss["sonnet"]),
        "jev_vs_haiku": agreement(iss["jev"], iss["haiku"]),
        "jev_confident_ge_0.85": {
            "n": len(jev_hi),
            "agree_with_sonnet": sum(iss["jev"][i] == iss["sonnet"][i] for i in jev_hi) / len(jev_hi)},
    },
    "models_on_prs": {"haiku_vs_sonnet": agreement(prs["haiku"], prs["sonnet"])},
    "issue_vs_pr": {
        "haiku": agreement(iss["haiku"], prs["haiku"]),
        "sonnet": agreement(iss["sonnet"], prs["sonnet"]),
        "sonnet_confusion_rows_issue_cols_pr": confusion,
        "pr_insufficient_info": {m: sum(prs[m][i] is None for i in ids) for m in prs},
    },
}

os.makedirs("results", exist_ok=True)
with open("results/stats.json", "w") as f:
    json.dump(stats, f, indent=2)

cols = ["instance_id", "repo", "issue_haiku", "issue_sonnet", "issue_jev", "issue_jev_confidence",
        "pr_haiku", "pr_sonnet", "issue_pr_agree_sonnet", "agree_all_four"]
with open("results/scores.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(cols)
    for i in ids:
        w.writerow([i, repo[i], iss["haiku"][i], iss["sonnet"][i], iss["jev"][i], issue["jev"][i]["confidence"],
                    prs["haiku"][i], prs["sonnet"][i], int(i in set(agree_sonnet)), int(i in set(agree_all))])

print(json.dumps(stats, indent=2))

# Level 3 (design-like) tasks: every task at least one of the four Claude ratings scores 3.
with open("results/level3.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["instance_id", "repo", "claude_ratings_at_3_of_4", "jev_at_3",
                "issue_haiku", "issue_sonnet", "pr_haiku", "pr_sonnet"])
    rows3 = []
    for i in ids:
        four = [iss["haiku"][i], iss["sonnet"][i], prs["haiku"][i], prs["sonnet"][i]]
        n3 = sum(x == 3 for x in four)
        if n3:
            rows3.append((n3, i, four))
    for n3, i, four in sorted(rows3, key=lambda t: (-t[0], t[1])):
        w.writerow([i, repo[i], n3, int(iss["jev"][i] == 3), *four])
