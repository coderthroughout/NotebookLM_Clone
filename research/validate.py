from __future__ import annotations

from typing import List
import tldextract

from .models import PageContent, SourceCredibility


WHITELIST_DOMAINS = {
    "mit.edu": 0.95,
    "ocw.mit.edu": 0.95,
    "harvard.edu": 0.95,
    "stanford.edu": 0.95,
    "khanacademy.org": 0.9,
    "openstax.org": 0.9,
    "nih.gov": 0.9,
    "ncbi.nlm.nih.gov": 0.92,
    "nasa.gov": 0.95,
    "noaa.gov": 0.9,
    "britannica.com": 0.85,
    "encyclopedia.com": 0.8,
    "unesco.org": 0.88,
    "who.int": 0.9,
    "edu": 0.85,
    "wikipedia.org": 0.75,
    "arxiv.org": 0.9,
    "nature.com": 0.95,
    "sciencedirect.com": 0.9,
    "springer.com": 0.88,
    "ieee.org": 0.9,
    "nationalgeographic.org": 0.85,
    "byjus.com": 0.55,
}


def domain_from_url(url: str) -> str:
    u = str(url)
    ext = tldextract.extract(u)
    domain = ".".join([p for p in [ext.domain, ext.suffix] if p])
    sub = ext.subdomain
    if sub:
        fqdn = f"{sub}.{domain}"
        return fqdn
    return domain


def score_source(page: PageContent) -> SourceCredibility:
    d = domain_from_url(page.url)
    base = 0.5
    reasons: List[str] = []

    # Whitelist bump
    for k, bump in WHITELIST_DOMAINS.items():
        if d.endswith(k):
            base = max(base, bump)
            reasons.append(f"whitelist:{k}")
            break

    # Heuristics
    text_len = len(page.text or "")
    if text_len > 1500:
        base += 0.05
        reasons.append("rich_text")
    if page.author:
        base += 0.03
        reasons.append("author_present")
    if page.site_name:
        base += 0.02
        reasons.append("site_name_present")

    base = max(0.0, min(1.0, base))
    return SourceCredibility(url=page.url, domain=d, score=base, reasons=reasons)


