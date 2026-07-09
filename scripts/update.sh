#!/usr/bin/env bash
# Monthly refresh: scrape -> download new -> indexes -> git push -> HF upload.
# Run from anywhere; requires `hf auth login` done once for the upload step.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STAGING="${HF_STAGING:-/ssd/gcf/hf-staging}"
HF_REPO="gcf3711/audit-report-archive"
cd "$ROOT"

echo "== update $(date -u +%FT%TZ) =="
git pull --rebase -q

uv sync -q
uv run python -m audit_collector scrape
uv run python -m audit_collector download          # incremental: skips existing files
uv run python -m audit_collector build-index

# enrichment: all layers are incremental (new reports only); the LLM layer
# uses the local claude CLI and only sees entries the cheap layers left open
uv run python -m audit_enrich extract
uv run python -m audit_enrich enrich
uv run python -m audit_enrich llm || echo "llm layer incomplete (quota?); next run resumes"

git add data/catalog data/enrichment indexes README.md
if ! git diff --cached --quiet; then
    git commit -q -m "Update catalogs $(date -u +%F)"
    git push -q
    echo "pushed metadata update"
else
    echo "no metadata changes"
fi

# mirror new report files into the staging tree (hardlinks; never deletes,
# and keeps the .cache upload state so re-uploads are skipped)
mkdir -p "$STAGING/reports" "$STAGING/catalog" "$STAGING/enrichment"
cp -aln data/reports/. "$STAGING/reports/"
cp -a data/catalog/. "$STAGING/catalog/"
cp -a data/enrichment/. "$STAGING/enrichment/"
hf upload-large-folder "$HF_REPO" --repo-type dataset "$STAGING"
echo "== done $(date -u +%FT%TZ) =="
