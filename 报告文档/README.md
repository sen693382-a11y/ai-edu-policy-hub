# JZ-AIEdu｜人工智能教育政策资料库（五地）

> **当前交付：V4.3 江苏浙江研究范围规范化 + 研究纳入层级筛选（2026-11-21）。**
> 覆盖北京、上海、江苏、浙江、广东五地。在四类资料之外**新增独立字段「研究纳入层级」**：A核心/B相关/C补充/待人工确认，
> 本轮仅复核江苏、浙江；京沪粤标「未复核（京沪粤）」，**不代表非核心政策**，勿据此做五地分级对比。
> AI 综述助手模块已冻结（代码保留、按钮停用），本轮 API 调用 0 次。
> 早期阶段的 `backend/`、`scripts/`、`tests/`、`data/policy_hub.db` 保留为历史记录，**不再运行、不再扩展**。

## 三个交付物（直接可用）

| 文件 | 说明 |
|---|---|
| `人工智能教育政策资料库·五地总表.xlsx` | 工作表1「政策资料总表」175 条（五地，含研究纳入层级等新列）；另有「采集汇总」「检索覆盖表」「待获取原文的政策线索」「逐条分级明细」「江苏浙江核心政策清单」「待补齐原文」 |
| `index.html` | 双击即可本地打开；省级地区筛选（五地）+ 关键词/年份/类别/教育阶段/主题/核验状态 + **研究纳入层级（仅苏浙）**；无筛选时分页（20 条/页） |
| `政策原始文件/` | 五地政策原始文件；北京/上海/广东新增资料位于同名子目录 |

**V4.3 苏浙范围调整**：江苏 72 + 浙江 65 = 137 条逐条复核 → A核心 9（去重后独立 **7 份**：江苏3、浙江4）、B相关 11、C补充 106、待人工确认 11；
识别新闻误列为正式政策 10 条、重复来源 6 条。真正的苏浙核心样本仅 7 份（2024–2025 年、省级+泰州/绍兴），
2023/2026 年与多数地市存在缺口。逐条分级见 `collect/v43_js_zj_tiers.json`，报告见 `V4.1_江苏浙江资料研究范围调整报告.md`。

**V4.2 实测结果**：五地合计 **175 条**（江苏 72 · 浙江 65 · 北京 20 · 上海 10 · 广东 8）；
其中前三类政策 150 条、第四类政策线索 24 条、随包辅助清单 1 条（后两类默认隐藏、不计入正式政策）。
已核验 136 / 待核验 14（线索与辅助材料单列）。北京 19 条随包 URL 全部 HTTP 200；上海 10、广东 8 条逐条检索官方出处并补齐 36 条 URL。
新增三地 37 条中已核验 36、待核验 1（教育部通知：官网仅有新闻稿，无原文页）。
省级筛选、类别/年份/关键词/主题/阶段/状态筛选、分页与重置均经 Chrome 无头实测通过。
详见 `V4.0_五地资料整合与筛选调整报告.md` 与 `V4.1_联网复核与分页功能报告.md`。

## 复现命令

```bat
python collect\collect_policy.py --sources collect\sources_v31.json --out collect\records_v31.json --delay 0.8  :: 重新真实采集（需网络）
python collect\build_outputs_v31.py                                                                              :: 复核 + 重新生成 Excel/HTML/正文副本
```

采集源清单 `collect/sources_v31.json`；逐条字段与证据 `collect/records_v31.json`；
人工纠错裁定 `collect/review_overrides.json`；覆盖表 `collect/coverage_v31.json`。

---

<details>
<summary>历史阶段（V1.0/V2.0，已停用，仅供追溯）</summary>

旧版含 SQLite schema v6、迁移、API、2A 官方来源核验、2B 离线采集模块与 99 项测试；
相关代码在 `backend/`、`scripts/`、`tests/`，文档在 `docs/`。按 V3.0 方向不再维护。

</details>

---

## 1. 本机启动（Windows）

