"""Code4rena — https://code4rena.com/reports

No working public JSON API, but the complete report list is embedded in the
Next.js RSC flight payload of the listing page (self.__next_f.push chunks).
Reports themselves are server-rendered HTML pages at /reports/<slug>; the
durable mirror is the code-423n4 GitHub findings repos (kept in extra).
"""

from __future__ import annotations

import json
import re

from .. import http
from ..models import Report

LISTING = "https://code4rena.com/reports"
_CHUNK = re.compile(r'self\.__next_f\.push\(\[1,"((?:[^"\\]|\\.)*)"\]\)')
_ROW = re.compile(r'^[0-9a-f]+:(\{.*\})\s*$', re.MULTILINE)
_DATE = re.compile(r"(20\d{2}-\d{2}-\d{2})")


def scrape(key: str, cfg: dict) -> list[Report]:
    resp = http.get(LISTING, allow_redirects=True)
    resp.raise_for_status()

    payload = "".join(
        json.loads(f'"{chunk}"') for chunk in _CHUNK.findall(resp.text)
    )

    reports: dict[str, Report] = {}
    for m in _ROW.finditer(payload):
        try:
            row = json.loads(m.group(1))
        except json.JSONDecodeError:
            continue
        if not isinstance(row, dict) or "slug" not in row or "sponsor" not in row:
            continue
        slug = row["slug"]
        if slug in reports:
            continue
        date_m = _DATE.search(row.get("date") or "")
        url = f"https://code4rena.com/reports/{slug}"
        reports[slug] = Report(
            source=key,
            project=row.get("sponsor") or row.get("title") or slug,
            title=row.get("title") or slug,
            date=date_m.group(1) if date_m else None,
            report_url=url,
            download_url=row.get("alt_url") or url,
            file_type="pdf" if (row.get("alt_url") or "").endswith(".pdf") else "html",
            extra={"findings_repo": row.get("findings"), "contest_id": row.get("contest")},
        )
    return list(reports.values())
