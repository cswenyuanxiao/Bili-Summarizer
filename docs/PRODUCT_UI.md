# 产品与 UI 规范

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

## 移动端弹窗规范
- 弹窗容器使用 `max-h-[90vh]` + `overflow-y-auto`。
- 右上角必须有关闭按钮。
- 弹窗内容过长时保持滚动可操作。

## 层级规范
- Header：z=40
- Dropdown：z=70
- Modal：z=50+
- Toast：z=100

## 禁止事项
- 禁止在可点击卡片上不绑定任何事件。
- 禁止 `overflow-hidden` 包裹下拉菜单。
