"""Shared helpers: polite HTTP, URL canonicalization, title similarity."""
import difflib
import hashlib
import html as html_lib
import re
import time
from datetime import datetime, timezone
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests

USER_AGENT = "dig-ai/0.1 (personal launch radar; +https://github.com/dig-ai)"

_TRACKING_PARAMS = {"ref", "ref_src", "fbclid", "gclid", "si", "s", "mc_cid", "mc_eid"}

_last_hit = {}
_delay = 1.5


def set_delay(seconds):
    global _delay
    _delay = seconds


def get(url, headers=None, params=None, timeout=25):
    """GET with a per-host politeness delay and a proper User-Agent."""
    host = urlsplit(url).netloc
    wait = _last_hit.get(host, 0.0) + _delay - time.monotonic()
    if wait > 0:
        time.sleep(wait)
    merged = {"User-Agent": USER_AGENT}
    if headers:
        merged.update(headers)
    resp = requests.get(url, headers=merged, params=params, timeout=timeout)
    _last_hit[host] = time.monotonic()
    resp.raise_for_status()
    return resp


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def canonical_url(url):
    """Normalize a URL for hashing: lowercase host, no www/utm/fragment/trailing slash."""
    parts = urlsplit(url.strip())
    host = parts.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    query = urlencode([
        (k, v) for k, v in parse_qsl(parts.query)
        if not k.lower().startswith("utm_") and k.lower() not in _TRACKING_PARAMS
    ])
    return urlunsplit((parts.scheme.lower() or "https", host, parts.path.rstrip("/"), query, ""))


def domain_of(url):
    host = urlsplit(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def item_hash(item):
    """Stable id for dedupe: source-specific id when present, else canonical URL."""
    key = item.get("id") or canonical_url(item["url"])
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]


def norm_title(title):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", title.lower())).strip()


def similar(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()


def strip_html(text):
    return re.sub(r"\s+", " ", html_lib.unescape(re.sub(r"<[^>]+>", " ", text or ""))).strip()
