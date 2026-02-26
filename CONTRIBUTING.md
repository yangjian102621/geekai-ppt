# 贡献指南

感谢你对 GeekAI-PPT 的关注与贡献。本文档说明如何搭建开发环境、代码约定以及提交流程。

## 开发环境

### 环境要求

- Python 3.9+
- Node.js 18+
- pnpm / npm / yarn（前端依赖）

### 搭建步骤

1. **克隆仓库**
   ```bash
   git clone <repository-url>
   cd geekai-ppt
   ```

2. **后端**
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.sample .env   # 按需编辑 .env
   python main.py        # 默认 http://localhost:8002
   ```

3. **前端**
   ```bash
   cd web
   npm install   # 或 pnpm install
   npm run dev   # 默认 http://localhost:3000
   ```

4. 确保后端 `.env` 中已配置有效的 `API_KEY`（如 GeekAI），否则生成功能无法使用。

### 推荐版本

- Python：3.10 或 3.11
- Node：18 LTS 或 20 LTS

## 代码风格与约定

- **Python**：4 空格缩进；函数与变量使用 `snake_case`；Pydantic 模型使用 `PascalCase`。可选用 Black、isort 等格式化工具。
- **Vue / JavaScript**：2 空格缩进；组件文件使用 `PascalCase.vue`；与现有风格保持一致。
- 提交前建议在本地运行后端与前端，确保无语法错误与明显功能回归。

## 分支与提交流程

1. 基于 `main` 创建功能分支，例如：`feature/xxx` 或 `fix/xxx`。
2. 在分支上完成修改，提交信息建议简短、动词开头（中英文均可），例如：
   - `feat: 增加导出 PDF 选项`
   - `fix: 修复幻灯片删除后索引错位`
3. 向 `main` 发起 **Pull Request**，PR 中请包含：
   - 变更说明（做了什么、为什么）
   - 验证步骤（如何自测）
   - 若涉及 UI，请附截图或录屏。

## 文档与配置变更

- 若新增或修改环境变量，请同步更新 `backend/.env.sample` 或 `web/.env.sample` 及 README 中的配置说明。
- 若新增 API 或重要行为变更，请在 README 或相关文档中补充说明。

## Issue

- 使用 Issue 报告 Bug 或提出功能建议时，请尽量描述清楚：环境、复现步骤、预期与实际行为。
- 安全相关问题请勿在公开 Issue 中披露，参见 [SECURITY.md](SECURITY.md)。

## 行为准则

参与本项目即表示同意遵守我们的 [行为准则](CODE_OF_CONDUCT.md)，营造友好、包容的协作环境。
