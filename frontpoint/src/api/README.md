# API 服务使用说明

## 概述

API 服务层是前端与后端交互的桥梁，负责处理所有网络请求。该层集成了 Mock 数据支持，可以通过环境变量灵活切换使用真实 API 或 Mock 数据。

## 服务模块

### 1. 宠物档案管理服务 (petProfile.ts)

- `getAllPetProfiles()` - 获取所有猫咪档案
- `createPetProfile(data)` - 创建猫咪档案
- `updatePetProfile(catId, data)` - 更新猫咪档案
- `deletePetProfile(catId)` - 删除猫咪档案
- `getPetProfile(catId)` - 获取单个猫咪档案详情

### 2. 交友广场服务 (social.ts)

- `publishDynamic(data)` - 发布动态
- `getDynamicsList(params)` - 获取动态列表
- `getMyDynamicsList(params)` - 获取我的动态列表
- `getDynamicDetail(dynamicId)` - 获取动态详情
- `likeDynamic(dynamicId)` - 点赞动态
- `unlikeDynamic(dynamicId)` - 取消点赞
- `postComment(dynamicId, data)` - 发表评论
- `deleteComment(commentId)` - 删除评论
- `deleteDynamic(dynamicId)` - 删除动态

### 3. 好友消息服务 (message.ts)

- `getFriendList(params)` - 获取好友列表
- `sendMessage(data)` - 发送消息
- `revokeMessage(messageId)` - 撤回消息
- `updateReadStatus(data)` - 更新消息已读状态
- `sendQuickMeow(data)` - 发送快捷喵语
- `getConversationList(params)` - 获取会话列表
- `getConversationMessages(targetUserId, params)` - 获取会话消息
- `deleteConversation(targetUserId)` - 删除会话

### 4. 喵喵情绪台服务 (emotion.ts)

- `recognizeEmotion(data)` - 情绪识别
- `getEmotionRecords(params)` - 获取情绪记录
- `getEmotionRecordDetail(recordId)` - 获取情绪记录详情
- `getEmotionStatistics(params)` - 获取情绪统计数据
- `getWarningList(params)` - 获取健康预警列表
- `markWarningStatus(warningId, status)` - 标记预警状态
- `getWeeklyReport(params)` - 获取情绪周报

### 5. AI养育助理服务 (aiAssistant.ts)

- `chatWithAI(data)` - 与AI对话
- `getChatHistory(params)` - 获取对话历史
- `clearSession(sessionId)` - 清空会话
- `emergencyHelp(data)` - 紧急求助

## Mock 数据集成

所有 API 服务函数都已集成 Mock 数据支持：

```typescript
// 在 petProfile.ts 中的示例
export function getAllPetProfiles() {
  // 如果启用了Mock，则使用apiService
  if (import.meta.env.VITE_ENABLE_MOCK === 'true') {
    return apiService.getAllPetProfiles();
  }
  
  return request<CatProfileListResponse>({
    url: '/pet-profiles/list',
    method: 'get'
  });
}
```

## 环境变量配置

在 `.env` 文件中配置 API 基础 URL 和 Mock 服务：

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1  # API 基础 URL
VITE_ENABLE_MOCK=false  # 是否启用 Mock 数据服务
```

## 使用示例

### 在 Store 中使用

```typescript
// 在 cats.ts 中
actions: {
  async fetchAllCats() {
    this.loading = true;
    try {
      const response = await getAllPetProfiles(); // 自动根据环境变量选择真实API或Mock数据
      this.cats = response.data;
    } catch (error) {
      console.error('获取猫咪档案列表失败:', error);
    } finally {
      this.loading = false;
    }
  }
}
```

### 在 Composable 中使用

```typescript
// 在 useCatManagement.ts 中
export function useCatManagement() {
  const createCat = async (catData: CreateCatProfileRequest) => {
    try {
      // 使用 Store 中的方法，自动处理 API/Mock 切换
      const result = await useCatsStore().addCat(catData);
      return result;
    } catch (err) {
      console.error('创建猫咪档案失败:', err);
      throw err;
    }
  };
  
  return { createCat };
}
```

## 错误处理

API 服务层使用统一的错误处理机制，确保错误信息的一致性：

```typescript
// 在 utils/request.ts 中
request.interceptors.response.use(
  response => {
    const res = response.data;
    if (res.code !== 200) {
      console.error(res.msg);
      return Promise.reject(new Error(res.msg || 'Error'));
    } else {
      return res;
    }
  },
  error => {
    console.error(error);
    return Promise.reject(error);
  }
);
```

## 开发注意事项

1. **类型安全**：所有 API 函数都应使用 TypeScript 类型定义
2. **错误处理**：统一处理 API 调用错误
3. **Mock 支持**：确保所有 API 函数都能根据环境变量切换 Mock 数据
4. **响应格式**：遵循统一的响应格式 `{code, msg, data}`