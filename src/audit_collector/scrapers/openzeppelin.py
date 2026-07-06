"""OpenZeppelin — https://www.openzeppelin.com/research#security-audits

The research page only shows the ~100 most recent posts. Full enumeration goes
through the HubSpot site-search JSON API (term required; 'audit' returns the
full blog archive) filtered to the "Security Audits" tags. Reports are HTML
pages under /news/<slug> — there are no PDFs.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from .. import http
from ..models import Report

SEARCH = "https://www.openzeppelin.com/_hcms/search"
_TAG_RE = re.compile(r"<[^>]+>")


def scrape(key: str, cfg: dict) -> list[Report]:
    reports = []
    offset, total = 0, None
    while total is None or offset < total:
        resp = http.get(SEARCH, params={
            "term": "audit", "type": "BLOG_POST", "limit": 200, "offset": offset,
        }, min_interval=1.0)
        resp.raise_for_status()
        data = resp.json()
        total = data["total"]
        for item in data["results"]:
            tags = item.get("tags") or []
            if not any(t.startswith("Security Audits") for t in tags):
                continue
            title = _TAG_RE.sub("", item["title"])
            title = re.sub(r"\s*-\s*OpenZeppelin blog\s*$", "", title).strip()
            date = None
            if item.get("publishedDate"):
                date = datetime.fromtimestamp(
                    item["publishedDate"] / 1000, tz=timezone.utc
                ).strftime("%Y-%m-%d")
            project = re.sub(r"(?i)\s*(security\s+)?(audit|assessment|review)s?\s*$", "", title).strip() or title
            reports.append(Report(
                source=key,
                project=project,
                title=title,
                date=date,
                report_url=item["url"],
                file_type="html",
                extra={"tags": tags, "author": item.get("authorFullName")},
            ))
        print(f"  offset {offset}: {len(reports)} audits so far (total posts {total})", flush=True)
        offset += 200
    return reports
