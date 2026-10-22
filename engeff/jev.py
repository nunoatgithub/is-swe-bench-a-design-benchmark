"""Jev (TypeSafe System One) backend: scores each issue on the 0-3 engineering-effort scale.

Jev takes a `state` and typed questions and returns calibrated probabilities. A Score
question over four ordered levels maps one-to-one onto our scale. Unlike the LLM passes it
returns no free-text reason; it returns `probabilities` per level instead.

Docs: https://docs.typesafe.ai/primitives/score   Endpoint: POST https://api.typesafe.ai/v1/systemone
"""
import os
import time

import requests

from .scale import INSTRUCTIONS, LEVELS

URL = "https://api.typesafe.ai/v1/systemone"
QUESTION_ID = "effort"


def build_payload(problem_statement: str, model: str) -> dict:
    return {
        "state": problem_statement,
        "model": model,
        "questions": {
            QUESTION_ID: {"type": "score", "instructions": INSTRUCTIONS, "criteria": LEVELS},
        },
    }


def to_record(instance_id: str, body: dict) -> dict:
    """Map a Jev response onto the shared result schema (see rubrics/issue.md)."""
    ans = body["answers"][QUESTION_ID]
    return {
        "instance_id": instance_id,
        "score": round(ans["score"]),
        "score_raw": ans["score"],
        "confidence": ans["confidence"],
        "probabilities": ans["probabilities"],
        "reason": None,
        "model": body.get("model"),
        "usage": body.get("usage"),
    }


def score_issue(issue: dict, model: str = "jev-latest", session: requests.Session | None = None,
                retries: int = 5) -> dict:
    http = session or requests
    headers = {"Authorization": f"Bearer {os.environ['TYPESAFE_API_KEY']}"}
    payload = build_payload(issue["problem_statement"], model)
    for attempt in range(retries):
        r = http.post(URL, json=payload, headers=headers, timeout=60)
        if r.status_code == 429 or r.status_code >= 500:
            time.sleep(min(2 ** attempt, 30))
            continue
        r.raise_for_status()
        return to_record(issue["instance_id"], r.json())
    r.raise_for_status()
    raise RuntimeError("unreachable")
