<template>
  <div class="min-h-[100dvh] bg-[radial-gradient(circle_at_15%_-10%,#ffe4cd_0%,#fff7ef_30%,#f7f8fd_100%)] px-4 pt-3 pb-6">
    <header class="sticky top-0 z-20 -mx-4 flex items-center justify-between border-b border-orange-500/10 bg-white/88 px-4 py-3 backdrop-blur-md">
      <button type="button" class="grid h-9 w-9 place-items-center text-slate-600" @click="router.push({ name: 'Social' })">
        <van-icon name="arrow-left" size="20" />
      </button>

      <h1 class="text-xl font-bold tracking-tight text-orange-500">喵喵台</h1>

      <button type="button" class="grid h-9 w-9 place-items-center text-slate-600" @click="showToolsMenu = true">
        <van-icon name="apps-o" size="20" />
      </button>
    </header>

    <section v-if="loading" class="py-10 text-center">
      <van-loading size="24" />
      <div class="mt-3 text-sm text-on-surface-variant">正在准备喵喵台...</div>
    </section>

    <section v-else-if="!hasCats" class="mt-6 rounded-2xl border border-surface-container-high bg-white p-6 text-center">
      <div class="text-3xl">🐱</div>
      <div class="mt-3 text-base font-semibold text-on-background">还没有猫咪档案</div>
      <div class="mt-1 text-sm text-on-surface-variant">先添加一只猫咪，才能使用喵喵台翻译功能</div>
      <button
        type="button"
        class="mt-5 h-11 w-full rounded-xl bg-primary text-on-primary font-semibold shadow-cta active:scale-[0.99]"
        @click="router.push({ name: 'AddCat' })"
      >
        添加猫咪
      </button>
    </section>

    <section v-else>
      <div class="mt-5 text-center">
        <h2 class="text-[26px] font-bold tracking-tight text-[#2b1f15]">喵喵台</h2>
        <p class="mt-1 text-[14px] text-[#7a6f68]">{{ selectedCatHint }}</p>
        <button
          type="button"
          class="mt-3 inline-flex items-center gap-1 rounded-full border border-[#ffd7bf] bg-white px-4 py-1.5 text-[13px] font-semibold text-[#da6d2f]"
          @click="showCatSheet = true"
        >
          切换猫咪
          <van-icon name="arrow-down" size="12" />
        </button>
      </div>

      <div class="relative mt-3 flex h-80 items-center justify-center overflow-hidden">
        <div class="absolute h-72 w-72 rounded-full border border-orange-300/35"></div>
        <div class="absolute h-60 w-60 rounded-full border border-orange-300/40"></div>

        <button
          type="button"
          class="relative z-10 flex h-40 w-40 flex-col items-center justify-center rounded-full bg-[linear-gradient(160deg,#ff8d2a_0%,#ff6b35_100%)] text-white shadow-[0_14px_32px_rgba(255,107,53,0.38)] active:scale-95"
          :disabled="analyzing"
          @click="openAudioPicker"
        >
          <van-icon name="volume-o" size="38" />
          <span class="mt-2 text-sm font-bold">{{ analyzing ? '识别中...' : '正在倾听...' }}</span>
        </button>

        <input ref="audioInputRef" type="file" accept="audio/*" class="hidden" @change="onAudioSelected" />

        <div class="absolute bottom-7 flex items-end gap-1">
          <span
            v-for="(h, idx) in trendBars"
            :key="idx"
            class="w-1 rounded-full bg-orange-500/70"
            :style="{ height: `${h * 6 + 12}px` }"
          ></span>
        </div>
      </div>

      <section class="space-y-4">
        <article class="rounded-2xl border border-orange-500/10 bg-white p-5 shadow-[0_6px_18px_rgba(20,27,43,0.06)]">
          <div class="mb-4 flex items-center justify-between">
            <span class="rounded-full bg-orange-100 px-3 py-1 text-xs font-bold text-orange-600">当前状态</span>
            <van-icon name="smile-o" color="#f97316" size="22" />
          </div>

          <h3 class="text-[24px] font-bold text-on-background">心情指数：{{ moodLabel }}</h3>
          <p class="mt-3 text-[15px] leading-relaxed text-slate-600">
            {{ moodDescription }}
          </p>

          <div class="mt-5 h-2 w-full overflow-hidden rounded-full bg-slate-200">
            <div class="h-full rounded-full bg-[#ff9800]" :style="{ width: `${moodScore}%` }"></div>
          </div>

          <div class="mt-3 flex justify-between text-xs text-slate-500">
            <span>焦虑</span>
            <span>平静</span>
            <span>兴奋</span>
          </div>
        </article>

        <article class="rounded-2xl bg-[linear-gradient(160deg,#ff8d2a_0%,#ff6b35_100%)] p-6 text-center text-white shadow-[0_12px_30px_rgba(255,107,53,0.35)]">
          <van-icon name="star-o" size="28" />
          <p class="mt-3 text-sm font-medium">AI 深度分析</p>
          <p class="mt-2 text-[22px] font-bold leading-tight">{{ deepInsight }}</p>
        </article>

        <article class="rounded-2xl border border-orange-500/10 bg-white p-5 shadow-[0_6px_18px_rgba(20,27,43,0.06)]">
          <h4 class="text-[22px] font-bold text-on-background">今日频率</h4>
          <div class="mt-5 flex h-32 items-end justify-between gap-2">
            <div
              v-for="(h, idx) in frequencyBars"
              :key="idx"
              class="flex-1 rounded-t-sm"
              :class="idx === activeBarIndex ? 'bg-[#ff9800]' : 'bg-orange-300/75'"
              :style="{ height: `${Math.max(15, h * 20)}px` }"
            ></div>
          </div>
          <p class="mt-3 text-center text-sm text-slate-500">近6小时活跃度</p>
        </article>

        <article class="rounded-2xl border border-orange-500/10 bg-white p-5 shadow-[0_6px_18px_rgba(20,27,43,0.06)]">
          <div class="mb-4 flex items-center justify-between gap-3">
            <div>
              <h4 class="text-[22px] font-bold text-on-background">历史足迹</h4>
              <p class="mt-1 text-sm text-slate-500">音频记录和情绪翻译都在这里</p>
            </div>
            <button
              type="button"
              class="rounded-full bg-[#fff2e8] px-4 py-2 text-sm font-bold text-[#ff9800]"
              @click="router.push({ name: 'AudioHistory' })"
            >
              查看全部音频
            </button>
          </div>

          <div v-if="records.length === 0" class="rounded-xl bg-surface-container-low p-4 text-sm text-on-surface-variant">
            暂无历史记录，上传一段音频开始第一次翻译吧。
          </div>

          <div v-else class="space-y-3">
            <button
              v-for="item in records.slice(0, 2)"
              :key="item.id"
              type="button"
              class="flex w-full items-center gap-3 rounded-xl p-3 text-left hover:bg-surface"
              @click="openRecordDetail(item)"
            >
              <div class="grid h-10 w-10 place-items-center rounded-full" :class="item.emotionTag.includes('警') ? 'bg-red-100 text-red-500' : 'bg-sky-100 text-sky-500'">
                <van-icon :name="item.emotionTag.includes('警') ? 'warning-o' : 'chart-trending-o'" size="20" />
              </div>
              <div class="min-w-0 flex-1">
                <p class="truncate text-lg font-bold text-on-background">{{ item.emotionTag }}</p>
                <p class="text-sm text-slate-500">{{ item.createdAt }} · 翻译：{{ shortDescription(item.emotionDescription) }}</p>
              </div>
              <van-icon name="arrow" class="text-slate-400" />
            </button>
          </div>
        </article>
      </section>
    </section>

    <van-action-sheet v-model:show="showToolsMenu" title="AI 工具">
      <div class="p-4">
        <button
          type="button"
          class="flex w-full items-center justify-between rounded-xl border border-orange-500/20 bg-orange-50 px-4 py-3 text-left transition-colors hover:bg-orange-100"
          @click="goToVisualRecognition"
        >
          <div class="flex items-center gap-3">
            <div class="grid h-10 w-10 place-items-center rounded-lg bg-white text-orange-500">
              <van-icon name="photo-o" size="20" />
            </div>
            <div>
              <div class="text-sm font-bold text-orange-700">视觉识别</div>
              <div class="text-xs text-orange-600">ViT 面部微表情识别</div>
            </div>
          </div>
          <van-icon name="arrow" color="#ff6b35" />
        </button>

        <button
          type="button"
          class="mt-3 flex w-full items-center justify-between rounded-xl border border-purple-500/20 bg-purple-50 px-4 py-3 text-left transition-colors hover:bg-purple-100"
          @click="goToAudioVisualFusion"
        >
          <div class="flex items-center gap-3">
            <div class="grid h-10 w-10 place-items-center rounded-lg bg-white text-purple-600">
              <van-icon name="sound-o" size="20" />
            </div>
            <div>
              <div class="text-sm font-bold text-purple-700">视听融合</div>
              <div class="text-xs text-purple-600">多模态情绪融合分析</div>
            </div>
          </div>
          <van-icon name="arrow" color="#764ba2" />
        </button>
      </div>
    </van-action-sheet>

    <van-action-sheet v-model:show="showCatSheet" title="猫咪管理">
      <div class="p-4">
        <div class="mb-3 text-xs text-on-surface-variant">当前：{{ selectedCatHint }}</div>
        <div class="space-y-2">
          <button
            v-for="cat in cats"
            :key="cat.id"
            type="button"
            class="flex w-full items-center justify-between rounded-xl px-3 py-3"
            :class="cat.id === selectedCatId ? 'bg-orange-50 text-orange-600' : 'bg-surface-container-low text-on-background'"
            @click="selectCat(cat.id)"
          >
            <span class="text-sm font-semibold">{{ cat.name }} · {{ cat.breed || '未填写品种' }}</span>
            <van-icon v-if="cat.id === selectedCatId" name="success" />
          </button>
        </div>

        <div class="mt-4 grid grid-cols-2 gap-2">
          <van-button type="primary" @click="router.push({ name: 'AddCat' })">添加猫咪</van-button>
          <van-button plain type="primary" :disabled="!selectedCatId" @click="goEditCat">编辑当前</van-button>
        </div>
      </div>
    </van-action-sheet>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { closeToast, showToast } from 'vant';
