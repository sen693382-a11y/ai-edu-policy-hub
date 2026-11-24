#!/usr/bin/env bash
# 每周一 08:00 自动执行五地人工智能教育政策增量采集
(crontab -l 2>/dev/null; echo "0 8 * * 1 cd $(cd "$(dirname "$0")/.." && pwd) && python3 collector/auto_collector.py --config collector/sources_config.json --live >> collector/collect.log 2>&1") | crontab -
echo "已注册每周一 08:00 Cron 自动采集任务"
