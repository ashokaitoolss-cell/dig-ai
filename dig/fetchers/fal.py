"""fal.ai model registry via sitemap diff.

A /models/... URL never seen before means a brand-new model endpoint —
these often appear before any public announcement.
"""
import re

from ..util import get

_SITEMAPS = ("https://fal.ai/models/sitemap.xml", "https://fal.ai/sitemap.xml")
_LOC = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>")


def fetch(src):
    locs, last_err = [], None
    for sitemap in _SITEMAPS:
        try:
            locs = _LOC.findall(get(sitemap).text)
        except Exception as exc:
            last_err = exc
            continue
        if locs:
            break
    if not locs:
        raise RuntimeError("no fal.ai sitemap reachable: %s" % last_err)

    model_urls = [u for u in locs if "/models/" in u and not u.endswith(".xml")]
    # sitemap index: follow child sitemaps
    for child in [u for u in locs if u.endswith(".xml")][:5]:
        try:
            model_urls += [u for u in _LOC.findall(get(child).text) if "/models/" in u]
        except Exception:
            continue

    # keep model endpoints (owner/name and owner/name/variant) — drop doc subpages
    _subpages = {"api", "examples", "playground", "requests"}
    slugs = {}
    for url in model_urls:
        slug = url.split("/models/", 1)[1].strip("/")
        parts = slug.split("/")
        if not slug or len(parts) > 3 or parts[-1] in _subpages:
            continue
        slugs.setdefault(slug, url)

    return [
        {
            "id": "fal:" + slug,
            "title": "New fal.ai model endpoint: " + slug,
            "url": url,
            "text": "A new model endpoint appeared in the fal.ai public registry (often before any announcement).",
        }
        for slug, url in sorted(slugs.items())
    ]
