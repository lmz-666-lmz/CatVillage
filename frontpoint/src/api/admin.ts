import request from '@/utils/request';

export interface AdminStats {
  users: number;
  pets: number;
  dynamics: number;
  emotion_records: number;
  today_users: number;
  today_dynamics: number;
  messages: number;
  health_records: number;
  ai_chats: number;
  active_users: number;
  disabled_users: number;
  admins: number;
}

export interface AdminUser {
  id: string;
  username: string;
  nickname: string;
  isActive: boolean;
  isAdmin: boolean;
}

export interface AdminPet {
  id: string;
  name: string;
  breed: string;
  age?: number | null;
  weight?: number | null;
  owner: string;
  createdAt: string;
}

export interface AdminDynamic {
  id: string;
  content: string;
  author: string;
  likeCount: number;
  commentCount: number;
  isRecommended: boolean;
  recommendedAt?: string;
  createdAt: string;
}

export interface AdminEmotionRecord {
  id: number;
  petName: string;
  label: string;
  confidence?: number | null;
  recordTime: string;
}

export interface AdminListResponse<T> {
  list: T[];
  total: number;
  page: number;
  pageSize: number;
}

type ListParams = {
  page?: number;
  pageSize?: number;
  keyword?: string;
};

export function getAdminStats() {
  return request<AdminStats>({
    url: '/admin/stats',
    method: 'get'
  });
}

export function getAdminUsers(params: ListParams) {
  return request<AdminListResponse<AdminUser>>({
    url: '/admin/users',
    method: 'get',
    params
  });
}

export function setAdminUserActive(userId: string, value: boolean) {
  return request<{ success: boolean }>({
    url: `/admin/users/${userId}/active`,
    method: 'put',
    data: { value }
  });
}

export function setAdminUserRole(userId: string, value: boolean) {
  return request<{ success: boolean }>({
    url: `/admin/users/${userId}/admin`,
    method: 'put',
    data: { value }
  });
}

export function resetAdminUserPassword(userId: string, password: string) {
  return request<{ success: boolean }>({
    url: `/admin/users/${userId}/password`,
    method: 'put',
    data: { password }
  });
}

export function getAdminPets(params: ListParams) {
  return request<AdminListResponse<AdminPet>>({
    url: '/admin/pets',
    method: 'get',
    params
  });
}

export function getAdminDynamics(params: ListParams) {
  return request<AdminListResponse<AdminDynamic>>({
    url: '/admin/dynamics',
    method: 'get',
    params
  });
}

export function deleteAdminDynamic(dynamicId: string) {
  return request<{ success: boolean }>({
    url: `/admin/dynamics/${dynamicId}`,
    method: 'delete'
  });
}

export function setAdminDynamicRecommended(dynamicId: string, value: boolean) {
  return request<{ success: boolean }>({
    url: `/admin/dynamics/${dynamicId}/recommend`,
    method: 'put',
    data: { value }
  });
}

export function getAdminEmotionRecords(params: ListParams) {
  return request<AdminListResponse<AdminEmotionRecord>>({
    url: '/admin/emotion-records',
    method: 'get',
    params
  });
}

export interface AdminMessage {
  id: string;
  senderName: string;
  receiverId: string;
  content: string;
  messageType: string;
  sentAt: string;
}

export interface AdminHealthRecord {
  id: number;
  kind: 'weight' | 'feeding';
  petName: string;
  owner: string;
  metric: string;
  note: string;
  recordedAt: string;
}

export interface AdminOverview {
  health: {
    activeUsers: number;
    disabledUsers: number;
    admins: number;
    aiConfigured: boolean;
  };
  today: {
    dynamics: number;
    emotions: number;
    messages: number;
    aiChats: number;
  };
  week: {
    dynamics: number;
    emotions: number;
    messages: number;
    feedings: number;
    weights: number;
  };
  daily: Array<{
    date: string;
    users: number;
    dynamics: number;
    emotions: number;
    messages: number;
  }>;
  recentActivities: Array<{
    id: string;
    type: 'dynamic' | 'emotion';
    title: string;
    desc: string;
    time: string;
  }>;
}

export function getAdminMessages(params: ListParams) {
  return request<AdminListResponse<AdminMessage>>({
    url: '/admin/messages',
    method: 'get',
    params
  });
}

export function getAdminOverview() {
  return request<AdminOverview>({
    url: '/admin/overview',
    method: 'get'
  });
}

export function getAdminHealthRecords(params: ListParams & { kind?: 'weight' | 'feeding' }) {
  return request<AdminListResponse<AdminHealthRecord>>({
    url: '/admin/health-records',
    method: 'get',
    params
  });
}

export function deleteAdminHealthRecord(kind: AdminHealthRecord['kind'], recordId: number) {
  return request<{ success: boolean }>({
    url: `/admin/health-records/${kind}/${recordId}`,
    method: 'delete'
  });
}

export function deleteAdminUser(userId: string) {
  return request<{ success: boolean }>({
    url: `/admin/users/${userId}`,
    method: 'delete'
  });
}

export function deleteAdminPet(petId: string) {
  return request<{ success: boolean }>({
    url: `/admin/pets/${petId}`,
    method: 'delete'
  });
}

export function deleteAdminEmotionRecord(recordId: number) {
  return request<{ success: boolean }>({
    url: `/admin/emotion-records/${recordId}`,
    method: 'delete'
  });
}

export function deleteAdminMessage(messageId: string) {
  return request<{ success: boolean }>({
    url: `/admin/messages/${messageId}`,
    method: 'delete'
  });
}

export interface AdminConfig {
  aiApiKey: string;
  aiBaseUrl: string;
  aiModel: string;
  adminUsername: string;
  runtimeOnly?: boolean;
}

export interface AdminHotTopic {
  id?: string;
  topic: string;
  count: number;
  isDefault: boolean;
  sortOrder?: number;
  isRecommended?: boolean;
  isVisible?: boolean;
}

export interface AdminHotTopicsResponse {
  list: AdminHotTopic[];
  defaultTopics: string[];
}

export function getAdminHotTopics() {
  return request<AdminHotTopicsResponse>({ url: '/admin/topics/hot', method: 'get' });
}

export function updateAdminDefaultTopics(topics: string[]) {
  return request<{ success: boolean; defaultTopics: string[] }>({
    url: '/admin/topics/default',
    method: 'put',
    data: { topics }
  });
}

export function getAdminTopics() {
  return request<{ list: AdminHotTopic[]; total: number }>({ url: '/admin/topics', method: 'get' });
}

export function createAdminTopic(data: Partial<AdminHotTopic>) {
  return request<AdminHotTopic>({ url: '/admin/topics', method: 'post', data });
}

export function updateAdminTopic(topicId: string, data: Partial<AdminHotTopic>) {
  return request<AdminHotTopic>({ url: `/admin/topics/${topicId}`, method: 'put', data });
}

export function deleteAdminTopic(topicId: string) {
  return request<{ success: boolean }>({ url: `/admin/topics/${topicId}`, method: 'delete' });
}

export function sortAdminTopics(items: Array<{ id: string; sortOrder: number }>) {
  return request<{ success: boolean; list: AdminHotTopic[] }>({
    url: '/admin/topics/sort',
    method: 'put',
    data: { items }
  });
}

export function getAdminConfig() {
  return request<AdminConfig>({ url: '/admin/config', method: 'get' });
}

export function updateAdminConfig(data: Partial<AdminConfig>) {
  return request<{ success: boolean }>({ url: '/admin/config', method: 'put', data });
}
