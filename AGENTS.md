## A) 产品与路由（不可随意改动）
- 路由结构固定：
  /  /product  /pricing  /docs  /dashboard  /billing  /invite  /developer
- 新增路由必须说明：入口、权限、导航位置、与上述页面关系；避免重复功能页面。

## B) UI 统一风格（必须遵守）
- 视觉语言：流光渐变 + 玻璃质感卡片 + 微动效。
- 组件基准：page-hero / page-card / badge-pill / card-action
- 动效：float / wiggle，避免高频抖动；如实现动效，需支持 prefers-reduced-motion 降级。

## C) 交互硬规则（违者不合并）
- 所有视觉上可点击的卡片必须有真实点击逻辑；使用 card-action，保证 cursor + focus。
- 重要动作优先使用弹窗引导（Pricing / Dashboard / Billing / Invite / ApiKey）。
- 移动端弹窗：
  - 容器 max-h-[90vh] + overflow-y-auto
  - 右上角必须有关闭按钮
  - 内容长时保持滚动可操作
- 层级（z-index）：
  - Header: z=40
  - Dropdown: z=70
  - Modal: z=50+
  - Toast: z=100
- 禁止：
  - 禁止可点击卡片无事件绑定
  - 禁止 overflow-hidden 包裹下拉菜单（下拉/弹层需 portal/floating 方案）

## D) 工程与接口行为（稳定性优先）
- 任何对外行为变化：必须同步更新 docs/（至少一处“单一事实来源”文档）。
- 新增关键流程要输出可定位的 error code / request_id（如项目已有规范则遵循项目规范）。

## E) 修改策略
- 优先修复/扩展现有组件与模式；避免引入新的 UI 体系或重复组件。
- 变更需要最小验证闭环：给出具体步骤（访问页面/触发弹窗/预期 UI 与交互结果）。
