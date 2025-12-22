# Bili-Summarizer 部署与上线指南

您的视频总结工具已准备就绪。以下是正式上线的步骤：

## 1. 环境变量配置
确保根目录下的 `.env` 文件包含最新的配置：
```env
GOOGLE_API_KEY=您的谷歌API密钥
# 如果使用了 PayPal 等支付功能，请确保 ClientID 和 Secret 也是生产环境的
```

## 2. 数据库迁移
如果是首次部署，程序会自动创建 `summarizer.db`。如果您需要重置数据库：
```bash
rm summarizer.db
```

## 3. 运行生产环境
我们提供了一个一键启动脚本：
```bash
chmod +x start_prod.sh
./start_prod.sh
```
该脚本使用 `gunicorn` 运行，比开发环境的 `uvicorn --reload` 更稳定。

## 4. 测试与正式版区别
| 功能 | 正式版 (Port 8000) | 测试版 (Port 8001) |
| :--- | :--- | :--- |
| **入口逻辑** | `web_app/main.py` | `web_app/main_test.py` |
| **点数消耗** | 每次总结扣除 10 点 | **不扣点数** |
| **Token 核验** | **隐藏** (用户无感) | **显示** (方便成本测算) |
| **新用户赠送** | 30 点数 | 30 点数 |

## 5. 维护建议
- 定期清理 `videos/` 文件夹（虽然程序会自动清理，但如果中途崩溃可能会有残余）。
- 监控 `summarizer.db` 以备份用户信息。
