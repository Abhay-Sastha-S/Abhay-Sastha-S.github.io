import re, sys, json, datetime, pathlib

n = int(sys.argv[1])
root = pathlib.Path(__file__).resolve().parent.parent
idx = root / "index.html"
SCHOLAR = "https://scholar.google.com/citations?user=QTYlmK0AAAAJ&hl=en"

item = (
    f'\n          <a class="cites" href="{SCHOLAR}">{n} citation{"" if n == 1 else "s"}</a>\n          '
    if n > 0 else ""
)

html = idx.read_text()
html = re.sub(
    r"<!-- cites:start -->.*?<!-- cites:end -->",
    f"<!-- cites:start -->{item}<!-- cites:end -->",
    html,
    flags=re.S,
)
idx.write_text(html)

(root / "assets" / "scholar.json").write_text(
    json.dumps({"citations": n, "updated": datetime.date.today().isoformat()}, indent=2) + "\n"
)
print(f"wrote {n} citations")
