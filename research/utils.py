from __future__ import annotations

from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode


STRIP_QUERY_KEYS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "gclid",
    "fbclid",
    "igshid",
    "mc_cid",
    "mc_eid",
}


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    # strip fragment
    fragmentless = parsed._replace(fragment="")
    # strip tracking params
    query = parse_qsl(fragmentless.query, keep_blank_values=True)
    kept = [(k, v) for k, v in query if k.lower() not in STRIP_QUERY_KEYS]
    new_query = urlencode(kept)
    cleaned = fragmentless._replace(query=new_query)
    # remove default ports
    netloc = cleaned.netloc.replace(":80", "").replace(":443", "")
    cleaned = cleaned._replace(netloc=netloc)
    return urlunparse(cleaned)


