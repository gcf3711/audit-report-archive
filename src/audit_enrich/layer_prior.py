"""Layer 1 — per-source priors (method: source-prior).

Applies the `priors:` table from config/enrichment-rules.yaml to every
report of a source, plus the default audit_kind for firm sources.
"""

from __future__ import annotations

from . import store
from .schema import FIELDS, RULES


def enrich(source: str, records: dict[str, dict]) -> int:
    prior = RULES["priors"].get(source, {})
    default_kind = RULES["default_audit_kind"]
    changed = 0
    for record in records.values():
        for field, rule in prior.items():
            value = rule["values"] if FIELDS[field]["type"] == "list" else rule["value"]
            changed += store.apply(record, field, value, "source-prior", rule["confidence"])
        if "audit_kind" not in prior:
            changed += store.apply(record, "audit_kind", default_kind["value"],
                                   "source-prior", default_kind["confidence"])
    return changed
