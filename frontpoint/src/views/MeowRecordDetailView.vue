<template>
  <div class="min-h-[100dvh] bg-[#f5f7fb] px-4 pt-3 pb-8">
    <van-nav-bar title="历史详情" left-arrow @click-left="router.back()" />

    <section v-if="loading" class="py-10 text-center">
      <van-loading size="24" />
      <div class="mt-3 text-sm text-[#748094]">正在加载记录详情...</div>
    </section>

    <section v-else-if="error" class="mt-4 rounded-[22px] border border-[rgba(226,232,240,0.92)] bg-[rgba(255,255,255,0.92)] p-6 text-center shadow-[0_12px_26px_rgba(23,32,51,0.06)]">
      <div class="text-base font-semibold text-[#172033]">记录加载失败</div>
      <div class="mt-2 text-sm text-[#748094]">{{ error }}</div>
      <van-button class="mt-4" type="primary" @click="loadDetail">重试</van-button>
    </section>

    <section v-else class="mt-4 space-y-4">
      <article class="rounded-[22px] border border-[rgba(226,232,240,0.92)] bg-[rgba(255,255,255,0.92)] p-5 shadow-[0_12px_26px_rgba(23,32,51,0.06)]">
        <div class="mb-3 flex items-center justify-between">
          <h2 class="text-lg font-bold text-[#172033]">记录信息</h2>
          <span class="rounded-full bg-[#f97316]/15 px-3 py-1 text-xs font-bold text-[#f97316]">{{ moodLabel }}</span>
        </div>

        <div class="space-y-2 text-sm text-[#748094]">
          <div>猫咪：{{ catLabel }}</div>
          <div>识别时间：{{ detailTime }}</div>
          <div>置信度：{{ confidenceText }}</div>
        </div>
      </article>

      <article class="rounded-[22px] border border-[rgba(226,232,240,0.92)] bg-[rgba(255,255,255,0.92)] p-5 shadow-[0_12px_26px_rgba(23,32,51,0.06)]">
        <h3 class="text-base font-bold text-[#172033]">完整分析</h3>
        <p class="mt-3 text-sm leading-relaxed text-[#748094]">{{ descriptionText }}</p>

        <div class="mt-4 h-2 w-full overflow-hidden rounded-full bg-[#edf2f7]">
          <div class="h-full rounded-full bg-[#f97316]" :style="{ width: `${confidencePercent}%` }"></div>
        </div>
      </article>

      <article class="rounded-[22px] border border-[rgba(226,232,240,0.92)] bg-[rgba(255,255,255,0.92)] p-5 shadow-[0_12px_26px_rgba(23,32,51,0.06)]">
        <h3 class="text-base font-bold text-[#172033]">建议行动</h3>
        <div class="mt-3 space-y-2">
          <div v-for="tip in recommendations" :key="tip" class="rounded-xl bg-[#f7fafc] px-3 py-3 text-sm text-[#172033]">
            {{ tip }}
          </div>
        </div>
      </article>

      <article class="rounded-[22px] border border-[rgba(226,232,240,0.92)] bg-[rgba(255,255,255,0.92)] p-5 shadow-[0_12px_26px_rgba(23,32,51,0.06)]">
        <h3 class="text-base font-bold text-[#172033]">音频回放</h3>

        <div v-if="audioUrl" class="mt-3">
          <audio :src="audioUrl" controls class="w-full"></audio>
        </div>

        <div v-else class="mt-3 rounded-xl bg-[#f7fafc] p-4 text-sm text-[#748094]">
          当前后端记录未返回音频地址，暂不可回放。后端补充 `audio_url` 字段后此处会自动可播。
        </div>
      </article>

      <button type="button" class="h-12 w-full rounded-[16px] bg-[#fff1f2] text-[15px] font-extrabold text-[#e11d48]" @click="deleteCurrentRecord">
        删除这条记录
      </button>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { showConfirmDialog, showToast } from 'vant';
import { useEmotionAnalysis } from '@/composables/useEmotionAnalysis';
import { createAuthorizedAudioObjectUrl } from '@/api/emotion';

const props = defineProps<{ recordId: string }>();
const route = useRoute();
const router = useRouter();
const { fetchEmotionRecordDetail, removeEmotionRecord } = useEmotionAnalysis();

const loading = ref(false);
const error = ref<string | null>(null);

const detailLabel = ref(String(route.query.tag || '未知'));
const detailConfidence = ref(Number(route.query.confidence || 0));
const detailDescription = ref(String(route.query.desc || ''));
const detailTime = ref(String(route.query.time || ''));
const audioUrl = ref('');

const catLabel = computed(() => String(route.query.cat || '未指定猫咪'));
const moodLabel = computed(() => detailLabel.value || '未知');
const confidencePercent = computed(() => {
  const n = Math.round(detailConfidence.value * 100);
  return Math.max(10, Math.min(99, n));
});
const confidenceText = computed(() => `${confidencePercent.value}%`);
const descriptionText = computed(() => {
  if (detailDescription.value) {
    return detailDescription.value;
  }
  if (moodLabel.value.includes('警') || moodLabel.value.includes('焦')) {
    return '检测到紧张或警惕信号，请先排查环境刺激，并观察饮水、食欲与排泄变化。';
  }
  if (moodLabel.value.includes('兴')) {
    return '检测到较高活跃状态，可通过互动玩具消耗精力并保持规律作息。';
  }
  return '整体状态较稳定，建议持续记录叫声变化并保持日常陪伴。';
});

const recommendations = computed(() => {
  if (moodLabel.value.includes('警') || moodLabel.value.includes('焦')) {
    return ['减少噪音和陌生刺激，提供安静休息区', '观察 24 小时内进食和饮水是否异常', '若持续异常，建议联系兽医'];
  }
  if (moodLabel.value.includes('兴')) {
    return ['安排 10-15 分钟互动游戏释放精力', '使用益智喂食器降低单次进食速度', '睡前降低环境刺激帮助平稳入睡'];
  }
  return ['保持规律喂食和陪伴节奏', '持续记录每天 2-3 次叫声样本', '每周查看一次情绪趋势变化'];
});

const loadDetail = async () => {
  loading.value = true;
  error.value = null;
  try {
    const data = await fetchEmotionRecordDetail(props.recordId);
    detailLabel.value = data.emotionTag || detailLabel.value;
    detailConfidence.value = data.confidence ?? detailConfidence.value;
    detailDescription.value = data.emotionDescription || detailDescription.value;
    detailTime.value = data.createdAt || detailTime.value;
    audioUrl.value = data.audioUrl ? await createAuthorizedAudioObjectUrl(data.audioUrl) : '';
  } catch {
    error.value = '请稍后重试';
  } finally {
    loading.value = false;
  }
};

const deleteCurrentRecord = async () => {
  try {
    await showConfirmDialog({
      title: '删除记录',
      message: '确认删除这条情绪/叫声记录吗？'
    });
  } catch {
    return;
  }
  try {
    await removeEmotionRecord(props.recordId);
    showToast({ type: 'success', message: '记录已删除' });
    router.back();
  } catch {
    showToast({ type: 'fail', message: '删除失败，请稍后重试' });
  }
};

onMounted(loadDetail);
</script>
