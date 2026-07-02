"""Newest Hugging Face models per pipeline tag, filtered for early traction
(likes + downloads above a small threshold) so empty repos don't flood the feed."""
from ..util import get

API = "https://huggingface.co/api/models"

DEFAULT_TAGS = [
    "text-to-video", "text-to-image", "image-to-video", "image-to-image",
    "text-to-3d", "text-to-audio", "text-to-speech",
]


def fetch(src):
    min_traction = src.get("min_traction", 5)
    items, seen = [], set()
    for tag in src.get("pipeline_tags", DEFAULT_TAGS):
        resp = get(API, params={
            "pipeline_tag": tag, "sort": "createdAt", "direction": -1, "limit": 25,
        })
        for model in resp.json():
            model_id = model.get("id")
            if not model_id or model_id in seen:
                continue
            likes = model.get("likes") or 0
            downloads = model.get("downloads") or 0
            if likes + downloads < min_traction:
                continue
            seen.add(model_id)
            items.append({
                "id": "hf:" + model_id,
                "title": "New Hugging Face model: " + model_id,
                "url": "https://huggingface.co/" + model_id,
                "text": "pipeline: %s; %d likes, %d downloads shortly after creation" % (tag, likes, downloads),
            })
    return items
