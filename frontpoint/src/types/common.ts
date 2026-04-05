export interface ApiResponse<T = Record<string, unknown>> {
  code: number;
  msg: string;
  data: T;
}

export interface PageParams {
  page: number;
  pageSize: number;
}

export interface PageResponse<T> {
  list: T[];
  total: number;
  page: number;
  pageSize: number;
}

export interface User {
  id: string;
  username: string;
  nickname: string;
  avatar: string;
  email?: string;
  phone?: string;
  createdAt: string;
  updatedAt: string;
}