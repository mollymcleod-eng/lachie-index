import json, pathlib, sys

tpl = pathlib.Path("lachie.template.html").read_text(encoding="utf-8")
tides = pathlib.Path("tides.json").read_text(encoding="utf-8")

assert "__TIDE_DATA__" in tpl, "placeholder missing"
# Embed as a JS string literal containing the JSON payload.
out = tpl.replace("__TIDE_DATA__", json.dumps(tides))

dest = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "Lachie-Index.html")
dest.write_text(out, encoding="utf-8")
print(f"wrote {dest}  ({len(out)/1024:.1f} KB)")
