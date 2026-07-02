"""Persistence: seen.json (dedupe state) and log.jsonl (tuning log)."""
import json
from pathlib import Path

EMPTY = {"seen": {}, "recent": [], "failures": {}}

MAX_SEEN = 50000


def load(path):
    p = Path(path)
    if not p.exists():
        return json.loads(json.dumps(EMPTY))
    state = json.loads(p.read_text())
    for key, default in EMPTY.items():
        state.setdefault(key, json.loads(json.dumps(default)))
    return state


def save(path, state):
    if len(state["seen"]) > MAX_SEEN:
        newest = sorted(state["seen"].items(), key=lambda kv: kv[1])[-MAX_SEEN:]
        state["seen"] = dict(newest)
    Path(path).write_text(json.dumps(state, ensure_ascii=False) + "\n")


def append_log(path, records, cap=5000):
    p = Path(path)
    lines = p.read_text().splitlines() if p.exists() else []
    lines += [json.dumps(r, ensure_ascii=False) for r in records]
    p.write_text("\n".join(lines[-cap:]) + "\n")
