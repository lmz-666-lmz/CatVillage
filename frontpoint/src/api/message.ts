import request from '@/utils/request';
import type { 
  FriendListResponse,
  SendMessageRequest,
  SendMessageResponse,
  RevokeMessageResponse,
  UpdateReadStatusRequest,
  UpdateReadStatusResponse,
  QuickMeowRequest,
  QuickMeowResponse,
  ConversationListResponse,
  ConversationMessagesResponse,
  DeleteConversationResponse
} from '@/types/message';

// 获取好友列表
export function getFriendList(params: { page: number; pageSize: number }) {
  return request<FriendListResponse>({
    url: '/friends/list',
    method: 'get',
    params
  });
}

// 发送消息
export function sendMessage(data: SendMessageRequest) {
  return request<SendMessageResponse>({
    url: '/messages/send',
    method: 'post',
    data
  });
}

// 撤回消息
export function revokeMessage(messageId: string) {
  return request<RevokeMessageResponse>({
    url: `/messages/${messageId}/revoke`,
    method: 'put'
  });
}

// 更新消息已读状态
export function updateReadStatus(data: UpdateReadStatusRequest) {
  return request<UpdateReadStatusResponse>({
    url: '/messages/read-status',
    method: 'put',
    data
  });
}

// 发送快捷喵语
export function sendQuickMeow(data: QuickMeowRequest) {
  return request<QuickMeowResponse>({
    url: '/messages/quick-meow',
    method: 'post',
    data
  });
}

// 获取会话列表
export function getConversationList(params: { page: number; pageSize: number }) {
  return request<ConversationListResponse>({
    url: '/conversations/list',
    method: 'get',
    params
  });
}

// 获取会话历史消息
export function getConversationMessages(targetUserId: string, params: { page: number; pageSize: number }) {
  return request<ConversationMessagesResponse>({
    url: `/conversations/${targetUserId}/messages`,
    method: 'get',
    params
  });
}

// 删除会话
export function deleteConversation(targetUserId: string) {
  return request<DeleteConversationResponse>({
    url: `/conversations/${targetUserId}`,
    method: 'delete'
  });
}