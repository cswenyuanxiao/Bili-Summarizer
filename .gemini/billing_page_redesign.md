# 账单页面设计更新

## 变更说明
将 `/billing` 账单页面的前端设计改为与 `/pricing` 页面一致的全页展示，替代原先的“点击按钮打开弹窗”模式。

## 修改内容
1.  **重写 `frontend/src/pages/BillingPage.vue`**
    *   移除原先仅作为入口的简单页面。
    *   采用了与 `PricingPage.vue` 一致的 Hero 头部设计。
    *   将原 `BillingModal.vue` 中的数据获取与展示逻辑迁移至页面内。
    *   实现了直接在页面加载时获取账单数据 (`fetchBilling`)。
    *   使用了 `ArrowPathIcon` 作为加载/刷新图标。
    *   保留了 `useAuth` 和 `useReveal` 的集成。

## 效果
*   用户访问 `/billing` 时，直接展示账单列表，无需额外点击。
*   视觉风格与全站保持一致（Header, Page Card 等）。
*   提供了刷新按钮和空状态/未登录状态的友好提示。

## 验证
*   页面加载时会自动触发 `fetchBilling`。
*   未登录用户会看到登录提示。
*   数据加载中显示 loading 状态。
*   数据加载失败显示错误信息。
*   成功加载显示账单列表，支持下载发票。
