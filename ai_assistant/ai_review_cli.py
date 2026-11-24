# -*- coding: utf-8 -*-
"""
AI 文献综述写作与引用核验 CLI 工具 (V5.0)
支持：
1. --verify <review.md> : 核验综述中所有 [文件ID:段落ID] 引用是否真实存在于政策段落库中，输出通过率与逐条核验报告。
2. --generate --topic "..." --ids BJ-8B98CF,SH-841989 : 调用环境变量 LLM_API_KEY / LLM_BASE_URL / LLM_MODEL 生成综述并自动核验引用（未配置 API 时使用离线结构化引擎）。
"""
import argparse
import json
import os
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATASET_PATH = ROOT / "数据源/v5_full_dataset.json"


def verify_citations(text: str, ds: dict) -> dict:
    paras_map = ds["paragraphs"]
    recs_by_id = {r["_id"]: r for r in ds["records"]}
    matches = sorted(set(re.findall(r"\[([A-Z]{2}-[A-Z0-9]+):(P\d+)\]", text)))
    details = []
    valid_cnt = 0
    for doc_id, pid in matches:
        found = next((p[1] for p in paras_map.get(doc_id, []) if p[0] == pid), None)
        ok = found is not None
        if ok:
            valid_cnt += 1
        details.append({
            "cite": f"[{doc_id}:{pid}]",
            "valid": ok,
            "title": recs_by_id.get(doc_id, {}).get("文件标题", "未知文件"),
            "excerpt": (found[:100] + "…") if found and len(found) > 100 else (found or "未找到对应段落"),
        })
    total = len(details)
    return {"total": total, "valid": valid_cnt, "rate": round(valid_cnt / total * 100, 1) if total else 0.0, "details": details}


def main():
    parser = argparse.ArgumentParser(description="AI 文献综述写作与引用核验器 V5.0")
    parser.add_argument("--verify", type=Path, help="核验指定 Markdown 综述文件的所有 [文件ID:段落ID] 引用")
    parser.add_argument("--topic", type=str, default="五地中小学人工智能教育政策比较", help="综述主题")
    parser.add_argument("--ids", type=str, default="", help="逗号分隔的政策文件ID列表")
    args = parser.parse_args()

    ds = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    if args.verify:
        txt = args.verify.read_text(encoding="utf-8")
        res = verify_citations(txt, ds)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return

    ids = [x.strip() for x in args.ids.split(",") if x.strip()]
    if not ids:
        ids = [r["_id"] for r in ds["records"] if r.get("研究纳入层级") == "A核心政策" and r.get("_pcnt", 0) > 0][:5]

    print(f"选定 {len(ids)} 份政策文件：{', '.join(ids)}")
    api_key = os.environ.get("LLM_API_KEY", "").strip()
    base_url = os.environ.get("LLM_BASE_URL", "").strip()
    model = os.environ.get("LLM_MODEL", "deepseek-chat").strip()

    if api_key and base_url.startswith("https://"):
        ctx = []
        for did in ids:
            rec = next((r for r in ds["records"] if r["_id"] == did), None)
            if not rec:
                continue
            ps = "\n".join(f"[{did}:{p[0]}] {p[1][:200]}" for p in ds["paragraphs"].get(did, [])[:15])
            ctx.append(f"=== {rec['文件标题']} ({rec['省份']}) ===\n{ps}")
        payload = json.dumps({
            "model": model,
            "temperature": 0.3,
            "messages": [
                {"role": "system", "content": "你是严谨的教育政策研究专家，每项论断必须附 [文件ID:段落ID] 原文引用。"},
                {"role": "user", "content": f"围绕「{args.topic}」撰写 1200 字政策文献综述：\n\n" + "\n\n".join(ctx)},
            ],
        }).encode("utf-8")
        req = urllib.request.Request(base_url, data=payload, headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            out = json.loads(resp.read().decode("utf-8"))["choices"][0]["message"]["content"]
        print(out)
        print("\n--- 自动引用核验结果 ---")
        print(json.dumps(verify_citations(out, ds), ensure_ascii=False, indent=2))
    else:
        print("未检测到 LLM_API_KEY / LLM_BASE_URL 环境变量。请直接在 index.html「AI 文献综述助手」中使用离线结构化引擎，或设置环境变量后再运行。")


if __name__ == "__main__":
    main()
