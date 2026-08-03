#!/usr/bin/env python3
"""Fetch a per-DOI citation count for every DOI in assets/dois.txt.

Primary source: OpenAlex (free, no key, datacenter-friendly).
Per-DOI fallback: Crossref. Both are public APIs.

Prints a JSON object {doi: count} to stdout and exits 0 on success.
Exits non-zero if not a single DOI could be resolved, so the caller can
keep the last committed values rather than write wrong numbers.
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

    counts = {}
    for doi in dois:
        for name, fn in (("openalex", openalex), ("crossref", crossref)):
            try:
                counts[doi] = fn(doi)
                print("  %-8s %s -> %d" % (name, doi, counts[doi]), file=sys.stderr)
                break
            except Exception as e:
                print("  %-8s %s failed: %s" % (name, doi, e), file=sys.stderr)

    if not counts:
        print("no DOIs resolved", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(counts))


if __name__ == "__main__":
    main()
