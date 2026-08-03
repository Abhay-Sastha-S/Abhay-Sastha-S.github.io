#!/usr/bin/env python3
"""Sum citation counts across the DOIs in assets/dois.txt.

Primary source: OpenAlex (free, no key, datacenter-friendly).
Per-DOI fallback: Crossref. Both are public APIs.

Prints the integer total to stdout and exits 0 on success.
Exits non-zero if not a single DOI could be resolved, so the caller can
keep the last committed value rather than write a wrong number.
"""
import json, sys, pathlib, urllib.request, urllib.parse

MAILTO = "s.abhaysastha@gmail.com"          # OpenAlex "polite pool" contact
ROOT = pathlib.Path(__file__).resolve().parent.parent
DOI_FILE = ROOT / "assets" / "dois.txt"


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": f"portfolio-cites (mailto:{MAILTO})"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def openalex(doi):
    u = "https://api.openalex.org/works/https://doi.org/%s?mailto=%s" % (
        urllib.parse.quote(doi, safe=""), MAILTO)
    return int(_get(u).get("cited_by_count"))


def crossref(doi):
    u = "https://api.crossref.org/works/%s" % urllib.parse.quote(doi, safe="")
    return int(_get(u)["message"].get("is-referenced-by-count"))


def main():
    dois = []
    for line in DOI_FILE.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            dois.append(line)

    total, resolved = 0, 0
    for doi in dois:
        n = None
        for name, fn in (("openalex", openalex), ("crossref", crossref)):
            try:
                n = fn(doi)
                print("  %-8s %s -> %d" % (name, doi, n), file=sys.stderr)
                break
            except Exception as e:
                print("  %-8s %s failed: %s" % (name, doi, e), file=sys.stderr)
        if n is not None:
            total += n
            resolved += 1

    if resolved == 0:
        print("no DOIs resolved", file=sys.stderr)
        sys.exit(1)

    print(total)


if __name__ == "__main__":
    main()
