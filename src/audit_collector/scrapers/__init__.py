"""Scraper dispatch: source config `type` -> scrape function.

Each scraper module exposes `scrape(key: str, cfg: dict) -> list[Report]`.
"""

from __future__ import annotations

import importlib

from ..models import Report


def scrape_source(key: str, cfg: dict) -> list[Report]:
    module = importlib.import_module(f".{cfg['type']}", package=__name__)
    reports = module.scrape(key, cfg)
    for r in reports:
        r.source = key
        if not r.listing_url:
            r.listing_url = cfg.get("listing_url")
    return reports
