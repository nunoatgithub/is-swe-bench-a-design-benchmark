# Subagent prompt

Each chunk was rated by one Claude Code subagent (`Agent` tool, `model` = `haiku` or `sonnet`)
with this prompt. `<SOURCE>` is `issue` or `pr`, `<MODEL>` is `haiku` or `sonnet`, `<N>` is the
chunk size (25 for Haiku, 50 for Sonnet) and `<K>` the zero-padded chunk number.

```
Working dir: <repo root>. Read rubrics/<SOURCE>.md and chunks/<SOURCE>_<N>/chunk_<K>.json
(a JSON list of <N> {instance_id, ...}). Rate EVERY instance following the rubric, judging each
on its own. Write the results with the Write tool to raw/<SOURCE>_<MODEL>/chunk_<K>.jsonl
(one JSON line per instance, exactly the rubric's format, <N> lines). Do not read or use any
other files, in particular nothing under raw/. Reply only 'done <N>' when finished.
```

The agents see only their own chunk and the rubric, never each other's output. Claude Code runs at
most 20 subagents concurrently by default, so the 20 Haiku chunks run first and the 10 Sonnet
chunks follow.
