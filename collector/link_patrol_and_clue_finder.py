# -*- coding: utf-8 -*-
"""
官方原文链接失效巡检 & 待获取线索自动检索脚本 (V5.2)
用法：
  1. 离线自检（导出待巡检官链与24条待获取线索检索任务表）：
     python3 collector/link_patrol_and_clue_finder.py
  2. 真实联网巡检全部官链 HTTP 状态（生成 link_health_report.json，可直接导入网页「自动采集中心」）：
     python3 collector/link_patrol_and_clue_finder.py --live --delay 0.5
"""
import argparse
import json
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATASET_PATH = ROOT / "数据源/v5_full_dataset.json"
OUT_REPORT = ROOT / "collector/link_health_report.json"


def check_url(url: str, timeout: int = 10) -> tuple[str, bool, str]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (AI-Edu-Policy-LinkPatrol/5.2)"},
        method="HEAD",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = getattr(resp, "status", 200)
            final_url = resp.geturl()
            if final_url != url:
                return f"HTTP {code} (跳转)", True, final_url
            return f"HTTP {code}", True, final_url
    except urllib.error.HTTPError as e:
        if e.code in (405, 403):
            # Fallback to GET if HEAD is disallowed
            try:
                req_get = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req_get, timeout=timeout) as resp2:
                    return f"HTTP {getattr(resp2, 'status', 200)}", True, resp2.geturl()
            except Exception as e2:
                return f"ERR {e2}", False, ""
        return f"HTTP {e.code}", False, ""
    except Exception as e:
        return f"TIMEOUT/ERR: {type(e).__name__}", False, ""


def main():
    parser = argparse.ArgumentParser(description="官链失效巡检与待获取线索补全助手 V5.2")
    parser.add_argument("--live", action="store_true", help="开启真实联网 HTTP 状态巡检")
    parser.add_argument("--delay", type=float, default=0.4, help="每次请求间隔秒数")
    args = parser.parse_args()

    ds = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    recs = ds["records"]
    clues = [r for r in recs if "线索" in str(r.get("资料类别", ""))]
    urls = [r for r in recs if str(r.get("官方原文URL", "")).startswith("http")]

    ok_cnt = 0
    broken_items = []
    warn_cnt = 0

    if args.live:
        for r in urls:
            status, ok, final_u = check_url(r["官方原文URL"])
            if ok:
                ok_cnt += 1
                if "跳转" in status:
                    warn_cnt += 1
            else:
                broken_items.append({
                    "id": r.get("_id"),
                    "province": r.get("省份"),
                    "title": r.get("文件标题"),
                    "url": r["官方原文URL"],
                    "status": status,
                })
            time.sleep(args.delay)
    else:
        ok_cnt = len(urls)
        warn_cnt = len(recs) - len(urls)

    report = {
        "checked_at": datetime.now().isoformat(timespec="seconds"),
        "mode": "LIVE" if args.live else "DRY_RUN",
        "summary": {
            "total_records": len(recs),
            "checked_urls": len(urls),
            "ok": ok_cnt,
            "broken": len(broken_items),
            "redirect_or_warn": warn_cnt,
            "pending_clues": len(clues),
        },
        "broken_items": broken_items,
        "clue_queries": [
            {
                "province": c.get("省份"),
                "title": c.get("文件标题"),
                "status": c.get("政策状态"),
                "suggested_query": f"{c.get('省份','')} {c.get('文件标题','')} site:gov.cn",
            }
            for c in clues
        ],
    }
    OUT_REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[{report['mode']}] 巡检官链: {len(urls)} 条 | 正常: {ok_cnt} | 失效: {len(broken_items)} | 待补全线索: {len(clues)} 条 -> {OUT_REPORT.name}")


if __name__ == "__main__":
    main()
