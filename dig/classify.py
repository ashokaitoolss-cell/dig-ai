"""Batch classification of candidate items via the Claude API."""
import json
import re

from anthropic import Anthropic

CATEGORIES = {
    "video-gen", "image-gen", "3d", "audio-music", "editing-vfx",
    "avatar-lipsync", "creative-platform", "model-infra", "other",
    "research", "funding",
}

KINDS = {"launch", "research", "funding", "skip"}

SKIPPED = {"kind": "skip", "category": "other", "relevance": 1,
           "headline": "", "summary": "", "detail": ""}


def classify_batch(items, model, prompt_template):
    """Classify a list of items in one API call. Returns one dict per item, in order."""
    client = Anthropic()
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
        message = client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(block.text for block in message.content if block.type == "text")
        try:
            results = _parse_json_array(text)
            by_index = {r["i"]: _normalize(r) for r in results
                        if isinstance(r, dict) and "i" in r}
            return [by_index.get(i, dict(SKIPPED)) for i in range(len(items))]
        except (ValueError, KeyError, TypeError) as exc:
            last_err = exc
    raise ValueError("classifier returned unparseable output: %s" % last_err)


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
