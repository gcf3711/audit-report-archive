"""CertiK Skynet — https://skynet.certik.com

Not scrapable without a real browser: the whole site (including robots.txt)
sits behind a Cloudflare managed challenge for non-residential IPs, the
Next.js page props are AES-encrypted client side (no open JSON API), and
recent reports are only viewable on-site (no public PDFs). The official
route is the CertiK Partner API (https://api.certik-skynet.com/public-docs/),
which requires an API key from APIsupport@certik.com.
"""

from __future__ import annotations

from ..models import Report


def scrape(key: str, cfg: dict) -> list[Report]:
    raise RuntimeError(
        "CertiK Skynet is Cloudflare-blocked and has no public report API. "
        "Options: run a headless browser from a residential IP, or request a "
        "CertiK Partner API key (see this module's docstring)."
    )
