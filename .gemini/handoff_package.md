# Bili-Summarizer 项目交接包

> **最后更新**: 2025-12-26 01:41  
> **Token消耗**: 84k/200k (42%)  
> **阶段**: Phase 2 - 功能扩展

---

## 1. 功能目标与验收标准

1. **视频总结**: 输入B站URL → AI生成总结+转录+思维导图 ✅
2. **订阅推送**: 关注UP主 → 每日推送新视频待总结 ✅
3. **热门推荐**: 展示B站热门视频，一键AI总结 ✅
4. **收藏管理**: 保存喜欢的总结（当前localStorage，待后端集成）🟡
5. **批量处理**: 输入多个URL并发总结（当前前端模拟，待后端对接）🟡

---

## 2. 技术栈 & 版本

### 后端
- **Python 3.10+** / FastAPI 0.100+
- **Supabase** (PostgreSQL + Auth)
- **httpx** (异步HTTP) + **APScheduler** (定时任务)
- **Gemini API** (AI总结)

### 前端  
- **Vue 3.4+** / Vite 7.3 / TypeScript
- **Vue Router 4.x** / Pinia (状态管理)
- **@heroicons/vue** (图标) / Tailwind思想的自定义样式

### 运行端口
- 后端: `http://localhost:8000`
- 前端: `http://localhost:5173`

---

## 3. 关键文件清单

### 后端核心
```
web_app/
├── main.py                    # FastAPI入口，路由注册，启动调度器
├── subscriptions.py           # B站API交互：搜索UP主、获取视频（含WBI签名+风控重试）
├── routers/
│   ├── subscriptions.py       # 订阅相关API端点（搜索/订阅/列表/视频）
│   ├── trending.py            # 热门视频API（调用B站热门接口）
│   └── __init__.py            # 路由注册中心
├── wbi.py                     # B站WBI签名工具（防风控）
├── bilibili_rate_limiter.py   # 令牌桶限流器（新增，未集成）
└── bilibili_cache.py          # 视频列表缓存（新增，未集成）
```

### 前端核心
```
frontend/src/
├── App.vue                    # 根组件：导航栏（含"工具集"下拉菜单）
├── router/index.ts            # 路由配置：7个页面
├── pages/
│   ├── HomePage.vue           # 主页：URL输入+总结展示
│   ├── TrendingPage.vue       # 热门推荐页 ✅
│   ├── FavoritesPage.vue      # 收藏夹页（localStorage）🟡
│   ├── BatchPage.vue          # 批量处理页（前端模拟）🟡
│   ├── SubscriptionsPage.vue  # 订阅管理页 ✅
│   ├── ComparePage.vue        # 总结对比
│   └── TemplatesPage.vue      # 自定义模板
└── composables/
    ├── useAuth.ts             # Supabase认证
    └── useSummarize.ts        # 总结API调用
```

### 配置文件
```
.env                           # 环境变量：SUPABASE_URL, GEMINI_API_KEY, BILIBILI_SESSDATA(可选)
frontend/vite.config.ts        # Vite代理配置 → localhost:8000
```

---

## 4. 关键接口 & 数据模型

### 后端API
```python
# 搜索UP主
GET /api/subscriptions/search?keyword={name}
→ {"users": [{"mid", "name", "avatar", "fans", "videos"}]}

# 获取订阅列表
GET /api/subscriptions
→ {"subscriptions": [{"id", "up_mid", "up_name", "created_at"}]}

# 获取UP主最新视频
GET /api/subscriptions/videos?mid={mid}&count=5
→ {"videos": [{"bvid", "title", "pic", "created", "length"}]}

# 热门视频
GET /api/trending/videos
→ {"videos": [{"bvid", "title", "pic", "view", "like", "url"}]}
```

### 前端数据模型
```typescript
// 订阅项
interface Subscription {
  id: string
  up_mid: string
  up_name: string
  up_avatar: string
  created_at: string
  videos?: Video[]        // 懒加载
  videosLoading?: boolean
}

// 视频
interface Video {
  bvid: string
  title: string
  pic: string
  created: number  // 时间戳
  length: number   // 秒
}
```

---

## 5. 约束与边界

### 技术约束
- ✅ **B站API风控严格**: 必须用WBI签名 + 真实Cookie + 限流，建议添加`BILIBILI_SESSDATA`到`.env`
- ✅ **Vite代理绑定**: 前端硬编码代理到`localhost:8000`，后端必须跑这个端口
- ✅ **Supabase Auth**: 所有需登录的端点需验证`Authorization: Bearer <token>`

### 性能约束
- B站API请求间隔建议 ≥2s（避免-352错误）
- 订阅检查定时任务：每1小时运行一次
- 单次总结耗时：30s-2min（取决于视频长度）

### 不可改动边界
- Supabase数据库schema（已上线）
- WBI签名算法（B站反爬机制）
- Gemini API调用方式（核心功能）

---

## 6. 当前状态 & 卡住点

### ✅ 已完成
1. 核心总结功能（视频 → 总结+转录+思维导图）
2. 订阅系统（搜索UP主、关注、获取新视频）
3. 热门推荐页（展示B站热榜）
4. 导航栏优化（emoji → Heroicons，合并"工具集"下拉菜单）
5. B站风控基础应对（WBI签名 + 重试逻辑）

### 🟡 进行中
1. **B站风控优化**: 已创建`bilibili_rate_limiter.py`和`bilibili_cache.py`，但**未集成到主代码**
2. **收藏夹功能**: 前端页面完成，但后端API**未实现**（需要Supabase表+RLS）
3. **批量处理**: 前端UI完成，后端**未实现**（需要任务队列+并发控制）

### ❌ 当前卡点
**无严重阻塞**，但优化建议：
1. **B站风控时好时坏**: 建议立即添加`BILIBILI_SESSDATA`环境变量（成功率95%+）
2. **端口混乱**: 曾出现7860/8000端口冲突，现已统一到8000
3. **图标迁移**: 已将主要页面emoji换成Heroicons，但`HomePage.vue`部分Badge仍用emoji

---

## 7. 快速启动命令

```bash
# 后端
cd /Users/wenyuan/Desktop/summarizer
python -m uvicorn web_app.main:app --reload --port 8000

# 前端
cd frontend
npm run dev -- --port 5173

# 访问
open http://localhost:5173
```

---

## 8. 下一步建议

**优先级排序**：
1. 🔴 **添加SESSDATA** → 解决B站风控（5分钟，高收益）
2. 🟡 **集成限流器+缓存** → 优化B站API调用（30分钟）
3. 🟡 **实现收藏夹后端** → 完成功能闭环（2小时）
4. 🟢 **批量处理后端** → 高级功能（4小时）

---

**如何在新对话使用此交接包**：
```
你："继续Bili-Summarizer开发，上下文见附件（粘贴此文件内容）"
AI：快速恢复上下文（约5k token），立即开始工作
```
