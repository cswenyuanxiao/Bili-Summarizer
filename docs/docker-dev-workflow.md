# Docker 开发工作流指南

本文档介绍如何高效地在本地开发和验证新功能。

---

## 快速参考

| 命令 | 耗时 | 适用场景 |
|------|------|----------|
| `docker-compose up -d --build` | 1-3 分钟 | 生产环境验证 |
| `docker-compose up -d --build backend` | 30-90 秒 | 只改后端 |
| `docker-compose -f docker-compose.dev.yml up` | 首次 2 分钟，后续 0 秒 | 开发迭代 |
| 本地 `npm run dev` + `uvicorn --reload` | 0 秒 | 日常开发 |

---

## 方案 A：本地开发（最快 ⚡）

直接在本地运行前后端，改动后**瞬间生效**。

### 启动命令

```bash
# 终端 1：启动后端
cd /path/to/summarizer
uvicorn web_app.main:app --reload --port 7860

# 终端 2：启动前端
cd /path/to/summarizer/frontend
npm run dev -- --host 0.0.0.0
```

### 访问地址

- 前端：`http://localhost:5173`
- 后端 API：`http://localhost:7860`

> Vite 会自动将 `/api` 请求代理到后端。

---

## 方案 B：Docker 开发模式（推荐容器化开发）

使用 `docker-compose.dev.yml`，支持**热更新**。

### 启动命令

```bash
docker-compose -f docker-compose.dev.yml up
```

### 特点

| 优势 | 说明 |
|------|------|
| ✅ 后端热更新 | `web_app/` 代码改动后自动重载 |
| ✅ 前端热更新 | Vue 文件改动后即时刷新 |
| ⚡ 首次启动约 1-2 分钟 | 之后改代码**无需重建** |

### 访问地址

- 前端：`http://localhost:5173`
- 后端直连：`http://localhost:7860`

---

## 方案 C：生产环境验证

完整构建 Docker 镜像，模拟生产环境。

### 全量构建

```bash
docker-compose up -d --build
```

耗时：**1-3 分钟**

### 仅重建单个服务

如果只改了后端代码：

```bash
docker-compose up -d --build backend
```

如果只改了前端代码：

```bash
docker-compose up -d --build frontend
```

这样比全量重建快约 **50%**。

### 访问地址

- 应用：`http://localhost`（Nginx 代理，端口 80）

---

## 推荐工作流

```
┌─────────────────────────────────────────────────────────────┐
│                      日常开发流程                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   1. 本地开发（方案 A）                                      │
│      ├── 快速迭代，改动即时生效                              │
│      └── 适合功能开发、调试                                  │
│                              ↓                              │
│   2. Docker 开发模式验证（方案 B）                           │
│      ├── 验证容器化环境兼容性                                │
│      └── 适合跨平台测试                                      │
│                              ↓                              │
│   3. 生产环境完整构建（方案 C）                              │
│      ├── 上线前最终验证                                      │
│      └── 确保与生产环境一致                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 常用命令速查

```bash
# 查看容器状态
docker-compose ps

# 查看后端日志
docker logs bili-summarizer-backend -f

# 查看前端日志
docker logs bili-summarizer-frontend -f

# 停止所有容器
docker-compose down

# 清理并重建（解决缓存问题）
docker-compose down --rmi local
docker-compose up -d --build
```

---

## 故障排查

### 端口占用

```bash
# 检查 80 端口
lsof -i :80

# 检查 7860 端口
lsof -i :7860
```

### 容器无法启动

```bash
# 查看详细日志
docker-compose logs backend
docker-compose logs frontend

# 进入容器调试
docker exec -it bili-summarizer-backend /bin/bash
```

### 前端资源未更新

```bash
# 清理 Docker 构建缓存
docker builder prune -f

# 重新构建
docker-compose up -d --build frontend
```
