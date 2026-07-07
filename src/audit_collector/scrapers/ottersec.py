"""OtterSec — https://osec.io/audits

Single server-rendered page listing every audit as /reports/<uuid> links.
Each link 302-redirects to a short-lived signed PDF URL, so the stable
/reports/<uuid> URL is both provenance and download URL (the downloader
follows redirects).
"""

from __future__ import annotations

from bs4 import BeautifulSoup

from .. import http
from ..models import Report

LISTING = "https://osec.io/audits"


def scrape(key: str, cfg: dict) -> list[Report]:
    resp = http.get(LISTING)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    reports = []
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if not href.startswith("/reports/") or href in seen:
            continue
        seen.add(href)
        title = a.get_text(" ", strip=True) or href.rsplit("/", 1)[-1]
        reports.append(Report(
            source=key,
            project=title,
            title=title,
            report_url=f"https://osec.io{href}",
            file_type="pdf",
        ))
    return reports
