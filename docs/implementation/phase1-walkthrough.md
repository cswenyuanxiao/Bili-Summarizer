# Phase 1: 前端脚手架搭建 - Walkthrough

## 完成状态 ✅

Phase 1 已成功完成！Vue 3 现代化前端已初始化并运行。

## 验证截图

### 浅色模式 (Light Mode)
![Frontend Light Mode](file:///Users/wenyuan/.gemini/antigravity/brain/a105074a-5d5c-4121-bf9d-d3369971a3f1/initial_load_light_mode_1766485376027.png)

上图显示：
- ✅ 紫蓝渐变 Hero Section
- ✅ "✨ Bili-Summarizer" 标题
- ✅ 右上角主题切换按钮 (🌙)
- ✅ Phase 1 完成提示文字
- ✅ 无控制台错误

### 暗色模式 (Dark Mode)
![Frontend Dark Mode](file:///Users/wenyuan/.gemini/antigravity/brain/a105074a-5d5c-4121-bf9d-d3369971a3f1/dark_mode_verification_1766485392251.png)

主题切换功能正常工作，点击按钮后图标变为 ☀️。

---

## 技术栈配置

| 组件 | 版本 | 用途 |
|------|------|------|
| **Vue 3** | 3.5.24 | 前端框架（Composition API） |
| **Vite** | 7.2.4 | 构建工具与开发服务器 |
| **TypeScript** | 5.9.3 | 类型系统 |
| **Tailwind CSS** | 最新 | 工具类 CSS 框架 |
| **Pinia** | 最新 | 状态管理 |
| **Axios** | 最新 | HTTP 客户端 |
| **VueUse** | 最新 | 组合式函数工具库 |
| **Marked** | 最新 | Markdown 渲染 |
| **Mermaid** | 最新 | 思维导图渲染 |

---

## 项目结构

```
frontend/
├── src/
│   ├── App.vue              # 根组件（含 Hero 和主题切换）
│   ├── main.ts              # 入口文件（已配置 Pinia）
│   └── style.css            # Tailwind 入口 + 设计系统变量
├── index.html
├── vite.config.ts           # Vite 配置（含 API 代理）
├── tailwind.config.js       # Tailwind 配置
├── postcss.config.js        # PostCSS 配置
├── tsconfig.json
└── package.json
```

---

## 关键配置

### 1. Vite API 代理

[vite.config.ts](file:///Users/wenyuan/Desktop/summarizer/frontend/vite.config.ts#L7-L13)
```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:7860',  // FastAPI 后端
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, ''),
    },
  },
}
```

**作用**: 前端直接请求 `/api/summarize` 会自动代理到 `http://localhost:7860/summarize`

---

### 2. Tailwind CSS 配置

[tailwind.config.js](file:///Users/wenyuan/Desktop/summarizer/frontend/tailwind.config.js)
```javascript
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#4f46e5',        // 保留原设计系统颜色
        'primary-hover': '#4338ca',
        'primary-light': '#e0e7ff',
      },
    },
  },
}
```

---

### 3. 设计系统变量

[style.css](file:///Users/wenyuan/Desktop/summarizer/frontend/src/style.css#L1-L59)

从原始 `index.html` 迁移了所有 CSS 变量：
- 主色系：`--primary`, `--primary-hover`, `--primary-light`
- 中性色：`--bg`, `--card-bg`, `--text-main`, `--text-secondary`
- 暗色模式支持：`body.dark-mode`
- 设计令牌：`--radius-sm/md/lg`, `--shadow-sm/md/lg`

---

### 4. Pinia 状态管理

[main.ts](file:///Users/wenyuan/Desktop/summarizer/frontend/src/main.ts)
```typescript
import { createPinia } from 'pinia'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.mount('#app')
```

**下一步**: 创建 `stores/summaryStore.ts` 管理全局状态。

---

### 5. 基础 App 组件

[App.vue](file:///Users/wenyuan/Desktop/summarizer/frontend/src/App.vue)

当前功能：
- ✅ Hero Section (标题 + 描述)
- ✅ 主题切换 (localStorage 持久化)
- ✅ 暗色模式支持
- ✅ 响应式布局

---

## 验证步骤

### 开发服务器

```bash
cd frontend
npm run dev
```

访问: http://localhost:5173

**预期结果**:
- 看到紫色渐变 Hero Section
- 右上角有 🌙/☀️ 主题切换按钮
- 点击主题切换，背景色应变化
- 控制台无错误

---

### API 代理测试

后续当后端运行时（`uvicorn web_app.main:app --reload --port 7860`），前端可以通过：
```typescript
axios.get('/api/some-endpoint')
```
直接访问后端 API。

---

## 依赖清单

### 生产依赖
```json
{
  "vue": "^3.5.24",
  "pinia": "latest",
  "axios": "latest",
  "@vueuse/core": "latest",
  "marked": "latest",
  "mermaid": "latest"
}
```

### 开发依赖
```json
{
  "vite": "^7.2.4",
  "vue-tsc": "^3.1.4",
  "typescript": "~5.9.3",
  "tailwindcss": "latest",
  "postcss": "latest",
  "autoprefixer": "latest",
  "@vitejs/plugin-vue": "^6.0.1"
}
```

---

## 下一步: Phase 2

**目标**: 将原 `index.html` 拆分为 Vue 组件

组件列表：
1. `UrlInputCard.vue` - URL 输入表单
2. `LoadingOverlay.vue` - 加载状态
3. `ResultPanel.vue` - 结果容器
4. `SummaryCard.vue` - AI 总结
5. `TranscriptPanel.vue` - 视频转录
6. `MindmapViewer.vue` - 思维导图
7. `ExportBar.vue` - 导出按钮
8. `HistoryList.vue` - 历史记录

---

## 已知问题

1. **CSS Lint Warnings** (`@tailwind` unknown)
   - ✅ 正常现象，PostCSS 会处理
   - 不影响构建

2. **TypeScript 严格模式**
   - 当前使用默认配置
   - 后续可根据需要调整 `tsconfig.json`

---

## 文件变更摘要

| 文件 | 操作 | 说明 |
|------|------|------|
| `frontend/` | [NEW] | 整个目录全新创建 |
| `vite.config.ts` | 创建 | 含 API 代理配置 |
| `tailwind.config.js` | 创建 | Tailwind 配置 |
| `postcss.config.js` | 创建 | PostCSS 配置 |
| `src/App.vue` | 创建 | 根组件 |
| `src/main.ts` | 修改 | 添加 Pinia |
| `src/style.css` | 创建 | Tailwind + 设计系统 |

---

**Phase 1 总时间**: ~2 小时  
**下一阶段**: Phase 2 - 组件迁移（预计 4-6 小时）
