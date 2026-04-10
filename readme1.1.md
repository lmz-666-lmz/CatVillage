# CatVillage v1.1 升级对比说明（基于 Git）

生成时间：2026-04-10

## 1. 对比基线

本说明基于当前工作区的 Git 变更生成，包含两部分：

1. 已跟踪文件改动：`git diff --stat` / `git diff --name-status`
2. 新增未跟踪文件：`git ls-files --others --exclude-standard`

## 2. 变更规模总览

### 2.1 已跟踪文件改动（未提交）

- 变更文件数：23
- 新增行数：1805
- 删除行数：683
- 变更类型：全部为 `M`（修改）

### 2.2 新增未跟踪文件

- 新增文件数：22

## 3. 本次升级重点（按模块归类）

### 3.1 前端功能扩展（主升级）

新增多个页面与组件，用户中心和猫咪管理能力明显增强：

- 新增页面：
	- `frontpoint/src/views/WelcomeView.vue`
	- `frontpoint/src/views/SettingsView.vue` 及 6 个子页面（账号、安全、隐私、通知、历史、关于、协议）
	- `frontpoint/src/views/MyPetsView.vue`
	- `frontpoint/src/views/MyFavoritesView.vue`
	- `frontpoint/src/views/AddFriendView.vue`
	- `frontpoint/src/views/AudioHistoryView.vue`
	- `frontpoint/src/views/FeedRecordView.vue`
	- `frontpoint/src/views/ProfessionalDoctorsView.vue`
	- `frontpoint/src/views/ProfileView.vue`
- 新增组件：
	- `frontpoint/src/components/PostCard.vue`
	- `frontpoint/src/components/ai/MessageBubble.vue`
- 新增用户展示资料工具：
	- `frontpoint/src/utils/userProfile.ts`

### 3.2 路由与现有页面重构

以下核心页面/模块存在较大修改，显示本次升级不只是“新增页面”，也包括“原有体验重做”：

- 路由：`frontpoint/src/router/index.ts`
- AI 与消息相关：
	- `frontpoint/src/views/AIAssistantView.vue`
	- `frontpoint/src/views/ChatDetailView.vue`
	- `frontpoint/src/views/MessagesView.vue`
	- `frontpoint/src/composables/useAIAssistant.ts`
	- `frontpoint/src/composables/useMessaging.ts`
	- `frontpoint/src/api/message.ts`
	- `backend/app/api/v1/message.py`
- 猫咪资料与健康相关：
	- `frontpoint/src/views/CatArchiveView.vue`
	- `frontpoint/src/views/CatsView.vue`
	- `frontpoint/src/views/AddCatView.vue`
	- `frontpoint/src/views/EditCatView.vue`
	- `frontpoint/src/views/EmotionsView.vue`
	- `frontpoint/src/api/health.ts`
- 社区相关：
	- `frontpoint/src/views/SocialView.vue`
	- `frontpoint/src/views/SocialDetailView.vue`
	- `frontpoint/src/views/CreatePostView.vue`
- 账号登录相关：
	- `frontpoint/src/views/LoginView.vue`
	- `frontpoint/src/views/RegisterView.vue`
	- `frontpoint/src/views/UserProfileView.vue`

### 3.3 开发与运维辅助

- 新增本地调试配置：`.vscode/launch.json`
- 新增后端数据辅助脚本：
	- `backend/_check_counts.py`（表记录数检查）
	- `backend/_clear_pet_data.py`（清理宠物相关数据）
- 新增资源文件：`backend/uploads/social/c48db6d33ff54c4f9e340173eb39ba4a.jpg`

## 4. 文件清单

### 4.1 已跟踪并修改的文件（23）

1. `backend/app/api/v1/message.py`
2. `frontpoint/src/api/health.ts`
3. `frontpoint/src/api/message.ts`
4. `frontpoint/src/composables/useAIAssistant.ts`
5. `frontpoint/src/composables/useMessaging.ts`
6. `frontpoint/src/mock/mockAI.ts`
7. `frontpoint/src/router/index.ts`
8. `frontpoint/src/types/message.ts`
9. `frontpoint/src/utils/index.ts`
10. `frontpoint/src/views/AIAssistantView.vue`
11. `frontpoint/src/views/AddCatView.vue`
12. `frontpoint/src/views/CatArchiveView.vue`
13. `frontpoint/src/views/CatsView.vue`
14. `frontpoint/src/views/ChatDetailView.vue`
15. `frontpoint/src/views/CreatePostView.vue`
16. `frontpoint/src/views/EditCatView.vue`
17. `frontpoint/src/views/EmotionsView.vue`
18. `frontpoint/src/views/LoginView.vue`
19. `frontpoint/src/views/MessagesView.vue`
20. `frontpoint/src/views/RegisterView.vue`
21. `frontpoint/src/views/SocialDetailView.vue`
22. `frontpoint/src/views/SocialView.vue`
23. `frontpoint/src/views/UserProfileView.vue`

### 4.2 新增未跟踪文件（22）

1. `.vscode/launch.json`
2. `backend/_check_counts.py`
3. `backend/_clear_pet_data.py`
4. `backend/uploads/social/c48db6d33ff54c4f9e340173eb39ba4a.jpg`
5. `frontpoint/src/components/PostCard.vue`
6. `frontpoint/src/components/ai/MessageBubble.vue`
7. `frontpoint/src/utils/userProfile.ts`
8. `frontpoint/src/views/AddFriendView.vue`
9. `frontpoint/src/views/AudioHistoryView.vue`
10. `frontpoint/src/views/FeedRecordView.vue`
11. `frontpoint/src/views/MyFavoritesView.vue`
12. `frontpoint/src/views/MyPetsView.vue`
13. `frontpoint/src/views/ProfessionalDoctorsView.vue`
14. `frontpoint/src/views/ProfileView.vue`
15. `frontpoint/src/views/SettingsAboutView.vue`
16. `frontpoint/src/views/SettingsAccountView.vue`
17. `frontpoint/src/views/SettingsHistoryView.vue`
18. `frontpoint/src/views/SettingsNotificationView.vue`
19. `frontpoint/src/views/SettingsPolicyView.vue`
20. `frontpoint/src/views/SettingsPrivacyView.vue`
21. `frontpoint/src/views/SettingsView.vue`
22. `frontpoint/src/views/WelcomeView.vue`

## 5. 升级结论

本次 v1.1 升级属于“中大型版本更新”，特点如下：

- 用户侧：新增欢迎页、设置中心、我的萌宠、我的收藏、加好友、音频历史、投喂记录、专业医生等完整功能入口。
- 产品侧：围绕“猫咪档案 + 社区 + AI + 健康记录”形成更完整闭环。
- 技术侧：前端页面与路由改动集中，后端消息接口有同步调整，并增加了数据运维脚本支持。

---

如果你需要，我可以在下一版把这个文件再补成“可发布公告版”（对外口吻），或者“提测版”（附测试点清单）。
