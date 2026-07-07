"""Paladin Blockchain Security — https://paladinsec.co/audits/

The audits listing paginates via a nonce-protected JetEngine ajax call, but
per-project pages (/projects/<slug>/) are server-rendered and hold direct PDF
links. Slugs are enumerated from the Wayback CDX index plus the live listing's
first page (newest projects); pages already in the catalog are not re-fetched.
"""

from __future__ import annotations

import re

from .. import catalog
from .. import http
from ..models import Report

BASE = "https://paladinsec.co"
CDX = ("http://web.archive.org/cdx/search/cdx"
       "?url=paladinsec.co/projects/*&collapse=urlkey&fl=original")
_SLUG = re.compile(r"paladinsec\.co/projects/([^/?#]+)/?$")
# PDF links live inside embedded JSON with escaped slashes (https:\/\/...)
_PDF = re.compile(r'https:(?:\\/|/)+paladinsec\.co(?:\\/|/)assets(?:\\/|/)audits(?:\\/|/)[^"\'\\<>]+\.pdf')
_DATE = re.compile(r"/(\d{4})(\d{2})(\d{2})_")


def _slugs() -> set[str]:
    slugs = set()
    resp = http.get(CDX, min_interval=1.0)
    resp.raise_for_status()
    for line in resp.text.splitlines():
        m = _SLUG.search(line.strip())
        if m:
            slugs.add(m.group(1))
    listing = http.get(f"{BASE}/audits/", min_interval=1.0)
    for m in re.finditer(r'href="https?://paladinsec\.co/projects/([^/"]+)/"', listing.text):
        slugs.add(m.group(1))
    slugs.discard("page")
    return slugs


def scrape(key: str, cfg: dict) -> list[Report]:
    known = {}  # detail page -> reports already catalogued
    for r in catalog.load(key):
        known.setdefault(r.extra.get("detail_page"), []).append(r)

    reports = []
    fetched = missing = 0
    for slug in sorted(_slugs()):
        detail = f"{BASE}/projects/{slug}/"
        if detail in known:
            reports.extend(known[detail])
            continue
        try:
            resp = http.get(detail, min_interval=0.8, allow_redirects=True)
            resp.raise_for_status()
        except Exception:
            missing += 1  # project page removed / never live
            continue
        fetched += 1
        name = slug.replace("-", " ").title()
        pdfs = [p.replace("\\/", "/") for p in _PDF.findall(resp.text)]
        for pdf in dict.fromkeys(pdfs):
            m = _DATE.search(pdf)
            date = f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else None
            reports.append(Report(
                source=key,
                project=name,
                title=pdf.rsplit("/", 1)[-1].removesuffix(".pdf").replace("_", " "),
                date=date,
                report_url=pdf,
                file_type="pdf",
                extra={"detail_page": detail},
            ))
        if fetched % 25 == 0:
            print(f"  {fetched} pages fetched, {len(reports)} reports", flush=True)
    print(f"  {fetched} pages fetched, {missing} gone, {len(reports)} reports", flush=True)
    return reports
