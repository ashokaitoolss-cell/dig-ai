"""RSS/Atom feeds via feedparser."""
import feedparser

from ..util import get, strip_html

ACCEPT = "application/rss+xml, application/atom+xml, application/xml;q=0.9, */*;q=0.8"


def fetch(src):
    resp = get(src["url"], headers={"Accept": ACCEPT})
    parsed = feedparser.parse(resp.content)
    items = []
    for entry in parsed.entries[:30]:
        link = entry.get("link")
        title = (entry.get("title") or "").strip()
        if not link or not title:
            continue
        items.append({
            "id": entry.get("id") or link,
            "title": title,
            "url": link,
            "text": strip_html(entry.get("summary", ""))[:400],
        })
    return items
