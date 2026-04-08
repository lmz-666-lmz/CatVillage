// 应用常量定义

// API相关常量
export const API_CONSTANTS = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  TIMEOUT: 10000, // 请求超时时间（毫秒）
  RETRY_COUNT: 3, // 请求重试次数
};

// 本地存储键名常量
export const STORAGE_KEYS = {
  TOKEN: 'token',
  USER_INFO: 'userInfo',
  CURRENT_CAT_ID: 'currentCatId',
  THEME: 'theme',
  LANGUAGE: 'language',
};

// 路由相关常量
export const ROUTE_NAMES = {
  HOME: 'Home',
  LOGIN: 'Login',
  REGISTER: 'Register',
  CATS: 'Cats',
  ADD_CAT: 'AddCat',
  EDIT_CAT: 'EditCat',
  SOCIAL: 'Social',
  CREATE_POST: 'CreatePost',
  MESSAGES: 'Messages',
  EMOTIONS: 'Emotions',
  AI_ASSISTANT: 'AIAssistant',
  USER_PROFILE: 'UserProfile',
  NOT_FOUND: 'NotFound',
};

// 猫咪性别常量
export const CAT_GENDER = {
  FEMALE: 0, // 母
  MALE: 1,   // 公
} as const;

// 消息类型常量
export const MESSAGE_TYPES = {
  TEXT: 'text',
  IMAGE: 'image',
  AUDIO: 'audio',
  QUICK_MEOW: 'quick_meow',
} as const;

// 快捷喵语类型
export const QUICK_MEOW_TYPES = {
  HELLO: 'hello',
  HUNGRY: 'hungry',
  TIRED: 'tired',
  PLAYFUL: 'playful',
  SCARED: 'scared',
  ANGRY: 'angry',
} as const;

// 情绪标签常量
export const EMOTION_TAGS = {
  HAPPY: '开心',
  COMFORTABLE: '舒适',
  PAIN_WARNING: '疼痛警告',
  ANXIOUS: '焦虑',
  STRESS: '应激',
  HUNGRY: '饥饿',
} as const;

// 预警级别常量
export const WARNING_LEVELS = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
} as const;

// 预警状态常量
export const WARNING_STATUS = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  RESOLVED: 'resolved',
} as const;

// 系统主题常量
export const THEMES = {
  LIGHT: 'light',
  DARK: 'dark',
  AUTO: 'auto',
} as const;

// 系统语言常量
export const LANGUAGES = {
  ZH_CN: 'zh-CN',
  EN_US: 'en-US',
} as const;

// 错误码常量
export const ERROR_CODES = {
  SUCCESS: 200,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  SERVER_ERROR: 500,
} as const;

// 分页相关常量
export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_SIZE: 10,
  MAX_SIZE: 100,
} as const;

// 本地存储相关常量
export const LOCAL_STORAGE = {
  MAX_SIZE: 10 * 1024 * 1024, // 10MB
  QUOTA_EXCEEDED_ERROR: 'QuotaExceededError',
} as const;