/* eslint-disable @typescript-eslint/no-explicit-any */

import { ref, computed } from 'vue';
import type { 
  ChatWithAIRequest, 
  ChatWithAIResponse, 
  ChatHistoryRequest,
  EmergencyHelpRequest,
} from '@/types/aiAssistant';
import { 
  chatWithAI, 
  getChatHistory, 
  clearSession,
  emergencyHelp
} from '@/api/aiAssistant';

/**
 * AI助理 Composable
 * 提供AI对话、历史记录管理、紧急帮助等操作方法
 */
export function useAIAssistant() {
  const loading = ref(false);
  const error = ref<string | null>(null);
  const chatHistory = ref<ChatWithAIResponse[]>([]);

  /**
   * 发起AI对话
   */
  const sendMessageToAI = async (data: ChatWithAIRequest) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await chatWithAI(data);
      // 将新消息添加到历史记录
      chatHistory.value.push(response.data);
      return response.data;
    } catch (err: any) {
      error.value = err.message || 'AI对话请求失败';
      console.error('AI对话请求失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 获取对话历史
   */
  const fetchChatHistory = async (params: ChatHistoryRequest) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await getChatHistory(params);
      chatHistory.value = response.data.list || [];
      return response.data;
    } catch (err: any) {
      error.value = err.message || '获取对话历史失败';
      console.error('获取对话历史失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 清空会话
   */
  const clearCurrentSession = async (sessionId: string) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await clearSession(sessionId);
      // 清空本地聊天记录
      chatHistory.value = [];
      return response.data;
    } catch (err: any) {
      error.value = err.message || '清空会话失败';
      console.error('清空会话失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 一键求助
   */
  const requestEmergencyHelp = async (data: EmergencyHelpRequest) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await emergencyHelp(data);
      return response.data;
    } catch (err: any) {
      error.value = err.message || '紧急求助失败';
      console.error('紧急求助失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 获取当前聊天历史
   */
  const getCurrentChatHistory = computed(() => chatHistory.value);

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
    sendMessageToAI,
    fetchChatHistory,
    clearCurrentSession,
    requestEmergencyHelp,

    // Getters
    getCurrentChatHistory,
    isLoading,
    getError
  };
}