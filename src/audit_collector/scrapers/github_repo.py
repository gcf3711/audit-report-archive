"""Generic scraper for audit reports published as files in a GitHub repo.

Uses a blobless clone (--filter=blob:none) so we can enumerate every file and
read per-file git history locally without hitting GitHub API rate limits.
Report files are served from raw.githubusercontent.com pinned to the HEAD
commit, which keeps download URLs stable for provenance.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from urllib.parse import quote

from ..models import Report
from ..registry import DATA_DIR

GIT_CACHE = DATA_DIR / "cache" / "git"

DEFAULT_EXCLUDE = ["readme", "license", "template", "logo", "contributing"]

_MONTHS = {m: i + 1 for i, m in enumerate(
    "january february march april may june july august september october november december".split()
)}
_MONTH_NAME = re.compile(
    r"(?i)\b(" + "|".join(_MONTHS) + r")\w*[ _.-]*(20\d{2})"
)

# filename patterns that carry the report date
_DATE_PATTERNS = [
    re.compile(r"(20\d{2})[-_.](\d{2})[-_.](\d{2})"),  # 2023-05-17
    re.compile(r"(20\d{2})[-_.](\d{2})(?!\d)"),        # 2023-05
    re.compile(r"(?<!\d)(\d{2})[-_.](20\d{2})"),       # 05-2023
    re.compile(r"(?<!\d)(20\d{2})(?!\d)"),             # 2023
]

_NAME_NOISE = re.compile(
    r"(?i)[-_ ]?(security[-_ ]?)?(audit|review|report|assessment|final|public|v?\d+(\.\d+)+)[-_ ]?"
)


def _run(args: list[str], cwd: Path | None = None) -> str:
    return subprocess.run(
        args, cwd=cwd, check=True, capture_output=True, text=True
    ).stdout


def _clone_or_update(repo: str) -> Path:
    dest = GIT_CACHE / repo.replace("/", "__")
    if dest.exists():
        _run(["git", "fetch", "--quiet", "origin"], cwd=dest)
        _run(["git", "reset", "--soft", "origin/HEAD"], cwd=dest)
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        _run([
            "git", "clone", "--quiet", "--filter=blob:none", "--no-checkout",
            f"https://github.com/{repo}.git", str(dest),
        ])
    return dest


def _file_added_dates(repo_dir: Path) -> dict[str, str]:
    """Map each path to the date of the oldest commit touching it."""
    out = _run(
        ["git", "log", "--format=|%cs", "--name-only", "--all"], cwd=repo_dir
    )
    dates: dict[str, str] = {}
    current = None
    for line in out.splitlines():
        if line.startswith("|"):
            current = line[1:]
        elif line and current:
            dates[line] = current  # log is newest-first; last write wins = oldest
    return dates


def _date_from_name(path: str) -> str | None:
    m = _MONTH_NAME.search(path)
    if m:
        return f"{m.group(2)}-{_MONTHS[m.group(1).lower()]:02d}"
    for pat in _DATE_PATTERNS:
        m = pat.search(path)
        if not m:
            continue
        g = m.groups()
        if len(g) == 3:
            return f"{g[0]}-{g[1]}-{g[2]}"
        if len(g) == 2:
            year, month = (g[0], g[1]) if g[0].startswith("20") else (g[1], g[0])
            if 1 <= int(month) <= 12:
                return f"{year}-{month}"
            return year
        return g[0]
    return None


def _project_from_name(path: str) -> str:
    stem = Path(path).stem
    stem = re.sub(r"20\d{2}[-_.]?\d{0,2}[-_.]?\d{0,2}", "", stem)
    stem = _MONTH_NAME.sub(" ", stem)
    stem = re.sub(r"(?i)\b(" + "|".join(_MONTHS) + r")\b", " ", stem)
    stem = _NAME_NOISE.sub(" ", stem)
    stem = re.sub(r"[.,]+\s*$", "", stem.strip())
    stem = re.sub(r"[-_]+", " ", stem).strip()
    if not stem:
        stem = Path(path).parent.name.replace("-", " ").replace("_", " ")
    return stem.strip() or Path(path).stem


def scrape(key: str, cfg: dict) -> list[Report]:
    repo = cfg["repo"]
    paths = cfg.get("paths") or []
    extensions = tuple(cfg.get("extensions") or [".pdf"])
    exclude = [e.lower() for e in (cfg.get("exclude") or []) + DEFAULT_EXCLUDE]

    repo_dir = _clone_or_update(repo)
    head = _run(["git", "rev-parse", "HEAD"], cwd=repo_dir).strip()
    files = _run(["git", "ls-tree", "-r", "--name-only", "HEAD"], cwd=repo_dir)
    added = _file_added_dates(repo_dir)

    reports = []
    for path in files.splitlines():
        if not path.lower().endswith(extensions):
            continue
        if paths and not any(path.startswith(p.rstrip("/") + "/") for p in paths):
            continue
        name_l = Path(path).name.lower()
        if any(x in name_l for x in exclude):
            continue
        qpath = quote(path)
        reports.append(Report(
            source=key,
            project=_project_from_name(path),
            title=Path(path).stem.replace("_", " ").replace("-", " ").strip(),
            date=_date_from_name(path) or added.get(path),
            report_url=f"https://github.com/{repo}/blob/{head}/{qpath}",
            download_url=f"https://raw.githubusercontent.com/{repo}/{head}/{qpath}",
            file_type=Path(path).suffix.lstrip(".").lower(),
            extra={"repo": repo, "path": path, "commit": head},
        ))
    return reports
