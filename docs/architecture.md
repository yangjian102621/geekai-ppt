# 架构与模块说明

本文档简要说明后端与前端核心模块及数据流，便于二次开发与教学使用。

## 整体架构

```
┌─────────────┐     HTTP/JSON      ┌─────────────┐     GeekAI API         ┌─────────────────┐
│  Vue 3 前端  │ ◄────────────────► │  FastAPI    │ ◄────────────────────► │ Gemini 模型     │
│  (web/)     │                    │  后端       │     (规划 + 图像生成)   │ (逻辑/视觉)     │
└─────────────┘                    └──────┬──────┘                        └─────────────────┘
                                         │
                                         ▼
                                  ┌─────────────┐
                                  │ SQLite +    │
                                  │ 本地文件    │
                                  │ (storage/)  │
                                  └─────────────┘
```

- **前端**：创建/编辑演示文稿、上传文档、触发规划与生成、查看版本历史。
- **后端**：接收请求 → 调用 LLM 规划大纲 → 调用图像模型生成每页幻灯片 → 持久化到数据库与 `storage/images/`。
- **存储**：SQLite 存演示文稿/幻灯片/版本元数据；图片按会话 ID 存于 `backend/storage/images/`。

## 后端核心模块

| 文件 | 职责 |
|------|------|
| `main.py` | FastAPI 应用入口；路由（演示文稿 CRUD、规划、生成、上传、API Key、用户等）；CORS、静态文件、中间件。 |
| `llm_planner.py` | 调用大模型生成 PPT 大纲与每页视觉描述（prompt）；支持「全文规划」与「插入模式」；依赖 `API_KEY`、`BASE_URL`、`MODEL_LOGIC`。 |
| `image_gen.py` | 调用视觉模型生成单页幻灯片图片；支持新建/修改/插入；依赖 `API_KEY`、`BASE_URL`、`MODEL_IMAGE`。 |
| `repository.py` | 数据访问层：演示文稿、幻灯片、版本、用户、积分、配置等 CRUD；不直接处理 HTTP。 |
| `database.py` | SQLAlchemy 引擎与会话；表初始化与迁移；种子数据（默认管理员、系统配置等）。 |
| `models.py` | ORM 模型定义（Presentation、Slide、SlideVersion、User、Admin 等）。 |
| `file_handler.py` | 上传文档解析：PDF、DOCX、TXT、MD 等，提取文本供规划阶段使用。 |
| `auth.py` | 认证与鉴权（如 JWT 或 Session），供需要登录的路由使用。 |

### 生成流程（二阶段）

1. **规划阶段**：前端调用 `/ppt/plan`（或等价），后端使用 `LLMPlanner` 根据主题与可选文档内容，生成结构化大纲和每页的视觉 prompt。
2. **渲染阶段**：前端按页请求生成（或批量），后端使用 `ImageGenerator` 对每页调用图像模型，保存到 `storage/images/{session_id}/`，并在 DB 中写入 `SlideVersion` 记录。
3. **版本管理**：每张幻灯片对应多条 `SlideVersion`，通过 `active_version_id` 指向当前展示版本；支持切换历史版本。

## 前端核心模块

| 路径 | 职责 |
|------|------|
| `web/src/views/` | 页面级组件：创建页（Creator）、编辑器（EditorView）、我的作品（MyWorksView）、画廊预览（GalleryPreviewView）等。 |
| `web/src/components/` | 可复用组件：编辑器画布、缩略图条（FilmStrip）、版本选择、登录/导航等。 |
| `web/src/stores/` | Pinia 状态：演示文稿列表、当前编辑的幻灯片与版本、用户状态等。 |
| `web/src/js/services/` | API 封装：请求后端接口（presentations、plan、generate、upload 等）。 |
| `web/src/config.js` | 前端配置入口，如 `VITE_API_BASE_URL`。 |

前端通过 `VITE_API_BASE_URL`（或代理 `/api`）与后端通信；生产部署时需确保该地址指向实际后端。

## 数据流示例：从「创建」到「生成一页」

1. 用户在前端输入主题（可选上传文档）→ 前端调用规划接口。
2. 后端 `llm_planner` 返回大纲与每页 prompt → 前端展示大纲，用户确认或编辑。
3. 用户点击「生成」→ 前端按页或批量请求 `generate_slide`。
4. 后端对每一页调用 `image_gen`，写入 `SlideVersion` 与图片文件 → 返回图片 URL 与版本信息。
5. 前端更新 Pinia 与 UI，展示新生成的幻灯片；用户可切换版本或触发「修改后重新生成」。

## 扩展与二次开发建议

- **更换模型/API**：修改 `backend/.env` 中的 `BASE_URL`、`MODEL_LOGIC`、`MODEL_IMAGE`；若协议与 GeekAI API 兼容，通常只需改配置；否则需适配 `llm_planner.py` 与 `image_gen.py` 的调用方式。
- **新增字段或表**：在 `models.py` 中扩展，在 `database.py` 中增加迁移逻辑，在 `repository.py` 与 `main.py` 中暴露读写。
- **前端定制**：可修改 `web/.env.sample` 中的 `VITE_TITLE`、`VITE_LOGO` 等，或增加新页面/路由与后端新接口对接。
