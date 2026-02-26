# Repository Guidelines

## 项目结构与模块组织
- `backend/`: FastAPI 后端；核心入口在 `backend/main.py`，数据与会话逻辑集中在 `backend/repository.py`、`backend/database.py`。
- `backend/storage/`: 会话 JSON、生成图片与数据库文件；运行时会写入，请避免提交大文件与临时资源。
- `frontend/`: Vue 3 + Vite 前端；主要代码在 `frontend/src/`，包含 `components/`、`views/`、`stores/`、`services/`、`styles/` 与 `router/`。
- `frontend/src-react-backup/`: 历史 React 版本备份，仅作参考。

## 构建、测试与本地开发命令
后端（Python/FastAPI）：
- `cd backend && pip install -r requirements.txt`：安装依赖。
- `cd backend && python main.py`：启动开发服务（默认 `http://localhost:8002`）。
- `cd backend && uvicorn main:app --host 0.0.0.0 --port 8002 --reload`：热更新启动。
- `cd backend && bash start.sh`：一键创建虚拟环境并启动服务。

前端（Vue/Vite）：
- `cd frontend && npm install`：安装依赖。
- `cd frontend && npm run dev`：启动开发服务（默认 `http://localhost:3000`）。
- `cd frontend && npm run build`：生产构建。
- `cd frontend && npm run preview`：本地预览构建产物。

测试：当前未发现自动化测试目录或脚本，新增测试时请同步补充命令与说明。

## 代码风格与命名约定
- Python：4 空格缩进；函数与变量使用 `snake_case`；Pydantic 模型使用 `PascalCase`。
- Vue/TypeScript：2 空格缩进；组件文件使用 `PascalCase.vue`；普通文件用 `camelCase` 或语义化命名（如 `services/api.ts`）。
- 保持与现有文件一致，避免混用缩进或命名风格。

## 测试指南
- 暂无既定框架；如新增建议放在 `backend/tests/` 或 `frontend/src/__tests__/`，并在此文件补充运行方式与覆盖范围。

## 提交与 Pull Request 指南
- Git 历史未体现固定提交规范；建议使用简短、动词开头的中文或英文描述（例如：`fix api key save`）。
- PR 需包含：变更说明、验证步骤；涉及 UI 变更请附截图或录屏。
- 若修改 `backend/.env` 或 API 地址（如 `frontend/src/services/api.ts`），请在 PR 中明确提醒。

## 配置与安全提示
- `backend/.env` 包含 GeekAI API Key 等敏感信息，请勿提交。
- 前端默认请求后端 `http://localhost:8002`，部署时请同步调整配置。
