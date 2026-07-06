"""Load the source registry from config/sources.yaml."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config" / "sources.yaml"
DATA_DIR = ROOT / "data"
CATALOG_DIR = DATA_DIR / "catalog"
REPORTS_DIR = DATA_DIR / "reports"


def load_sources(path: Path = CONFIG_PATH) -> dict[str, dict]:
    with open(path) as f:
        sources = yaml.safe_load(f)
    for key, cfg in sources.items():
        cfg.setdefault("type", "github_repo")
        cfg.setdefault("name", key)
    return sources
