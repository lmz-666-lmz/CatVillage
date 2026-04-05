import { mockCats, getMockCatList, getMockCatDetail, mockUpdateCatProfile, mockAddCat } from './mockCats';
import { 
  mockDynamics, 
  mockComments,
  getMockUserProfile, 
  getMockComments, 
  mockLikeDynamic, 
  mockAddComment,
  getMockSocialFeeds
} from './mockSocial';
import { 
  mockConversations, 
  getMockFriendsList, 
  getMockMessageList, 
  getMockConversations, 
  mockSendMessage,
  mockRevokeMessage,
  mockUpdateReadStatus
} from './mockMessages';
import { 
  getMockChatHistory, 
  mockClearSession, 
  mockEmergencyHelp,
  mockChatWithAI
} from './mockAI';
import { 
  getMockEmotionRecords, 
  getMockEmotionRecordDetail, 
  getMockEmotionStatistics, 
  getMockWarningList, 
  mockMarkWarningStatus,
  getMockWeeklyReport,
  mockRecognizeEmotion
} from './mockEmotion';

// 导入类型定义
import type { CatProfile } from '@/types';
import type { ChatWithAIRequest } from '@/types/aiAssistant';

export class MockHandler {
  // 猫咪相关API
  public async getCatList() {
    return await getMockCatList();
  }

  public async getCatDetail(catId: string) {
    return await getMockCatDetail(catId);
  }

  public async updateCatProfile(catId: string, data: Partial<CatProfile>) {
    return await mockUpdateCatProfile(catId, data);
  }

  public async addCat(data: Omit<CatProfile, 'id' | 'userId' | 'createdAt' | 'updatedAt'>) {
    return await mockAddCat(data);
  }

  public async deleteCatProfile(catId: string) {
    const index = mockCats.findIndex((cat) => cat.id === catId);
    if (index === -1) {
      throw new Error('猫咪不存在');
    }
    mockCats.splice(index, 1);
    return { data: { success: true } };
  }

  // 社交相关API
  public async getSocialFeeds(params: { page: number; pageSize: number; catId?: string }) {
    return await getMockSocialFeeds(params);
  }

  public async getUserProfile(userId: string) {
    return await getMockUserProfile(userId);
  }

  public async getComments(dynamicId: string) {
    return await getMockComments(dynamicId);
  }

  public async getDynamicDetail(dynamicId: string) {
    const dynamic = mockDynamics.find((item) => item.id === dynamicId);
    if (!dynamic) {
      throw new Error('动态不存在');
    }
    return { data: dynamic };
  }

  public async likeDynamic(dynamicId: string) {
    return await mockLikeDynamic(dynamicId);
  }

  public async unlikeDynamic(dynamicId: string) {
    // Unlike 实际上就是取消点赞，我们可以简单地调用 like 功能
    return await mockLikeDynamic(dynamicId);
  }

  public async postComment(dynamicId: string, content: string) {
    return await mockAddComment(dynamicId, content);
  }

  public async deleteComment(commentId: string) {
    // 找到要删除的评论
    const commentIndex = mockComments.findIndex(comment => comment.id === commentId);
    if (commentIndex !== -1) {
      mockComments.splice(commentIndex, 1);
      return { data: { success: true } };
    } else {
      throw new Error('评论不存在');
    }
  }

  // 消息相关API
  public async getFriendsList(params: { page: number; pageSize: number }) {
    return await getMockFriendsList(params);
  }

  public async getMessages(conversationId: string, params: { page: number; pageSize: number }) {
    // conversationId 实际上是目标用户ID
    return await getMockMessageList({ targetUserId: conversationId, ...params });
  }

  public async getConversations() {
    return await getMockConversations();
  }

  public async sendMessage(targetUserId: string, content: string) {
    return await mockSendMessage(targetUserId, content);
  }

  public async sendQuickMeow(targetUserId: string, meowType: string) {
    // 快速喵语本质上也是发送消息，只是内容是预设的
    return await mockSendMessage(targetUserId, `[快速喵语] ${meowType}`);
  }

  public async deleteConversation(conversationId: string) {
    // 找到要删除的会话
    const conversationIndex = mockConversations.findIndex(conv => conv.id === conversationId);
    if (conversationIndex !== -1) {
      mockConversations.splice(conversationIndex, 1);
      return { data: { success: true } };
    } else {
      throw new Error('会话不存在');
    }
  }

  public async revokeMessage(messageId: string) {
    return await mockRevokeMessage(messageId);
  }

  public async updateReadStatus(messageIds: string[]) {
    return await mockUpdateReadStatus(messageIds);
  }

  // AI助手相关API
  public async chatWithAI(data: ChatWithAIRequest) {
    return await mockChatWithAI(data);
  }

  public async getChatHistory(params: { sessionId?: string; catId?: string; page: number; pageSize: number }) {
    return await getMockChatHistory(params);
  }

  public async clearSession(sessionId: string) {
    return await mockClearSession(sessionId);
  }

  public async emergencyHelp(warningId: string) {
    return await mockEmergencyHelp(warningId);
  }

  // 情绪分析相关API
  public async recognizeEmotion(data: File) {
    return await mockRecognizeEmotion(data);
  }

  public async getEmotionRecords(params: { page: number; pageSize: number; catId?: string }) {
    return await getMockEmotionRecords(params);
  }

  public async getEmotionRecordDetail(recordId: string) {
    return await getMockEmotionRecordDetail(recordId);
  }

  public async getEmotionStatistics(params: { catId?: string; startDate?: string; endDate?: string }) {
    return await getMockEmotionStatistics(params);
  }

  public async getWarningList(params: { page: number; pageSize: number; catId?: string; status?: string }) {
    return await getMockWarningList(params);
  }

  public async markWarningStatus(warningId: string, status: string) {
    return await mockMarkWarningStatus(warningId, status);
  }

  public async getWeeklyReport(params: { catId?: string; week?: string }) {
    return await getMockWeeklyReport(params);
  }
}

// 创建全局实例
const mockHandler = new MockHandler();

export { mockHandler };