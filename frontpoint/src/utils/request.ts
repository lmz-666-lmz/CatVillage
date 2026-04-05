import axios, {
  type AxiosError,
  type AxiosRequestConfig,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
  AxiosHeaders
} from 'axios';
import type { ApiResponse } from '@/types/common';

// 创建axios实例
const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1', // 默认API基础URL
  timeout: 10000, // 请求超时时间
});

// 请求拦截器
client.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 从localStorage获取token
    const token = localStorage.getItem('token');
    if (token) {
      // 在请求头中添加Authorization
      if (!config.headers) {
        config.headers = new AxiosHeaders();
      }

      // 使用 set 方法设置header
      if (typeof config.headers.set === 'function') {
        config.headers.set('Authorization', `Bearer ${token}`);
      } else {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error: AxiosError) => {
    // 请求错误处理
    console.error('Request Error:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
client.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    // 响应错误处理
    console.error('Response Error:', error);
    
    // 根据HTTP状态码进行错误处理
    if (error.response && error.response.status) {
      switch (error.response.status) {
        case 400:
          console.error('Request Parameter Error');
          break;
        case 401:
          console.error('Unauthorized, please login again');
          // 清除token并跳转到登录页
          localStorage.removeItem('token');
          break;
        case 403:
          console.error('Access Forbidden');
          break;
        case 404:
          console.error('Resource Not Found');
          break;
        case 500:
          console.error('Server Internal Error');
          break;
        default:
          console.error(`Connection Error: ${error.response.status}`);
      }
    }
    
    return Promise.reject(error);
  }
);

const request = async <T>(config: AxiosRequestConfig): Promise<ApiResponse<T>> => {
  const response = await client.request<ApiResponse<T>>(config);
  const res = response.data;

  if (res.code !== 200) {
    if (res.code === 401) {
      console.error('Unauthorized, redirecting to login...');
      localStorage.removeItem('token');
    } else {
      console.error('API Error:', res.msg || 'Unknown Error');
    }
    return Promise.reject(new Error(res.msg || 'Error'));
  }

  return res;
};

export default request;