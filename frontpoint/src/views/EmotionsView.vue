<template>
  <div class="bg-background px-6 pt-6 pb-8">
    <div v-if="loading" class="rounded-2xl border border-surface-container-high bg-surface-container-lowest px-4 py-10 text-center text-sm text-on-surface-variant">
      <van-loading size="20" />
      <div class="mt-3">正在加载情绪识别页面...</div>
    </div>

    <div v-else-if="error" class="rounded-2xl border border-surface-container-high bg-surface-container-lowest px-4 py-10 text-center text-sm text-on-surface-variant">
      <div class="text-base font-semibold text-on-background">情绪识别加载失败</div>
      <div class="mt-2">{{ error }}</div>
      <van-button class="mt-4" type="primary" @click="reload">重试</van-button>
    </div>

    <div v-else>
    <header class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold tracking-tight text-on-background">异常预警</h1>
        <p class="mt-1 text-sm text-on-surface-variant">{{ selectedCatName }}</p>
      </div>
      <van-button size="small" plain type="primary" :disabled="!hasCats" @click="refresh">刷新</van-button>
    </header>

    <section v-if="!hasCats" class="mt-6 rounded-2xl border border-surface-container-high bg-surface-container-lowest p-6 text-center">
      <div class="text-3xl">🎧</div>
      <div class="mt-3 text-base font-semibold text-on-background">还没有猫咪档案</div>
      <div class="mt-1 text-sm text-on-surface-variant">先添加猫咪，才能上传音频做情绪识别</div>
      <van-button class="mt-5" block type="primary" @click="router.push({ name: 'AddCat' })">去添加猫咪</van-button>
    </section>

    <section v-else class="mt-6 space-y-4">
      <div class="rounded-2xl bg-gradient-to-br from-[#ab3500] to-[#ff6b35] p-5 text-white shadow-[0_12px_40px_rgba(171,53,0,0.15)]">
        <div class="flex items-start justify-between gap-3">
          <div>
            <h2 class="text-2xl font-extrabold tracking-tight">异常预警</h2>
            <p class="mt-1 text-sm text-white/80">预警发布：今日</p>
          </div>
          <div class="rounded-xl bg-white/20 p-2 backdrop-blur-md">
            <van-icon name="warning-o" size="24" color="#fff" />
          </div>
        </div>
        <div class="mt-4 rounded-lg bg-white/10 px-3 py-2 text-sm font-bold">{{ selectedCatName }}</div>
      </div>

      <div class="rounded-2xl border border-surface-container-high bg-surface-container-lowest p-4">
        <div class="mb-2 text-sm font-semibold text-on-background">上传音频分析</div>
        <div class="mt-2">
          <van-uploader
            v-model="audioList"
            :max-count="1"
            accept="audio/*"
            :preview-image="false"
          />
        </div>
        <div class="mt-3">
          <button
            type="button"
            class="h-11 w-full rounded-xl bg-primary text-on-primary font-semibold shadow-cta disabled:opacity-60"
            :disabled="analyzing || !audioFile"
            @click="analyze"
          >
            {{ analyzing ? '识别中...' : '开始识别' }}
          </button>
        </div>
      </div>

      <div class="rounded-2xl border border-surface-container-high bg-surface-container-lowest p-4">
        <div class="text-sm font-semibold text-on-background">异常说明</div>
        <div v-if="!lastResult" class="mt-2 text-sm text-on-surface-variant">上传音频后点击“开始识别”</div>
        <div v-else class="mt-3 space-y-1">
          <div class="text-base font-semibold text-on-background">{{ lastResult.emotionTag }}</div>
          <div class="text-xs text-on-surface-variant">置信度：{{ (lastResult.confidence * 100).toFixed(1) }}%</div>
          <div class="mt-2 text-sm text-on-background">{{ lastResult.emotionDescription || '暂无描述' }}</div>
        </div>
      </div>

      <div class="rounded-2xl border border-surface-container-high bg-surface-container-lowest p-4">
        <div class="mb-3 text-sm font-semibold text-on-background">建议处理方式</div>
        <div class="space-y-2">
          <div class="flex items-center justify-between rounded-xl bg-surface-container-low px-4 py-3">
            <div class="flex items-center gap-3">
              <div class="grid h-9 w-9 place-items-center rounded-full bg-secondary-container">
                <van-icon name="passed" color="#585f6c" />
              </div>
              <span class="text-sm font-semibold text-on-background">检查饮水与排泄</span>
            </div>
            <van-icon name="arrow" color="#8d7168" />
          </div>

          <div class="flex items-center justify-between rounded-xl border-l-4 border-primary bg-primary-container/10 px-4 py-3">
            <div class="flex items-center gap-3">
              <div class="grid h-9 w-9 place-items-center rounded-full bg-primary text-white">
                <van-icon name="service-o" />
              </div>
              <div>
                <div class="text-sm font-bold text-primary">立即咨询兽医</div>
                <div class="text-[10px] font-bold uppercase tracking-wider text-on-primary-fixed-variant/70">高优先级行动</div>
              </div>
            </div>
            <van-icon name="phone-o" color="#ab3500" />
          </div>
        </div>
      </div>

      <div class="rounded-2xl border border-surface-container-high bg-surface-container-lowest p-4">
        <div class="flex items-center justify-between">
          <div class="text-sm font-semibold text-on-background">历史记录</div>
          <div class="text-xs text-on-surface-variant">最近 10 条</div>
        </div>

        <div v-if="historyLoading" class="py-6 text-center">
          <van-loading size="20" />
        </div>

        <div v-else-if="records.length === 0" class="mt-3 text-sm text-on-surface-variant">暂无记录</div>

        <div v-else class="mt-3 space-y-2">
          <div
            v-for="rec in records"
            :key="rec.id"
            class="rounded-xl border border-surface-container-high bg-surface-container-high p-3"
          >
            <div class="flex items-center justify-between gap-2">
              <div class="text-sm font-semibold text-on-background">{{ rec.emotionTag }}</div>
              <div class="text-xs text-on-surface-variant">{{ rec.createdAt }}</div>
            </div>
            <div class="mt-1 text-xs text-on-surface-variant">置信度：{{ (rec.confidence * 100).toFixed(1) }}%</div>
          </div>
        </div>
      </div>
    </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { closeToast, showToast } from 'vant';
