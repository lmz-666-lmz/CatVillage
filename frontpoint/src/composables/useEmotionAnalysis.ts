/* eslint-disable @typescript-eslint/no-explicit-any */

import { ref, computed } from 'vue';
import type { 
  EmotionRecord, 
  EmotionRecognitionRequest
} from '@/types/emotion';
import { 
  recognizeEmotion, 
  getEmotionRecords, 
  getEmotionRecordDetail, 
  getEmotionStatistics,
  getWarningList,
  markWarningStatus,
  getWeeklyReport
} from '@/api/emotion';

/**
 * 情绪分析 Composable
 * 提供情绪识别、记录管理、统计分析等操作方法
 */
export function useEmotionAnalysis() {
  const loading = ref(false);
  const error = ref<string | null>(null);
  const records = ref<EmotionRecord[]>([]);

  /**
   * 上传音频并识别情绪
   */
  const analyzeEmotion = async (data: EmotionRecognitionRequest) => {
    loading.value = true;
    error.value = null;

    try {
      const formData = new FormData();
      formData.append('catId', data.catId);
      formData.append('audioFile', data.audioFile);
      const response = await recognizeEmotion(formData);
      return response.data;
    } catch (err: any) {
      error.value = err.message || '情绪识别失败';
      console.error('情绪识别失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 获取情绪识别历史记录
   */
  const fetchEmotionRecords = async (params: { page: number; pageSize: number; catId?: string }) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await getEmotionRecords(params);
      records.value = response.data.list || [];
      return response.data;
    } catch (err: any) {
      error.value = err.message || '获取情绪记录失败';
      console.error('获取情绪记录失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 获取单条情绪记录详情
   */
  const fetchEmotionRecordDetail = async (recordId: string) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await getEmotionRecordDetail(recordId);
      return response.data;
    } catch (err: any) {
      error.value = err.message || '获取情绪记录详情失败';
      console.error('获取情绪记录详情失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 获取情绪统计可视化数据
   */
  const fetchEmotionStatistics = async (params: { catId?: string; startDate?: string; endDate?: string }) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await getEmotionStatistics(params);
      return response.data;
    } catch (err: any) {
      error.value = err.message || '获取情绪统计失败';
      console.error('获取情绪统计失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 获取健康预警列表
   */
  const fetchWarningList = async (params: { page: number; pageSize: number; catId?: string; status?: string }) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await getWarningList(params);
      return response.data;
    } catch (err: any) {
      error.value = err.message || '获取预警列表失败';
      console.error('获取预警列表失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 标记预警状态
   */
  const updateWarningStatus = async (warningId: string, status: string) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await markWarningStatus(warningId, status);
      return response.data;
    } catch (err: any) {
      error.value = err.message || '更新预警状态失败';
      console.error('更新预警状态失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 生成情绪周报
   */
  const generateWeeklyReport = async (params: { catId?: string; week?: string }) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await getWeeklyReport(params);
      return response.data;
    } catch (err: any) {
      error.value = err.message || '生成周报失败';
      console.error('生成周报失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 获取当前情绪记录列表
   */
  const getCurrentRecords = computed(() => records.value);

  /**
   * 是否正在加载
   */
  const isLoading = computed(() => loading.value);

  /**
   * 获取错误信息
   */
  const getError = computed(() => error.value);

  return {
    // Methods
    analyzeEmotion,
    fetchEmotionRecords,
    fetchEmotionRecordDetail,
    fetchEmotionStatistics,
    fetchWarningList,
    updateWarningStatus,
    generateWeeklyReport,

    // Getters
    getCurrentRecords,
    isLoading,
    getError
  };
}