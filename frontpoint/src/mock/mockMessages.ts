import type { FriendResponse, MessageResponse, ConversationResponse } from '@/types/message';

// 模拟好友数据
export const mockFriends: FriendResponse[] = [
  {
    id: 'friend-1',
    userId: 'user-2',
    username: '铲屎官小张',
    nickname: '小张',
    avatar: 'https://placekitten.com/100/101',
    lastOnlineAt: new Date(Date.now() - 300000).toISOString(), // 5分钟前
    isOnline: true,
  },
  {
    id: 'friend-2',
    userId: 'user-3',
    username: '喵星人守护者',
    nickname: '喵守护',
    avatar: 'https://placekitten.com/100/102',
    lastOnlineAt: new Date(Date.now() - 3600000).toISOString(), // 1小时前
    isOnline: false,
  },
  {
    id: 'friend-3',
    userId: 'user-4',
    username: '猫咪医生Dr.Li',
    nickname: '李医生',
    avatar: 'https://placekitten.com/100/103',
    lastOnlineAt: new Date().toISOString(), // 在线
    isOnline: true,
  }
];

// 模拟消息数据
export const mockMessages: MessageResponse[] = [
  {
    id: 'msg-1',
    senderId: 'user-2',
    receiverId: 'user-1',
    content: '奶茶今天怎么样？',
    messageType: 'text',
    sentAt: new Date(Date.now() - 1200000).toISOString(), // 20分钟前
    status: 'read'
  },
  {
    id: 'msg-2',
    senderId: 'user-1',
    receiverId: 'user-2',
    content: '很好哦，刚吃完饭',
    messageType: 'text',
    sentAt: new Date(Date.now() - 1100000).toISOString(), // 18分钟前
    status: 'read'
  },
  {
    id: 'msg-3',
    senderId: 'user-2',
    receiverId: 'user-1',
    content: '那就好，我想预约看看她',
    messageType: 'text',
    sentAt: new Date(Date.now() - 1000000).toISOString(), // 16分钟前
    status: 'delivered'
  },
  {
    id: 'msg-4',
    senderId: 'user-3',
    receiverId: 'user-1',
    content: '记得按时给猫咪打疫苗',
    messageType: 'text',
    sentAt: new Date(Date.now() - 86400000).toISOString(), // 1天前
    status: 'read'
  },
  {
    id: 'msg-5',
    senderId: 'user-4',
    receiverId: 'user-1',
    content: '检查结果出来了，一切正常',
    messageType: 'text',
    sentAt: new Date(Date.now() - 1800000).toISOString(), // 30分钟前
    status: 'read'
  }
];

// 模拟会话数据
export const mockConversations: ConversationResponse[] = [
  {
    id: 'conv-1',
    targetUserId: 'user-2',
    targetType: 'user',
    lastMessage: '那就好，我想预约看看她',
    lastMessageType: 'text',
    unreadCount: 2,
    updatedAt: new Date(Date.now() - 1000000).toISOString(), // 16分钟前
    avatar: 'https://placekitten.com/100/101',
    nickname: '小张',
    isOnline: true
  },
  {
    id: 'conv-2',
    targetUserId: 'user-3',
    targetType: 'user',
    lastMessage: '记得按时给猫咪打疫苗',
    lastMessageType: 'text',
    unreadCount: 0,
    updatedAt: new Date(Date.now() - 86400000).toISOString(), // 1天前
    avatar: 'https://placekitten.com/100/102',
    nickname: '喵守护',
    isOnline: false
  },
  {
    id: 'conv-3',
    targetUserId: 'user-4',
    targetType: 'user',
    lastMessage: '检查结果出来了，一切正常',
    lastMessageType: 'text',
    unreadCount: 0,
    updatedAt: new Date(Date.now() - 1800000).toISOString(), // 30分钟前
    avatar: 'https://placekitten.com/100/103',
    nickname: '李医生',
    isOnline: true
  }
];

// 模拟获取好友列表
export const getMockFriendsList = (params: { page: number; pageSize: number }): Promise<{ data: { list: FriendResponse[]; total: number } }> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const start = (params.page - 1) * params.pageSize;
      const end = start + params.pageSize;
      const paginatedList = mockFriends.slice(start, end);
      
      resolve({ 
        data: { 
          list: paginatedList, 
          total: mockFriends.length 
        } 
      });
    }, 500);
  });
};

// 模拟获取消息列表
export const getMockMessageList = (params: { 
  targetUserId: string; 
  page: number; 
  pageSize: number 
}): Promise<{ data: { list: MessageResponse[]; total: number } }> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const conversationMessages = mockMessages.filter(
        msg => (msg.senderId === params.targetUserId || msg.receiverId === params.targetUserId) &&
               (msg.senderId === 'user-1' || msg.receiverId === 'user-1')
      );
      
      const start = (params.page - 1) * params.pageSize;
      const end = start + params.pageSize;
      const paginatedList = conversationMessages.slice(start, end);
      
      resolve({ 
        data: { 
          list: paginatedList, 
          total: conversationMessages.length 
        } 
      });
    }, 500);
  });
};

// 模拟获取会话列表
export const getMockConversations = (): Promise<{ data: ConversationResponse[] }> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ data: mockConversations });
    }, 500);
  });
};

// 模拟发送消息
export const mockSendMessage = (targetUserId: string, content: string): Promise<{ data: MessageResponse }> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const newMessage: MessageResponse = {
        id: `msg-${mockMessages.length + 1}`,
        senderId: 'user-1', // 当前用户发送
        receiverId: targetUserId,
        content,
        messageType: 'text',
        sentAt: new Date().toISOString(),
        status: 'sent'
      };

      mockMessages.push(newMessage);

      // 更新相关会话的最后消息
      const conversation = mockConversations.find(conv => 
        conv.targetUserId === targetUserId
      );
      if (conversation) {
        conversation.lastMessage = content;
        conversation.lastMessageType = 'text';
        conversation.updatedAt = newMessage.sentAt;
        conversation.unreadCount = 0; // 发送消息时重置未读计数
      }

      resolve({ data: newMessage });
    }, 300);
  });
};

// 模拟撤回消息
export const mockRevokeMessage = (messageId: string): Promise<{ data: { success: boolean } }> => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const messageIndex = mockMessages.findIndex(msg => msg.id === messageId);
      if (messageIndex !== -1 && mockMessages[messageIndex]) {
        mockMessages[messageIndex].content = '[消息已撤回]';
        mockMessages[messageIndex].status = 'delivered';
        resolve({ data: { success: true } });
      } else {
        reject(new Error('消息不存在'));
      }
    }, 300);
  });
};

// 模拟更新消息已读状态
export const mockUpdateReadStatus = (messageIds: string[]): Promise<{ data: { success: boolean } }> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      messageIds.forEach(id => {
        const message = mockMessages.find(msg => msg.id === id);
        if (message) {
          message.status = 'read';
          
          // 更新相关会话的未读消息数量
          const conversation = mockConversations.find(conv => 
            conv.targetUserId === message.receiverId || conv.targetUserId === message.senderId
          );
          if (conversation && conversation.unreadCount > 0) {
            conversation.unreadCount--;
          }
        }
      });

      resolve({ data: { success: true } });
    }, 300);
  });
};