import type { UploaderFileListItem } from 'vant';
import { useEmotionAnalysis } from '@/composables/useEmotionAnalysis';
import { useCatsStore, useCurrentCatStore } from '@/stores';
import type { RecognizeEmotionResponse } from '@/types/emotion';

const router = useRouter();
const catsStore = useCatsStore();
const currentCatStore = useCurrentCatStore();

const { analyzeEmotion, fetchEmotionRecords, getCurrentRecords } = useEmotionAnalysis();

const audioList = ref<UploaderFileListItem[]>([]);
const analyzing = ref(false);
const historyLoading = ref(false);
const lastResult = ref<RecognizeEmotionResponse | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);

const records = computed(() => getCurrentRecords.value);

const selectedCatId = computed(() => currentCatStore.getCurrentCatId || catsStore.getAllCats[0]?.id || '');
const hasCats = computed(() => catsStore.getAllCats.length > 0);
const selectedCatName = computed(() => {
  const id = selectedCatId.value;
  if (!id) {
    return '未选择猫咪';
  }
  const cat = catsStore.getCatById(id);
  return cat?.name ? `当前：${cat.name}` : '未选择猫咪';
});

const audioFile = computed(() => audioList.value[0]?.file || null);

const ensureCats = async () => {
  await catsStore.fetchAllCats();
  const first = catsStore.getAllCats[0];
  if (!currentCatStore.getCurrentCatId && first) {
    currentCatStore.setCurrentCat(first.id);
  }
};

const initData = async () => {
  loading.value = true;
  error.value = null;
  try {
    await ensureCats();
    await refresh();
  } catch {
    error.value = '加载失败，请检查登录状态或后端服务';
  } finally {
    loading.value = false;
  }
};

const reload = () => initData();

const analyze = async () => {
  const catId = selectedCatId.value;
  const file = audioFile.value;
  if (!catId || !file) {
    return;
  }

  analyzing.value = true;
  showToast({ type: 'loading', message: '正在识别...', duration: 0, forbidClick: true });
  try {
    lastResult.value = await analyzeEmotion({ catId, audioFile: file });
    closeToast();
    showToast({ type: 'success', message: '识别完成' });
    await refresh();
  } catch {
    closeToast();
    showToast({ type: 'fail', message: '识别失败，请稍后重试' });
  } finally {
    analyzing.value = false;
  }
};

const refresh = async () => {
  const catId = selectedCatId.value;
  if (!catId) {
    return;
  }
  historyLoading.value = true;
  try {
    await fetchEmotionRecords({ page: 1, pageSize: 10, catId });
  } catch {
    // ignore
  } finally {
    historyLoading.value = false;
  }
};

onMounted(async () => {
  await initData();
});
</script>
