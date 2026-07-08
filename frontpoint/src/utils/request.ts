import axios, {
  type AxiosError,
  type AxiosRequestConfig,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
  AxiosHeaders
} from 'axios';
import type { ApiResponse } from '@/types/common';
import { clearAccountRuntimeState } from '@/utils/userProfile';

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

const extractBackendMessage = (data: unknown): string | undefined => {
  if (!isRecord(data)) return undefined;
  const detail = data.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    const first = detail.find((item) => isRecord(item) && typeof item.msg === 'string') as Record<string, unknown> | undefined;
    if (typeof first?.msg === 'string') return first.msg;
  }
  return typeof data.msg === 'string' ? data.msg : undefined;
};

const toFriendlyRequestMessage = (error: AxiosError<unknown>) => {
  const status = error.response?.status;
  const backendMessage = extractBackendMessage(error.response?.data);
  if (backendMessage) return backendMessage;
  if (error.code === 'ECONNABORTED') return '请求处理时间较长，请稍后查看结果';
  if (error.code === 'ERR_NETWORK') return '网络异常，请检查网络后重试';
  if (status === 401) return '登录已过期，请重新登录';
  if (status === 403) return '没有权限执行该操作';
  if (status === 404) return '请求的内容不存在';
  if (status === 413) return '文件过大，请压缩后再上传';
  if (status === 422) return '提交内容格式不正确，请检查后再试';
  if (status && status >= 500) return '服务器暂时开小差，请稍后重试';
  return '请求失败，请稍后重试';
};

const cleanParams = (params: unknown) => {
  if (!isRecord(params)) {
    return params;
  }
  return Object.fromEntries(
    Object.entries(params).filter(([, value]) => value !== undefined && value !== null && value !== '')
  );
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
        clearAccountRuntimeState({ includeToken: true });
      }
    }

    return Promise.reject(error);
  }
);

// 核心请求函数：已修正兼容性逻辑
const request = async <T>(config: AxiosRequestConfig): Promise<RequestResult<T>> => {
  try {
    const response = await client.request({
      ...config,
      params: cleanParams(config.params)
    });
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
        clearAccountRuntimeState({ includeToken: true });
      }
      return Promise.reject(createRequestError(res.msg || 'API Error', res.code, res.code));
    }

    return res as unknown as RequestResult<T>;
  } catch (error) {
    const axiosError = error as AxiosError<unknown>;
    const status = axiosError.response?.status;

    if (status === 401) {
      clearAccountRuntimeState({ includeToken: true });
    }

    return Promise.reject(createRequestError(toFriendlyRequestMessage(axiosError), status));
  }
};

export default request;
