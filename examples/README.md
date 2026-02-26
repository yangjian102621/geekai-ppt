# 示例与教学资源

本目录用于存放与项目相关的示例文件，便于理解数据格式与流程。

## 内容说明

- **会话/幻灯片结构**：后端使用 SQLite 存储演示文稿与幻灯片元数据，图片保存在 `backend/storage/images/{presentation_id}/`。若需了解「单次生成」对应的数据结构，可参考 API 返回的 JSON（如 `GET /presentations/{id}` 或幻灯片列表）。
- **截图与效果图**：可在本目录或 `docs/screenshots/` 下放置界面截图、生成效果示例，用于 README 或文档展示（请勿提交过大或涉密图片）。
- **自定义提示词**：若你修改了 `docs/system_prompt.md` 或后端中的 prompt 常量，可在此保存一份「示例 prompt → 效果」说明，便于教学与复现。

## 使用建议

- 克隆仓库后，可直接按照主 README 的「快速开始」运行项目，用真实 API 生成一份演示文稿，即可得到完整的数据流体验。
- 二次开发时，可参考 [docs/architecture.md](../docs/architecture.md) 了解模块划分与数据流。
