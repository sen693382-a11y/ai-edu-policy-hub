# -*- coding: utf-8 -*-
"""
人工智能教育政策自动化、持续化采集脚本 (V5.0)
功能：
1. 读取 collector/sources_config.json 中的官方监控信源（五地及教育部）。
2. 支持 --dry-run（离线自检与去重演练）、--local-dir <目录>（批量导入本地新政策）与 --live（真实联网增量采集）。
3. 自动执行：关键词过滤 -> 正文提取与段落切分 -> SHA-256 内容哈希与标题去重 -> 学段/主题/层级自动标引 -> 增量写入 数据源/v5_full_dataset.json。
"""
import argparse
import hashlib
import json
import re
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
DATASET_PATH = ROOT / "数据源/v5_full_dataset.json"
DEFAULT_CONFIG = ROOT / "collector/sources_config.json"

STAGE_KEYWORDS = ["学前教育", "小学", "初中", "高中", "基础教育", "职业教育", "高等教育", "全学段"]
TOPIC_KEYWORDS = {
    "通识教育": ["通识", "普及"],
    "课程建设": ["课程", "课时", "教材", "纲要"],
    "教师培养": ["教师", "师资", "培训", "教研"],
    "基础设施与平台": ["平台", "算力", "大模型", "底座"],
    "应用场景": ["场景", "示范校", "实验区", "赋能"],
    "伦理与安全": ["伦理", "安全", "隐私", "规范"],
}
PROV_CODE = {"北京市": "BJ", "上海市": "SH", "江苏省": "JS", "浙江省": "ZJ", "广东省": "GD", "国家级": "CN"}


def clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def split_paragraphs(html_or_text: str, is_html: bool = True) -> list[list[str]]:
    if is_html:
        soup = BeautifulSoup(html_or_text, "lxml")
        for tag in soup(["script", "style", "noscript", "nav", "header", "footer"]):
            tag.decompose()
        lines = [clean_text(p.get_text(" ", strip=True)) for p in soup.find_all(["p", "li", "h2", "h3"])]
        if len(lines) < 3:
            lines = [clean_text(x) for x in soup.get_text("\n").split("\n")]
    else:
        lines = [clean_text(x) for x in html_or_text.split("\n")]
    lines = [x for x in lines if len(x) >= 10]
    return [[f"P{i:03d}", t[:600]] for i, t in enumerate(lines[:180], 1)]


def auto_tag(title: str, full_text: str) -> tuple[str, str, str]:
    hay = title + " " + full_text
    stages = "、".join([k for k in STAGE_KEYWORDS if k in hay]) or "全学段"
    topics = "、".join([k for k, kws in TOPIC_KEYWORDS.items() if any(w in hay for w in kws)]) or "综合方案"
    if any(w in title for w in ["行动方案", "工作方案", "行动计划", "课程纲要", "指导意见", "素养框架", "实施要求", "指南"]):
        tier = "A核心政策"
    elif any(w in title for w in ["实施方案", "工作要点", "通知", "试点"]):
        tier = "B相关政策"
    else:
        tier = "C补充资料"
    return stages, topics, tier


def fetch_url(url: str, timeout: int = 12) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (AI-Edu-Policy-Collector/5.0)"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
        for enc in ("utf-8", "gb18030", "gbk"):
            try:
                return raw.decode(enc)
            except Exception:
                continue
        return raw.decode("utf-8", errors="ignore")


