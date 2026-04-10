/* eslint-disable @typescript-eslint/no-explicit-any */

import { ref, computed } from 'vue';
import type { 
  Friend, 
  Conversation,
  SendMessageRequest,
  QuickMeowRequest
} from '@/types/message';
import { 
  getFriendList, 
  getFollowerList,
  sendMessage, 
  revokeMessage, 
  updateReadStatus, 
  sendQuickMeow,
  getConversationList,
  getConversationMessages,
  deleteConversation
} from '@/api/message';

/**
 * 消息功能 Composable
 * 提供好友管理、消息发送、会话管理等操作方法
 */
export function useMessaging() {
  const loading = ref(false);
  const error = ref<string | null>(null);
  const friends = ref<Friend[]>([]);
  const followers = ref<Friend[]>([]);
  const conversations = ref<Conversation[]>([]);

  /**
   * 获取好友列表
   */
  const fetchFriendList = async (params: { page: number; pageSize: number; keyword?: string }) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await getFriendList(params);
      friends.value = response.data.list || [];
      return response.data;
    } catch (err: any) {
      error.value = err.message || '获取好友列表失败';
      console.error('获取好友列表失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const fetchFollowerList = async (params: { page: number; pageSize: number }) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await getFollowerList(params);
      followers.value = response.data.list || [];
      return response.data;
    } catch (err: any) {
      error.value = err.message || '获取粉丝列表失败';
      console.error('获取粉丝列表失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 发送消息
   */
  const sendNewMessage = async (messageData: SendMessageRequest) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await sendMessage(messageData);
      return response.data;
    } catch (err: any) {
      error.value = err.message || '发送消息失败';
      console.error('发送消息失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 撤回消息
   */
  const revokeAMessage = async (messageId: string) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await revokeMessage(messageId);
      return response.data;
    } catch (err: any) {
      error.value = err.message || '撤回消息失败';
      console.error('撤回消息失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 更新消息已读状态
   */
  const markAsRead = async (messageIds: string[]) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await updateReadStatus({ messageIds });
      return response.data;
    } catch (err: any) {
      error.value = err.message || '更新已读状态失败';
      console.error('更新已读状态失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 发送快捷喵语
   */
  const sendQuickMeowMessage = async (receiverId: string, meowType: string) => {
    loading.value = true;
    error.value = null;

    try {
      const requestData: QuickMeowRequest = { receiverId, meowType };
      const response = await sendQuickMeow(requestData);
      return response.data;
    } catch (err: any) {
      error.value = err.message || '发送快捷喵语失败';
      console.error('发送快捷喵语失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 获取会话列表
   */
  const fetchConversationList = async (params: { page: number; pageSize: number }) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await getConversationList(params);
      conversations.value = response.data.list || [];
      return response.data;
    } catch (err: any) {
      error.value = err.message || '获取会话列表失败';
      console.error('获取会话列表失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 获取会话历史消息
   */
  const fetchConversationMessages = async (targetUserId: string, params: { page: number; pageSize: number }) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await getConversationMessages(targetUserId, params);
      return response.data;
    } catch (err: any) {
      error.value = err.message || '获取会话消息失败';
      console.error('获取会话消息失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 删除会话
   */
  const removeConversation = async (targetUserId: string) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await deleteConversation(targetUserId);
      // 从本地会话列表中移除
      conversations.value = conversations.value.filter(conv => conv.targetUserId !== targetUserId);
      return response.data;
    } catch (err: any) {
      error.value = err.message || '删除会话失败';
      console.error('删除会话失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 获取当前好友列表
   */
  const getCurrentFriends = computed(() => friends.value);
  const getCurrentFollowers = computed(() => followers.value);

  /**
   * 获取当前会话列表
   */
  const getCurrentConversations = computed(() => conversations.value);

  /**
   * 是否正在加载
   */
  const isLoading = computed(() => loading.value);

  /**
   * 获取错误信息
   */
  const getError = computed(() => error.value);

  return {
    // Methods
    fetchFriendList,
    fetchFollowerList,
    sendNewMessage,
    revokeAMessage,
    markAsRead,
    sendQuickMeowMessage,
    fetchConversationList,
    fetchConversationMessages,
    removeConversation,

    // Getters
    getCurrentFriends,
    getCurrentFollowers,
    getCurrentConversations,
    isLoading,
    getError
  };
}