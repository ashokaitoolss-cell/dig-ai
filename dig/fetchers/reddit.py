"""New posts from selected subreddits via the public JSON endpoints."""
from ..util import get

DEFAULT_SUBS = ["StableDiffusion", "aivideo", "singularity"]


def fetch(src):
    items = []
    for sub in src.get("subreddits", DEFAULT_SUBS):
        resp = get("https://www.reddit.com/r/%s/new.json" % sub, params={"limit": 25})
        for child in resp.json().get("data", {}).get("children", []):
            data = child.get("data", {})
            title = (data.get("title") or "").strip()
            if not title:
                continue
            url = data.get("url_overridden_by_dest") or \
                "https://www.reddit.com" + data.get("permalink", "")
            items.append({
                "id": "reddit:" + str(data.get("name")),
                "title": title,
                "url": url,
                "text": ("posted in r/%s. " % sub) + (data.get("selftext") or "")[:350],
            })
    return items
