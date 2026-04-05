# Mock 数据服务使用说明

## 概述

Mock 数据服务是为了在后端 API 尚未完成或不可用时，提供模拟数据支持前端开发和测试。通过环境变量控制，可以灵活切换使用真实 API 或 Mock 数据。

## 环境变量配置

在 `.env` 文件中配置 Mock 服务开关：

```env
VITE_ENABLE_MOCK=true  # 启用 Mock 数据服务
# VITE_ENABLE_MOCK=false  # 使用真实 API（默认）
```

## 使用方法

### 1. 在 API 服务中使用

所有 API 服务函数都已经集成了 Mock 支持。只需设置环境变量 `VITE_ENABLE_MOCK=true`，API 调用将自动返回 Mock 数据。

```typescript
// 当 VITE_ENABLE_MOCK=true 时，此调用将返回 Mock 数据
const response = await getAllPetProfiles();
```

### 2. 在 Store 中使用

Store 中的方法也会根据环境变量自动使用 Mock 数据：

```typescript
const catsStore = useCatsStore();
// 当启用 Mock 时，此方法将获取 Mock 猫咪数据
await catsStore.fetchAllCats();
```

### 3. 在 Composables 中使用

Composables 中的方法同样支持 Mock 数据：

```typescript
const { getAllCats, createCat } = useCatManagement();
// 当启用 Mock 时，这些方法将使用 Mock 数据
const cats = getAllCats.value;
await createCat(mockCatData);
```

## Mock 数据结构

### 猫咪档案 Mock 数据

- 包含 id、name、breed、age 等基本信息
- 包含医疗历史、疫苗状态等健康信息
- 模拟真实猫咪档案数据

### 社交功能 Mock 数据

- 包含动态内容、图片、视频等
- 包含点赞、评论、分享等交互数据
- 模拟用户社交行为

### 消息功能 Mock 数据

- 包含好友列表和用户信息
- 包含消息记录和会话历史
- 模拟实时消息交互

### 情绪分析 Mock 数据

- 包含情绪识别记录和音频URL
- 包含情绪标签和置信度
- 模拟健康预警信息

### AI助理 Mock 数据

- 包含对话历史和问答记录
- 模拟AI响应和建议
- 包含紧急求助功能

## 开发注意事项

1. **环境变量**：确保在开发环境中正确设置 `VITE_ENABLE_MOCK` 变量
2. **数据一致性**：Mock 数据应尽量贴近真实数据结构
3. **功能完整性**：Mock 实现应覆盖所有 API 功能点
4. **错误处理**：Mock 数据服务也应包含适当的错误处理

## 测试

启用 Mock 服务后，可以进行全面的前端功能测试，无需依赖后端服务。