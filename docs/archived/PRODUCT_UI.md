# 产品与 UI 规范

Last updated: 2025-12-24  
Owner: Frontend

## UI 统一风格
- 视觉语言：流光渐变 + 玻璃质感卡片 + 微动效。
- 组件基准：`page-hero`、`page-card`、`badge-pill`、`card-action`。
- 动效：轻浮动（float）、轻摇（wiggle），避免高频抖动。

## 路由结构
- `/` 首页
- `/product` 产品
- `/pricing` 方案
- `/docs` 使用文档
- `/dashboard` 仪表盘
- `/billing` 账单
- `/invite` 邀请
- `/developer` 开发者 API

## 交互规范
- 所有视觉上可点击的卡片必须有真实点击逻辑。
- 卡片样式使用 `card-action`，保证 cursor + focus。
- 重要动作优先使用弹窗引导（Pricing / Dashboard / Billing / Invite / ApiKey）。

## 可访问性（最低标准）
- `card-action` 必须支持 `Tab/Enter/Space`。
- Modal 支持 `Esc` 关闭与 focus trap（避免背景可操作）。
- 必要按钮添加 `aria-label`。

## 可点击判定标准
- 若视觉上出现：阴影/浮层/箭头/“立即”类 CTA，则视为可点击。
- 可点击元素必须具备 hover、focus 与实际事件。

## 移动端弹窗规范
- 弹窗容器使用 `max-h-[90vh]` + `overflow-y-auto`。
- 右上角必须有关闭按钮。
- 弹窗内容过长时保持滚动可操作。

## 层级规范（token 建议）
- `z-header=40`
- `z-dropdown=70`
- `z-modal=90`
- `z-toast=100`

## 弹窗模板化
- Header（标题 + 说明 + 关闭按钮）
- Body（表单/内容）
- Footer（主次按钮 + 错误态 + 加载态）

## 禁止事项
- 禁止在可点击卡片上不绑定任何事件。
- 禁止 `overflow-hidden` 包裹下拉菜单。
