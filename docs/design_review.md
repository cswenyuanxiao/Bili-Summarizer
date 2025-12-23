# 88code.ai 设计借鉴分析（面向 Bili-Summarizer）

## 观察范围
来源：`website /88code - 平价Claude Code_Codex中转.htm` + 相关 CSS。重点关注布局结构、视觉层次、动效与交互反馈。

## 可借鉴的设计策略
1. 主题与色彩体系（OKLCH + 语义变量）
- 使用 OKLCH 定义 `--background/--foreground/--card/--border/--primary`，确保亮/暗主题在不同设备上的对比度更稳定。
- 通过 `--background-95/80/70/50` 生成半透明层级，解决大背景和卡片叠层的对比问题。
- 借鉴：在 Bili-Summarizer 中将现有 RGB tokens 升级为语义 token + OKLCH，保证玻璃卡片在深色背景下依然清晰。

2. Hero 视觉层级（多层背景 + 纵深分层）
- 使用多层背景：
  - 顶部 radial glow
  - 底部渐隐遮罩
  - 前景 ray 纹理动画（低透明）
- 借鉴：在首页 hero 区，给现有 aurora 加一个顶部 radial glow 与底部渐隐遮罩，增强空间纵深与聚焦感。

3. 统一的“卡片语言”
- 卡片统一使用：圆角、细边框、浅阴影、轻微悬停抬升。
- `card-hover-elevate`：hover 时边框变主色 + 轻微上移 + 柔和高光。
- 借鉴：将 Bili-Summarizer 的 Summary/Transcript/Mindmap/History 等卡片统一“边框 + 提升”的交互反馈强度，增强整体一致性。

4. 轻量交互动效
- 主题切换：View Transitions + clip-path 扩散动画。
- Ray 动画：超长周期（90s）避免注意力干扰。
- 借鉴：保留低频动效（大背景缓动），关键交互点用短时、单一动效。

5. 文案与徽章系统
- 通过“标签胶囊”来强化功能亮点（如 Hero 下方的关键能力标签）。
- 价格卡片用 badge 做层级标注（最受欢迎/性价比）。
- 借鉴：对 Bili-Summarizer 的“能力标签”与“套餐推荐”引入 badge 体系，减少纯文本堆叠。

6. 导航与顶部栏
- 顶部固定 + 透明背景 + 背景模糊，保证内容前景强调同时保留纵深。
- 借鉴：保持你现有的 sticky header，同时强化 hover 状态与 active 状态（可借 nav-item-active 风格）。

## 可直接套用的视觉模块（建议落地）
1. 顶部 Hero 的“多层背景”结构
- 目标：增强视觉深度与聚焦。
- 内容：
  - radial glow
  - 底部渐隐遮罩
  - 轻量纹理（类似 ray）

2. 卡片 hover 统一策略
- 目标：统一交互反馈，减少不一致的 hover 体验。
- 内容：
  - 统一 hover 上移幅度（2-4px）
  - 统一边框 highlight
  - 统一 shadow 扩散范围

3. Pricing / 方案区块的阶梯感
- 目标：突出推荐方案并提升转化。
- 内容：
  - 推荐卡片加高亮背景与阴影
  - 使用 badge 标记“推荐 / 热门”

4. 主题色分层
- 目标：增强视觉识别度，同时可读性不下降。
- 内容：
  - 主色用于 CTA 与高亮
  - 二级色用于标签与小组件

## 具体可迁移建议（Bili-Summarizer）
- 首页 Hero：引入“顶部 radial glow + 底部渐隐遮罩”，让 aurora 层更有结构性。
- 卡片体系：增加 card-hover-elevate 风格（边框 + 阴影 + 轻抬）并统一应用在 Summary/Transcript/History 等组件。
- 标签体系：在功能卖点/步骤说明中加入胶囊标签（减少纯文本列表）。
- 主题 token：新增语义色阶（如 `--bg-80/--bg-60`）提升玻璃卡片在深色模式下的可读性。

## 风格落地注意事项
- 避免大幅度动效：当前产品本身功能密集，背景动效应低频且轻量。
- 统一间距系统：与刚完成的 gap 体系配套，不再分散使用 `mb/mt`。
- 维持品牌调性：88code 的暖色偏橙，你的主色是偏冷的蓝/紫，建议只借鉴结构与动效，不复制色板。

