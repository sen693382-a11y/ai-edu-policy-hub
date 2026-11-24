# -*- coding: utf-8 -*-
"""
Rebuild root index.html from 数据源/v5_full_dataset.json, collector/sources_config.json,
and collector/app_v5_template.html.
Designed to run automatically inside GitHub Actions after collector/auto_collector.py.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATASET = ROOT / "数据源/v5_full_dataset.json"
SOURCES = ROOT / "collector/sources_config.json"
TEMPLATE = ROOT / "collector/app_v5_template.html"
OUT_HTML = ROOT / "index.html"


def main():
    ds = json.loads(DATASET.read_text(encoding="utf-8"))
    for idx, rec in enumerate(ds["records"], 1):
        if not rec.get("_rid"):
            rec["_rid"] = f"R{idx:04d}"

    src_cfg = json.loads(SOURCES.read_text(encoding="utf-8"))
    sources = src_cfg.get("sources", src_cfg) if isinstance(src_cfg, dict) else src_cfg

    tpl = TEMPLATE.read_text(encoding="utf-8")
    v5_json = json.dumps(
        {"records": ds["records"], "paragraphs": ds["paragraphs"]},
        ensure_ascii=False,
        separators=(",", ":"),
    ).replace("</script>", "<\\/script>")
    src_json = json.dumps(
        sources, ensure_ascii=False, separators=(",", ":")
    ).replace("</script>", "<\\/script>")

    html = tpl.replace("__V5_DATA__", v5_json).replace("__INITIAL_SOURCES__", src_json)
    assert "__V5_DATA__" not in html and "__INITIAL_SOURCES__" not in html
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"[BUILD_HTML] Rebuilt {OUT_HTML.name} ({OUT_HTML.stat().st_size / 1024 / 1024:.2f} MB) | records={len(ds['records'])} | indexed_docs={len(ds['paragraphs'])}")


if __name__ == "__main__":
    main()
