"""Quantstamp — https://certificate.quantstamp.com/

JSON API with a fixed page size of 15; paginate by offset until `total`.
`link` is site-relative and is either a PDF or an HTML report page.
"""

from __future__ import annotations

from .. import http
from ..models import Report

BASE = "https://certificate.quantstamp.com"


def scrape(key: str, cfg: dict) -> list[Report]:
    reports = []
    offset, total = 0, None
    while total is None or offset < total:
        resp = http.get(f"{BASE}/api/certificates", params={"offset": offset})
        resp.raise_for_status()
        data = resp.json()
        total = data["total"]
        for item in data["data"]:
            link = (item.get("link") or "").lstrip("/")
            if not link:
                continue
            url = f"{BASE}/{link}"
            reports.append(Report(
                source=key,
                project=item.get("projectName") or "",
                title=item.get("projectName") or "",
                date=(item.get("publishedAt") or "")[:10] or None,
                report_url=url,
                file_type="pdf" if link.lower().endswith(".pdf") else "html",
                extra={
                    "tags": [t["name"] for t in item.get("tags") or []],
                    "project_group": item.get("projectGroupName"),
                },
            ))
        offset += 15
        if offset % 150 == 0:
            print(f"  {offset}/{total}", flush=True)
    return reports
