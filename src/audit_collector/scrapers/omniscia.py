"""Omniscia — https://omniscia.io/reports.html

The reports page loads the complete dataset from a CSV. Each client row has an
`audits` cell that is itself CSV with repeated 7-field tuples:
title, url, chains, tags, integrations, language, timestamp_ms.
Server returns 406 unless a full browser User-Agent is sent.
"""

from __future__ import annotations

import csv
import io
from datetime import datetime, timezone

from .. import http
from ..models import Report

DATA_URL = "https://omniscia.io/assets/data/clients.csv"


def scrape(key: str, cfg: dict) -> list[Report]:
    resp = http.get(DATA_URL, headers={"Referer": "https://omniscia.io/reports.html"})
    resp.raise_for_status()

    reports, private = [], 0
    for row in csv.DictReader(io.StringIO(resp.text)):
        cells = next(csv.reader([row["audits"]])) if row.get("audits") else []
        for i in range(0, len(cells) - 6, 7):
            title, url, chains, tags, integrations, language, ts = cells[i:i + 7]
            if not url or url == "N/A":
                private += 1
                continue
            date = None
            if ts.strip().isdigit():
                date = datetime.fromtimestamp(
                    int(ts) / 1000, tz=timezone.utc
                ).strftime("%Y-%m-%d")
            reports.append(Report(
                source=key,
                project=row["client"],
                title=title or row["client"],
                date=date,
                report_url=url,
                file_type="html",
                extra={
                    "chains": chains, "tags": tags,
                    "language": language, "integrations": integrations,
                },
            ))
    print(f"  {len(reports)} public audits ({private} private entries skipped)", flush=True)
    return reports
