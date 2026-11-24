@echo off
chcp 65001 >nul
echo 正在注册 Windows 每周一 08:00 自动采集任务...
schtasks /Create /TN "AI_Edu_Policy_AutoCollect" /TR "cmd /c cd /d %~dp0.. && python collector\auto_collector.py --config collector\sources_config.json --live" /SC WEEKLY /D MON /ST 08:00 /F
pause