| 步骤 | 操作 | 说明 |
|---|---|---|
| 首次 | 双击 `setup.bat` | 创建 `.venv`、安装依赖、初始化数据库、跑测试 |
| 每次 | 双击 `start.bat` | 初始化/增量迁移后启动本地服务 |
| 浏览 | 打开 `http://127.0.0.1:8765/` | 首页列出可用接口；API 交互文档在 `/docs` |

命令行等价（PowerShell）：

```powershell
$py = "C:\Users\Sen\.workbuddy\binaries\python\versions\3.13.12\python.exe"
& $py -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe scripts\init_db.py
& .\.venv\Scripts\python.exe scripts\run_tests.py
& .\.venv\Scripts\python.exe scripts\serve.py
```

断网 / 未装依赖时仍可运行（核心数据层零第三方依赖）：

```powershell
& $py scripts\init_db.py
& $py scripts\run_tests.py
& $py scripts\serve.py --stdlib     # 标准库 HTTP 适配器
```

服务默认只监听 `127.0.0.1:8765`，脚本会拒绝其他绑定地址。

---

## 2. 项目结构

```
JZ-AIEdu-Policy-Hub/
├── backend/
│   ├── config.py                      # 路径、schema 目标版本、监听地址
│   ├── db/
│   │   ├── connection.py              # SQLite 连接（外键 ON / WAL / Row 工厂）
│   │   ├── migrations.py              # 版本迁移执行器（sha256 校验 + 事务）
│   │   └── migrations/                # 001 核心表 / 002 FTS5 / 003 统计视图 / 004 P0 触发器
│   ├── models/                        # 模型说明（结构以 SQL 迁移为准）
│   ├── repositories/
│   │   ├── base.py                    # 字典校验、审核日志、sha256
│   │   ├── policy_repo.py             # 政策实体、多标签、版本、正式政策计数
│   │   ├── resource_repo.py           # 中文检索、多维筛选、统计、去重、导出
│   │   └── catalog_repo.py            # 地区、字典、来源站点、覆盖状态、任务日志
│   ├── services/
│   │   ├── seed.py                    # 26 地区 / 85 字典项 / 55 站点 / 104 覆盖记录
│   │   └── verification.py            # P0 来源核验服务（含人工导入）
│   └── api/
│       ├── router.py                  # 框架无关的 API 分发（参数化 SQL + HTML 转义）
│       ├── fastapi_app.py             # FastAPI / uvicorn 适配器
│       └── server.py                  # 零依赖标准库 HTTP 适配器
├── data/
│   ├── regions.json                   # 26 个行政检索单位（GB/T 2260 代码）
│   ├── dictionaries.json              # 分类与状态字典
│   ├── source_sites.json              # 官方来源登记表 + 用户提供的 3 条测试 URL
│   ├── test_fixtures.json             # 独立合成测试数据（.invalid 域）
│   └── policy_hub.db                  # 生产库（初始化生成）
├── storage/attachments/               # 附件与 backups/
├── scripts/                           # init_db / run_tests / serve / smoke_api / backup_db / check_env
├── tests/                             # 49 项自动化测试
├── docs/                              # 结构说明、测试报告、来源登记、已知问题
├── frontend/                          # 阶段三占位（当前为空）
├── requirements.txt
├── setup.bat / start.bat / test.bat
└── README.md
```

---

## 3. 阶段一实现清单

| PRD 阶段一任务 | 代码位置 | 实际验证 |
|---|---|---|
| 初始化前后端项目、本地环境 | `requirements.txt`、`setup.bat`、`.venv` | 依赖安装成功（exit 0） |
| SQLite + 版本迁移机制 | `backend/db/migrations.py`、`migrations/001~004.sql` | v1→v3 首次应用、v4 增量应用；重复迁移不重跑；篡改校验值被拦截 |
| PRD 核心数据表 | `migrations/001_init.sql` | 17 张表 + 5 个视图，外键开启 |
| 26 个行政检索单位 | `data/regions.json` → `seed.py` | 2 省 + 24 市，代码集合精确匹配 |
| 三类资料字典 | `data/dictionaries.json` | 正式政策 / 官方解读 / 官方动态 / 征求意见稿 |
| 教育阶段、方向、主题、文件形式字典 | 同上 | 85 个字典项、18 个可多标签 tag |
| 基础读写、审核状态、来源记录 | `repositories/*`、`services/verification.py` | 49 项测试 |
| 独立测试数据与自动化测试 | `data/test_fixtures.json`、`tests/`、`scripts/run_tests.py` | unittest 49/49、pytest 49/49 |
| API 基础框架 | `backend/api/*` | 12 项真实 HTTP 冒烟检查全部通过 |
| 数据表结构说明 | `docs/数据库结构说明.md` | — |
| 地区与分类配置文件 | `data/*.json` | — |
| 第一阶段测试报告 | `docs/第一阶段测试报告.md` | — |

