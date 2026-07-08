"""Enrichment pipeline (phase 2) — derives chain/language/category metadata
for collected audit reports.

Reads the collector's output (data/catalog/, data/reports/) and writes its
own, keyed by catalog id:

    data/cache/text/<source>/<file>.txt    extracted report text (layer 0)
    data/enrichment/<source>.json          enrichment records (layers 1-3)

It never modifies collector data. Layers, cheapest first, each module one
layer: textcache (0) -> layer_prior (1) -> layer_regex (2) -> layer_llm (3,
local `claude` CLI, no API token). Field merge authority lives in store.py;
schema + vocabularies in config/enrichment.yaml; deterministic rules in
config/enrichment-rules.yaml.
"""
