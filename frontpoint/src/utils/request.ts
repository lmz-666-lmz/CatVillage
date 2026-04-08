import axios, {
  type AxiosError,
  type AxiosRequestConfig,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
  AxiosHeaders
} from 'axios';
import { showToast } from 'vant';
import type { ApiResponse } from '@/types/common';

type OAuthTokenResponse = {
  access_token: string;
  token_type?: string;
};

type StandardApiEnvelope = {
  code: number;
  msg: string;
  data: unknown;
};

type RequestResult<T> = T extends { access_token: string } ? T : ApiResponse<T>;

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null;

const isOAuthTokenResponse = (value: unknown): value is OAuthTokenResponse => {
  if (!isRecord(value)) {
    return false;
  }
  return typeof value.access_token === 'string' && value.access_token.length > 0;
};

const isStandardApiEnvelope = (value: unknown): value is StandardApiEnvelope => {
  if (!isRecord(value)) {
    return false;
  }
  return typeof value.code === 'number' && typeof value.msg === 'string' && 'data' in value;
};

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
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 15000,
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

    if (error.code === 'ERR_NETWORK') {
      showToast({ type: 'fail', message: '网络异常：后端服务未启动或跨域未配置' });
    } else if (error.response?.status === 500) {
      showToast({ type: 'fail', message: '服务器内部错误，请检查后端日志' });
    } else if (error.response?.status === 404) {
      showToast({ type: 'fail', message: '接口地址不存在，请核对路由' });
    } else {
      showToast({ type: 'fail', message: `请求失败：${error.message || '未知错误'}` });
    }

    return Promise.reject(error);
  }
);

// 核心请求函数：已修正兼容性逻辑
const request = async <T>(config: AxiosRequestConfig): Promise<RequestResult<T>> => {
  try {
    const response = await client.request(config);
    const res: unknown = response.data;

    // 💥 兼容处理：如果是 OAuth2 登录返回的 Token 格式，直接返回数据
    if (isOAuthTokenResponse(res)) {
      return res as unknown as RequestResult<T>;
    }

    if (!isStandardApiEnvelope(res)) {
      return Promise.reject(createRequestError('Invalid API response'));
    }

    // 标准业务接口校验
    if (res.code !== 200) {
      if (res.code === 401) {
        console.error('Unauthorized, redirecting to login...');
        localStorage.removeItem('token');
      }
      return Promise.reject(createRequestError(res.msg || 'API Error', res.code, res.code));
    }

    return res as unknown as RequestResult<T>;
  } catch (error) {
    const axiosError = error as AxiosError<unknown>;
    const status = axiosError.response?.status;
    const backendData = axiosError.response?.data;
    const backendMessage =
      isRecord(backendData) && typeof backendData.detail === 'string'
        ? backendData.detail
        : isRecord(backendData) && typeof backendData.msg === 'string'
          ? backendData.msg
          : undefined;

    if (status === 401) {
      localStorage.removeItem('token');
    }

    return Promise.reject(createRequestError(backendMessage || axiosError.message || 'Network Error', status));
  }
};

export default request;