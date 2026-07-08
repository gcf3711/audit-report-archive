"""Enrichment record storage and the field-merge authority rule.

One JSON file per source (data/enrichment/<source>.json), a list of records
keyed by catalog id. All layers write through `apply()`, which enforces the
authority rule from config/enrichment.yaml:

    manual is never overwritten; otherwise higher confidence wins; at equal
    confidence the later method in schema.METHODS wins. For list fields a
    strictly stronger pass replaces, an equally strong pass unions.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from .schema import (CONFIDENCE, ENRICH_DIR, FIELDS, METHODS, SCHEMA_VERSION,
                     check_value)


def _authority(method: str, confidence: str) -> tuple[int, int]:
    if method == "manual":
        return (len(CONFIDENCE), len(METHODS))
    return (CONFIDENCE.index(confidence), METHODS.index(method))


def new_record(report_id: str) -> dict:
    return {
        "id": report_id,
        "schema_version": SCHEMA_VERSION,
        "enriched_at": None,
        "text_extracted": None,
        "provenance": {},
    }


def apply(record: dict, field: str, value, method: str, confidence: str) -> bool:
    """Merge one extracted value into a record. Returns True if it changed."""
    is_list = FIELDS[field]["type"] == "list"
    values = value if is_list else [value]
    values = [v for v in values if check_value(field, v)]
    if not values:
        return False

    prov = record["provenance"].get(field)
    new_auth = _authority(method, confidence)
    if prov:
        old_auth = _authority(prov["method"], prov["confidence"])
        if new_auth < old_auth:
            return False
        if new_auth == old_auth and is_list:
            merged = sorted(set(record.get(field) or []) | set(values))
            if merged == record.get(field):
                return False
            record[field] = merged
            return True
        if new_auth == old_auth:
            return False

    record[field] = sorted(set(values)) if is_list else values[0]
    record["provenance"][field] = {"method": method, "confidence": confidence}
    return True


def touch(record: dict) -> None:
    record["enriched_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")


def load(source: str) -> dict[str, dict]:
    path = ENRICH_DIR / f"{source}.json"
    if not path.exists():
        return {}
    return {r["id"]: r for r in json.loads(path.read_text())}


def save(source: str, records: dict[str, dict]) -> None:
    ENRICH_DIR.mkdir(parents=True, exist_ok=True)
    ordered = sorted(records.values(), key=lambda r: r["id"])
    (ENRICH_DIR / f"{source}.json").write_text(
        json.dumps(ordered, indent=1, ensure_ascii=False) + "\n")
