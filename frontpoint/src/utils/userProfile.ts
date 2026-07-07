import { reactive } from 'vue';
import type { DynamicResponse } from '@/types/social';
import { getDefaultUserAvatar } from '@/utils/image';

export interface UserDisplayProfile {
  nickname: string;
  avatarUrl: string;
  miaoId: string;
}

const PROFILE_STORAGE_PREFIX = 'user-display-profile';
const CURRENT_USER_ID_KEY = 'currentUserId';
const LEGACY_PROFILE_KEYS = ['avatar', 'userAvatar', PROFILE_STORAGE_PREFIX];
const LEGACY_RUNTIME_KEYS = [
  'currentUser',
  'current_pet_id',
  'currentPet',
  'currentPetId',
  'selectedCat',
  'selectedPet',
  'catId',
  'petId',
  'currentCatId',
  'cats'
];

export const DEFAULT_NICKNAME = '猫村村民';
export const DEFAULT_AVATAR = getDefaultUserAvatar();

const buildDefaultMiaoId = () => {
  const token = localStorage.getItem('token') || '';
  const seed = token || `${Date.now()}${Math.random().toString(36).slice(2)}`;
  const numeric = seed
    .split('')
    .reduce((acc, cur) => acc + cur.charCodeAt(0), 0)
    .toString()
    .slice(0, 10)
    .padEnd(10, '7');
  return `MV${numeric}`;
};

const safeParse = (raw: string | null): Partial<UserDisplayProfile> | null => {
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw) as Partial<UserDisplayProfile>;
  } catch {
    return null;
  }
};

export const getCurrentUserId = () => localStorage.getItem(CURRENT_USER_ID_KEY) || '';

const getStorageKey = (userId = getCurrentUserId()) => (
  userId ? `${PROFILE_STORAGE_PREFIX}:${userId}` : ''
);

export const clearLegacyProfileKeys = () => {
  LEGACY_PROFILE_KEYS.forEach((key) => localStorage.removeItem(key));
};

export const clearAccountRuntimeState = (options: { includeToken?: boolean } = {}) => {
  if (options.includeToken) {
    localStorage.removeItem('token');
  }
  localStorage.removeItem(CURRENT_USER_ID_KEY);
  localStorage.removeItem('is_admin');
  LEGACY_RUNTIME_KEYS.forEach((key) => localStorage.removeItem(key));
  clearLegacyProfileKeys();
  Object.assign(globalProfile, {
    nickname: DEFAULT_NICKNAME,
    avatarUrl: getDefaultUserAvatar(),
    miaoId: ''
  });
};

export const setCurrentUserIdentity = (user: {
  id: string;
  username: string;
  nickname?: string | null;
  avatar_url?: string | null;
  avatarUrl?: string | null;
}) => {
  clearLegacyProfileKeys();
  localStorage.setItem(CURRENT_USER_ID_KEY, user.id);
  const storageKey = getStorageKey(user.id);
  const existing = safeParse(localStorage.getItem(storageKey));
  const serverAvatar = (user.avatar_url || user.avatarUrl || '').trim();
  const userSeed = user.id || user.username;
  const profile: UserDisplayProfile = {
    nickname: (user.nickname || user.username || '').trim() || DEFAULT_NICKNAME,
    avatarUrl: serverAvatar || getDefaultUserAvatar(userSeed),
    miaoId: (user.username || existing?.miaoId || '').trim() || buildDefaultMiaoId()
  };
  localStorage.setItem(storageKey, JSON.stringify(profile));
  Object.assign(globalProfile, profile);
  return profile;
};

export const getUserDisplayProfile = (): UserDisplayProfile => {
  const storageKey = getStorageKey();
  const parsed = storageKey ? safeParse(localStorage.getItem(storageKey)) : null;
  const userId = getCurrentUserId();
  return {
    nickname: (parsed?.nickname || '').trim() || DEFAULT_NICKNAME,
    avatarUrl: (parsed?.avatarUrl || '').trim() || getDefaultUserAvatar(userId),
    miaoId: (parsed?.miaoId || '').trim() || buildDefaultMiaoId()
  };
};

export const globalProfile = reactive<UserDisplayProfile>(getUserDisplayProfile());

export const setUserDisplayProfile = (profile: UserDisplayProfile) => {
  const storageKey = getStorageKey();
  if (!storageKey) {
    return;
  }
  localStorage.setItem(storageKey, JSON.stringify(profile));
  Object.assign(globalProfile, profile);
};

export const patchUserDisplayProfile = (patch: Partial<UserDisplayProfile>) => {
  const current = getUserDisplayProfile();
  const next: UserDisplayProfile = {
    nickname: (patch.nickname ?? current.nickname).trim() || DEFAULT_NICKNAME,
    avatarUrl: (patch.avatarUrl ?? current.avatarUrl).trim() || DEFAULT_AVATAR,
    miaoId: (patch.miaoId ?? current.miaoId).trim() || buildDefaultMiaoId()
  };
  setUserDisplayProfile(next);
  return next;
};

export const applyDisplayProfileToDynamic = <T extends DynamicResponse>(dynamic: T): T => {
  return dynamic;
};
