"""Score all SWE-bench Verified issues with Jev (resumable).

    export TYPESAFE_API_KEY=...
    python run_jev.py                  # writes raw/issue_jev.jsonl
    python run_jev.py --dry-run        # print the first request payload and exit
"""
import argparse
import json
from concurrent.futures import ThreadPoolExecutor

import requests

from engeff import data, jev

OUT = "raw/issue_jev.jsonl"

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="jev-latest")
ap.add_argument("--workers", type=int, default=8)
ap.add_argument("--limit", type=int, help="only the first N pending issues (for a trial run)")
ap.add_argument("--dry-run", action="store_true")
args = ap.parse_args()

issues = data.load_issues()
if args.dry_run:
    print(json.dumps(jev.build_payload(issues[0]["problem_statement"][:200] + "...", args.model), indent=2))
    raise SystemExit

done = data.done_ids(OUT)
pending = [i for i in issues if i["instance_id"] not in done][: args.limit]
session = requests.Session()


def work(issue):
    try:
        return jev.score_issue(issue, args.model, session)
    except Exception as e:  # not written, so it is retried on the next run
        print(f"{issue['instance_id']}: {type(e).__name__}: {e}")


with ThreadPoolExecutor(args.workers) as ex:
    for n, rec in enumerate(ex.map(work, pending), 1):
        if rec:
            data.append(OUT, rec)
        if n % 25 == 0:
            print(f"{n}/{len(pending)}")
