"""Hacker News via the Algolia search API: keyword queries + Show HN stories."""
import re
import time

from ..util import get

API = "https://hn.algolia.com/api/v1/search_by_date"

DEFAULT_QUERIES = ["video model", "image model", "AI video", "diffusion"]

# Show HN is unfiltered by query, so gate it on creative-AI keywords
# to avoid burning classifier tokens on every launch under the sun.
_SHOW_HN = re.compile(
    r"\b(ai|video|image|3d|audio|music|voice|diffusion|animation|render|"
    r"generat\w*|model|creative|film|vfx|motion|avatar|lip.?sync)\b", re.I)


def fetch(src):
    fresh_since = int(time.time()) - 3 * 86400
    items, seen = [], set()

    def add(hits, title_filter=None):
        for hit in hits:
            story_id = hit.get("objectID")
            title = (hit.get("title") or "").strip()
            if not story_id or story_id in seen or not title:
                continue
            if title_filter and not title_filter.search(title):
                continue
            seen.add(story_id)
            items.append({
                "id": "hn:" + story_id,
                "title": title,
                "url": hit.get("url") or "https://news.ycombinator.com/item?id=" + story_id,
                "text": "%d points on Hacker News" % (hit.get("points") or 0),
            })

    for query in src.get("queries", DEFAULT_QUERIES):
        resp = get(API, params={
            "tags": "story", "query": query, "hitsPerPage": 20,
            "numericFilters": "created_at_i>%d" % fresh_since,
        })
        add(resp.json().get("hits", []))

    resp = get(API, params={
        "tags": "show_hn", "hitsPerPage": 30,
        "numericFilters": "created_at_i>%d" % fresh_since,
    })
    add(resp.json().get("hits", []), title_filter=_SHOW_HN)
    return items
