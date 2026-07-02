"""Batch classification of candidate items.

Two backends:
  api        — Anthropic API (needs ANTHROPIC_API_KEY, pay-per-token)
  claude-cli — headless `claude -p` (runs on a Claude subscription, no API key)
"""
import json
import re
import subprocess

CATEGORIES = {
    "video-gen", "image-gen", "3d", "audio-music", "editing-vfx",
    "avatar-lipsync", "creative-platform", "model-infra", "other",
    "research", "funding",
}

KINDS = {"launch", "research", "funding", "skip"}

SKIPPED = {"kind": "skip", "category": "other", "relevance": 1,
           "headline": "", "summary": "", "detail": ""}


def classify_batch(items, model, prompt_template, backend="api",
                   cli_bin="claude", cli_model="haiku"):
    """Classify a list of items in one model call. Returns one dict per item, in order."""
    payload = [
        {
            "i": i,
            "title": item["title"][:200],
            "source": item["source"],
            "url": item["url"],
            "text": (item.get("text") or "")[:400],
        }
        for i, item in enumerate(items)
    ]
    prompt = prompt_template.replace(
        "{{ITEMS}}", json.dumps(payload, ensure_ascii=False, indent=1))

    last_err = None
    for _ in range(2):  # one retry on malformed output
        if backend == "claude-cli":
            text = _generate_cli(prompt, cli_bin, cli_model)
        else:
            text = _generate_api(prompt, model)
        try:
            results = _parse_json_array(text)
            by_index = {r["i"]: _normalize(r) for r in results
                        if isinstance(r, dict) and "i" in r}
            return [by_index.get(i, dict(SKIPPED)) for i in range(len(items))]
        except (ValueError, KeyError, TypeError) as exc:
            last_err = exc
    raise ValueError("classifier returned unparseable output: %s" % last_err)


def _generate_api(prompt, model):
    from anthropic import Anthropic
    message = Anthropic().messages.create(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in message.content if block.type == "text")


def _generate_cli(prompt, cli_bin, cli_model):
    proc = subprocess.run(
        [cli_bin, "-p", "--model", cli_model],
        input=prompt.encode("utf-8"), capture_output=True, timeout=900)
    if proc.returncode != 0:
        raise RuntimeError("claude CLI failed: %s" %
                           proc.stderr.decode("utf-8", "ignore")[:300])
    return proc.stdout.decode("utf-8", "ignore")


def _parse_json_array(text):
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("no JSON array in response")
    return json.loads(text[start:end + 1])


def _normalize(raw):
    kind = raw.get("kind")
    if kind not in KINDS:
        # older prompt shape: fall back to is_launch
        kind = "launch" if raw.get("is_launch") else "skip"
    category = raw.get("category", "other")
    if kind in ("research", "funding"):
        category = kind
    try:
        relevance = max(1, min(10, int(float(raw.get("relevance", 1)))))
    except (ValueError, TypeError):
        relevance = 1
    return {
        "kind": kind,
        "category": category if category in CATEGORIES else "other",
        "relevance": relevance,
        "headline": str(raw.get("headline") or "").strip()[:90],
        "summary": str(raw.get("summary") or "").strip()[:500],
        "detail": str(raw.get("detail") or "").strip()[:1200],
    }
