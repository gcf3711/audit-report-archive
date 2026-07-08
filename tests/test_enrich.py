"""Tests for the enrichment merge rule and deterministic extraction."""

from audit_enrich import store
from audit_enrich.layer_regex import enrich_filename, enrich_text
from audit_enrich.schema import ecosystems_for


def test_higher_confidence_wins():
    r = store.new_record("x/y")
    assert store.apply(r, "chains", ["solana"], "source-prior", "low")
    assert store.apply(r, "chains", ["ethereum"], "text-regex", "medium")
    assert r["chains"] == ["ethereum"]
    # lower authority cannot undo it
    assert not store.apply(r, "chains", ["solana"], "filename", "low")
    assert r["chains"] == ["ethereum"]


def test_equal_authority_unions_lists_keeps_scalars():
    r = store.new_record("x/y")
    store.apply(r, "chains", ["ethereum"], "text-regex", "medium")
    store.apply(r, "chains", ["arbitrum"], "text-regex", "medium")
    assert r["chains"] == ["arbitrum", "ethereum"]
    store.apply(r, "category", "defi-dex", "llm", "medium")
    assert not store.apply(r, "category", "nft", "llm", "medium")
    assert r["category"] == "defi-dex"


def test_manual_never_overwritten():
    r = store.new_record("x/y")
    store.apply(r, "category", "oracle", "manual", "high")
    assert not store.apply(r, "category", "defi-dex", "llm", "high")
    assert r["category"] == "oracle"


def test_vocab_violations_dropped():
    r = store.new_record("x/y")
    assert not store.apply(r, "chains", ["not-a-chain"], "llm", "high")
    assert store.apply(r, "chains", ["solana", "bogus"], "llm", "high")
    assert r["chains"] == ["solana"]


def test_filename_and_text_extraction():
    entry = {"title": "Uniswap V3 on Arbitrum audit",
             "local_path": "data/reports/x/uniswap.pdf", "report_url": "u"}
    r = store.new_record("x/uniswap")
    enrich_filename(entry, r)
    assert r["chains"] == ["arbitrum"]

    enrich_text(r, "Scope: pragma solidity 0.8.19, deployed on Ethereum. "
                   "Code at github.com/Uniswap/v3-core commit abc.")
    assert "ethereum" in r["chains"]
    assert r["languages"] == ["solidity"]
    assert r["provenance"]["languages"]["confidence"] == "high"  # pragma marker
    assert r["scope"]["repo"] == "https://github.com/Uniswap/v3-core"


def test_ecosystem_mapping():
    assert ecosystems_for(["arbitrum", "solana", "starknet"]) == \
        ["cairo", "evm", "solana"]
