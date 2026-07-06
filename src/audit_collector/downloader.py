"""Download report files listed in a catalog into data/reports/<source>/."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from . import http
from .models import Report, slugify
from .registry import REPORTS_DIR, ROOT

MIN_FILE_SIZE = 1000  # smaller responses are almost certainly error pages


def _filename(report: Report) -> str:
    url = report.download_url or report.report_url
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    ext = report.file_type or "pdf"
    return f"{slugify(report.title)}_{url_hash}.{ext}"


def download_report(report: Report, min_interval: float = 0.5) -> bool:
    """Fetch one report. Returns True if the file is present afterwards."""
    url = report.download_url or report.report_url
    out = REPORTS_DIR / report.source / _filename(report)

    if report.local_path and (ROOT / report.local_path).exists():
        return True
    if out.exists() and out.stat().st_size >= MIN_FILE_SIZE:
        report.local_path = str(out.relative_to(ROOT))
        return True
    # reuse files downloaded under an older naming scheme (same URL hash suffix)
    url_hash = out.stem.rsplit("_", 1)[-1]
    for old in out.parent.glob(f"*_{url_hash}.{report.file_type or 'pdf'}"):
        if old.stat().st_size >= MIN_FILE_SIZE:
            report.local_path = str(old.relative_to(ROOT))
            return True

    try:
        resp = http.get(url, min_interval=min_interval, allow_redirects=True)
        resp.raise_for_status()
    except Exception as e:
        print(f"    FAIL {url}: {e}", flush=True)
        return False

    content = resp.content
    if len(content) < MIN_FILE_SIZE and report.file_type == "pdf":
        print(f"    FAIL {url}: response too small ({len(content)} bytes)", flush=True)
        return False
    if report.file_type == "pdf" and not content.startswith(b"%PDF") and b"%PDF" not in content[:1024]:
        print(f"    FAIL {url}: not a PDF", flush=True)
        return False

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(content)
    report.local_path = str(out.relative_to(ROOT))
    report.sha256 = hashlib.sha256(content).hexdigest()
    report.size_bytes = len(content)
    report.downloaded_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return True


def download_all(reports: list[Report], min_interval: float = 0.5) -> tuple[int, int]:
    ok = fail = 0
    todo = [r for r in reports if not (r.local_path and (ROOT / r.local_path).exists())]
    print(f"  {len(todo)} to download ({len(reports) - len(todo)} already present)", flush=True)
    for i, r in enumerate(todo):
        if download_report(r, min_interval=min_interval):
            ok += 1
        else:
            fail += 1
        if (i + 1) % 25 == 0:
            print(f"  [{i + 1}/{len(todo)}] ok={ok} fail={fail}", flush=True)
    return ok, fail
