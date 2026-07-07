"""Hats Finance — audit competitions on GitHub.

No central index: finalized competition repos (named <Project>-0x<vault>)
in the hats-finance org carry either a root report.md or an
'audit/Hats - Audit Report.pdf'. Org repos are listed via the GitHub API,
falling back to the org page HTML when rate-limited; both report layouts
are probed via raw.githubusercontent.com (not API rate-limited).
"""

from __future__ import annotations

import re
from urllib.parse import quote

from .. import http
from ..models import Report

ORG = "hats-finance"
_COMP = re.compile(r"^(.*)-(0x[0-9a-fA-F]{40})$")
_CANDIDATES = ["report.md", "audit/Hats - Audit Report.pdf"]


def _repos_via_api() -> list[dict]:
    repos, page = [], 1
    while True:
        resp = http.get(f"https://api.github.com/orgs/{ORG}/repos",
                        params={"per_page": 100, "page": page}, min_interval=1.0)
        resp.raise_for_status()
        batch = resp.json()
        if not isinstance(batch, list):
            raise RuntimeError(f"unexpected API response: {batch}")
        repos.extend(batch)
        if len(batch) < 100:
            return repos
        page += 1


def _repos_via_html() -> list[dict]:
    names, page = set(), 1
    while page < 20:
        resp = http.get(f"https://github.com/orgs/{ORG}/repositories",
                        params={"page": page}, min_interval=1.0)
        resp.raise_for_status()
        found = set(re.findall(r'"name":"([^"]+)"', resp.text)) - names
        comp_found = {n for n in found if _COMP.match(n)}
        if not comp_found and page > 1:
            break
        names |= found
        page += 1
    return [{"name": n, "default_branch": None} for n in sorted(names)]


def scrape(key: str, cfg: dict) -> list[Report]:
    try:
        repos = _repos_via_api()
    except Exception as e:
        print(f"  API listing failed ({e}); falling back to HTML", flush=True)
        repos = _repos_via_html()

    reports = []
    for repo in repos:
        m = _COMP.match(repo["name"])
        if not m or "test" in repo["name"].lower():
            continue
        project, vault = m.groups()
        branches = [repo["default_branch"]] if repo.get("default_branch") else ["main", "master"]
        hit = None
        for branch in branches:
            for cand in _CANDIDATES:
                raw = (f"https://raw.githubusercontent.com/{ORG}/{repo['name']}"
                       f"/{branch}/{quote(cand)}")
                try:
                    if http.get(raw, min_interval=0.3).status_code == 200:
                        hit = (branch, cand, raw)
                        break
                except Exception:
                    continue
            if hit:
                break
        if not hit:
            continue  # not finalized / no published report
        branch, cand, raw = hit
        name = project.replace("-", " ").strip()
        reports.append(Report(
            source=key,
            project=name,
            title=f"{name} audit competition",
            date=(repo.get("pushed_at") or "")[:10] or None,
            report_url=f"https://github.com/{ORG}/{repo['name']}/blob/{branch}/{quote(cand)}",
            download_url=raw,
            file_type="md" if cand.endswith(".md") else "pdf",
            extra={"vault": vault, "repo": repo["name"]},
        ))
    print(f"  {len(reports)} finalized competitions (of {len(repos)} repos)", flush=True)
    return reports