import { useEmotionAnalysis } from '@/composables/useEmotionAnalysis';
import type { EmotionRecord, RecognizeEmotionResponse } from '@/types/emotion';
import { useCatsStore, useCurrentCatStore } from '@/stores';

const router = useRouter();
const catsStore = useCatsStore();
const currentCatStore = useCurrentCatStore();
const { analyzeEmotion, fetchEmotionRecords, getCurrentRecords } = useEmotionAnalysis();

const loading = ref(false);
const error = ref<string | null>(null);
const analyzing = ref(false);
const showCatSheet = ref(false);
const showToolsMenu = ref(false);
const audioInputRef = ref<HTMLInputElement | null>(null);
const lastResult = ref<RecognizeEmotionResponse | null>(null);

const cats = computed(() => catsStore.getAllCats);
const selectedCatId = computed(() => currentCatStore.getCurrentCatId || '');
const hasCats = computed(() => cats.value.length > 0);
const records = computed<EmotionRecord[]>(() => getCurrentRecords.value);

const formatAge = (ageInMonths: number) => {
  const years = Math.floor((ageInMonths || 0) / 12);
  const months = (ageInMonths || 0) % 12;
  if (years <= 0) {
    return `${months}个月`;
  }
  return `${years}岁${months}个月`;
};

