"""Layer 0 — extract report text into data/cache/text/<source>/<file>.txt.

Only the opening of each report is kept (title page + scope section carry
the metadata we mine); PDFs go through pdftotext, HTML through
BeautifulSoup, Markdown is taken as-is. An empty result file marks a
report whose text cannot be extracted (scanned PDF etc.), so reruns skip
it without retrying forever.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from bs4 import BeautifulSoup

from .schema import ROOT, TEXT_DIR

PDF_PAGES = 6          # pdftotext -l: first pages only
MAX_CHARS = 12_000     # cap per report, enough for title + scope


def _pdf_text(path: Path) -> str:
    proc = subprocess.run(
        ["pdftotext", "-q", "-l", str(PDF_PAGES), str(path), "-"],
        capture_output=True, text=True, timeout=60)
    return proc.stdout


def _html_text(path: Path) -> str:
    soup = BeautifulSoup(path.read_text(errors="replace"), "html.parser")
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    return soup.get_text(" ", strip=True)


def text_path(local_path: str) -> Path:
    rel = Path(local_path).relative_to("data/reports")
    return TEXT_DIR / rel.parent / (rel.stem + ".txt")


def get_text(local_path: str) -> str | None:
    """Cached text for a report, None if not extracted (yet or ever)."""
    p = text_path(local_path)
    if not p.exists():
        return None
    return p.read_text(errors="replace") or None


def extract_source(source: str) -> tuple[int, int, int]:
    """Extract text for every downloaded report of a source.

    Returns (extracted, failed, skipped-already-done).
    """
    catalog = json.loads((ROOT / "data/catalog" / f"{source}.json").read_text())
    done = failed = skipped = 0
    for entry in catalog:
        local = entry.get("local_path")
        if not local:
            continue
        src_file = ROOT / local
        out = text_path(local)
        if out.exists() or not src_file.exists():
            skipped += 1
            continue
        try:
            if src_file.suffix == ".pdf":
                text = _pdf_text(src_file)
            elif src_file.suffix == ".html":
                text = _html_text(src_file)
            else:  # .md, .org and other plain text
                text = src_file.read_text(errors="replace")
        except Exception:
            text = ""
        text = " ".join(text.split())[:MAX_CHARS]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
        if text:
            done += 1
        else:
            failed += 1
    return done, failed, skipped
