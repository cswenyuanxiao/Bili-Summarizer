# Changelog

Last updated: 2025-12-25  
Owner: Core Eng

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