const selectedCatHint = computed(() => {
  const id = currentCatStore.getCurrentCatId;
  if (!id) {
    return cats.value[0] ? '暂未选择，点击下方切换猫咪' : '未选择（请先添加猫咪）';
  }
  const cat = catsStore.getCatById(id);
  return cat ? `${cat.name} · ${cat.breed || '未填写品种'} · ${formatAge(cat.age)}` : '未选择（当前猫咪不存在）';
});

const moodLabel = computed(() => {
  const tag = lastResult.value?.emotionTag || records.value[0]?.emotionTag || '平静';
  if (tag.includes('警') || tag.includes('紧张') || tag.includes('焦')) {
    return '警惕';
  }
  if (tag.includes('兴') || tag.includes('活跃')) {
    return '兴奋';
  }
  return '愉快';
});

const moodScore = computed(() => {
  const score = Math.round((lastResult.value?.confidence ?? records.value[0]?.confidence ?? 0.72) * 100);
  return Math.min(98, Math.max(20, score));
});

const moodDescription = computed(() => {
  return (
    lastResult.value?.emotionDescription ||
    records.value[0]?.emotionDescription ||
    '您的猫咪目前处于非常放松的状态，尾巴轻微摆动。它可能在表达对环境的满意和对您的信任。'
  );
});

