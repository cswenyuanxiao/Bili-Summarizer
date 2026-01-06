# Changelog

Last updated: 2026-01-05  
Owner: Core Eng

## [2.3.4] - 2026-01-05

### Added
- **撒花特效**：总结完成时触发视觉反馈。
- **词云可视化**：基于关键词权重渲染词云面板。
- **手气不错**：一键填充精选视频链接，解决冷启动。
- **成就徽章**：本地记录四类轻量成就并展示在 Dashboard。

### Changed
- **总结 Prompt**：新增关键词 JSON 输出要求。
- **UI 视觉规范**：输入区与图标使用统一尺寸与 Heroicons，禁止 emoji 功能图标。

### Documentation
- 更新 `docs/API_REFERENCE.md` 的 usage 关键字段

## [2.3.5] - 2026-01-05

### Added
- **抖音 Cookie 支持**：通过 `DOUYIN_COOKIE` 传入登录态，提升抖音链接下载成功率。
- **SaveTik 调试模式**：支持截图与 HTML dump（`DOUYIN_SAVETIK_DEBUG`）。

### Changed
- **总结 Prompt**：增强结构化深度解析与概念解释要求，提升内容丰富度。
- **思维导图输出**：强化 Markdown 无序列表格式要求，避免纯文本缩进导致结构丢失。

### Documentation
- 更新 `docs/CONFIGURATION.md` 新增 `DOUYIN_COOKIE`

## [2.3.3] - 2026-01-05

### Fixed
- **思维导图首帧空白**：SVG 未挂载时的渲染时序问题已修复，避免首次渲染丢失。
- **思维导图兜底生成**：当总结中缺失标准列表时，从正文拆句生成最小可渲染脑图。

### Changed
- **总结卡片视觉对齐**：按 notegpt 风格映射字体/颜色/圆角与引用样式。

### Documentation
- 更新 `docs/API_REFERENCE.md` 的请求参数与 mindmap 输出说明

## [2.3.2] - 2026-01-05

### Fixed
- **转录显示偶发为空**：后端聚合 summary + transcript，`summary_complete` 仅在转录就绪后发送，避免前端提前关闭 SSE 丢包。
- **字幕转录解析空**：字幕解析为空时不再提前返回 subtitle 模式，继续下载视频以补齐转录。
- **转录提速**：视频场景下优先抽取轻量音频进行转录，减少上传与转录耗时。

### Changed
- **总结输出风格**：禁止客套开场，要求先给概述后分节输出
- **总结展示样式**：优化排版密度与小标题视觉层级
- **总结布局升级**：新增摘要卡片、要点标签、引用块分区
- **总结卡片规范化**：按“卡片可扫读/层级清晰”原则重构布局

### Documentation
- 更新 `docs/API_REFERENCE.md` 的 SSE 事件说明

## [2.3.1] - 2026-01-05

### Added
- **思维导图升级为 Markmap (✅ 已完成)**：
  - 后端 Prompt 改为输出 Markdown 无序列表
  - 前端使用 Markmap 渲染交互式脑图（缩放/拖拽）

### Documentation
- 整理 docs 目录结构（testing/、diagnostics/）
- 更新文档索引与 CoT 设计链接
- 新增 `docs/AI_CONTEXT.md` 作为统一上下文入口
- 新增 `docs/SESSION_ENTRYPOINT.md` 作为新对话必读入口
- `docs/START_HERE.md` 增加新对话必读硬性规则

## [2.3.0] - 2026-01-04

### Added - AI 能力增强
- **多语言总结输出 (✅ 已完成)**：
  - 后端：`summarizer_gemini.py` 添加语言映射和 Prompt 多语言指令
  - 后端：`main.py` 和 `schemas/summarize.py` 添加 `output_language` 参数
  - 前端：`UrlInputCard.vue` 新增语言选择器（支持中/英/日/韩/西/法）
  - 支持思维导图节点自动翻译为目标语言
  
- **思维链 (CoT) 展示 (✅ 已完成)**：
  - 后端：`summarizer_gemini.py` 添加 `[COT_START]` Prompt 指令和解析逻辑
  - 后端：CoT 数据嵌入 `usage` 字典，保持 API 兼容性
  - Schema：`SummarizeRequest` 添加 `enable_cot` 参数
  - 前端：创建 `CoTPanel.vue` 组件，使用渐进式动画展示分析步骤
  - 前端：`HomePage.vue` 集成并监听 usage 数据

- **图表生成 (✅ 已完成)**：
  - 后端：Prompt 添加 JSON 图表数据生成指令
  - 后端：解析图表 JSON 数据并嵌入 `usage` 字典
  - 前端：安装 `chart.js` 和 `vue-chartjs`
  - 前端：创建 `ChartPanel.vue` 组件，支持 Bar/Line/Pie 图表
  - 前端：`HomePage.vue` 集成图表展示

### Documentation
- 更新 `README.md` v2.3 功能状态（全部标记为已上线）
- 更新 `CHANGELOG.md` 详细记录所有修改
- 更新 `types/api.ts` 添加 CoT 和图表类型定义

---

## [2.1.0] - 2025-12-25

### Added
- **Pro 无限使用功能**：Pro 订阅用户在订阅期内享受无限次总结，积分冻结
  - 后端：`credits.py` 新增 `should_charge_credits()` 检查订阅状态
  - API：Dashboard 返回 `is_pro_active` 标志
  - 前端：显示 `∞` 符号和"Pro 无限使用"提示

