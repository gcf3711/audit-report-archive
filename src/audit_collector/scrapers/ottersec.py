"""OtterSec — https://osec.io/audits

Single server-rendered page with a table of audits: Date | Name | Chain |
Bugs | View PDF. The /reports/<uuid> link 302-redirects to a short-lived
signed PDF URL, so the stable uuid URL is both provenance and download URL
(the downloader follows redirects). The chain column is kept in extra.
"""

from __future__ import annotations

from datetime import datetime

from bs4 import BeautifulSoup

from .. import http
from ..models import Report

LISTING = "https://osec.io/audits"


def _row_fields(link) -> tuple[str | None, str | None, str | None]:
    """(date, name, chain) from the table row containing the PDF link."""
    row = link
    for _ in range(4):  # walk up to the row element
        row = row.parent
        cells = [t.get_text(" ", strip=True) for t in row.find_all(recursive=False)]
        if len(cells) >= 4:
            date_s, name, chain = cells[0], cells[1], cells[2]
            try:
                date = datetime.strptime(date_s, "%B %d, %Y").date().isoformat()
            except ValueError:
                date = None
            return date, name or None, chain or None
    return None, None, None


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
        date, name, chain = _row_fields(a)
        title = name or href.rsplit("/", 1)[-1]
        reports.append(Report(
            source=key,
            project=title,
            title=title,
            date=date,
            report_url=f"https://osec.io{href}",
            file_type="pdf",
            extra={"chain": chain} if chain else {},
        ))
    return reports
