"""Replicate public model listing — diff for new model slugs.

Works unauthenticated where the API allows it; set REPLICATE_API_TOKEN
(a free account token) if you see 401/403 in state/log.jsonl.
"""
import os

from ..util import get


def fetch(src):
    headers = {}
    token = os.environ.get("REPLICATE_API_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    resp = get("https://api.replicate.com/v1/models", headers=headers)
    items = []
    for model in resp.json().get("results", []):
        slug = "%s/%s" % (model.get("owner"), model.get("name"))
        items.append({
            "id": "replicate:" + slug,
            "title": "New Replicate model: " + slug,
            "url": model.get("url") or "https://replicate.com/" + slug,
            "text": (model.get("description") or "")[:400],
        })
    return items