const deepInsight = computed(() => {
  const text = moodDescription.value;
  if (text.includes('吃') || text.includes('食')) {
    return '它可能想吃罐头了';
  }
  if (text.includes('警') || text.includes('不适')) {
    return '建议关注环境变化';
  }
  return '状态稳定，继续观察';
});

const frequencyBars = computed(() => {
  const bins = [0, 0, 0, 0, 0, 0];
  const now = Date.now();
  for (const item of records.value.slice(0, 100)) {
    const ts = Date.parse(item.createdAt);
    if (Number.isNaN(ts)) {
      continue;
    }
    const hours = (now - ts) / 1000 / 3600;
    if (hours < 0 || hours > 6) {
      continue;
    }
    const idx = Math.min(5, Math.floor(hours));
    const bucket = 5 - idx;
    bins[bucket] = (bins[bucket] ?? 0) + 1;
  }
  return bins;
});

const trendBars = computed(() => {
  const source = frequencyBars.value;
  return source.map((n, i) => n + (i % 2));
});

const activeBarIndex = computed(() => {
  let max = 0;
  let idx = 0;
  frequencyBars.value.forEach((v, i) => {
    if (v >= max) {
      max = v;
      idx = i;
    }
  });
  return idx;
});

const selectCat = (catId: string) => {
  currentCatStore.setCurrentCat(catId);
  showCatSheet.value = false;
  void loadRecords();
  showToast({ type: 'success', message: '已切换当前猫咪' });
};

const openAudioPicker = () => {
  if (!selectedCatId.value) {
    showToast({ type: 'fail', message: '请先选择猫咪' });
    return;
  }
  audioInputRef.value?.click();
};

const onAudioSelected = async (event: Event) => {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file || !selectedCatId.value) {
    return;
  }

  analyzing.value = true;
  showToast({ type: 'loading', message: '正在翻译猫语...', duration: 0, forbidClick: true });
  try {
    const res = await analyzeEmotion({ catId: selectedCatId.value, audioFile: file });
    lastResult.value = res;
    closeToast();
    showToast({ type: 'success', message: '翻译完成' });
    await loadRecords();
  } catch {
    closeToast();
    showToast({ type: 'fail', message: '识别失败，请稍后重试' });
  } finally {
    analyzing.value = false;
    input.value = '';
  }
};

const shortDescription = (desc: string) => {
  if (!desc) {
    return '暂无描述';
  }
  return desc.length > 12 ? `${desc.slice(0, 12)}...` : desc;
};

const loadRecords = async () => {
  if (!selectedCatId.value) {
    return;
  }
  try {
    await fetchEmotionRecords({ page: 1, pageSize: 20, catId: selectedCatId.value });
  } catch {
    // Keep UI usable even if history request fails.
  }
};

const goEditCat = () => {
  if (!selectedCatId.value) {
    return;
  }
  router.push({ name: 'EditCat', params: { id: selectedCatId.value } });
};

const openRecordDetail = (item: EmotionRecord) => {
  router.push({
    name: 'MeowRecordDetail',
    params: { recordId: item.id },
    query: {
      tag: item.emotionTag,
      confidence: String(item.confidence ?? 0),
      desc: item.emotionDescription || '',
      time: item.createdAt,
      cat: selectedCatHint.value,
    },
  });
};

const goToVisualRecognition = () => {
  showToolsMenu.value = false;
  router.push({ name: 'VisualRecognition' });
};

const goToAudioVisualFusion = () => {
  showToolsMenu.value = false;
  router.push({ name: 'AudioVisualFusion' });
};

const refresh = async () => {
  if (loading.value) {
    return;
  }
  loading.value = true;
  error.value = null;
  try {
    await catsStore.fetchAllCats();
    const first = catsStore.getAllCats[0];
    if (!currentCatStore.getCurrentCatId && first) {
      currentCatStore.setCurrentCat(first.id);
    }
    await loadRecords();
  } catch {
    error.value = '加载失败，请检查登录状态或后端服务';
  } finally {
    loading.value = false;
  }
};

const reload = () => refresh();

onMounted(refresh);
</script>