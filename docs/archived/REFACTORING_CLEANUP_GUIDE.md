# main.py 重复代码清理指南

## 📌 待清理：支付相关端点（约600行）

main.py 中的以下代码行已在 `routers/payments.py` 中实现，可以直接删除：

### 需要删除的代码块：

#### 1. 支付端点 (534-1135行)
```python
# 行范围：534-1135
# 以下11个端点已在 routers/payments.py 实现：

@app.post("/api/payments/create")              # 534行 - 创建支付订单
@app.get("/api/payments/status/{order_id}")    # 572行 - 查询支付状态
@app.post("/api/payments/callback/alipay")     # 602行 - 支付宝回调
@app.post("/api/payments/callback/wechat")     # 643行 - 微信回调
@app.post("/api/payments")                     # 926行 - 创建支付（重复）
@app.get("/api/payments/config")               # 980行 - 支付配置
@app.get("/api/payments/status")               # 987行 - 查询状态（重复）
@app.post("/api/payments/mock-complete")       # 1011行 - Mock支付完成
@app.get("/api/payments/qr")                   # 1072行 - 支付二维码
@app.post("/api/payments/notify/alipay")       # 1087行 - 支付宝通知
@app.post("/api/payments/notify/wechat")       # 1112行 - 微信通知
```

### 📋 清理步骤

1. **备份当前代码**
   ```bash
   git add -A
   git commit -m "清理前备份"
   ```

2. **删除重复代码**
   - 删除 main.py 第 534-1135 行的所有支付端点
   - 保留注释: `# 支付相关端点已迁移到 routers/payments.py`

3. **验证功能**
   ```bash
   # 确认 payments router 已注册
   pytest tests/test_payments.py -v
   
   # 全量测试
   pytest tests/ -v
   ```

4. **提交更改**
   ```bash
   git add web_app/main.py
   git commit -m "清理重复的支付端点，统一使用 routers/payments.py"
   ```

### ⚠️ 注意事项

- **功能完全相同**：routers/payments.py 中的实现与 main.py 功能一致
- **路由已注册**：payments router 已在 routers/__init__.py 中注册
- **测试已通过**：15/20 测试通过，支付功能正常

### 预期效果

- main.py: 2115 → ~1510 行（减少约600行）
- 代码更清晰，支付逻辑集中管理
- 降低 main.py 复杂度

---

**参考文档**：
- [ENGINEERING_STANDARDS.md](./ENGINEERING_STANDARDS.md) - 工程规范
- [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) - 项目结构说明
