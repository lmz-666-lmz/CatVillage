import request from '@/utils/request';

type BackendLoginResponse = {
  access_token: string;
  token_type: string;
};

type BackendRegisterResponse = {
  id: string;
  username: string;
  nickname?: string;
  avatar_url?: string | null;
  avatarUrl?: string | null;
  is_active?: boolean;
  created_at?: string;
};

type BackendProfileResponse = {
  id: string;
  username: string;
  nickname: string;
  avatar_url?: string | null;
  avatarUrl?: string | null;
  is_active: boolean;
};

export function loginUser(username: string, password: string) {
  const payload = new URLSearchParams();
  payload.append('username', username);
  payload.append('password', password);

  return request<BackendLoginResponse>({
    url: '/auth/login',
    method: 'post',
    data: payload,
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  });
}

export function registerUser(username: string, password: string) {
  return request<BackendRegisterResponse>({
    url: '/auth/register',
    method: 'post',
    data: {
      username,
      password
    }
  });
}

export function getMe() {
  return request<{
    id: string;
    username: string;
    nickname: string;
    avatar_url?: string | null;
    avatarUrl?: string | null;
    is_admin: boolean;
    is_active: boolean;
  }>({
    url: '/auth/me',
    method: 'get',
  });
}

export function updateUserProfile(data: { nickname?: string; avatarUrl?: string }) {
  return request<BackendProfileResponse>({
    url: '/auth/profile',
    method: 'put',
    data: {
      nickname: data.nickname,
      avatar_url: data.avatarUrl,
      avatarUrl: data.avatarUrl
    }
  });
}
