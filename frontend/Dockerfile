# Stage 1: 构建阶段
FROM node:20-alpine AS builder

WORKDIR /app

# 复制依赖文件
COPY package*.json ./

# 安装依赖 (使用 ci 更快更可靠)
RUN --mount=type=cache,target=/root/.npm npm ci

# 复制源代码
COPY . .

# 构建生产版本
RUN npm run build

# Stage 2: 生产阶段
FROM nginx:alpine

# 从构建阶段复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露 80 端口
EXPOSE 80

# 启动 Nginx
CMD ["nginx", "-g", "daemon off;"]
