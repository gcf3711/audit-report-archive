# Audit Report Archive

An integrated archive of public smart-contract **audit reports** from major
audit firms, with provenance metadata (project, date, original URL). Metadata
and Markdown indexes are tracked in git; the report files themselves are not
committed (copyright stays with the audit firms) and are fully reproducible
with one command.

Current scope is **collection only** — report content analysis is a later phase.

## Status

<!-- STATUS:BEGIN -->
**6185** reports catalogued across **23** sources — **6153** verified downloadable (fetched locally), **32** unavailable (upstream dead links or archive-only). Last updated **2026-07-06**.

| Source | Reports | Downloadable | Unavailable | Listing |
|---|---|---|---|---|
| [ChainSecurity](indexes/chainsecurity.md) | 391 | 388 | 3 | https://www.chainsecurity.com/smart-contract-audit-reports |
| [Trail of Bits](indexes/trailofbits.md) | 433 | 433 | 0 | https://github.com/trailofbits/publications |
| [MixBytes](indexes/mixbytes.md) | 234 | 234 | 0 | https://github.com/mixbytes/audits_public |
| [Certora](indexes/certora.md) | 171 | 171 | 0 | https://github.com/Certora/SecurityReports |
| [Spearbit](indexes/spearbit.md) | 140 | 140 | 0 | https://github.com/spearbit/portfolio |
| [Cantina](indexes/cantina.md) | 681 | 677 | 4 | https://cantina.xyz/security-reviews |
| [Quantstamp](indexes/quantstamp.md) | 392 | 391 | 1 | https://certificate.quantstamp.com/ |
| [Sigma Prime](indexes/sigmaprime.md) | 146 | 146 | 0 | https://github.com/sigp/public-audits |
| [OpenZeppelin](indexes/openzeppelin.md) | 386 | 386 | 0 | https://www.openzeppelin.com/research#security-audits |
| [PeckShield](indexes/peckshield.md) | 488 | 488 | 0 | https://github.com/peckshield/publications |
| [Code4rena](indexes/code4rena.md) | 410 | 408 | 2 | https://code4rena.com/reports |
| [ABDK](indexes/abdk.md) | 216 | 216 | 0 | https://github.com/abdk-consulting/audits |
| [CertiK](indexes/certik.md) | 0 | 0 | 0 | https://skynet.certik.com/leaderboards/team-verified |
| [Statemind](indexes/statemind.md) | 48 | 48 | 0 | https://github.com/statemindio/public-audits |
| [Halborn](indexes/halborn.md) | 282 | 282 | 0 | https://github.com/HalbornSecurity/PublicReports |
| [Omniscia](indexes/omniscia.md) | 281 | 271 | 10 | https://omniscia.io/reports.html |
| [Zellic](indexes/zellic.md) | 386 | 386 | 0 | https://github.com/Zellic/publications |
| [Runtime Verification](indexes/runtimeverification.md) | 107 | 107 | 0 | https://github.com/runtimeverification/publications |
| [Pessimistic](indexes/pessimistic.md) | 180 | 180 | 0 | https://github.com/pessimistic-io/audits |
| [ConsenSys Diligence](indexes/consensys.md) | 139 | 127 | 12 | https://diligence.consensys.io/audits/ |
| [Nethermind](indexes/nethermind.md) | 181 | 181 | 0 | https://github.com/NethermindEth/PublicAuditReports |
| [Cyfrin](indexes/cyfrin.md) | 195 | 195 | 0 | https://github.com/Cyfrin/cyfrin-audit-reports |
| [Sherlock](indexes/sherlock.md) | 298 | 298 | 0 | https://github.com/sherlock-protocol/sherlock-reports |
<!-- STATUS:END -->

Each source name above links to its per-source table in [indexes/](indexes/)
— date, project, report URL and local fetch state for every report.

## Getting the report files

The files are not in this repo. Two ways to get them:

```bash
# 1. from the Hugging Face dataset mirror (fast, one shot)
hf download gcf3711/audit-report-archive --repo-type dataset \
    --include 'reports/*' --local-dir data

# 2. re-fetch from the original publishers
uv run python -m audit_collector download
```

