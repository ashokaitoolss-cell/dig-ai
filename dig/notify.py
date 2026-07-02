"""Instant push notifications via ntfy.sh."""
import requests

EMOJI = {
    "video-gen": "🎬", "image-gen": "🎨", "3d": "🧊", "audio-music": "🎵",
    "editing-vfx": "✂️", "avatar-lipsync": "🗣", "creative-platform": "🛠",
    "model-infra": "⚙️", "other": "📡",
}


def send(entry, topic, high_priority_threshold, extra=""):
    """Publish one launch. Uses ntfy's JSON endpoint because plain HTTP headers
    are latin-1 only and the title carries a category emoji."""
    payload = {
        "topic": topic,
        "title": "%s %s" % (EMOJI.get(entry["category"], "📡"), entry["headline"]),
        "message": (entry["summary"] + extra).rstrip(),
        "click": entry["url"],
        "tags": [entry["category"]],
        "priority": 4 if entry["relevance"] >= high_priority_threshold else 3,
    }
    resp = requests.post("https://ntfy.sh", json=payload, timeout=15)
    resp.raise_for_status()
