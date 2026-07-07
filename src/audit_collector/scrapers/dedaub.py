"""Dedaub — https://dedaub.com/audits/

The audit index is JS-rendered, but /audits/sitemap.xml enumerates every
report page (https://dedaub.com/audits/<client>/<slug>/, server-rendered
HTML). Depth distinguishes report pages from client index pages.
"""

from __future__ import annotations

import re

from .. import http
from ..models import Report

SITEMAP = "https://dedaub.com/audits/sitemap.xml"
_URL = re.compile(r"<loc>(https://dedaub\.com/audits/([^/<]+)/([^/<]+)/)</loc>")


def scrape(key: str, cfg: dict) -> list[Report]:
    resp = http.get(SITEMAP)
    resp.raise_for_status()

    reports = []
    for url, client, slug in _URL.findall(resp.text):
        title = slug.replace("-", " ").title()
        date = None
        m = re.search(r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*-(\d{1,2})-(\d{4})$", slug)
        if m:
            months = ["jan", "feb", "mar", "apr", "may", "jun",
                      "jul", "aug", "sep", "oct", "nov", "dec"]
            date = f"{m.group(3)}-{months.index(m.group(1)) + 1:02d}-{int(m.group(2)):02d}"
        reports.append(Report(
            source=key,
            project=client.replace("-", " ").title(),
            title=title,
            date=date,
            report_url=url,
            file_type="html",
        ))
    return reports
