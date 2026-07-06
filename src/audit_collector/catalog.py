"""Per-source catalog files under data/catalog/<source>.json.

The catalog is the source of truth for report metadata. Scraping refreshes
listing metadata but preserves download state (local_path/sha256/...) for
reports that were already fetched.
"""

from __future__ import annotations

import json

from .models import Report
from .registry import CATALOG_DIR


def load(source: str) -> list[Report]:
    path = CATALOG_DIR / f"{source}.json"
    if not path.exists():
        return []
    return [Report.from_dict(d) for d in json.loads(path.read_text())]


def save(source: str, reports: list[Report]) -> None:
    CATALOG_DIR.mkdir(parents=True, exist_ok=True)
    path = CATALOG_DIR / f"{source}.json"
    data = [r.to_dict() for r in sorted(reports, key=lambda r: (r.date or "", r.id))]
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def merge(existing: list[Report], fresh: list[Report]) -> list[Report]:
    """Update catalog with a fresh scrape, keeping download state and any
    previously seen reports that disappeared from the listing."""
    by_key: dict[str, Report] = {r.report_url: r for r in existing}
    # provenance: match on report_url first, fall back to id
    by_id = {r.id: r for r in existing}
    merged: dict[str, Report] = dict(by_key)
    for r in fresh:
        old = by_key.get(r.report_url) or by_id.get(r.id)
        if old:
            r.local_path = old.local_path
            r.sha256 = old.sha256
            r.size_bytes = old.size_bytes
            r.downloaded_at = old.downloaded_at
            merged.pop(old.report_url, None)
        merged[r.report_url] = r
    return list(merged.values())
