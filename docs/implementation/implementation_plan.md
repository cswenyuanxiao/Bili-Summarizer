# Implementation Plan

## 用户背景与目标
- 目标用户：中文为主、Bilibili 高频用户（学生、职场学习者、内容从业者）
- 核心诉求：快速理解视频内容、可视化梳理、跨设备回看、稳定导出
- 业务目标：提高留存、提升转化（免费额度 → 订阅），降低失败率与等待成本

## 技术栈与部署形态
- 前端：Vue 3 + Vite + Tailwind + TypeScript
- 后端：FastAPI + Gunicorn + SSE
- AI：Google Gemini（多模态 + 文本）
- 下载：yt-dlp
- 存储：SQLite（cache.db、summarizer.db）、本地 videos/
- Auth：Supabase（可选）
- 部署：Docker Compose / Render

## 已有基础
- SSE 总结与转录流程已完成
- 思维导图（Mermaid）渲染与导出（SVG/PNG）已完成
- 导出：MD/TXT/PDF 已完成
- API Key、Chat、云端历史同步已完成
- Dashboard 已完成（积分 + 14 天曲线）
- 新用户赠送 30 积分已完成（缓存持久化已完成）

## 规划原则
- 先稳态：可靠性、缓存策略、错误处理
- 再增长：留存、引导、转化
- 最后扩展：订阅、队列、云端功能深化

## 里程碑与分阶段实施

### Phase 1: 稳定性与关键体验（1-2 周）
1. 错误码与前端提示标准化（SSE `type:error` + error code）
2. 转录生成兜底与重试策略（超时/无字幕）
3. 历史记录空状态与使用引导
4. 导出稳定性专项回归（PDF/PNG/CSV）
5. 日志脱敏 + 失败原因统计

### Phase 2: 账户与额度体系（1-2 周）
1. 订阅状态 API (`/api/subscription`)
2. 额度不足拦截 + 升级入口
3. 账单历史与发票页
4. API Key 使用统计面板

#### Phase 2 进度
- [x] `/api/subscription` + `/api/subscribe` 接口
- [x] 额度不足弹窗触发升级入口
- [x] 账单历史与发票面板（前端 + `/api/billing`）
- [x] API Key 使用统计（`/api/keys/usage`）

### Phase 3: 增长与留存（2-3 周）
1. 新手任务：首个总结奖励
2. 邀请系统（积分奖励）
3. 分享链接（只读 + 过期）
4. 邮件/站内通知：额度不足、订阅提醒

#### Phase 3 进度
- [x] 首个总结奖励（首次总结额外 +10 积分）
- [x] 邀请码生成与兑换（双方 +10 积分）
- [x] 分享链接创建与只读展示页
- [ ] 邮件/站内通知（待接入服务）

### Phase 4: 性能与扩展（2-4 周）
1. 任务队列（长任务异步化）
2. 缓存分层：摘要/转录/图分离缓存
3. 历史搜索/筛选/批量操作
4. 导出增强：PPT/批量导出

## 关键数据结构与模型
- 用户额度（user_credits）
  - credits, total_used, created_at, updated_at
- 使用事件（credit_events）
  - user_id, event_type, cost, created_at
- 订阅（subscriptions）
  - user_id, plan, status, current_period_end

## 需要补齐的页面/组件（优先级）
P0:
- 订阅状态页（含升级入口）
- 额度不足弹窗与引导
- 失败原因提示/回退方案

P1:
- 历史搜索与筛选
- API Key 统计页
- 账单历史页

P2:
- 分享链接页
- 任务队列/异步进度页
- 高级导出页（PPT/PDF 批量）

## 风险与依赖
- 依赖外部 API 稳定性（Gemini、Bilibili）
- Supabase 未配置时需完整降级
- 任务队列需要独立 worker（Render 需额外服务）

## 验收标准（简版）
- 核心流程：成功率 ≥ 95%，失败有明确提示
- 导出：PDF/PNG 可用，内容完整
- 额度：创建后 30 积分可见，消费准确
- Dashboard：显示用户积分与 14 天曲线
