"""Split the inputs into chunk files that Claude Code subagents rate in parallel.

    python prepare_chunks.py --source issues --size 25   # -> chunks/issue_25/
    python prepare_chunks.py --source prs    --size 50   # -> chunks/pr_50/

`issues` reads the SWE-bench Verified problem statements; `prs` reads the output of
fetch_prs.py (PR title + body).
"""
import argparse
import json
import os

from engeff import data

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
ap.add_argument("--source", choices=["issues", "prs"], required=True)
ap.add_argument("--size", type=int, default=25, help="instances per chunk (one subagent each)")
args = ap.parse_args()

if args.source == "issues":
    rows = data.load_issues()
    name = f"issue_{args.size}"
else:
    with open("swebench_verified_prs.jsonl") as f:
        rows = [{k: r[k] for k in ("instance_id", "title", "body")} for r in map(json.loads, f)]
    rows.sort(key=lambda r: r["instance_id"])
    name = f"pr_{args.size}"

out_dir = os.path.join("chunks", name)
os.makedirs(out_dir, exist_ok=True)
for i in range(0, len(rows), args.size):
    with open(f"{out_dir}/chunk_{i // args.size:02d}.json", "w") as f:
        json.dump(rows[i:i + args.size], f, indent=1)
print(f"{len(rows)} rows -> {(len(rows) + args.size - 1) // args.size} chunks in {out_dir}")
