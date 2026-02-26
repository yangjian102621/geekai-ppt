# 二次开发与教学指南

本文档面向希望基于本项目做定制或用于教学的开发者，提供最小必要说明。

## 快速跑通一次生成流程

1. **环境**：Python 3.9+、Node 18+；后端 `backend/.env` 中配置有效 `API_KEY`（如 [GeekAI](https://geekai.pro)）。
2. **启动**：后端 `python main.py`（默认 8002），前端 `cd web && npm install && npm run dev`（默认 3000）。
3. **操作**：在前端创建演示文稿 → 输入主题（可选上传文档）→ 规划 → 生成。即可在「我的作品」或编辑器中看到生成的幻灯片与版本历史。

理解该流程后，可结合 [architecture.md](architecture.md) 查看各模块职责与数据流。

## 常见定制场景

### 更换模型或 API 提供商

- 修改 `backend/.env`：`BASE_URL`、`MODEL_LOGIC`、`MODEL_IMAGE`。若 API 与当前调用协议兼容，通常无需改代码。
- 若协议不同，需在 `backend/llm_planner.py` 与 `backend/image_gen.py` 中调整 HTTP 调用与参数（如 model 字段、请求体格式）。

### 修改 PPT 风格或规则

- 内容与结构规则：`backend/llm_planner.py` 中的 `PPT_CORE_PRINCIPLES`、`PPT_OUTPUT_RULES` 等常量，以及 `docs/system_prompt.md`（若被引用）。
- 图像风格：`backend/image_gen.py` 中的默认 style prompt 或传入的 `style_template` 参数。

### 扩展数据字段

- 在 `backend/models.py` 中为对应 ORM 增加字段。
- 在 `backend/database.py` 中增加迁移函数（如 `migrate_add_xxx`），并在 `main.py` 的 `startup()` 中调用。
- 在 `backend/repository.py` 与 `main.py` 中读写新字段并暴露给前端。

### 前端定制

- 应用标题、Logo、API 地址：通过 `web/.env` 中 `VITE_*` 配置（见 `web/.env.sample`）。
- 新增页面或接口：在 `web/src/views/` 与 `web/src/js/services/` 中增加页面与 API 调用，并在路由中注册。

## 教学建议

- **课堂演示**：用一份固定主题（如「机器学习简介」）跑通规划 → 生成，再打开浏览器开发者工具展示请求/响应，对应到 `docs/architecture.md` 中的二阶段流程。
- **作业**：例如「修改 prompt 使生成的 PPT 更简洁」或「为演示文稿增加一个“标签”字段并在列表中展示」。
- **安全**：统一使用示例 API Key 或本地 Mock，避免学生将个人 Key 提交到作业仓库。