## 3b. 阶段二进度（2A 完成 / 2B 离线部分完成）

| 子阶段 | 状态 | 交付物 |
|---|---|---|
| 2A 官方来源核验 | 完成 | 8 条已确认江苏省设区市教育局来源；`docs/2A_阶段报告.md`、`docs/2A_已确认来源清单.md`、`docs/2A_来源覆盖表.csv` |
| 2B 采集模块 | 完成（离线可测部分） | `backend/services/collector/`、`scripts/collect.py`、`docs/2B_阶段报告.md`、`docs/2B_离线采集结果.json` |
| 2B 真实网络采集 | **未执行** | 批量网络访问被拒绝，未重试/绕行；需用户重新授权后小批次进行 |
| 2C 真实性/去重/分类 | 未开始 | — |
| 2D 扩大检索与覆盖 | 部分准备 | 检索计划已生成（832 任务），真实覆盖报告待采集后更新 |

---

## 4. 新增 P0「来源溯源与真实性」落地方式

| 要求 | 实现 |
|---|---|
| 必备溯源字段 | `resource` 表含 `source_url / final_url / source_agency / original_issuer / source_type / published_date / verified_at / verification_status / attachment_urls_json / local_copy_path / content_hash` |
| 禁止 AI 编造政策与链接 | 生产库零政策、零资料；每条已确认来源必须有实际访问 URL、页面机构证据、独立依据、快照与哈希；未核实来源 `base_url` 为 NULL |
| 无法核实 → 待核验 | 默认 `verification_status='pending'`；`v_formal_policy` 只计入已核验 + 已审核 + 非草案 + 有正式原文的资料 |
| HTTP 200 ≠ 已核验 | 必须存在 `source_check` 的 `passed` 记录，且 HTTP 2xx + 标题/发文机关/日期/正文四项比对全部通过 |
| 人工导入同样受约束 | 采集与人工导入共用 `insert_resource` + `mark_resource_verified`；**数据库层 4 个触发器**兜底，绕过 API 直接改库也会被拒绝 |
| 保留原始与跳转 URL | `source_url` 与 `final_url` 分列；无跳转时由核验记录提供实际 URL，绝不编造替代链接 |
| 导出保留来源与状态 | `/api/export`、`/api/export.csv` 固定包含 `source_url / final_url / verification_status / verified_at` |
| 官方转载不生成新政策 | 转载作为 `Resource` 关联既有 `Policy`；去重队列 `duplicate_candidate` 只标记不自动合并 |
| 前端「查看官方原文」 | 阶段三实现；阶段一详情接口已返回 `official_link / link_dead / has_local_copy` |
| AI 摘要需原文证据 | 阶段一未接入任何大模型；`source_check` + `content_hash` 为未来证据链预留 |

---

## 5. 三种统计口径（严格区分）

| 口径 | 定义 | 当前生产库 |
|---|---|---|
| 独立正式政策数量 | `v_formal_policy` 中 Policy 实体去重计数 | 0 |
| 资料记录数量 | `resource` 表行数（含原文、转载、解读、动态） | 0 |
| 标签出现次数 | `policy_tag` + `resource_tag` 行数 | 0 |

---

## 6. 常用命令

