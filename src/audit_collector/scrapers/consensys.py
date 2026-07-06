"""ConsenSys Diligence — https://diligence.consensys.io/audits/

The live site (now diligence.security) sits behind a Cloudflare managed
challenge that blocks plain HTTP clients, so we read the listing from the
most recent Wayback Machine snapshot: a single page containing every audit
(no pagination). report_url points at the live site for provenance;
download_url goes through Wayback so the HTML report can actually be fetched.
"""

from __future__ import annotations

import re

from .. import http
from ..models import Report

WAYBACK_LISTING = "https://web.archive.org/web/2026/https://diligence.security/audits/"

_ROW = re.compile(
    r'<a href="([^"]*/audits/(\d{4})/(\d{2})/[^"]+)">([^<]+)</a></td>\s*<td[^>]*>([^<]+)</td>'
)

# the audits lived on several hosts over the years; Wayback coverage differs
_HOST_VARIANTS = [
    "https://diligence.security{path}",
    "https://consensys.io/diligence{path}",
    "https://consensys.net/diligence{path}",
    "https://diligence.consensys.io{path}",
]


def _wayback_snapshot(path: str) -> str | None:
    """Find an archived copy of an audit page under any historical host."""
    for variant in _HOST_VARIANTS:
        url = variant.format(path=path)
        try:
            resp = http.get("https://archive.org/wayback/available",
                            params={"url": url}, min_interval=0.3)
            snap = resp.json().get("archived_snapshots", {}).get("closest")
        except Exception:
            continue
        if snap and snap.get("available"):
            return snap["url"]
    return None


def scrape(key: str, cfg: dict) -> list[Report]:
    resp = http.get(WAYBACK_LISTING, allow_redirects=True, min_interval=1.0)
    resp.raise_for_status()

    seen = set()
    reports = []
    for m in _ROW.finditer(resp.text):
        href, year, month, name, date_text = m.groups()
        # strip the Wayback prefix to recover the live URL
        live = re.sub(r"^https?://web\.archive\.org/web/\d+/", "", href)
        if not live.startswith("http"):
            live = "https://diligence.security" + live[live.index("/audits/"):]
        if live in seen:
            continue
        seen.add(live)
        path = live[live.index("/audits/"):]
        snapshot = _wayback_snapshot(path)
        reports.append(Report(
            source=key,
            project=name.strip(),
            title=name.strip(),
            date=f"{year}-{month}",
            report_url=live,
            download_url=snapshot or f"https://web.archive.org/web/2026/{live}",
            file_type="html",
            extra={"date_text": date_text.strip(), "archived": bool(snapshot)},
        ))
        if len(reports) % 25 == 0:
            print(f"  {len(reports)} processed", flush=True)
    print(f"  {len(reports)} audits from Wayback listing "
          f"({sum(1 for r in reports if r.extra['archived'])} with archived copy)", flush=True)
    return reports
