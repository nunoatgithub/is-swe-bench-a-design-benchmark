"""Fetch PR title, body, labels and dates for every SWE-bench Verified instance.

    export GITHUB_TOKEN=...        # read-only, no scopes needed; unauthenticated limit is 60 req/hour
    python fetch_prs.py            # writes swebench_verified_prs.jsonl (resumable)

The PR number is the numeric suffix of `instance_id` (e.g. django__django-11099 -> 11099).
"""
import json
import os
import time

import requests
from datasets import load_dataset

OUT = "swebench_verified_prs.jsonl"


def get(url, headers):
    while True:
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code in (403, 429) and r.headers.get("X-RateLimit-Remaining") == "0":
            reset = int(r.headers["X-RateLimit-Reset"])
            time.sleep(max(reset - time.time(), 0) + 5)
            continue
        return r


def main():
    token = os.environ["GITHUB_TOKEN"]
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    ds = load_dataset("princeton-nlp/SWE-bench_Verified", split="test")

    done = set()
    if os.path.exists(OUT):
        with open(OUT) as f:
            done = {json.loads(line)["instance_id"] for line in f}

    with open(OUT, "a") as f:
        for row in ds:
            iid = row["instance_id"]
            if iid in done:
                continue
            repo, num = row["repo"], int(iid.rsplit("-", 1)[1])

            pr = get(f"https://api.github.com/repos/{repo}/pulls/{num}", headers)
            if pr.status_code != 200:
                print(f"{iid}: HTTP {pr.status_code}")
                continue
            pr = pr.json()

            record = {
                "instance_id": iid,
                "repo": repo,
                "pull_number": num,
                "title": pr["title"],
                "body": pr["body"] or "",
                "labels": [l["name"] for l in pr["labels"]],
                "created_at": pr["created_at"],
                "merged_at": pr["merged_at"],
                "url": pr["html_url"],
            }
            f.write(json.dumps(record) + "\n")
            f.flush()


if __name__ == "__main__":
    main()
