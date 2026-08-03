#!/usr/bin/env python3
"""Write per-DOI citation counts into index.html.

Usage: update_cites.py <path-to-json-file | json-string>
  where the JSON is an object {doi: count}.

For each `<span class="cite" data-cite="DOI"></span>` in the page, set its
text to "N citations" (hidden when N is 0). Also writes assets/scholar.json
with the per-paper breakdown, the total, and the date.
"""
import re, sys, json, datetime, pathlib

arg = sys.argv[1]
p = pathlib.Path(arg)
counts = json.loads(p.read_text() if p.is_file() else arg)
root = pathlib.Path(__file__).resolve().parent.parent
idx = root / "index.html"
html = idx.read_text()


def label(n):
    return "" if n <= 0 else "%d citation%s" % (n, "" if n == 1 else "s")


def repl(m):
    doi = m.group("doi")
    if doi not in counts:
        return m.group(0)                      # leave unknown badges untouched
    return '<span class="cite" data-cite="%s">%s</span>' % (doi, label(counts[doi]))


html, n_sub = re.subn(
    r'<span class="cite" data-cite="(?P<doi>[^"]+)">.*?</span>',
    repl, html, flags=re.S)
idx.write_text(html)

(root / "assets" / "scholar.json").write_text(json.dumps({
    "papers": counts,
    "total": sum(counts.values()),
    "updated": datetime.date.today().isoformat(),
}, indent=2) + "\n")

print("updated %d badge(s): %s" % (n_sub, counts))
