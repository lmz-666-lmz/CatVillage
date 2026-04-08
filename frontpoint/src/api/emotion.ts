import request from '@/utils/request';
import type { 
  EmotionRecordsListResponse,
  EmotionRecordResponse,
  EmotionStatisticsResponse,
  WarningResponse,
  WeeklyReportResponse,
  RecognizeEmotionResponse
} from '@/types/emotion';
import type { ApiResponse } from '@/types';

type BackendEmotionRecord = {
  id: number;
  pet_id: string;
  label: string;
  confidence: number | null;
  record_time: string;
};

type BackendRecordsResponse = {
  total: number;
  list: BackendEmotionRecord[];
};

type BackendRecognizeResponse = {
  label: string;
  confidence: number | null;
  translation?: {
    human?: string;
    science?: string;
  };
  record_id?: number;
};

type BackendStatisticsResponse = {
  pet_id: string;
  days: number;
  total: number;
  distribution: Array<{ label: string; count: number; percentage: number }>;
};

type BackendWeeklyReportResponse = {
  pet_id: string;
  period_days: number;
  total: number;
  distribution: Array<{ label: string; count: number; percentage: number }>;
  summary: string;
  week_start?: string;
  week_end?: string;
};

const toEmotionRecord = (item: BackendEmotionRecord): EmotionRecordResponse => ({
  id: String(item.id),
  catId: item.pet_id,
  userId: '',
  audioUrl: '',
  emotionTag: item.label,
  confidence: item.confidence ?? 0,
  emotionDescription: '',
  createdAt: item.record_time
});

// 上传音频并识别情绪
export function recognizeEmotion(data: FormData): Promise<ApiResponse<RecognizeEmotionResponse>> {
  const petId = data.get('petId') || data.get('catId');
  const audioFile = data.get('file') || data.get('audioFile');
  const normalized = new FormData();
  if (petId) {
    normalized.append('pet_id', String(petId));
  }
  if (audioFile) {
    normalized.append('file', audioFile as Blob);
  }

  return request<BackendRecognizeResponse>({
    url: '/emotions/recognize',
    method: 'post',
    headers: { 'Content-Type': 'multipart/form-data' },
    data: normalized
  }).then((response) => ({
    ...response,
    data: {
      emotionTag: response.data.label,
      confidence: response.data.confidence ?? 0,
      emotionDescription: response.data.translation?.human || response.data.translation?.science || '',
      recordId: response.data.record_id ? String(response.data.record_id) : ''
    }
  }));
}

// 获取情绪识别历史记录
export function getEmotionRecords(params: { page: number; pageSize: number; catId?: string }): Promise<ApiResponse<EmotionRecordsListResponse>> {
  const skip = Math.max(0, (params.page - 1) * params.pageSize);
  const limit = Math.max(1, params.pageSize);

  return request<BackendRecordsResponse>({
    url: '/emotions/records/list',
    method: 'get',
    params: {
      pet_id: params.catId,
      skip,
      limit
    }
  }).then((response) => ({
    ...response,
    data: {
      list: response.data.list.map(toEmotionRecord),
      total: response.data.total,
      page: params.page,
      pageSize: params.pageSize
    }
  }));
}

// 获取单条情绪记录详情
export function getEmotionRecordDetail(recordId: string): Promise<ApiResponse<EmotionRecordResponse>> {
  return request<BackendEmotionRecord>({
    url: `/emotions/records/${recordId}`,
    method: 'get'
  }).then((response) => ({
    ...response,
    data: toEmotionRecord(response.data)
  }));
}

// 获取情绪统计可视化数据
export function getEmotionStatistics(params: { catId?: string; startDate?: string; endDate?: string }): Promise<ApiResponse<EmotionStatisticsResponse>> {
  return request<BackendStatisticsResponse>({
    url: '/emotions/statistics',
    method: 'get',
    params: {
      pet_id: params.catId,
      start_date: params.startDate,
      end_date: params.endDate
    }
  }).then((response) => ({
    ...response,
    data: {
      moodTrend: [],
      emotionDistribution: response.data.distribution.map((item: { label: string; count: number; percentage: number }) => ({
        emotionTag: item.label,
        count: item.count,
        percentage: item.percentage
      })),
      avgConfidence: 0,
      warningCount: 0
    }
  }));
}

// 获取健康预警列表
export function getWarningList(params: { page: number; pageSize: number; catId?: string; status?: string }): Promise<ApiResponse<{ list: WarningResponse[]; total: number }>> {
  const skip = Math.max(0, (params.page - 1) * params.pageSize);
  const limit = Math.max(1, params.pageSize);

  return request<{ list: WarningResponse[]; total: number }>({
    url: '/emotions/warnings/list',
    method: 'get',
    params: {
      pet_id: params.catId,
      status: params.status,
      skip,
      limit
    }
  });
}

// 标记预警状态
export function markWarningStatus(warningId: string, status: string): Promise<ApiResponse<{ success: boolean }>> {
  return request<{ success: boolean }>({
    url: `/emotions/warnings/${warningId}/status`,
    method: 'put',
    data: { status }
  });
}

// 生成情绪周报
export function getWeeklyReport(params: { catId?: string; week?: string }): Promise<ApiResponse<WeeklyReportResponse>> {
  return request<BackendWeeklyReportResponse>({
    url: '/emotions/weekly-report',
    method: 'get',
    params: {
      pet_id: params.catId,
      week_start: params.week
    }
  }).then((response) => ({
    ...response,
    data: {
      weekStartDate: response.data.week_start || params.week || '',
      weekEndDate: response.data.week_end || '',
      summary: response.data.summary,
      moodTrends: [],
      avgEmotion: response.data.distribution[0]?.label || '',
      avgConfidence: 0,
      warningCount: 0,
      highlightMoments: [],
      recommendations: []
    }
  }));
}