"""Fetcher registry.

Contract: every fetcher is `fetch(source_cfg) -> list[dict]` where each dict has
  title (str), url (str), and optionally id (stable source-specific id) and
  text (short snippet handed to the classifier).
`source` / `source_id` are filled in by the pipeline. Fetchers raise on failure;
the pipeline catches per-source so one broken source never kills a run.
"""
from . import fal, hackernews, html_page, huggingface, reddit, replicate, rss

FETCHERS = {
    "fal": fal.fetch,
    "hackernews": hackernews.fetch,
    "html": html_page.fetch,
    "huggingface": huggingface.fetch,
    "reddit": reddit.fetch,
    "replicate": replicate.fetch,
    "rss": rss.fetch,
}
