"""dapp.org (DappHub reviews) — https://dapp.org.uk

Dormant org with a fixed set of five reviews. The homepage is a static
server-rendered index linking to /reports/<slug>.html pages.
"""

from __future__ import annotations

import re

from .. import http
from ..models import Report

HOME = "https://dapp.org.uk"


def scrape(key: str, cfg: dict) -> list[Report]:
    resp = http.get(HOME)
    resp.raise_for_status()

    reports = []
    for href in dict.fromkeys(re.findall(r'href="\.?/?(reports/[^"]+\.html)"', resp.text)):
        slug = href.rsplit("/", 1)[-1].removesuffix(".html")
        name = slug.replace("-", " ").title()
        reports.append(Report(
            source=key,
            project=name,
            title=f"{name} review",
            report_url=f"{HOME}/{href.lstrip('/')}",
            file_type="html",
        ))
    return reports