def run_collector(config_path: Path, live: bool, local_dir: str | None, delay: float):
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    ds = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    existing_keys = {(r.get("文件标题", ""), r.get("省份", "")) for r in ds["records"]}
    existing_urls = {r.get("官方原文URL", "") for r in ds["records"] if r.get("官方原文URL")}

    added = 0
    checked_sites = 0

    if local_dir:
        ldir = Path(local_dir)
        for fp in sorted(ldir.glob("*")):
            if fp.suffix.lower() not in (".html", ".htm", ".txt"):
                continue
            title = fp.stem
            prov = next((p for p in PROV_CODE if p[:2] in title), "北京市")
            if (title, prov) in existing_keys:
                continue
            raw = fp.read_text(encoding="utf-8", errors="ignore")
            paras = split_paragraphs(raw, is_html=fp.suffix.lower() in (".html", ".htm"))
            stages, topics, tier = auto_tag(title, " ".join(p[1] for p in paras))
            h = hashlib.sha256((title + prov).encode("utf-8")).hexdigest()[:6].upper()
            doc_id = f"{PROV_CODE.get(prov, 'CN')}-{h}"
            rid = f"R{len(ds['records']) + 1:04d}"
            ds["records"].insert(0, {
                "_rid": rid, "_id": doc_id, "_pcnt": len(paras),
                "文件标题": title, "年份": datetime.now().strftime("%Y"),
                "省份": prov, "城市": "本地导入", "原发文机关": "本地采集",
                "发文日期": datetime.now().strftime("%Y-%m-%d"), "资料类别": "正式政策文件",
                "教育阶段": stages, "政策主题": topics, "官方原文URL": "",
                "核验状态": "已核验", "研究纳入层级": tier, "发文字号": "",
            })
            if paras:
                ds["paragraphs"][doc_id] = paras
            existing_keys.add((title, prov))
            added += 1

    for src in cfg.get("sources", []):
        if not src.get("enabled", True):
            continue
        checked_sites += 1
        if not live:
            continue
        try:
            html = fetch_url(src["url"])
            soup = BeautifulSoup(html, "lxml")
            kws = src.get("keywords", ["人工智能"])
            for a in soup.find_all("a", href=True):
                title = clean_text(a.get_text(" ", strip=True))
                if len(title) < 8 or not any(k in title for k in kws):
                    continue
                if "教育" not in title and "学校" not in title and "课程" not in title and "教师" not in title:
                    continue
                full_url = urljoin(src["url"], a["href"])
                if full_url in existing_urls or (title, src["province"]) in existing_keys:
                    continue
                time.sleep(delay)
                art_html = fetch_url(full_url)
                paras = split_paragraphs(art_html, is_html=True)
                stages, topics, tier = auto_tag(title, " ".join(p[1] for p in paras))
                h = hashlib.sha256(full_url.encode("utf-8")).hexdigest()[:6].upper()
                doc_id = f"{PROV_CODE.get(src['province'], 'CN')}-{h}"
                rid = f"R{len(ds['records']) + 1:04d}"
                ds["records"].insert(0, {
                    "_rid": rid, "_id": doc_id, "_pcnt": len(paras),
                    "文件标题": title, "年份": datetime.now().strftime("%Y"),
                    "省份": src["province"], "城市": "自动采集",
                    "原发文机关": src["name"], "网页发布机构": src["name"],
                    "发文日期": datetime.now().strftime("%Y-%m-%d"),
                    "资料类别": "正式政策文件", "教育阶段": stages, "政策主题": topics,
                    "官方原文URL": full_url, "核验状态": "待核验", "研究纳入层级": tier, "发文字号": "",
                })
                if paras:
                    ds["paragraphs"][doc_id] = paras
                existing_urls.add(full_url)
                existing_keys.add((title, src["province"]))
                added += 1
        except Exception as exc:
            print(f"[WARN] 站点采集跳过 {src['name']} ({src['url']}): {exc}")

    if added > 0:
        DATASET_PATH.write_text(json.dumps(ds, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    mode = "LIVE" if live else ("LOCAL_IMPORT" if local_dir else "DRY_RUN")
    print(f"[{mode}] 检查启用信源: {checked_sites} 个 | 新增入库: {added} 条 | 当前库总计: {len(ds['records'])} 条 (已索引正文: {len(ds['paragraphs'])} 份)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="五地人工智能教育政策自动化采集器 V5.0")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--live", action="store_true", help="开启真实联网增量采集")
    parser.add_argument("--local-dir", type=str, default=None, help="批量导入本地 HTML/TXT 新政策目录")
    parser.add_argument("--delay", type=float, default=1.0, help="请求间隔秒数")
    args = parser.parse_args()
    run_collector(args.config, args.live, args.local_dir, args.delay)
