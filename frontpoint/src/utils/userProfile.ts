import { reactive } from 'vue';
import type { DynamicResponse } from '@/types/social';

export interface UserDisplayProfile {
  nickname: string;
  avatarUrl: string;
  miaoId: string;
}

const STORAGE_KEY = 'user-display-profile';

export const DEFAULT_NICKNAME = '猫村村民';
export const DEFAULT_AVATAR = 'https://api.dicebear.com/7.x/adventurer-neutral/svg?seed=catvillage-default';

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

export const getUserDisplayProfile = (): UserDisplayProfile => {
  const parsed = safeParse(localStorage.getItem(STORAGE_KEY));
  return {
    nickname: (parsed?.nickname || '').trim() || DEFAULT_NICKNAME,
    avatarUrl: (parsed?.avatarUrl || '').trim() || DEFAULT_AVATAR,
    miaoId: (parsed?.miaoId || '').trim() || buildDefaultMiaoId()
  };
};

export const globalProfile = reactive<UserDisplayProfile>(getUserDisplayProfile());

export const setUserDisplayProfile = (profile: UserDisplayProfile) => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(profile));
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
  if (!dynamic.isOwner) {
    return dynamic;
  }
  const profile = getUserDisplayProfile();
  return {
    ...dynamic,
    username: profile.nickname,
    avatar: profile.avatarUrl
  };
};
