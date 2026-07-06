"""Cantina — https://cantina.xyz/security-reviews

Public JSON API returns the whole portfolio in one request (the website only
shows the cantina_managed subset; the API also has Spearbit and competition
reports). Every record carries a direct reportPdfLink.
"""

from __future__ import annotations

import re

from .. import http
from ..models import Report

API = "https://api.cantina.xyz/api/v0/reports"

_GH_BLOB = re.compile(r"https://github\.com/([^/]+)/([^/]+)/blob/(.+)")


def _direct_url(url: str) -> str:
    """GitHub blob pages serve HTML; rewrite to the raw file for download."""
    m = _GH_BLOB.match(url)
    if m:
        return f"https://raw.githubusercontent.com/{m.group(1)}/{m.group(2)}/{m.group(3)}"
    return url


def scrape(key: str, cfg: dict) -> list[Report]:
    reports = []
    next_cursor = None
    while True:
        params = {"limit": 5000}
        if next_cursor:
            params["next"] = next_cursor
        resp = http.get(API, params=params)
        resp.raise_for_status()
        data = resp.json()
        for item in data["reports"]:
            url = item.get("reportPdfLink")
            if not url:
                continue
            date = (item.get("engagementEndDate")
                    or item.get("publishedAt")
                    or item.get("createdAt") or "")[:10] or None
            reports.append(Report(
                source=key,
                project=item.get("clientName") or item.get("projectTitle") or "",
                title=item.get("projectTitle") or item.get("clientName") or "",
                date=date,
                report_url=url,
                download_url=_direct_url(url),
                file_type="pdf" if url.lower().endswith(".pdf") else "html",
                extra={
                    "portfolio_page": f"https://cantina.xyz/portfolio/{item['id']}",
                    "engagement_kind": item.get("engagementKind"),
                    "repository_links": item.get("repositoryLinks"),
                    "commit_hashes": item.get("commitHashes"),
                },
            ))
        next_cursor = data.get("nextValue")
        if not next_cursor:
            return reports
