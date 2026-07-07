import { ref } from 'vue';
import type { CatProfile } from '@/types/cat';
import { getWarningList } from '@/api/emotion';
import { getWeightRecords, getFeedingRecords } from '@/api/health';

export interface HealthInfo {
  score: number;
  status: string;
}

export function useHealthScore() {
  const healthLoading = ref(false);
  const healthInfo = ref<HealthInfo>({ score: 0, status: '加载中' });

  const calculateScore = (
    cat: CatProfile | null,
    warningCounts: { high: number; medium: number; low: number },
    hasWeightRecords: boolean,
    hasFeedingRecords: boolean
  ): HealthInfo => {
    if (!cat) return { score: 0, status: '无数据' };

    let score = 70; // 基础分

    // 档案完整度 (+18 max)
    if (cat.weight && cat.weight > 0) score += 4;
    if (cat.age !== undefined && cat.age !== null && cat.age > 0) score += 2;
    if (cat.breed && cat.breed.trim()) score += 2;
    if (cat.isNeutered !== undefined && cat.isNeutered !== null) score += 3;
    if (cat.medicalHistory && cat.medicalHistory.trim()) score += 4;
    if (cat.vaccineStatus && cat.vaccineStatus.trim()) score += 3;

    // 健康记录 (+10 max)
    if (hasWeightRecords) score += 5;
    if (hasFeedingRecords) score += 5;

    // 预警扣分
    if (warningCounts.high + warningCounts.medium + warningCounts.low === 0) {
      score += 7; // 无预警加分
    }
    score -= warningCounts.high * 12;
    score -= warningCounts.medium * 6;
    score -= warningCounts.low * 2;

    score = Math.max(0, Math.min(100, Math.round(score)));

    let status: string;
    if (score >= 90) status = '优秀';
    else if (score >= 75) status = '良好';
    else if (score >= 60) status = '一般';
    else status = '需关注';

    return { score, status };
  };

  const fetchHealthData = async (catId: string) => {
    if (!catId) {
      healthInfo.value = { score: 0, status: '无数据' };
      return;
    }

    healthLoading.value = true;

    // 并行请求三类数据
    const [warningsRes, weightRes, feedingRes] = await Promise.allSettled([
      getWarningList({ page: 1, pageSize: 50, catId }).catch(() => null),
      getWeightRecords({ petId: catId, page: 1, pageSize: 5 }).catch(() => null),
      getFeedingRecords({ petId: catId, page: 1, pageSize: 5 }).catch(() => null)
    ]);

    const warnings = warningsRes.status === 'fulfilled' && warningsRes.value
      ? (warningsRes.value.data?.list || [])
      : [];
    const weightList = weightRes.status === 'fulfilled' && weightRes.value
      ? (weightRes.value.data?.list || [])
      : [];
    const feedingList = feedingRes.status === 'fulfilled' && feedingRes.value
      ? (feedingRes.value.data?.list || [])
      : [];

    const warningCounts = {
      high: warnings.filter((w: any) => w.level === 'high').length,
      medium: warnings.filter((w: any) => w.level === 'medium').length,
      low: warnings.filter((w: any) => w.level === 'low').length
    };

    healthLoading.value = false;
    return { warningCounts, hasWeightRecords: weightList.length > 0, hasFeedingRecords: feedingList.length > 0 };
  };

  return {
    healthLoading,
    healthInfo,
    calculateScore,
    fetchHealthData
  };
}
