"""Enrichment CLI.

    python -m audit_enrich extract [sources...]           # layer 0: text cache
    python -m audit_enrich enrich  [sources...]           # layers 1+2 (deterministic)
    python -m audit_enrich llm     [sources...] [--limit N] [--model haiku]
    python -m audit_enrich status                         # coverage per source

Layers are idempotent and per-source isolated; run them in any order,
rerun any time (`enrich` recomputes deterministic fields, `llm` only
touches reports that still have gaps and haven't been llm-processed).
"""

from __future__ import annotations

import argparse
import json

from . import layer_llm, layer_prior, layer_regex, store, textcache
from .schema import ROOT, ecosystems_for


def _sources(requested: list[str]) -> list[str]:
    have = sorted(p.stem for p in (ROOT / "data/catalog").glob("*.json"))
    if not requested:
        return have
    unknown = set(requested) - set(have)
    if unknown:
        raise SystemExit(f"unknown sources: {', '.join(sorted(unknown))}")
    return requested


def _catalog(source: str) -> list[dict]:
    return json.loads((ROOT / "data/catalog" / f"{source}.json").read_text())


def cmd_extract(args) -> None:
    for source in _sources(args.sources):
        done, failed, skipped = textcache.extract_source(source)
        print(f"{source:24} extracted={done} failed={failed} cached={skipped}",
              flush=True)


def cmd_enrich(args) -> None:
    for source in _sources(args.sources):
        records = store.load(source)
        changed = 0
        for entry in _catalog(source):
            record = records.setdefault(entry["id"], store.new_record(entry["id"]))
            changed += layer_regex.enrich_filename(entry, record)
            text = entry.get("local_path") and textcache.get_text(entry["local_path"])
            record["text_extracted"] = bool(text)
            if text:
                changed += layer_regex.enrich_text(record, text)
        changed += layer_prior.enrich(source, records)
        for record in records.values():
            if record.get("chains"):
                store.apply(record, "ecosystems", ecosystems_for(record["chains"]),
                            record["provenance"]["chains"]["method"],
                            record["provenance"]["chains"]["confidence"])
            store.touch(record)
        store.save(source, records)
        print(f"{source:24} records={len(records)} changes={changed}", flush=True)


def cmd_llm(args) -> None:
    remaining = args.limit
    for source in _sources(args.sources):
        records = store.load(source)
        texts = {}
        for entry in _catalog(source):
            record = records.get(entry["id"])
            if not record or record.get("llm_done") or not layer_llm.needs_llm(record):
                continue
            text = entry.get("local_path") and textcache.get_text(entry["local_path"])
            if text:
                texts[entry["id"]] = (record, text)
        todo = list(texts.values())[:remaining] if remaining else list(texts.values())
        for i in range(0, len(todo), layer_llm.BATCH):
            batch = todo[i:i + layer_llm.BATCH]
            try:
                changed = layer_llm.enrich_batch(batch, args.model)
            except Exception as e:
                print(f"{source}: batch failed: {e}", flush=True)
                continue
            for record, _ in batch:
                if record.get("chains"):
                    store.apply(record, "ecosystems", ecosystems_for(record["chains"]),
                                "llm", "medium")
                store.touch(record)
            store.save(source, records)
            print(f"{source:24} llm batch {i // layer_llm.BATCH + 1}: "
                  f"{len(batch)} reports, {changed} fields", flush=True)
        if remaining:
            remaining -= len(todo)
            if remaining <= 0:
                return


def cmd_status(args) -> None:
    print(f"{'source':24} {'records':>7} {'text':>5} {'chains':>6} "
          f"{'langs':>5} {'categ':>5} {'llm':>5}")
    totals = [0] * 6
    for source in _sources([]):
        records = list(store.load(source).values())
        if not records:
            continue
        n = len(records)
        cols = [n,
                sum(1 for r in records if r.get("text_extracted")),
                sum(1 for r in records if r.get("chains")),
                sum(1 for r in records if r.get("languages")),
                sum(1 for r in records if r.get("category")),
                sum(1 for r in records if r.get("llm_done"))]
        totals = [t + c for t, c in zip(totals, cols)]
        print(f"{source:24} {cols[0]:>7} " +
              " ".join(f"{c * 100 // n:>{w}}%" for c, w in zip(cols[1:], (4, 5, 4, 4, 4))))
    if totals[0]:
        n = totals[0]
        print(f"{'TOTAL':24} {n:>7} " +
              " ".join(f"{c * 100 // n:>{w}}%" for c, w in zip(totals[1:], (4, 5, 4, 4, 4))))


def main() -> None:
    parser = argparse.ArgumentParser(prog="audit_enrich")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, fn in [("extract", cmd_extract), ("enrich", cmd_enrich),
                     ("llm", cmd_llm), ("status", cmd_status)]:
        p = sub.add_parser(name)
        p.set_defaults(fn=fn)
        if name != "status":
            p.add_argument("sources", nargs="*")
        if name == "llm":
            p.add_argument("--limit", type=int, default=None,
                           help="max reports this run (default: all pending)")
            p.add_argument("--model", default="haiku")
    args = parser.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
