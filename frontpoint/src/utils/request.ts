import axios, {
  type AxiosError,
  type AxiosRequestConfig,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
  AxiosHeaders
} from 'axios';
import type { ApiResponse } from '@/types/common';

type RequestError = Error & {
  status?: number;
  code?: number;
};

const createRequestError = (message: string, status?: number, code?: number) => {
  const requestError = new Error(message) as RequestError;
  requestError.status = status;
  requestError.code = code;
  return requestError;
};

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 10000,
});

// 请求拦截器
client.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token');
    if (token) {
      if (!config.headers) {
        config.headers = new AxiosHeaders();
      }
      if (typeof config.headers.set === 'function') {
        config.headers.set('Authorization', `Bearer ${token}`);
      } else {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error: AxiosError) => {
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
client.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    console.error('Response Error:', error);
    if (error.response && error.response.status) {
      if (error.response.status === 401) {
        console.error('Unauthorized, please login again');
        localStorage.removeItem('token');
      }
    }
    return Promise.reject(error);
  }
);

// 核心请求函数：已修正兼容性逻辑
const request = async <T>(config: AxiosRequestConfig): Promise<ApiResponse<T> | any> => {
  try {
    const response = await client.request(config);
    const res = response.data as any;

    // 💥 兼容处理：如果是 OAuth2 登录返回的 Token 格式，直接返回数据
    if (res.access_token) {
      return res;
    }

    // 标准业务接口校验
    if (res.code !== 200) {
      if (res.code === 401) {
        console.error('Unauthorized, redirecting to login...');
        localStorage.removeItem('token');
      }
      return Promise.reject(createRequestError(res.msg || 'API Error', res.code, res.code));
    }

    return res;
  } catch (error) {
    const axiosError = error as AxiosError<any>;
    const status = axiosError.response?.status;
    const backendMessage = axiosError.response?.data?.detail || axiosError.response?.data?.msg;

    if (status === 401) {
      localStorage.removeItem('token');
    }

    return Promise.reject(createRequestError(backendMessage || axiosError.message || 'Network Error', status));
  }
};

export default request;