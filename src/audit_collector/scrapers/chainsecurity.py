"""ChainSecurity — https://www.chainsecurity.com/smart-contract-audit-reports

Listing paginates via ?47bc7508_page=N; each item links to a detail page at
/security-audit/<slug> which contains the PDF link (reports.chainsecurity.com).
"""

from __future__ import annotations

from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .. import catalog
from ..models import Report
from .. import http

BASE = "https://www.chainsecurity.com"


def _listing_items():
    """Yield (detail_url, meta) for every audit card across all listing pages.

    Cards carry fs-cmsfilter-field divs with report name, ISO date and topic.
    A static featured card repeats on every page — dedupe handles it.
    """
    seen: set[str] = set()
    page = 1
    while True:
        url = f"{BASE}/smart-contract-audit-reports"
        if page > 1:
            url += f"?47bc7508_page={page}"
        resp = http.get(url, min_interval=1.0)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        new = 0
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "/security-audit/" not in href:
                continue
            full = urljoin(BASE, href.split("?")[0])
            if full in seen:
                continue
            seen.add(full)
            new += 1
            meta = {}
            container = link
            for _ in range(4):  # card fields live near the link
                if container.find(attrs={"fs-cmsfilter-field": True}):
                    break
                container = container.parent or container
            for div in container.find_all(attrs={"fs-cmsfilter-field": True}):
                meta[div["fs-cmsfilter-field"]] = div.get_text(strip=True)
            yield full, meta
        print(f"  page {page}: {new} new ({len(seen)} total)", flush=True)
        if new == 0:
            return
        page += 1


def _pdf_url(detail_url: str) -> str | None:
    try:
        resp = http.get(detail_url, min_interval=0.5)
        resp.raise_for_status()
    except Exception as e:
        print(f"  detail page failed {detail_url}: {e}", flush=True)
        return None
    soup = BeautifulSoup(resp.text, "html.parser")
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.endswith(".pdf") or "reports.chainsecurity.com" in href:
            return urljoin(BASE, href)
    return None


def scrape(key: str, cfg: dict) -> list[Report]:
    # avoid re-fetching ~400 detail pages: reuse detail->pdf from prior scrapes
    known_pdf = {
        r.extra.get("detail_page"): r.report_url
        for r in catalog.load(key) if r.extra.get("detail_page")
    }

    reports = []
    for detail_url, meta in _listing_items():
        slug = detail_url.rstrip("/").split("/security-audit/")[-1]
        name = meta.get("report") or slug.replace("-", " ").title()
        pdf = known_pdf.get(detail_url) or _pdf_url(detail_url)
        if not pdf:
            print(f"  no PDF link on {detail_url}", flush=True)
            continue
        reports.append(Report(
            source=key,
            project=name,
            title=name,
            date=meta.get("date"),
            report_url=pdf,
            download_url=pdf,
            file_type="pdf",
            extra={"detail_page": detail_url, "topic": meta.get("topic")},
        ))
    return reports
