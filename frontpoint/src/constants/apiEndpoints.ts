// API端点常量定义

export const API_ENDPOINTS = {
  // 宠物数字档案管理
  PET_PROFILES: {
    BASE: '/pet-profiles',
    LIST: '/pet-profiles/list',
    CREATE: '/pet-profiles',
    UPDATE: (id: string) => `/pet-profiles/${id}`,
    DETAIL: (id: string) => `/pet-profiles/${id}`,
    DELETE: (id: string) => `/pet-profiles/${id}`,
  },

  // 交友广场
  SOCIAL: {
    BASE: '/social',
    DYNAMICS: {
      BASE: '/social/dynamics',
      LIST: '/social/dynamics/list',
      MY_LIST: '/social/dynamics/my/list',
      CREATE: '/social/dynamics',
      DETAIL: (id: string) => `/social/dynamics/${id}`,
      DELETE: (id: string) => `/social/dynamics/${id}`,
      LIKE: (id: string) => `/social/dynamics/${id}/like`,
      COMMENTS: (dynamicId: string) => `/social/dynamics/${dynamicId}/comments`,
    },
    COMMENTS: {
      BASE: '/social/comments',
      DELETE: (id: string) => `/social/comments/${id}`,
    },
  },

  // 好友消息
  MESSAGES: {
    BASE: '/messages',
    SEND: '/messages/send',
    REVOKE: (id: string) => `/messages/${id}/revoke`,
    READ_STATUS: '/messages/read-status',
    QUICK_MEOW: '/messages/quick-meow',
    CONVERSATIONS: {
      LIST: '/conversations/list',
      MESSAGES: (targetUserId: string) => `/conversations/${targetUserId}/messages`,
      DELETE: (targetUserId: string) => `/conversations/${targetUserId}`,
    },
    FRIENDS: {
      LIST: '/friends/list',
    },
  },

  // 喵喵情绪台
  EMOTION: {
    BASE: '/emotions',
    RECOGNIZE: '/emotions/recognize',
    RECORDS: {
      LIST: '/emotions/records/list',
      DETAIL: (id: string) => `/emotions/records/${id}`,
    },
    STATISTICS: '/emotions/statistics',
    WARNINGS: {
      LIST: '/emotions/warnings/list',
      STATUS: (id: string) => `/emotions/warnings/${id}/status`,
    },
    WEEKLY_REPORT: '/emotions/weekly-report',
  },

  // AI养育助理
  AI_ASSISTANT: {
    BASE: '/ai-assistant',
    CHAT: '/ai-assistant/chat',
    HISTORY: '/ai-assistant/history',
    SESSIONS: (id: string) => `/ai-assistant/sessions/${id}`,
    EMERGENCY_HELP: (id: string) => `/ai-assistant/emergency-help/${id}`,
  },

  // 用户认证
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
    PROFILE: '/auth/profile',
  },
};