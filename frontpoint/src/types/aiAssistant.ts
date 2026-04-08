// AI助理功能相关类型定义

// 与AI对话请求
export interface ChatWithAIRequest {
  catId: string;
  message: string;
  sessionId?: string; // 可选，会话ID，如果没有则创建新会话
}

// 与AI对话响应
export interface ChatWithAIResponse {
  id: string;
  sessionId: string;
  message: string;
  role: 'user' | 'assistant';
  timestamp: string;
}

export interface ChatHistoryEntry {
  id: string;
  pet_id: string;
  question: string;
  answer: string;
  created_at: string;
}

// 获取对话历史请求参数
export interface ChatHistoryRequest {
  catId: string;
  sessionId?: string; // 可选，会话ID，如果不提供则获取所有会话
  page: number;
  pageSize: number;
}

// 获取对话历史响应
export interface ChatHistoryResponse {
  list: ChatHistoryEntry[];
  total: number;
  page: number;
  pageSize: number;
}

// 清除会话请求
export interface ClearSessionRequest {
  sessionId: string;
}

// 清除会话响应
export interface ClearSessionResponse {
  success: boolean;
}

// 一键求助请求
export interface EmergencyHelpRequest {
  warningId: string;
  additionalInfo?: string; // 额外信息
}

// 一键求助响应
export interface EmergencyHelpResponse {
  success: boolean;
  advice: string; // 建议
  nextSteps: string[]; // 下一步操作
}

// AI助理会话类型
export interface AISession {
  id: string;
  catId: string;
  userId: string;
  title: string; // 会话标题，由AI根据首次提问生成
  createdAt: string;
  updatedAt: string;
}