### Hugging Face dataset mirror

https://huggingface.co/datasets/gcf3711/audit-report-archive — a mirror of
the local `data/` directory (5.3 GB total):

| Dataset path | Contents | Count | Local equivalent |
|---|---|---|---|
| `reports/<source>/` | report files — 4712 PDF + 1441 HTML | 6153 | `data/reports/<source>/` |
| `catalog/<source>.json` | per-source metadata (same as in git) | 22 | `data/catalog/<source>.json` |
| `README.md` | dataset card | 1 | — |

File names match the `local_path` field in the catalogs (`data/reports/...`
↔ `reports/...`), so the download command above restores files exactly where
the catalogs expect them.

Maintainer note — the mirror is uploaded with:

```bash
hf upload-large-folder gcf3711/audit-report-archive --repo-type dataset <staging-dir>
```

where the staging dir holds `reports/` (hardlink of `data/reports/`),
`catalog/` and the dataset card. `upload-large-folder` is resumable, so it
can be re-run after interruptions or data refreshes.

## Layout

```
config/sources.yaml        source registry (23 defaults; add new sources here)
src/audit_collector/       the collector package
  scrapers/                one module per source type
    github_repo.py         generic scraper for GitHub-hosted report repos
    chainsecurity.py, ...  custom scrapers for web-hosted listings
  downloader.py            fetches report files
  catalog.py               per-source metadata catalogs
  cli.py                   command-line interface
data/
  catalog/<source>.json    report metadata (tracked in git)
  reports/<source>/        downloaded report files (gitignored)
  cache/                   scratch (git clones, listing caches; gitignored)
indexes/<source>.md        per-source report tables (tracked in git)
```

## Usage

```bash
uv sync            # or: pip install -e .

python -m audit_collector list                  # show configured sources
python -m audit_collector scrape                # refresh all catalogs (or: scrape cyfrin sherlock)
python -m audit_collector download              # download report files
python -m audit_collector status                # per-source counts
python -m audit_collector build-index           # regenerate indexes/ + README status
```

Run with `PYTHONPATH=src` if not installed (`PYTHONPATH=src python -m audit_collector ...`).

## Metadata schema

Each catalog entry (`data/catalog/<source>.json`):

| field | meaning |
|---|---|
| `id` | `<source>/<slug>` |
| `source` / `source_name` | source key / display name |
| `project`, `title` | audited project, report title |
| `date` | ISO date (`YYYY-MM-DD`, `YYYY-MM`, or `YYYY`); best-effort |
| `report_url` | canonical origin URL of the report (provenance) |
| `download_url` | direct download URL when it differs |
| `listing_url` | page the report was discovered on |
| `local_path`, `sha256`, `size_bytes`, `downloaded_at` | download state |
| `extra` | source-specific details (repo path, commit, detail page, …) |

## Source-specific notes

- **certik** — not collectable without a real browser: Cloudflare challenge on
  every URL, page data AES-encrypted, no public PDFs. Official route is the
  CertiK Partner API (needs a key). The scraper fails with this explanation.
- **consensys** — live site (diligence.security) is Cloudflare-blocked for
  plain HTTP clients; listing metadata comes from a Wayback snapshot and
  report HTML is downloaded via Wayback.
- **runtimeverification** — their site API is Cloudflare-blocked from
  datacenter IPs; reports come from the runtimeverification/publications
  GitHub repo instead.
- **openzeppelin, omniscia, code4rena, consensys** — reports are HTML pages,
  not PDFs (saved as `.html`).
- **code4rena** — the platform announced it is closing; the durable mirror is
  the code-423n4 GitHub org (findings repo URL kept in `extra.findings_repo`).

## Adding a source

Append an entry to `config/sources.yaml`. For reports published in a GitHub
repo, `type: github_repo` with `repo:` (plus optional `paths:`, `extensions:`,
`exclude:`) is all that's needed. For a website, add a scraper module at
`src/audit_collector/scrapers/<type>.py` exposing
`scrape(key, cfg) -> list[Report]`.
