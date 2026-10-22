"""Issue loading and result I/O shared by all backends."""
import json
import os
from typing import Iterable

from datasets import load_dataset


def load_issues() -> list[dict]:
    """SWE-bench Verified issues as [{instance_id, problem_statement}]."""
    return [
        {"instance_id": r["instance_id"], "problem_statement": r["problem_statement"]}
        for r in load_dataset("princeton-nlp/SWE-bench_Verified", split="test")
    ]


def done_ids(path: str) -> set[str]:
    if not os.path.exists(path):
        return set()
    with open(path) as f:
        return {json.loads(l)["instance_id"] for l in f if l.strip()}


def append(path: str, record: dict) -> None:
    with open(path, "a") as f:
        f.write(json.dumps(record) + "\n")


def load_results(path: str) -> dict[str, dict]:
    with open(path) as f:
        return {r["instance_id"]: r for r in map(json.loads, filter(str.strip, f))}


def load_chunks(pattern_dir: str) -> dict[str, dict]:
    """Merge chunk_*.jsonl files written by Claude Code subagents."""
    import glob

    out: dict[str, dict] = {}
    for p in sorted(glob.glob(f"{pattern_dir}/chunk_*.jsonl")):
        out.update(load_results(p))
    return out
