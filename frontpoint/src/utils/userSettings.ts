export interface NotificationSettings {
  message: boolean;
  comment: boolean;
  like: boolean;
  follower: boolean;
}

export interface PrivacySettings {
  searchable: boolean;
  openInteraction: boolean;
}

export interface UnreadSummary {
  privateMessages: number;
  comments: number;
  likes: number;
  followers: number;
  total: number;
}

export const SETTINGS_CHANGED_EVENT = 'catvillage:settings-changed';

export const NOTIFICATION_STORAGE_KEY = 'settings-notification';
export const PRIVACY_STORAGE_KEY = 'settings-privacy';

export const DEFAULT_NOTIFICATION_SETTINGS: NotificationSettings = {
  message: true,
  comment: true,
  like: true,
  follower: true
};

export const DEFAULT_PRIVACY_SETTINGS: PrivacySettings = {
  searchable: true,
  openInteraction: true
};

const clampCount = (value: unknown) => {
  const num = Number(value || 0);
  return Number.isFinite(num) && num > 0 ? Math.floor(num) : 0;
};

const readJson = <T>(key: string, fallback: T): T => {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return fallback;
    return { ...fallback, ...JSON.parse(raw) };
  } catch {
    return fallback;
  }
};

export const getNotificationSettings = (): NotificationSettings =>
  readJson(NOTIFICATION_STORAGE_KEY, DEFAULT_NOTIFICATION_SETTINGS);

export const saveNotificationSettings = (value: NotificationSettings) => {
  localStorage.setItem(NOTIFICATION_STORAGE_KEY, JSON.stringify(value));
  window.dispatchEvent(new CustomEvent(SETTINGS_CHANGED_EVENT));
};

export const getPrivacySettings = (): PrivacySettings =>
  readJson(PRIVACY_STORAGE_KEY, DEFAULT_PRIVACY_SETTINGS);

export const savePrivacySettings = (value: PrivacySettings) => {
  localStorage.setItem(PRIVACY_STORAGE_KEY, JSON.stringify(value));
  window.dispatchEvent(new CustomEvent(SETTINGS_CHANGED_EVENT));
};

const baselineKey = () => {
  const userId = localStorage.getItem('currentUserId') || localStorage.getItem('username') || 'guest';
  return `message-notice-baseline:${userId}`;
};

type SocialNoticeKey = 'comments' | 'likes' | 'followers';
type SocialNoticeBaseline = Record<SocialNoticeKey, number>;

const readBaseline = (): SocialNoticeBaseline =>
  readJson(baselineKey(), { comments: 0, likes: 0, followers: 0 });

const saveBaseline = (value: SocialNoticeBaseline) => {
  localStorage.setItem(baselineKey(), JSON.stringify(value));
  window.dispatchEvent(new CustomEvent(SETTINGS_CHANGED_EVENT));
};

export const markNoticeCategorySeen = (category: SocialNoticeKey, summary: UnreadSummary) => {
  const baseline = readBaseline();
  baseline[category] = clampCount(summary[category]);
  saveBaseline(baseline);
};

export const applyNotificationSettings = (summary: Partial<UnreadSummary> | null | undefined): UnreadSummary => {
  const raw = {
    privateMessages: clampCount(summary?.privateMessages),
    comments: clampCount(summary?.comments),
    likes: clampCount(summary?.likes),
    followers: clampCount(summary?.followers),
    total: 0
  };
  const settings = getNotificationSettings();
  const baseline = readBaseline();
  const next = {
    privateMessages: settings.message ? raw.privateMessages : 0,
    comments: settings.comment ? Math.max(raw.comments - baseline.comments, 0) : 0,
    likes: settings.like ? Math.max(raw.likes - baseline.likes, 0) : 0,
    followers: settings.follower ? Math.max(raw.followers - baseline.followers, 0) : 0,
    total: 0
  };
  next.total = next.privateMessages + next.comments + next.likes + next.followers;
  return next;
};

export const formatBadgeCount = (value: number) => {
  if (value <= 0) return '';
  return value > 99 ? '99+' : String(value);
};
