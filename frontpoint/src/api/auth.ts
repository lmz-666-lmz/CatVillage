import request from '@/utils/request';

type BackendLoginResponse = {
  access_token: string;
  token_type: string;
};

type BackendRegisterResponse = {
  id: string;
  username: string;
  nickname?: string;
  is_active?: boolean;
  created_at?: string;
};

type BackendProfileResponse = {
  id: string;
  username: string;
  nickname: string;
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

export function updateUserProfile(nickname: string) {
  return request<BackendProfileResponse>({
    url: '/auth/profile',
    method: 'put',
    data: { nickname }
  });
}
