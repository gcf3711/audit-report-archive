"""Layer 3 — LLM extraction through the local `claude` CLI (headless mode).

No API token: `claude -p` runs on the machine's logged-in Claude Code
account. Reports still missing chains/languages/category after the
deterministic layers are batched (several reports per call), the model is
given the controlled vocabularies and must answer with one JSON object per
report; values outside the vocabulary are dropped at validation. Writes
with method `llm`, so per the authority rule it fills gaps and outranks
deterministic guesses of equal confidence, but never `manual`.
"""

from __future__ import annotations

import json
import subprocess

from . import store
from .schema import VOCAB

BATCH = 8            # reports per claude call
TEXT_PER_REPORT = 1800
TIMEOUT = 600
LLM_FIELDS = ["chains", "languages", "category", "audit_kind"]

PROMPT = """\
You classify smart-contract security audit reports. For EACH report excerpt
below, determine:
- chains: blockchains the audited code targets, ONLY from: {chains}
- languages: implementation languages of the audited code, ONLY from: {languages}
- category: single best protocol category, ONLY from: {categories}
- audit_kind: ONLY from: {audit_kinds}

Use null (or [] for lists) when the excerpt does not say — never guess.
Answer with ONLY a JSON array, one object per report, in input order:
[{{"n": 1, "chains": [...], "languages": [...], "category": "...", "audit_kind": "..."}}, ...]

{reports}"""


def needs_llm(record: dict) -> bool:
    return not record.get("chains") or not record.get("languages") \
        or not record.get("category")


def _call_claude(prompt: str, model: str) -> list[dict]:
    proc = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "json", "--model", model],
        capture_output=True, text=True, timeout=TIMEOUT)
    if proc.returncode != 0:
        raise RuntimeError(f"claude CLI failed: {proc.stderr[:300]}")
    result = json.loads(proc.stdout)["result"]
    start, end = result.find("["), result.rfind("]")
    if start < 0 or end < 0:
        raise ValueError(f"no JSON array in reply: {result[:200]}")
    return json.loads(result[start:end + 1])


def enrich_batch(batch: list[tuple[dict, str]], model: str) -> int:
    """batch: [(record, text), ...] -> merged field count."""
    sections = [f"--- report {i} ---\n{text[:TEXT_PER_REPORT]}"
                for i, (_, text) in enumerate(batch, 1)]
    prompt = PROMPT.format(
        chains=", ".join(VOCAB["chains"]),
        languages=", ".join(VOCAB["languages"]),
        categories=", ".join(VOCAB["categories"]),
        audit_kinds=", ".join(VOCAB["audit_kinds"]),
        reports="\n\n".join(sections))

    answers = {a.get("n"): a for a in _call_claude(prompt, model)}
    changed = 0
    for i, (record, _) in enumerate(batch, 1):
        answer = answers.get(i)
        if not answer:
            continue
        for field in LLM_FIELDS:
            value = answer.get(field)
            if value in (None, [], ""):
                continue
            changed += store.apply(record, field, value, "llm", "medium")
        record.setdefault("llm_done", True)
    return changed
