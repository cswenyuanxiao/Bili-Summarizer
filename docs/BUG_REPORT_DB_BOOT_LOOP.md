# Bug Report: Render 实例反复失败/恢复（DB 初始化导致的启动崩溃）

Last updated: 2025-12-25  
Owner: Core Eng

## 1. 故障摘要
- 标题：Render 部署实例循环失败（Worker boot error / 502）
- 影响范围：生产环境（Render）
- 严重级别：P0
- 状态：已修复（待线上验证）

## 2. 故障现象
- 浏览器访问返回 502
- Render 控制台反复出现：
  - Instance failed / Service recovered
  - Worker exited with code 3
- 典型日志：
  - `psycopg2.OperationalError: SSL connection has been closed unexpectedly`

## 3. 根本原因（Root Cause）
**启动阶段进行数据库初始化（建表/迁移）**，一旦数据库连接短暂不可用（如 Render 上的 Postgres SSL 抖动或连接池短暂耗尽），Gunicorn Worker 在 **import / startup 阶段** 直接抛异常，导致 Worker 启动失败并被重启，形成循环崩溃。

具体触发点包括：
- 模块导入即执行建表（`cache.py`、`credits.py`、`telemetry.py` 旧逻辑）。
- `main.py` 的 `startup` 中同步建表（核心表创建），在 DB 抖动时导致启动失败。

## 4. 诱因与放大因素
- Render 的数据库连接在冷启动或网络波动时可能短暂不可用。
- Gunicorn Worker 对 import 阶段异常极为敏感，直接触发 `Worker failed to boot`。
- 业务启动逻辑与 DB 初始化耦合，没有重试与降级策略。

## 5. 修复策略与实现
1) **移除模块级建表副作用**  
   - 将 `init_cache_db()`、`init_credits_db()`、`init_telemetry_db()` 从模块导入时执行移除。

2) **启动阶段异步重试初始化**  
   - 在 `startup` 中使用 `init_db_with_retry` 异步重试初始化，失败不会阻塞服务启动，避免 Worker 崩溃。

3) **核心表初始化改为重试任务**  
   - 将 `main.py` 启动时同步建表改为 `init_core_tables()` 并通过重试任务执行。

## 6. 影响评估
- 在 DB 短暂不可用时，服务可启动但部分接口会返回 500（降级），不会导致整站 502。
- DB 恢复后初始化任务自动完成，服务恢复完整功能。

## 7. 验证步骤（建议）
1) 部署前执行 **Clear Build Cache & Deploy**。
2) 观察日志：
   - `Core DB initialized`
   - `Cache DB initialized`
   - `Credits DB initialized`
   - `Telemetry DB initialized`
3) 访问首页不再 502；接口在 DB 恢复后正常。

## 8. 后续防线建议
- 禁止模块导入阶段做 DB IO（强制规则）。
- 启动期所有 DB 初始化必须具备重试与降级。
- 增加 DB 健康检查与连接池状态指标。

## 9. 回滚方案
- 回滚为旧的启动同步建表逻辑（不推荐）。
- 若必须回滚，需保证 DB 稳定可用并提升连接池上限以降低启动失败概率。