### Changed
- **架构重构**：main.py 模块化 (2895 行 → 模块化)
  - 新增 `web_app/routers/` 目录：health, dashboard, templates, share, payments
  - 新增 `web_app/startup/` 目录：db_init.py 异步数据库初始化
  - 新增 `web_app/dependencies.py`：集中管理 FastAPI 依赖注入
  
### Fixed
- **CI/CD 修复**：
  - 修复 CI preflight 健康检查失败（添加启动等待时间）
  - 修复 `requirements.txt` guard 触发问题
  - 修复 videos 目录不存在导致启动失败
- **Render 部署修复**：
  - 修复 502 Bad Gateway（healthCheckPath 路径错误）
  - 修复前端 SPA serving 缺失 index.html 处理
- **API 500 错误修复**：
  - templates.py, payments.py, share.py: 添加缺失的 `verify_session_token` 导入
  - startup/db_init.py: 添加缺失的数据库表（up_subscriptions, summary_templates 等）
  - 修复 `/api/templates`, `/api/payments`, `/api/share`, `/api/subscriptions` 500 错误
- **Supabase RLS 策略**：
  - 更新 summaries 表 INSERT 策略，允许 service_role 和后端 API 插入
- **前端订阅显示**：
  - 修复 DashboardPage.vue 硬编码"免费版"问题，改为动态获取真实订阅状态

### Database
- 新增 5 张表到启动初始化：`up_subscriptions`, `summary_templates`, `idempotency_keys`, `notification_queue`, `push_subscriptions`

---

## [2.0.0] - 2025-12-25

### Added - 阶段 1: 获客增长 (P0-P1)
- **分享卡片生成 (P0)**：`share_card.py` 支持 4 种模板、Pillow 渲染、24h 过期清理
- **收藏夹导入 (P1)**：`favorites.py` 解析 B 站收藏夹 URL，批量导入视频

### Added - 阶段 2: 用户留存 (P2-P3)
- **总结模板自定义 (P2)**：`templates.py` 支持预设模板 + 用户自定义 Prompt
- **语音播报 (P3)**：`tts.py` 集成 Edge TTS，支持多种中文语音

### Added - 阶段 3: 生态建设 (P4-P6)
- **每日推送 (P4)**：
  - `subscriptions.py` UP 主订阅管理
  - `notifications.py` 邮件/浏览器推送
  - `scheduler.py` APScheduler 定时任务
- **总结对比 (P5)**：`compare.py` 支持 2-4 视频 AI 深度对比
- **团队协作 (P6)**：`teams.py` 团队 CRUD、内容共享、评论系统

### Added - 前端
- `TemplatesPage.vue` 模板管理
- `SubscriptionsPage.vue` 订阅与推送
- `ComparePage.vue` 对比实验室
- `TeamsPage.vue` 团队协作
- `AudioPlayer.vue` TTS 播放器
- `ShareCardModal.vue` 分享卡片弹窗
- `FavoritesImportModal.vue` 收藏夹导入
- `HistorySelectModal.vue` 历史选择器
- `push.ts` + `sw.js` 浏览器推送

### Fixed
- `teams.py`: 修复表结构不匹配（JOIN 错误、字段名错误）
- `compare.py`: 修复 Supabase 数据源兼容性
- `subscriptions.py`: 修复 `notify_methods` JSON 解析

### Database
- 新增 8 张表：`summary_templates`, `up_subscriptions`, `notification_queue`, `push_subscriptions`, `teams`, `team_members`, `team_summaries`, `comments`

---

## [1.2.0] - 2025-12-25

### Added
- **支付全链路**：完整的支付订单创建、状态更新和发货流程
  - 支付宝 Wap Pay 集成
  - 微信支付 Native 集成
  - 订单状态管理（pending → paid → delivered）
- **回调幂等处理**：`idempotency.py` 模块防止重复回调导致重复发货
- **对账服务**：`reconciliation.py` 检测并修复数据不一致
  - 已支付未发货订单检测
  - 账单状态不匹配检测
  - 过期订单自动清理
- **批量总结**：`batch_summarize.py` 支持一次提交多个视频 URL
  - 最多 20 个 URL/批次
  - Semaphore 并发控制
  - 进度追踪与部分成功状态
- **新增 API 端点**：
  - `POST /api/payments/create` - 创建支付订单
  - `GET /api/payments/status/{order_id}` - 查询订单状态
  - `POST /api/payments/callback/alipay` - 支付宝回调
  - `POST /api/payments/callback/wechat` - 微信回调
  - `POST /api/admin/reconciliation` - 管理员对账
  - `POST /api/batch/summarize` - 批量总结
  - `GET /api/batch/{job_id}` - 查询批量任务状态

### Changed
- `payment_orders` 表新增 `transaction_id` 字段
- 数据库初始化新增 `idempotency_keys` 表
- 更新项目文档（README、ROADMAP、ARCHITECTURE、API_CONTRACT）

### Fixed
- 修复任务队列中同步函数阻塞事件循环的问题（使用 `run_in_executor`）

## [1.1.0] - 2024-12-24

### Added
- 稳定性优化模块
  - PDF 导出稳定性（中文字体、长文分页）
  - 思维导图渲染稳定性（预处理 + 降级）
  - 任务队列架构（asyncio.Queue + Worker）
  - 请求限流机制（令牌桶算法）
- 完整 API 文档页面 (`/api-docs`)
- 服务条款与隐私政策页面
- 用户反馈功能

## [1.0.0] - 2024-12-23

### Added
- 初始版本发布
- 核心总结功能
- 思维导图生成
- 视频播放集成
- 暗色模式
- 响应式设计
- 云端部署支持
