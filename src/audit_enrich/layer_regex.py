"""Layer 2 — deterministic keyword extraction.

Two passes with the same keyword tables (config/enrichment-rules.yaml):

  filename    over title + file name + report URL   (confidence: medium)
  text-regex  over the head of the extracted text   (confidence: medium,
              except unambiguous markers promoted to high)

Also pulls the in-scope GitHub repo from the text, and adds chains implied
by a found language (cairo -> starknet etc.).
"""

from __future__ import annotations

import re

from . import store
from .schema import RULES

TEXT_SCAN_CHARS = 3000   # only the report head: title page + scope
HIGH_MARKERS = {         # a match of these is proof, not a mention
    ("languages", "solidity"): re.compile(r"pragma solidity", re.I),
    ("languages", "vyper"): re.compile(r"@version|# pragma version", re.I),
}
IMPLIED_CHAIN = {"cairo": "starknet", "teal": "algorand",
                 "func": "ton", "tact": "ton", "michelson": "tezos"}
_REPO = re.compile(r"github\.com/([\w.-]+/[\w.-]+?)(?:\.git)?(?:[/#\s\"')]|$)")

_COMPILED: dict[str, dict[str, list[re.Pattern]]] = {
    field: {value: [re.compile(p, re.I) for p in patterns]
            for value, patterns in table.items()}
    for field, table in RULES["keywords"].items()}


def _scan(blob: str) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for field, table in _COMPILED.items():
        hits = [value for value, pats in table.items()
                if any(p.search(blob) for p in pats)]
        if hits:
            found[field] = hits
    return found


def _apply_found(record: dict, found: dict[str, list[str]], method: str) -> int:
    changed = 0
    for field, values in found.items():
        if field == "audit_kinds":  # scalar field, first (strongest) hit wins
            changed += store.apply(record, "audit_kind", values[0], method, "medium")
            continue
        changed += store.apply(record, field, values, method, "medium")
    implied = sorted({IMPLIED_CHAIN[l] for l in found.get("languages", [])
                      if l in IMPLIED_CHAIN})
    if implied:
        changed += store.apply(record, "chains", implied, method, "medium")
    return changed


def enrich_filename(entry: dict, record: dict) -> int:
    blob = " ".join(filter(None, [
        entry.get("title"), entry.get("project"),
        entry.get("local_path"), entry.get("report_url"),
        str(entry.get("extra") or "")])).lower()  # e.g. ottersec extra.chain
    return _apply_found(record, _scan(blob), "filename")


def enrich_text(record: dict, text: str) -> int:
    head = text[:TEXT_SCAN_CHARS]
    changed = _apply_found(record, _scan(head), "text-regex")
    for (field, value), pattern in HIGH_MARKERS.items():
        if pattern.search(text):
            changed += store.apply(record, field, [value], "text-regex", "high")
    if not record.get("scope"):
        m = _REPO.search(head)
        if m:
            record["scope"] = {"repo": f"https://github.com/{m.group(1)}"}
            changed += 1
    return changed
