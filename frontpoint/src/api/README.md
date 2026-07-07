# API 服务使用说明

前端运行时统一通过 `src/utils/request.ts` 调用真实后端 API，默认 `baseURL` 为 `/api/v1`，生产环境建议由 Nginx 反向代理到 FastAPI。

当前 API 模块：

- `auth.ts`：登录、注册、资料更新、退出登录。
- `petProfile.ts`：猫咪档案增删改查。
- `social.ts`：动态、评论、点赞、收藏、关注、热门话题。
- `message.ts`：好友、会话、私信。
- `emotion.ts`：音频情绪识别、历史记录、统计、周报、授权音频播放。
- `aiAssistant.ts`：AI 问答、历史、清空会话、预警求助。
- `health.ts`：体重与投喂记录。
- `vision.ts`：视觉识别和视听融合。

`src/mock/` 保留为历史样例数据，不再参与运行时请求拦截。部署与联调均以真实后端接口为准。
