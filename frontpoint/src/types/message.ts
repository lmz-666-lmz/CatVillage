// 消息功能相关类型定义

// 好友列表请求参数
export interface FriendListRequest {
  page: number;
  pageSize: number;
}

// 好友信息响应
export interface FriendResponse {
  id: string;
  userId: string;
  username: string;
  nickname: string;
  avatar: string;
  lastOnlineAt: string;
  isOnline: boolean;
}

// 发送消息请求
export interface SendMessageRequest {
  receiverId: string;
  content: string;
  messageType: 'text' | 'image' | 'audio' | 'quick_meow';
}

// 消息响应
export interface MessageResponse {
  id: string;
  senderId: string;
  receiverId: string;
  content: string;
  messageType: 'text' | 'image' | 'audio' | 'quick_meow';
  sentAt: string;
  status: 'sent' | 'delivered' | 'read';
}

// 会话列表请求参数
export interface ConversationListRequest {
  page: number;
  pageSize: number;
}

// 会话响应
export interface ConversationResponse {
  id: string;
  targetUserId: string;
  targetType: 'user' | 'cat'; // 与用户或猫咪的会话
  lastMessage: string;
  lastMessageType: 'text' | 'image' | 'audio' | 'quick_meow';
  unreadCount: number;
  updatedAt: string;
  avatar: string;
  nickname: string;
  isOnline: boolean;
}

// 获取会话历史消息请求参数
export interface ConversationMessagesRequest {
  targetUserId: string;
  page: number;
  pageSize: number;
}

// 获取会话历史消息响应
export interface ConversationMessagesResponse {
  list: MessageResponse[];
  total: number;
  page: number;
  pageSize: number;
}

// 发送快捷喵语请求
export interface SendQuickMeowRequest {
  receiverId: string;
  meowType: string;
}

// 更新消息已读状态请求
export interface UpdateReadStatusRequest {
  messageIds: string[];
}

// 消息撤回请求
export interface RevokeMessageRequest {
  messageId: string;
}

// 消息撤回响应
export interface RevokeMessageResponse {
  success: boolean;
}

// Backward-compatible aliases for older API/composable names.
export type Friend = FriendResponse;
export type Message = MessageResponse;
export type Conversation = ConversationResponse;
export type QuickMeowRequest = SendQuickMeowRequest;
export type FriendListResponse = {
  list: FriendResponse[];
  total: number;
};
export type SendMessageResponse = MessageResponse;
export type QuickMeowResponse = MessageResponse;
export type ConversationListResponse = {
  list: ConversationResponse[];
  total: number;
};
export interface UpdateReadStatusResponse {
  success: boolean;
}
export interface DeleteConversationResponse {
  success: boolean;
}