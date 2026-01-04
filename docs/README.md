# 📚 文档索引

> **快速入口**: 第一次接触项目？从 [START_HERE.md](START_HERE.md) 开始！  
> **最后更新**: 2026-01-05

---

## 🚀 核心文档

### 新手必读
- **[START_HERE.md](START_HERE.md)** - 快速开始指南，5分钟上手
- **[SESSION_ENTRYPOINT.md](SESSION_ENTRYPOINT.md)** - 新对话必读入口
- **[AI_CONTEXT.md](AI_CONTEXT.md)** - AI/IDE/CLI 统一上下文入口
- **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)** - 完整开发者指南（架构+结构+模型）

### 开发参考
- **[API_REFERENCE.md](API_REFERENCE.md)** - API文档（后端+外部依赖）
- **[CONFIGURATION.md](CONFIGURATION.md)** - 环境变量配置
- **[ENGINEERING_STANDARDS.md](ENGINEERING_STANDARDS.md)** - 代码规范
- **[cot_design.md](cot_design.md)** - CoT 设计与提示词

### 部署运维
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - 部署指南（本地+生产+Docker+安全）
- **[CHANGELOG.md](CHANGELOG.md)** - 版本变更记录

---

## 🗂️ 文档结构

```
docs/
├── README.md                  # 本文档（索引）
├── START_HERE.md              # 快速开始
├── SESSION_ENTRYPOINT.md      # 新对话必读入口
├── AI_CONTEXT.md              # AI/IDE/CLI 统一入口
├── DEVELOPER_GUIDE.md         # 开发者指南 ⭐
├── API_REFERENCE.md           # API参考 ⭐
├── CONFIGURATION.md           # 配置参考
├── DEPLOYMENT.md              # 部署指南 ⭐
├── ENGINEERING_STANDARDS.md   # 工程规范
├── CHANGELOG.md               # 变更日志
├── cot_design.md              # CoT 设计
├── testing/                   # 测试与验证指南
│   └── chart_testing_guide.md # 图表测试指南
├── diagnostics/               # 问题排查与缺陷记录
│   └── BUG_REPORT_COT.md       # CoT 缺陷记录
└── archived/                  # 历史文档（归档）
    ├── ARCHITECTURE.md        # 已合并到DEVELOPER_GUIDE
    ├── DATA_MODEL.md          # 已合并到DEVELOPER_GUIDE
    ├── API_CONTRACT.md        # 已合并到API_REFERENCE
    └── ...
```

---

## 📖 按角色查看

### 👨‍💻 我是开发者
1. 先读 **[START_HERE.md](START_HERE.md)**
2. 熟悉 **[AI_CONTEXT.md](AI_CONTEXT.md)** 的必读清单
3. 熟悉 **[DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)**
4. 查阅 **[API_REFERENCE.md](API_REFERENCE.md)**
5. 遵循 **[ENGINEERING_STANDARDS.md](ENGINEERING_STANDARDS.md)**

### 🚀 我是运维/部署
1. 先读 **[CONFIGURATION.md](CONFIGURATION.md)**
2. 执行 **[DEPLOYMENT.md](DEPLOYMENT.md)**
3. 关注 **[CHANGELOG.md](CHANGELOG.md)**

### 🆕 我是新人
1. **必读**: [START_HERE.md](START_HERE.md)
2. **了解**: [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) 的"项目概览"部分
3. **动手**: 按照START_HERE跑起来项目
4. **深入**: 根据任务查阅对应文档

---

## 🔍 按需查找

### 我想知道...

**"如何启动项目？"**  
→ [START_HERE.md](START_HERE.md)

**"项目架构是什么样的？"**  
→ [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md#系统架构)

**"API怎么调用？"**  
→ [API_REFERENCE.md](API_REFERENCE.md)

**"环境变量怎么配置？"**  
→ [CONFIGURATION.md](CONFIGURATION.md)

**"如何部署到生产环境？"**  
→ [DEPLOYMENT.md](DEPLOYMENT.md#部署到生产环境)

**"数据库表结构是什么？"**  
→ [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md#数据模型)

**"B站API老是报错-352怎么办？"**  
→ [DEPLOYMENT.md](DEPLOYMENT.md#故障排查) + [CONFIGURATION.md](CONFIGURATION.md) (添加SESSDATA)

**"代码规范是什么？"**  
→ [ENGINEERING_STANDARDS.md](ENGINEERING_STANDARDS.md)

**"如何验证图表功能？"**  
→ [testing/chart_testing_guide.md](testing/chart_testing_guide.md)

**"CoT 设计和提示词在哪里？"**  
→ [cot_design.md](cot_design.md)

**"最近更新了什么？"**  
→ [CHANGELOG.md](CHANGELOG.md)

---

## 📝 文档维护

### 更新原则
- ✅ 功能变更 → 更新CHANGELOG.md
- ✅ API变更 → 更新API_REFERENCE.md
- ✅ 架构调整 → 更新DEVELOPER_GUIDE.md
- ✅ 部署流程 → 更新DEPLOYMENT.md
- ✅ 配置新增 → 更新CONFIGURATION.md

### 归档策略
过时或已合并的文档移至 `archived/` 目录，保留历史参考。

---

## 🎯 快速链接

- **GitHub仓库**: (你的repo链接)
- **在线演示**: (如果部署了)
- **问题反馈**: GitHub Issues
- **项目交接包**: `../.gemini/handoff_package.md`

---

## 版本信息

- **项目名称**: Bili-Summarizer
- **当前版本**: Phase 2 - 功能扩展
- **文档版本**: v2.0 (2025-12-26 整合)
- **维护者**: Core Engineering Team
