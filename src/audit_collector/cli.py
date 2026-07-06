"""Command-line interface.

    python -m audit_collector list                 # show configured sources
    python -m audit_collector scrape [SOURCE ...]  # refresh catalog metadata
    python -m audit_collector download [SOURCE ...]# fetch report files
    python -m audit_collector build-index          # write INDEX.md + indexes/
    python -m audit_collector status               # counts per source
"""

from __future__ import annotations

import argparse
import sys
import traceback
from datetime import date

from . import catalog
from .downloader import download_all
from .registry import ROOT, load_sources
from .scrapers import scrape_source

INDEX_DIR = ROOT / "indexes"


def _select(sources: dict, names: list[str]) -> dict:
    if not names:
        return sources
    unknown = [n for n in names if n not in sources]
    if unknown:
        sys.exit(f"Unknown source(s): {', '.join(unknown)}. See `list`.")
    return {n: sources[n] for n in names}


def cmd_list(sources: dict, _args) -> None:
    for key, cfg in sources.items():
        print(f"{key:22} {cfg['type']:14} {cfg['listing_url']}")


def cmd_scrape(sources: dict, args) -> None:
    for key, cfg in _select(sources, args.sources).items():
        print(f"== {key} ==", flush=True)
        try:
            fresh = scrape_source(key, cfg)
        except Exception:
            traceback.print_exc()
            print(f"  scrape FAILED, catalog left untouched", flush=True)
            continue
        merged = catalog.merge(catalog.load(key), fresh)
        catalog.save(key, merged)
        print(f"  {len(fresh)} listed, catalog now {len(merged)}", flush=True)


def cmd_download(sources: dict, args) -> None:
    for key in _select(sources, args.sources):
        reports = catalog.load(key)
        if not reports:
            print(f"== {key} == no catalog, run scrape first", flush=True)
            continue
        print(f"== {key} == {len(reports)} in catalog", flush=True)
        ok, fail = download_all(reports, min_interval=args.interval)
        catalog.save(key, reports)
        print(f"  done: ok={ok} fail={fail}", flush=True)


def cmd_status(sources: dict, _args) -> None:
    total = have = 0
    print(f"{'source':22} {'listed':>7} {'downloaded':>11}")
    for key in sources:
        reports = catalog.load(key)
        n_have = sum(1 for r in reports if r.local_path and (ROOT / r.local_path).exists())
        total += len(reports)
        have += n_have
        print(f"{key:22} {len(reports):>7} {n_have:>11}")
    print(f"{'TOTAL':22} {total:>7} {have:>11}")


def _md(text: str) -> str:
    return (text or "").replace("|", "\\|").strip()


def cmd_build_index(sources: dict, _args) -> None:
    INDEX_DIR.mkdir(exist_ok=True)
    summary_rows = []
    total = have = 0
    for key, cfg in sources.items():
        reports = sorted(
            catalog.load(key),
            key=lambda r: (r.date or "", r.title), reverse=True,
        )
        # by catalog record, not file existence — stable on checkouts without data/reports
        n_have = sum(1 for r in reports if r.local_path)
        total += len(reports)
        have += n_have
        summary_rows.append(
            f"| [{cfg['name']}](indexes/{key}.md) | {len(reports)} | {n_have} "
            f"| {len(reports) - n_have} | {cfg['listing_url']} |"
        )
        lines = [
            f"# {cfg['name']}",
            "",
            f"Listing: {cfg['listing_url']} — {len(reports)} reports, "
            f"{n_have} downloadable ({len(reports) - n_have} unavailable upstream).",
            "",
            "| Date | Project | Report | Fetched |",
            "|---|---|---|---|",
        ]
        for r in reports:
            link = f"[{_md(r.title) or _md(r.project)}]({r.download_url or r.report_url})"
            lines.append(
                f"| {r.date or '—'} | {_md(r.project)} | {link} "
                f"| {'✓' if r.local_path else '✗'} |"
            )
        (INDEX_DIR / f"{key}.md").write_text("\n".join(lines) + "\n")

    today = date.today().isoformat()
    status = [
        f"**{total}** reports catalogued across **{len(sources)}** sources — "
        f"**{have}** verified downloadable (fetched locally), "
        f"**{total - have}** unavailable (upstream dead links or archive-only). "
        f"Last updated **{today}**.",
        "",
        "| Source | Reports | Downloadable | Unavailable | Listing |",
        "|---|---|---|---|---|",
        *summary_rows,
    ]

    (ROOT / "INDEX.md").write_text("\n".join([
        "# Audit Report Index", "", *status, "",
        "Per-source tables (linked above) list date, project, report URL and",
        "local fetch state for every report.", "",
    ]))

    readme = ROOT / "README.md"
    text = readme.read_text()
    begin, end = "<!-- STATUS:BEGIN -->", "<!-- STATUS:END -->"
    if begin in text and end in text:
        head, rest = text.split(begin, 1)
        _, tail = rest.split(end, 1)
        readme.write_text(head + begin + "\n" + "\n".join(status) + "\n" + end + tail)
    print(f"Wrote INDEX.md + {len(sources)} per-source indexes ({total} reports), "
          f"README status updated")


def main() -> None:
    parser = argparse.ArgumentParser(prog="audit_collector")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    p = sub.add_parser("scrape")
    p.add_argument("sources", nargs="*")
    p = sub.add_parser("download")
    p.add_argument("sources", nargs="*")
    p.add_argument("--interval", type=float, default=0.5,
                   help="min seconds between requests to the same host")
    sub.add_parser("status")
    sub.add_parser("build-index")

    args = parser.parse_args()
    sources = load_sources()
    {
        "list": cmd_list,
        "scrape": cmd_scrape,
        "download": cmd_download,
        "status": cmd_status,
        "build-index": cmd_build_index,
    }[args.cmd](sources, args)


if __name__ == "__main__":
    main()
