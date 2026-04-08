import request from '@/utils/request';
import type { 
  ChatWithAIRequest,
  ChatWithAIResponse,
  ChatHistoryRequest,
  ChatHistoryEntry,
  ChatHistoryResponse,
  ClearSessionResponse,
  EmergencyHelpRequest,
  EmergencyHelpResponse
} from '@/types/aiAssistant';
import type { ApiResponse } from '@/types';

type BackendChatResponse = {
  pet_id: string;
  reply: string;
  used_context?: {
    breed?: string | null;
    age?: number | null;
    latest_weight?: number | null;
  };
};

type BackendHistoryItem = ChatHistoryEntry;

type BackendHistoryResponse = {
  total: number;
  list: BackendHistoryItem[];
};

const toChatMessage = (data: BackendChatResponse): ChatWithAIResponse => ({
  id: `ai-${Date.now()}`,
  sessionId: data.pet_id,
  message: data.reply,
  role: 'assistant',
  timestamp: new Date().toISOString()
});

// 发起对话提问
export function chatWithAI(data: ChatWithAIRequest): Promise<ApiResponse<ChatWithAIResponse>> {
  return request<BackendChatResponse>({
    url: '/ai-assistant/chat',
    method: 'post',
    // AI 响应通常超过 10s；覆盖全局 axios timeout，避免前端 0B/挂起
    timeout: 60000,
    data: {
      pet_id: data.catId,
      user_message: data.message
    }
  }).then((response) => ({
    ...response,
    data: toChatMessage(response.data)
  }));
}

// 获取对话历史
export function getChatHistory(params: ChatHistoryRequest): Promise<ApiResponse<ChatHistoryResponse>> {
  const skip = Math.max(0, (params.page - 1) * params.pageSize);
  const limit = Math.max(1, params.pageSize);

  return request<BackendHistoryResponse>({
    url: '/ai-assistant/history',
    method: 'get',
    params: {
      pet_id: params.catId,
      skip,
      limit
    }
  }).then((response) => ({
    ...response,
    data: {
      list: response.data.list,
      total: response.data.total,
      page: params.page,
      pageSize: params.pageSize
    }
  }));
}

// 结束/清空会话
export function clearSession(sessionId: string): Promise<ApiResponse<ClearSessionResponse>> {
  return request<{ success: boolean }>({
    url: `/ai-assistant/sessions/${sessionId}`,
    method: 'delete'
  }).then((response) => ({
    ...response,
    data: {
      success: response.data.success
    }
  }));
}

// 一键求助（通过健康预警）
export function emergencyHelp(data: EmergencyHelpRequest): Promise<ApiResponse<EmergencyHelpResponse>> {
  return request<{ success: boolean; advice: string; next_steps: string[] }>({
    url: `/ai-assistant/emergency-help/${data.warningId}`,
    method: 'post',
    data
  }).then((response) => ({
    ...response,
    data: {
      success: response.data.success,
      advice: response.data.advice,
      nextSteps: response.data.next_steps
    }
  }));
}