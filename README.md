# Audit Report Archive

An integrated archive of public smart-contract **audit reports** from major
audit firms, with provenance metadata (project, date, original URL). Metadata
and Markdown indexes are tracked in git; the report files themselves are not
committed (copyright stays with the audit firms) and are fully reproducible
with one command.

Scope: **collection** (done, kept fresh monthly) and **metadata enrichment**
(phase 2, in progress — chain / language / category per report, see
[Enrichment](#enrichment-phase-2)); report content analysis is a later phase.

## Status

<!-- STATUS:BEGIN -->
**11215** reports catalogued across **47** sources (**9479** PDF, **1736** HTML) — **9377** verified downloadable (fetched locally), **1838** unavailable (upstream dead links or archive-only). Last updated **2026-07-15**.

| Source | Reports | PDF | HTML | Downloadable | Unavailable | Listing |
|---|---|---|---|---|---|---|
| [ChainSecurity](indexes/chainsecurity.md) | 393 | 393 | 0 | 388 | 5 | https://www.chainsecurity.com/smart-contract-audit-reports |
| [Trail of Bits](indexes/trailofbits.md) | 871 | 871 | 0 | 433 | 438 | https://github.com/trailofbits/publications |
| [MixBytes](indexes/mixbytes.md) | 234 | 234 | 0 | 234 | 0 | https://github.com/mixbytes/audits_public |
| [Certora](indexes/certora.md) | 344 | 344 | 0 | 171 | 173 | https://github.com/Certora/SecurityReports |
| [Spearbit](indexes/spearbit.md) | 140 | 140 | 0 | 140 | 0 | https://github.com/spearbit/portfolio |
| [Cantina](indexes/cantina.md) | 684 | 677 | 7 | 677 | 7 | https://cantina.xyz/security-reviews |
| [Quantstamp](indexes/quantstamp.md) | 393 | 148 | 245 | 391 | 2 | https://certificate.quantstamp.com/ |
| [Sigma Prime](indexes/sigmaprime.md) | 146 | 146 | 0 | 146 | 0 | https://github.com/sigp/public-audits |
| [OpenZeppelin](indexes/openzeppelin.md) | 390 | 0 | 390 | 386 | 4 | https://www.openzeppelin.com/research#security-audits |
| [PeckShield](indexes/peckshield.md) | 488 | 488 | 0 | 488 | 0 | https://github.com/peckshield/publications |
| [Code4rena](indexes/code4rena.md) | 411 | 2 | 409 | 408 | 3 | https://code4rena.com/reports |
| [ABDK](indexes/abdk.md) | 216 | 216 | 0 | 216 | 0 | https://github.com/abdk-consulting/audits |
| [CertiK](indexes/certik.md) | 0 | 0 | 0 | 0 | 0 | https://skynet.certik.com/leaderboards/team-verified |
| [Statemind](indexes/statemind.md) | 100 | 100 | 0 | 48 | 52 | https://github.com/statemindio/public-audits |
| [Halborn](indexes/halborn.md) | 282 | 282 | 0 | 282 | 0 | https://github.com/HalbornSecurity/PublicReports |
| [Omniscia](indexes/omniscia.md) | 281 | 0 | 281 | 271 | 10 | https://omniscia.io/reports.html |
| [Zellic](indexes/zellic.md) | 777 | 777 | 0 | 386 | 391 | https://github.com/Zellic/publications |
| [Runtime Verification](indexes/runtimeverification.md) | 215 | 215 | 0 | 107 | 108 | https://github.com/runtimeverification/publications |
| [Pessimistic](indexes/pessimistic.md) | 180 | 180 | 0 | 180 | 0 | https://github.com/pessimistic-io/audits |
| [ConsenSys Diligence](indexes/consensys.md) | 139 | 0 | 139 | 127 | 12 | https://diligence.consensys.io/audits/ |
| [Nethermind](indexes/nethermind.md) | 181 | 181 | 0 | 181 | 0 | https://github.com/NethermindEth/PublicAuditReports |
| [Cyfrin](indexes/cyfrin.md) | 195 | 195 | 0 | 195 | 0 | https://github.com/Cyfrin/cyfrin-audit-reports |
| [Sherlock](indexes/sherlock.md) | 298 | 298 | 0 | 298 | 0 | https://github.com/sherlock-protocol/sherlock-reports |
| [BlockSec](indexes/blocksec.md) | 413 | 413 | 0 | 204 | 209 | https://github.com/blocksecteam/audit-reports |
| [Zokyo](indexes/zokyo.md) | 311 | 311 | 0 | 311 | 0 | https://github.com/zokyo-sec/audit-reports |
| [CD Security](indexes/cdsecurity.md) | 67 | 67 | 0 | 67 | 0 | https://github.com/CDSecurity/audits |
| [Team Omega](indexes/teamomega.md) | 108 | 108 | 0 | 53 | 55 | https://github.com/OmegaAudits/audits |
| [Verilog Solutions](indexes/verilog.md) | 13 | 13 | 0 | 13 | 0 | https://github.com/Verilog-Solutions/.github |
| [Ackee Blockchain](indexes/ackee.md) | 96 | 96 | 0 | 96 | 0 | https://github.com/Ackee-Blockchain/public-audit-reports |
| [Hexens](indexes/hexens.md) | 307 | 307 | 0 | 153 | 154 | https://github.com/Hexens/Smart-Contract-Review-Public-Reports |
| [Oxorio](indexes/oxorio.md) | 47 | 47 | 0 | 47 | 0 | https://github.com/oxor-io/public_audits |
| [Pashov Audit Group](indexes/pashov.md) | 300 | 300 | 0 | 300 | 0 | https://github.com/pashov/audits |
| [Solidified](indexes/solidified.md) | 247 | 247 | 0 | 247 | 0 | https://github.com/solidified-platform/audits |
| [Electisec (yAudit)](indexes/yaudit.md) | 282 | 282 | 0 | 138 | 144 | https://github.com/electisec/reports |
| [Decurity](indexes/decurity.md) | 122 | 122 | 0 | 61 | 61 | https://github.com/Decurity/audits |
| [Oak Security](indexes/oaksecurity.md) | 321 | 306 | 15 | 321 | 0 | https://github.com/oak-security/audit-reports |
| [Informal Systems](indexes/informal.md) | 94 | 42 | 52 | 94 | 0 | https://github.com/informalsystems/audits |
| [ChainSafe](indexes/chainsafe.md) | 33 | 33 | 0 | 33 | 0 | https://github.com/ChainSafe/audits |
| [Bailsec](indexes/bailsec.md) | 95 | 95 | 0 | 95 | 0 | https://github.com/bailsec/BailSec |
| [Composable Security](indexes/composable.md) | 28 | 28 | 0 | 28 | 0 | https://github.com/ComposableSecurity/.github |
| [Coinspect](indexes/coinspect.md) | 42 | 42 | 0 | 42 | 0 | https://github.com/coinspect/publications |
| [Enigma Dark](indexes/enigmadark.md) | 28 | 28 | 0 | 28 | 0 | https://github.com/Enigma-Dark/security-review-reports |
| [OtterSec](indexes/ottersec.md) | 386 | 386 | 0 | 386 | 0 | https://osec.io/audits |
| [Dedaub](indexes/dedaub.md) | 178 | 0 | 178 | 178 | 0 | https://dedaub.com/audits/ |
| [Hats Finance](indexes/hatsfinance.md) | 36 | 21 | 15 | 26 | 10 | https://github.com/hats-finance |
| [dapp.org](indexes/dapporg.md) | 5 | 0 | 5 | 5 | 0 | https://dapp.org.uk |
| [Paladin Blockchain Security](indexes/paladin.md) | 298 | 298 | 0 | 298 | 0 | https://paladinsec.co/audits/ |
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
the local `data/` directory (~11 GB total):

| Dataset path | Contents | Count | Local equivalent |
|---|---|---|---|
| `reports/<source>/` | report files — 7672 PDF + 1624 HTML + 81 MD | 9377 | `data/reports/<source>/` |
| `catalog/<source>.json` | per-source metadata (same as in git) | 46 | `data/catalog/<source>.json` |
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
config/sources.yaml        source registry (add new sources here)
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

## Enrichment (phase 2)

`src/audit_enrich/` derives per-report metadata — target blockchains,
implementation languages, protocol category, audit kind, in-scope repo —
without touching collector data. Current coverage (all 9409 reports
processed, null when the report doesn't state it): chains 44%, languages
59%, category 74%.

### What's in the corpus

<!-- ENRICHMENT:BEGIN -->
Across **9409** reports, top 10 values per field (counts; full lists via `python -m audit_enrich stats`):

| Chain | Language | Category | Audit kind |
|---|---|---|---|
| ethereum (1913) | solidity (4462) | defi-dex (856) | private-audit (8257) |
| solana (600) | rust (655) | defi-yield (792) | competition (706) |
| cosmos (466) | go (158) | defi-lending (716) | formal-verification (226) |
| polygon (459) | cairo (155) | bridge-interop (607) | limited-review (190) |
| bitcoin (250) | move (63) | token-distribution (601) | other (26) |
| arbitrum (250) | javascript (48) | liquid-staking (416) | fuzzing-campaign (4) |
| starknet (233) | typescript (42) | chain-core (378) |  |
| algorand (228) | vyper (42) | defi-derivatives (348) |  |
| aptos (227) | yul (23) | dao-governance (304) |  |
| optimism (161) | other (20) | nft (295) |  |

Ecosystem totals: evm 2790 · solana 600 · cosmos 598 · other 481 · move 260 · bitcoin 250 · cairo 233 · polkadot 29.
<!-- ENRICHMENT:END -->

Records live in
`data/enrichment/<source>.json` keyed by catalog `id`; schema and controlled
vocabularies in [config/enrichment.yaml](config/enrichment.yaml),
deterministic rules in
[config/enrichment-rules.yaml](config/enrichment-rules.yaml).

Cheap layers run first; each value carries `provenance` (method +
confidence), and a later pass only overrides a stronger one by the authority
rule in `store.py` (manual edits always win):

```bash
python -m audit_enrich extract          # 0: report text -> data/cache/text/
python -m audit_enrich enrich           # 1+2: source priors + keyword/regex
python -m audit_enrich llm [--limit N]  # 3: local `claude` CLI for the gaps
python -m audit_enrich status           # coverage per source
python -m audit_enrich stats            # value distributions (chains/languages/...)
```

The LLM layer shells out to the logged-in Claude Code CLI (`claude -p`,
no API key) and only processes reports the deterministic layers left
incomplete; it is resumable and validates every answer against the
vocabularies.

## Metadata schema

Each catalog entry (`data/catalog/<source>.json`):

| field | meaning |
|---|---|
| `id` | `<source>/<title-slug>-<url-hash>` (stable + unique; enrichment join key) |
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
- **ottersec** — osec.io/reports/<uuid> URLs 302-redirect to short-lived
  signed PDF URLs; the stable uuid URL is kept as provenance.
- **dedaub** — the audit index is JS-rendered; reports are enumerated from
  /audits/sitemap.xml and saved as HTML pages. Their GitHub repo is frozen
  at Nov 2023, so the website is the canonical source.
- **hatsfinance** — audit competitions; one report.md per finalized
  competition repo in the hats-finance GitHub org (repos named
  `<project>-0x<vault>`); unfinalized competitions have no report yet.
- **paladin** — listing pagination is nonce-protected; project slugs are
  enumerated via the Wayback CDX index plus the live listing's first page,
  then PDFs are pulled from the live server-rendered project pages.

Researched but not collectable (nothing public to ingest): gauntlet (risk
modeling, not audits), fuzzland / watchpug / nomoi (reports only inside
client repos), secure3 (report repo deleted), hunter security (JS-only
site), lexfo / securing (no public archive), ruptura / dingbats (not
found), cmichel / stermi / 0xleastwood (work embedded in Spearbit/Code4rena
reports, already covered), blackthorn (publishes via Sherlock, covered),
alberto cuesta canada (no personal archive), nomic labs (3 Medium posts,
bot-blocked), ezrvaults (a Renzo Protocol product, not an audit firm).

## Adding a source (without touching existing data)

Everything is per-source isolated: each source has its own catalog file
(`data/catalog/<key>.json`), report directory (`data/reports/<key>/`) and
index page (`indexes/<key>.md`). Adding a source never rewrites another
source's data, and `catalog.merge` preserves download state across re-scrapes
— so the steps below are safe to run on a live archive.

**1. Register the source** — append one entry to `config/sources.yaml`:

```yaml
# reports live in a GitHub repo (covers most firms) — no code needed
mynewfirm:
  name: My New Firm
  type: github_repo
  listing_url: https://github.com/mynewfirm/audit-reports
  repo: mynewfirm/audit-reports
  paths: [reports]        # optional: only scan these subdirectories
  extensions: [.pdf, .md] # optional: default .pdf
  exclude: [templates/]   # optional: skip matching paths
```

For a website source instead, add a module
`src/audit_collector/scrapers/<type>.py` exposing
`scrape(key, cfg) -> list[Report]`, and set `type: <type>` in the yaml entry.

**2. Collect just that source** (existing sources are not touched):

```bash
uv run python -m audit_collector scrape mynewfirm
uv run python -m audit_collector download mynewfirm
uv run python -m audit_collector build-index   # refreshes indexes + README status
```

**3. Commit** `config/sources.yaml`, `data/catalog/mynewfirm.json`,
`indexes/` and `README.md`. The monthly update then keeps the new source
fresh automatically; the HF mirror picks up its files on the next
`scripts/update.sh` run.