| 目的 | 命令 |
|---|---|
| 环境自检（含官方站点可达性） | `python scripts/check_env.py` |
| 初始化 / 增量迁移 | `python scripts/init_db.py` |
| 只看结构不动数据 | `python scripts/init_db.py --check` |
| 重建数据库（危险） | `python scripts/init_db.py --force-reset` |
| 跑测试（标准库） | `python scripts/run_tests.py` |
| 跑测试（pytest） | `.venv\Scripts\python.exe -m pytest tests -q` |
| HTTP 冒烟测试 | `.venv\Scripts\python.exe scripts\smoke_api.py` |
| 启动服务 | `python scripts/serve.py` |
| 备份 | `python scripts/backup_db.py --backup` |
| 校验完整性 | `python scripts/backup_db.py --verify` |
| 恢复 | `python scripts/backup_db.py --restore storage/backups/xxx.db`（会先自动备份当前库） |
| 2B 离线夹具采集（零网络、临时库） | `python scripts/collect.py --offline` |
| 生成 2B 检索计划（只读生产库） | `python scripts/collect.py --plan` |
| 真实网络采集（**需显式授权**） | `python scripts/collect.py --live --authorize-network` |

---

## 7. 真实 / 测试数据隔离

1. **物理隔离**：所有测试在 `tempfile.TemporaryDirectory()` 中的独立 SQLite 文件运行，用后即删；冒烟测试同样用临时库。
2. **种子隔离**：`scripts/init_db.py` 只调用 `seed_all()`，绝不加载 `data/test_fixtures.json`；种子硬断言 `policy=0, resource=0`。
3. **逻辑隔离**：`data_origin` 字段（`UNSPECIFIED / REAL / TEST`），标记 `TEST` 的记录永远不能核验通过。
4. **可识别性**：合成标题带 `【测试数据·非真实政策】`，所有测试 URL 使用 RFC 2606 保留域 `.invalid`；`content_hash` 按真实正文计算 sha256，不写占位值。

---

## 8. 当前真实数据与未完成范围

| 项目 | 状态 |
|---|---|
| 真实政策 / 资料 | **0 / 0**（阶段二才开始采集） |
| 已核验来源 | 0；`source_site` 55 条全部 `待核验` |
| 覆盖状态 | 26 单位 × 4 年度（2023–2026）= 104 条，全部「未检索」 |
| 官方站点可达性 | 环境自检实测 `jyt.jiangsu.gov.cn`、`edu.nanjing.gov.cn`、`www.zjzs.net` 均 HTTP 200 |
| 阶段二待办 | 待授权后实地采集 3 条用户文章 URL；2A 已建白名单（8 条），2B 已建提取/附件/证据模块；2C 去重与分类、2D 覆盖报告待做 |
| 阶段三待办 | 6 个前端页面（首页 / 资料库 / 详情 / 时间轴 / 双政策比较 / 管理后台） |
| 阶段四待办 | 联调、备份恢复演练、Windows 全流程、正式交付报告 |

> 三条用户提供的测试地址记录在 `data/source_sites.json` 的 `provided_article_urls`，
> 全部标注「用户提供，未核验」，阶段一未写入数据库、未计入任何统计。

---

## 9. 文档索引

- `docs/项目结构说明.md` — 目录设计与前后端职责边界
- `docs/数据库结构说明.md` — 20 张表、8 个视图、字段与约束（schema v6）
- `docs/官方数据来源登记表.md` — 55 条登记项与可信度状态
- `docs/第一阶段测试报告.md` — 实际运行的测试与结果
- `docs/2A_阶段报告.md`、`docs/2A_已确认来源清单.md`、`docs/2A_来源覆盖表.csv` — 官方来源核验
- `docs/2B_阶段报告.md`、`docs/2B_离线采集结果.json`、`docs/2B_检索计划.json` — 采集模块与离线证据
- `docs/2B_回归校验.txt`、`docs/2B_核验摘要.json` — 阶段二回归记录
- `docs/已知问题清单.md` — 限制与风险
- `docs/env_check.json`、`docs/init_db_result.json`、`docs/test_results.json`、
  `docs/api_smoke_result.json`、`docs/pytest_run.log`、`docs/_final_verify_exit.txt` — 机器生成的原始证据
  （最后一项为交付前全套复验：初始化检查 / unittest / pytest / HTTP 冒烟 / 备份校验，退出码全为 0）
