<div align="center">
  <img src="web/public/images/logo.png" alt="GeekAI-PPT Logo" width="200">

  # GeekAI-PPT

  **有逻辑，又有审美** - AI 驱动的智能 PPT 生成平台

  [![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
  [![GitHub Stars](https://img.shields.io/github/stars/yangjian102621/geekai-ppt)](https://github.com/yangjian102621/geekai-ppt/stargazers)
  [![GitHub Forks](https://img.shields.io/github/forks/yangjian102621/geekai-ppt)](https://github.com/yangjian102621/geekai-ppt/network/members)
  [![GitHub Issues](https://img.shields.io/github/issues/yangjian102621/geekai-ppt)](https://github.com/yangjian102621/geekai-ppt/issues)
</div>

---

基于 AI 的 PPT 生成平台，通过自然语言描述或上传文档，快速生成具有现代科技美学的演示文稿。
_AI-powered presentation generator with modern tech aesthetics (FastAPI + Vue 3 + Gemini)._

## ✨ 功能特性

- **AI 驱动创作**：输入主题即可由 AI 自动规划大纲并生成幻灯片
- **文档智能解析**：支持上传 PDF、DOCX、TXT、MD 等格式，提取内容作为生成上下文
- **多版本管理**：每张幻灯片支持多版本历史，可回溯或切换不同版本
- **视觉风格统一**：采用现代科技/互联网风格，前后幻灯片风格保持连贯
- **灵活的编辑能力**：支持插入、删除、重排幻灯片，以及基于现有幻灯片的修改生成
- **回收站与恢复**：演示文稿和幻灯片支持软删除与恢复

## 🔗 在线体验与文档

- **在线文档**：[`https://docs.geekai.me/ppt`](https://docs.geekai.me/ppt)
- **在线演示**：[`https://ppt.geekai.pro`](https://ppt.geekai.pro)

## 🛠 技术栈

| 层级 | 技术                                                       |
| ---- | ---------------------------------------------------------- |
| 后端 | FastAPI、SQLAlchemy、GeekAI API（Google Gemini 模型）      |
| 前端 | Vue 3、Vite、TypeScript、Pinia、Element Plus、Tailwind CSS |
| 存储 | SQLite、本地文件（会话、图片）                             |

## 📦 快速开始

### 环境要求

- Python 3.9+
- Node.js 18+
- [GeekAI](https://geekai.pro/) API Key（用于调用 Gemini 模型，项目默认推荐）

### 1. 克隆项目

```bash
git clone <repository-url>
cd geekai-ppt
```

### 2. 启动后端

```bash
cd backend
pip install -r requirements.txt
python main.py
```

后端默认运行在 `http://localhost:8002`

### 3. 启动前端

```bash
cd web
npm install
npm run dev
```

前端默认运行在 `http://localhost:3000`

### 4. 配置环境变量

- **后端**：复制示例配置并填写 API Key 等（必填项见下方说明）。
  ```bash
  cp backend/.env.sample backend/.env
  # 编辑 backend/.env，至少填写 API_KEY
  ```
- **前端**：如需自定义 API 地址或应用信息，可复制并编辑：
  ```bash
  cp web/.env.sample web/.env
  ```
- 首次使用可在应用内配置 API Key，或直接在 `backend/.env` 中设置。

**示例后端配置（使用 GeekAI 中转，可按需替换为其他兼容 Gemini API 协议的服务）**：

```env
API_KEY=sk-or-v1-xxxxxxxx
BASE_URL=https://api.geekai.pro
MODEL_LOGIC=gemini-3-pro-preview
MODEL_IMAGE=gemini-3-pro-image-preview
PORT=8002
```

**常见问题**：

- 端口冲突：后端默认 `8002`、前端默认 `3000`，可在 `backend/.env` 中修改 `PORT`，前端通过 `VITE_API_BASE_URL` 指向后端。
- API Key 无效：请确认 `backend/.env` 中 `API_KEY` 与 `BASE_URL` 配置正确；使用 GeekAI 时推荐将 `BASE_URL` 设置为 `https://api.geekai.pro`。也可以改为任意兼容 Gemini API 协议的服务地址。
- 生成失败：检查后端日志；若为模型或配额限制，可更换 `MODEL_LOGIC` / `MODEL_IMAGE` 或上游模型服务提供商。

> ⚠️ `.env` 包含敏感信息，请勿提交到版本控制。仓库中仅提供 `.env.sample` 作为模板。

## ⚙️ 环境配置说明

各配置项含义与获取方式见：

- **后端**：[backend/.env.sample](backend/.env.sample) — `API_KEY`（必填）、`BASE_URL`、`MODEL_LOGIC`、`MODEL_IMAGE`、`PORT`
- **前端**：[web/.env.sample](web/.env.sample) — `VITE_API_BASE_URL`、应用标题/Logo/版本等可选项

## 📁 项目结构

```
geekai-ppt/
├── backend/                 # FastAPI 后端
│   ├── main.py             # 应用入口与 API 路由
│   ├── llm_planner.py      # LLM 大纲规划
│   ├── image_gen.py        # 图片生成（Gemini 视觉模型）
│   ├── file_handler.py     # 文档解析（PDF/DOCX/TXT/MD）
│   ├── repository.py       # 数据持久化与会话逻辑
│   ├── database.py         # 数据库初始化与迁移
│   └── storage/            # 运行时数据
│       ├── sessions/       # 会话 JSON
│       └── images/         # 生成的幻灯片图片
├── web/                    # Vue 3 前端
│   └── src/
│       ├── views/          # 页面（Creator、EditorView、MyWorksView）
│       ├── components/     # 组件（编辑器、缩略图、版本历史等）
│       ├── stores/         # Pinia 状态管理
│       ├── js/services/    # API 客户端
│       └── locale/         # 国际化
├── build/                  # 构建与 Docker
│   ├── build.sh            # 镜像构建与推送脚本
│   ├── dockerfile-api      # 后端镜像
│   └── dockerfile-web      # 前端镜像
├── docs/                   # 文档（含 architecture.md 架构说明）
└── examples/               # 示例与教学资源
```

更多模块说明与数据流见 [docs/architecture.md](docs/architecture.md)。

## 🔧 开发命令

### 后端

| 命令                                                                 | 说明                   |
| -------------------------------------------------------------------- | ---------------------- |
| `cd backend && pip install -r requirements.txt`                      | 安装依赖               |
| `cd backend && python main.py`                                       | 启动开发服务           |
| `cd backend && uvicorn main:app --host 0.0.0.0 --port 8002 --reload` | 热更新启动             |
| `cd backend && bash start.sh`                                        | 一键创建虚拟环境并启动 |

### 前端

| 命令                        | 说明             |
| --------------------------- | ---------------- |
| `cd web && npm install`     | 安装依赖         |
| `cd web && npm run dev`     | 启动开发服务     |
| `cd web && npm run build`   | 生产构建         |
| `cd web && npm run preview` | 本地预览构建产物 |

## 🏗 架构说明

### 生成流程

1. **规划阶段**：LLM 根据主题与上下文生成结构化大纲和视觉描述
2. **渲染阶段**：Gemini 视觉模型根据 prompt 生成每张幻灯片图片
3. **版本管理**：每次生成结果作为新版本保存，支持切换与回溯

### 主要 API

- 演示文稿：`/presentations` CRUD、回收站
- 大纲规划：`/ppt/plan` 生成大纲
- 幻灯片生成：`/ppt/generate_slide` 创建/修改/插入幻灯片
- API Key：`/api/key/*` 配置与验证
- 文档上传：`/upload/doc` 解析上传文档

### 存储说明

- 使用 SQLite 存储演示文稿、幻灯片及版本元数据
- 生成的图片保存在 `storage/images/{session_id}/`
- 部署时需确保 `storage/` 目录可写

## 🐳 Docker 构建与部署

默认仅支持 **amd64** 架构。构建并推送镜像到阿里云仓库后，在服务器上通过 docker-compose 拉取并运行。

### Base 镜像（加速 API 构建）

API 镜像基于 `geekai-ppt-api-base:latest` 构建，该镜像已包含 Python 运行时、系统依赖（如 poppler-utils）和 pip 依赖，日常构建 API 时不再重复下载安装依赖，速度更快。

- **仅在依赖变更时**（修改 `backend/requirements.txt` 或基础系统依赖）需要重新构建并推送 base 镜像：
  ```bash
  cd build
  ./build-base.sh        # 仅构建 base 镜像
  ./build-base.sh push   # 构建并推送到阿里云
  ```
- 全新环境（如 CI 或新机器）首次构建 API 前，需先本地执行 `./build-base.sh` 或从仓库拉取 base 镜像：
  ```bash
  docker pull registry.cn-shenzhen.aliyuncs.com/geekmaster/geekai-ppt-api-base:latest
  ```

### 1. 构建镜像并推送到阿里云

在 `build/` 目录下执行：

```bash
cd build
# 依赖未变更时，直接构建即可
./build.sh <版本号>        # 仅构建，例如 ./build.sh v1.0.0
./build.sh <版本号> push   # 构建并推送到 registry.cn-shenzhen.aliyuncs.com/geekmaster/
```

**构建说明**：

- **前端构建**：`build.sh` 会自动在本地执行 `cd ../web && npm run build`，然后将构建产物 `web/dist` 复制到 Docker 镜像中，避免在 Docker 内构建，节省时间。
- **API 构建**：若本次修改了 `backend/requirements.txt`，请先执行 `./build-base.sh` 或 `./build-base.sh push`，再执行上述 `build.sh`。

示例：

```bash
./build.sh v1.0.0          # 构建 geekai-ppt-api:v1.0.0 和 geekai-ppt-web:v1.0.0
./build.sh v1.0.0 push     # 构建后推送到阿里云镜像仓库
```

推送前请先登录镜像仓库：`docker login registry.cn-shenzhen.aliyuncs.com`。

### 2. 服务器上拉取并部署

在已安装 Docker 和 Docker Compose 的服务器上：

1. 将项目中的 `docker-compose.yaml` 放到部署目录。
2. 在部署目录创建 `.env`，配置 API Key 与 Base URL：

```env
API_KEY=your_api_key_here
BASE_URL=https://api.geekai.pro
```

3. 若构建时使用了非 `v1.0.0` 的版本号，请修改 `docker-compose.yaml` 中两处镜像 tag（`geekai-ppt-api` 与 `geekai-ppt-web` 的 tag）与之一致。
4. 拉取并启动：

```bash
docker-compose pull
docker-compose up -d
```

5. 访问：Web 为 `http://<服务器IP>`，API 为 `http://<服务器IP>:8002`。数据持久化在 compose 中配置的 volume（默认 `./data/storage`）。

### 3. 常用命令

| 命令                     | 说明           |
| ------------------------ | -------------- |
| `docker-compose pull`    | 拉取最新镜像   |
| `docker-compose up -d`   | 后台启动       |
| `docker-compose down`    | 停止并删除容器 |
| `docker-compose logs -f` | 查看日志       |

## 🤝 贡献与社区

欢迎提交 Issue 与 Pull Request。参与前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解开发环境与提交流程。

**自部署与线上服务**：本仓库为可自部署的开源版本，聚焦核心 PPT 生成能力。若未来提供线上 SaaS 服务，可能包含额外的管理、监控或团队协作功能，届时会另行说明。功能规划见 [ROADMAP.md](ROADMAP.md)；二次开发与教学可参考 [docs/development-guide.md](docs/development-guide.md)。

## 📄 许可

本项目采用 [MIT License](LICENSE)。详见项目根目录下的 `LICENSE` 文件。
