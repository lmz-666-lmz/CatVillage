<template>
  <div class="px-6 pt-6 pb-6">
    <header class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold tracking-tight text-on-background">情绪识别</h1>
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
      <div class="rounded-2xl border border-surface-container-high bg-surface-container-lowest p-4">
        <div class="text-sm font-semibold text-on-background">上传音频</div>
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
        <div class="text-sm font-semibold text-on-background">识别结果</div>
        <div v-if="!lastResult" class="mt-2 text-sm text-on-surface-variant">上传音频后点击“开始识别”</div>
        <div v-else class="mt-3 space-y-1">
          <div class="text-base font-semibold text-on-background">{{ lastResult.emotionTag }}</div>
          <div class="text-xs text-on-surface-variant">置信度：{{ (lastResult.confidence * 100).toFixed(1) }}%</div>
          <div class="mt-2 text-sm text-on-background">{{ lastResult.emotionDescription || '暂无描述' }}</div>
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
  try {
    await ensureCats();
    await refresh();
  } catch {
    showToast({ type: 'fail', message: '加载失败，请检查登录状态' });
  }
});
</script>
