# 商业化与支付

## 定价
- Starter Pack：¥1 / 30 积分
- Pro Pack：¥3 / 120 积分
- Pro 专业版：¥29.9 / 月

## 支付流程
1) 前端 `POST /api/payments`
2) 后端创建订单并返回支付链接/二维码
3) 回调 `/api/payments/notify/*`
4) 订单完成后写入账单与订阅/积分

## 支付环境变量
支付宝：
- `ALIPAY_APP_ID`
- `ALIPAY_PRIVATE_KEY`
- `ALIPAY_PUBLIC_KEY`
- `ALIPAY_NOTIFY_URL`
- `ALIPAY_RETURN_URL`（可选）
- `ALIPAY_ENV`（可选：`sandbox`）

微信：
- `WECHAT_APP_ID`
- `WECHAT_MCH_ID`
- `WECHAT_SERIAL_NO`
- `WECHAT_PRIVATE_KEY`
- `WECHAT_API_V3_KEY`
- `WECHAT_NOTIFY_URL`

回调安全：
- `PAYMENT_WEBHOOK_SECRET`

## 联调开关
- `PAYMENT_MOCK=1` 开启模拟支付
- `PAYMENT_MOCK=0` 生产默认关闭

## 注意事项
- 沙箱环境不能完全替代生产环境（支付宝/微信资质限制）。
- Render 环境变量必须在部署时设置。
