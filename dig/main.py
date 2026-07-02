"""dig.ai radar engine — fetch → dedupe → classify → notify → publish.

Usage:
    python -m dig.main             # normal run
    python -m dig.main --dry-run   # fetch + classify, print instead of notify, no writes
    python -m dig.main --seed      # mark everything currently visible as seen, send nothing
    SEED_MODE=1 python -m dig.main # same as --seed
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

import yaml

from . import state as st_mod
from . import util
from .classify import classify_batch
from .fetchers import FETCHERS
from .notify import EMOJI, send

ROOT = Path(__file__).resolve().parent.parent
SEEN_PATH = ROOT / "state" / "seen.json"
LOG_PATH = ROOT / "state" / "log.jsonl"
FEED_PATH = ROOT / "docs" / "feed.json"

RECENT_WINDOW_DAYS = 14  # window for fuzzy cross-source dedupe


def fetch_all(sources, state, log):
    items = []
    for src in sources:
        if not src.get("enabled", True):
            continue
        source_id = src["id"]
        try:
            fetched = FETCHERS[src["type"]](src)
            state["failures"][source_id] = 0
        except Exception as exc:  # fail soft: one broken source never kills the run
            count = state["failures"].get(source_id, 0) + 1
            state["failures"][source_id] = count
            log.append({"ts": util.now_iso(), "event": "fetch_error", "source": source_id,
                        "error": str(exc)[:300], "consecutive_failures": count})
            print("  [warn] %s: %s" % (source_id, exc), file=sys.stderr)
            continue
        for item in fetched:
            item["source"] = src.get("name", source_id)
            item["source_id"] = source_id
        items.extend(fetched)
        print("  [fetch] %s: %d" % (source_id, len(fetched)))
    return items


def _is_fuzzy_dup(title_norm, domain, entries):
    for _, seen_domain, seen_title in entries:
        ratio = util.similar(title_norm, seen_title)
        if ratio > 0.9 or (seen_domain == domain and ratio > 0.75):
            return True
    return False


def dedupe(items, state, log):
    """Drop exact repeats (seen hash) and cross-source repeats of the same
    launch (same target domain + similar title, or near-identical title)."""
    cutoff = time.time() - RECENT_WINDOW_DAYS * 86400
    state["recent"] = [entry for entry in state["recent"] if entry[0] > cutoff]
    fresh, batch_titles = [], []
    for item in items:
        if not item.get("title") or not item.get("url"):
            continue
        digest = util.item_hash(item)
        if digest in state["seen"]:
            continue
        title_norm = util.norm_title(item["title"])
        domain = util.domain_of(item["url"])
        if _is_fuzzy_dup(title_norm, domain, state["recent"]) or \
           _is_fuzzy_dup(title_norm, domain, batch_titles):
            state["seen"][digest] = util.now_iso()
            log.append({"ts": util.now_iso(), "event": "fuzzy_dup",
                        "source": item["source_id"], "title": item["title"][:150]})
            continue
        item.update(_hash=digest, _title_norm=title_norm, _domain=domain)
        batch_titles.append((time.time(), domain, title_norm))
        fresh.append(item)
    return fresh


def mark_seen(item, state):
    state["seen"][item["_hash"]] = util.now_iso()
    state["recent"].append([time.time(), item["_domain"], item["_title_norm"]])


def run(dry_run=False, seed=False):
    cfg = yaml.safe_load((ROOT / "config.yaml").read_text())
    sources = yaml.safe_load((ROOT / "sources.yaml").read_text())["sources"]
    util.set_delay(cfg.get("request_delay_seconds", 1.5))
    topic = os.environ.get("NTFY_TOPIC", "")

    if not seed and not dry_run:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            sys.exit("ANTHROPIC_API_KEY is not set")
        if not topic:
            sys.exit("NTFY_TOPIC is not set")

    state = st_mod.load(SEEN_PATH)
    log = []

    print("[1/4] fetching sources")
    items = fetch_all(sources, state, log)
    print("[2/4] deduplicating")
    fresh = dedupe(items, state, log)
    print("  %d fetched, %d new" % (len(items), len(fresh)))

    warnings = sorted(sid for sid, n in state["failures"].items()
                      if n >= cfg.get("failure_warning_after", 5))

    if seed:
        for item in fresh:
            mark_seen(item, state)
        log.append({"ts": util.now_iso(), "event": "seed_run", "seeded": len(fresh)})
        st_mod.save(SEEN_PATH, state)
        st_mod.append_log(LOG_PATH, log, cfg.get("log_cap_lines", 5000))
        print("[seed] marked %d items as seen — no notifications sent" % len(fresh))
        return

    launches, notified = [], 0
    if fresh:
        if dry_run and not os.environ.get("ANTHROPIC_API_KEY"):
            print("[3/4] ANTHROPIC_API_KEY not set — listing new items without classification")
            for item in fresh:
                print("  · %-14s %s" % (item["source_id"], item["title"][:100]))
            print("[dry run] state, feed and log untouched")
            return
        print("[3/4] classifying %d items" % len(fresh))
        prompt = (ROOT / "prompts" / "classifier.md").read_text()
        batch_size = cfg.get("classifier_batch_size", 20)
        results = []
        for i in range(0, len(fresh), batch_size):
            chunk = fresh[i:i + batch_size]
            try:
                results.extend(classify_batch(chunk, cfg["classifier_model"], prompt))
            except Exception as exc:
                # leave the chunk unseen so the next run retries it
                log.append({"ts": util.now_iso(), "event": "classify_error",
                            "error": str(exc)[:300], "items": len(chunk)})
                print("  [warn] classifier failed on a batch of %d: %s" % (len(chunk), exc),
                      file=sys.stderr)
                results.extend([None] * len(chunk))

        print("[4/4] notifying + publishing")
        for item, result in zip(fresh, results):
            if result is None:
                continue
            mark_seen(item, state)
            log.append({"ts": util.now_iso(), "event": "classified",
                        "source": item["source_id"], "title": item["title"][:150],
                        "url": item["url"], **result})
            if not result["is_launch"] or not result["headline"]:
                continue
            entry = {
                "id": item["_hash"],
                "headline": result["headline"],
                "summary": result["summary"],
                "category": result["category"],
                "relevance": result["relevance"],
                "url": item["url"],
                "source": item["source"],
                "timestamp": util.now_iso(),
            }
            launches.append(entry)
            if result["relevance"] < cfg.get("relevance_threshold", 6):
                continue
            if dry_run:
                print("  [dry-run ping] %s %s (rel %d) — %s" % (
                    EMOJI.get(entry["category"], ""), entry["headline"],
                    entry["relevance"], entry["url"]))
                continue
            extra = ""
            if warnings and notified == 0:
                extra = "\n\n⚠️ failing sources: " + ", ".join(warnings)
            try:
                send(entry, topic, cfg.get("high_priority_threshold", 8), extra)
                notified += 1
            except Exception as exc:
                log.append({"ts": util.now_iso(), "event": "notify_error",
                            "id": entry["id"], "error": str(exc)[:200]})
                print("  [warn] ntfy failed for %s: %s" % (entry["id"], exc), file=sys.stderr)
    else:
        print("[3/4] nothing new to classify")

    if dry_run:
        print("[dry run] %d launches found — state, feed and log untouched" % len(launches))
        for entry in launches:
            print("  %2d  %-17s %s" % (entry["relevance"], entry["category"], entry["headline"]))
        return

    if launches:
        feed = json.loads(FEED_PATH.read_text()) if FEED_PATH.exists() else []
        feed = launches + feed
        FEED_PATH.write_text(
            json.dumps(feed[:cfg.get("feed_cap", 500)], ensure_ascii=False, indent=1) + "\n")

    log.append({"ts": util.now_iso(), "event": "run_summary", "fetched": len(items),
                "new": len(fresh), "launches": len(launches), "notified": notified,
                "failing_sources": warnings})
    st_mod.save(SEEN_PATH, state)
    st_mod.append_log(LOG_PATH, log, cfg.get("log_cap_lines", 5000))
    print("[done] %d launches, %d notifications" % (len(launches), notified))


def main():
    parser = argparse.ArgumentParser(description="dig.ai radar engine")
    parser.add_argument("--dry-run", action="store_true",
                        help="fetch + classify, print instead of notify, write nothing")
    parser.add_argument("--seed", action="store_true",
                        help="mark everything currently visible as seen, send nothing")
    args = parser.parse_args()
    seed = args.seed or os.environ.get("SEED_MODE") == "1"
    run(dry_run=args.dry_run, seed=seed)


if __name__ == "__main__":
    main()
