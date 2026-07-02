"""Fallback for blogs without RSS: extract post links from the blog index page.

Config: url (index page), link_pattern (substring a post URL must contain),
max_items (default 15). New links are surfaced by the normal seen-diff.
"""
import re
from urllib.parse import urljoin

from ..util import canonical_url, get, strip_html

_ANCHOR = re.compile(r'<a\s[^>]*?href="([^"#]+)"[^>]*>(.*?)</a>', re.I | re.S)
_SKIP_TEXT = {"read more", "learn more", "view all", "see all", "read article", "read the post", "read post"}

# Several blogs (bfl.ai, others on Next.js) serve an empty JS shell to
# non-browser user agents but full server-rendered HTML to browsers.
_BROWSER_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
               "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def _slug_title(url):
    segment = url.rstrip("/").rsplit("/", 1)[-1]
    if "." in segment:
        return ""
    return re.sub(r"[-_]+", " ", segment).strip().capitalize()


def fetch(src):
    resp = get(src["url"], headers={"User-Agent": _BROWSER_UA})
    pattern = src.get("link_pattern", "")
    base = resp.url
    base_canon = canonical_url(base)
    items, seen = [], set()
    for href, inner in _ANCHOR.findall(resp.text):
        if href.startswith(("mailto:", "javascript:", "tel:")):
            continue
        url = urljoin(base, href.strip())
        if not url.startswith("http") or (pattern and pattern not in url):
            continue
        title = strip_html(inner)
        if len(title) < 8 or title.lower() in _SKIP_TEXT:
            # image-wrapped or "Read more" links: fall back to the URL slug
            title = _slug_title(url)
            if len(title) < 8:
                continue
        canon = canonical_url(url)
        if canon in seen or canon == base_canon:
            continue
        seen.add(canon)
        items.append({"id": canon, "title": title[:200], "url": url})
        if len(items) >= src.get("max_items", 15):
            break
    return items
