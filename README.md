# 人工智能教育政策资料库 V5.0（完整离线 + 零服务器云端部署包）

本压缩包已完整整合**全国五地（北京、上海、江苏、浙江、广东）全部政策原始文件**、五地总表、V5.0 交互式网页应用，以及面向 **GitHub Actions + GitHub Pages** 的零服务器自动采集与在线发布流水线。

## 一、目录结构

| 目录 / 文件 | 说明 |
|---|---|
| `index.html` | V5.0 主界面（双击即可离线使用，包含全文检索定位、8 维度横向对比、自动采集中心与 AI 文献综述助手） |
| `政策原始文件/` | 北京、上海、江苏、浙江、广东五地全部政策原始文件（PDF / DOCX / DOC / HTML） |
| `人工智能教育政策资料库·五地总表.xlsx` | 五地政策汇总 Excel 总表 |
| `数据源/` | `v5_full_dataset.json`（含 162 条记录与 11,610 段全文索引）及原始配置 JSON |
| `collector/` | `auto_collector.py`（官方信源自动采集器）、`build_html_v5.py`（网页重建器）、`sources_config.json`（17 个官方监控站点）与定时任务脚本 |
| `ai_assistant/` | `ai_review_cli.py`（命令行版 AI 综述生成与引用核验工具） |
| `.github/workflows/auto_collect_and_deploy.yml` | GitHub Actions 自动定时采集 + GitHub Pages 一键发布工作流 |
| `报告文档/` & `清单与归档/` | 项目历次核验与整理过程文档 |

## 二、零服务器免费云端部署（GitHub Actions + GitHub Pages，约 3 分钟）

1. **新建 GitHub 仓库**：登录 GitHub，新建一个 **Public（公开）** 仓库（例如 `ai-edu-policy-hub`）。
2. **推送本目录全部文件**：解压本包后，在解压目录内执行：
   ```bash
   git init
   git add .
   git commit -m "feat: 初始化人工智能教育政策资料库 V5.0"
   git branch -M main
   git remote add origin https://github.com/<你的用户名>/<仓库名>.git
   git push -u origin main
   ```
3. **开启 GitHub Pages 与 Actions 写权限**：
   - 进入仓库 **Settings → Pages**，将 **Build and deployment → Source** 设为 **GitHub Actions**。
   - 进入 **Settings → Actions → General → Workflow permissions**，勾选 **Read and write permissions** 并保存。
4. **完成**：GitHub 将自动运行首次构建并生成在线访问链接（`https://<你的用户名>.github.io/<仓库名>/`），此后**每周一北京时间 08:00** 自动巡检五地官方站点增量采集新政策、重建全文索引并更新网页；你也可以随时在 **Actions** 页面点击 **Run workflow** 手动触发。

## 三、本地离线使用

无需任何服务器或环境配置，直接双击 `index.html` 即可在浏览器中使用全部四大功能。
