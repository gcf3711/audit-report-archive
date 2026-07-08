"""Report metadata record shared by all scrapers."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass, field, asdict


def slugify(text: str, max_len: int = 80) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text[:max_len].rstrip("-") or "untitled"


@dataclass
class Report:
    source: str            # source key from sources.yaml, e.g. "trailofbits"
    project: str           # audited project / protocol name
    title: str             # report title (often same as project)
    report_url: str        # canonical URL of the report document (provenance)
    date: str | None = None        # ISO date: YYYY-MM-DD, YYYY-MM, or YYYY
    listing_url: str | None = None # page where the report was found
    download_url: str | None = None  # direct-download URL if != report_url
    file_type: str = "pdf"           # pdf | md | html
    local_path: str | None = None    # relative to repo root, set by downloader
    sha256: str | None = None
    size_bytes: int | None = None
    downloaded_at: str | None = None
    extra: dict = field(default_factory=dict)  # source-specific metadata

    @property
    def id(self) -> str:
        # title slug for readability + report_url hash for uniqueness
        # (titles collide: e.g. 97 Sigma Prime reports are just "review")
        url_hash = hashlib.md5(self.report_url.encode()).hexdigest()[:6]
        return f"{self.source}/{slugify(self.title)}-{url_hash}"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["id"] = self.id
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Report":
        d = {k: v for k, v in d.items() if k != "id"}
        return cls(**d)
