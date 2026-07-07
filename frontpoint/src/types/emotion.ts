// 情绪识别功能相关类型定义

// 上传音频识别情绪请求
export interface RecognizeEmotionRequest {
  catId: string;
  audioFile: File | Blob; // 音频文件
}

// 情绪识别响应
export interface RecognizeEmotionResponse {
  emotionTag: string;
  confidence: number;
  emotionDescription: string;
  recordId: string; // 记录ID，用于后续查询
}

// 情绪记录列表请求参数
export interface EmotionRecordsListRequest {
  catId: string;
  page: number;
  pageSize: number;
}

// 情绪记录响应
export interface EmotionRecordResponse {
  id: string;
  catId: string;
  userId: string;
  audioUrl: string;
  emotionTag: string;
  confidence: number;
  emotionDescription: string;
  createdAt: string;
}

// 情绪记录列表响应
export interface EmotionRecordsListResponse {
  list: EmotionRecordResponse[];
  total: number;
  page: number;
  pageSize: number;
}

// 情绪记录详情响应
export interface EmotionRecordDetailResponse {
  id: string;
  catId: string;
  userId: string;
  audioUrl: string;
  emotionTag: string;
  confidence: number;
  emotionDescription: string;
  createdAt: string;
  relatedWarnings?: WarningResponse[]; // 关联的健康预警
}

// 情绪统计数据请求参数
export interface EmotionStatisticsRequest {
  catId: string;
  startDate?: string; // YYYY-MM-DD
  endDate?: string; // YYYY-MM-DD
}

// 情绪统计数据响应
export interface EmotionStatisticsResponse {
  moodTrend: MoodTrendData[]; // 情绪趋势
  emotionDistribution: EmotionDistributionData[]; // 情绪分布
  avgConfidence: number; // 平均置信度
  warningCount: number; // 预警次数
}

// 情绪趋势数据
export interface MoodTrendData {
  date: string; // YYYY-MM-DD
  emotionTag: string;
  confidence: number;
}

// 情绪分布数据
export interface EmotionDistributionData {
  emotionTag: string;
  count: number;
  percentage: number;
}

// 健康预警列表请求参数
export interface WarningListRequest {
  catId: string;
  status?: 'pending' | 'processing' | 'resolved';
  page: number;
  pageSize: number;
}

// 健康预警响应
export interface WarningResponse {
  id: string;
  catId: string;
  userId: string;
  title: string;
  description: string;
  level: 'low' | 'medium' | 'high'; // 低、中、高级别
  status: 'pending' | 'processing' | 'resolved'; // 待处理、处理中、已解决
  createdAt: string;
  updatedAt: string;
  relatedRecordId?: string; // 关联的情绪记录ID
}

// 标记预警状态请求
export interface MarkWarningStatusRequest {
  status: 'pending' | 'processing' | 'resolved';
}

// 情绪周报请求参数
export interface WeeklyReportRequest {
  catId: string;
  weekStartDate: string; // YYYY-MM-DD，周开始日期
}

// 情绪周报响应
export interface WeeklyReportResponse {
  weekStartDate: string; // YYYY-MM-DD
  weekEndDate: string; // YYYY-MM-DD
  summary: string; // 本周总结
  moodTrends: MoodTrendData[]; // 情绪趋势
  avgEmotion: string; // 平均情绪
  avgConfidence: number; // 平均置信度
  warningCount: number; // 预警次数
  highlightMoments: HighlightMoment[]; // 高光时刻
  recommendations: Recommendation[]; // 建议
}

// 高光时刻
export interface HighlightMoment {
  date: string; // YYYY-MM-DD
  emotionTag: string;
  description: string;
}

// 建议
export interface Recommendation {
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
}

// Backward-compatible aliases for older API/composable names.
export type EmotionRecord = EmotionRecordResponse;
export type EmotionRecognitionRequest = RecognizeEmotionRequest;
export type Warning = WarningResponse;