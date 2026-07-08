"""Load config/enrichment.yaml and validate values against it."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
ENRICH_DIR = ROOT / "data" / "enrichment"
TEXT_DIR = ROOT / "data" / "cache" / "text"

_SCHEMA = yaml.safe_load((ROOT / "config" / "enrichment.yaml").read_text())
_RULES = yaml.safe_load((ROOT / "config" / "enrichment-rules.yaml").read_text())

SCHEMA_VERSION: int = _SCHEMA["schema_version"]
VOCAB: dict[str, list[str]] = _SCHEMA["vocab"]
METHODS: list[str] = _SCHEMA["methods"]
CONFIDENCE: list[str] = _SCHEMA["confidence"]
FIELDS: dict[str, dict] = _SCHEMA["fields"]
RULES: dict = _RULES

# chain -> ecosystem family (drives the derived `ecosystems` field)
ECOSYSTEM_OF = {
    **{c: "evm" for c in [
        "ethereum", "arbitrum", "optimism", "base", "polygon", "bsc",
        "avalanche", "fantom", "gnosis", "zksync-era", "scroll", "linea",
        "mantle", "celo", "moonbeam", "tron", "berachain", "sonic",
        "evm-other"]},
    "solana": "solana",
    "cosmos": "cosmos", "osmosis": "cosmos",
    "aptos": "move", "sui": "move",
    "polkadot": "polkadot",
    "bitcoin": "bitcoin", "lightning": "bitcoin",
    "starknet": "cairo",
}


def vocab_field(field: str) -> str | None:
    """Vocabulary name a field validates against, if any."""
    return FIELDS.get(field, {}).get("vocab")


def check_value(field: str, value: str) -> bool:
    vocab = vocab_field(field)
    return vocab is None or value in VOCAB[vocab]


def ecosystems_for(chains: list[str]) -> list[str]:
    return sorted({ECOSYSTEM_OF.get(c, "other") for c in chains})
