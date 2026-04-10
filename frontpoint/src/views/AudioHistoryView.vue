<template>
  <div class="min-h-[100dvh] bg-[#f6f7fb] px-4 pt-4 pb-8">
    <header class="sticky top-0 z-20 flex items-center justify-between bg-[#f6f7fb]/95 py-2 backdrop-blur">
      <button type="button" class="grid h-10 w-10 place-items-center text-[#ef642e]" @click="$router.back()">
        <van-icon name="arrow-left" size="22" />
      </button>
      <h1 class="text-[24px] font-black tracking-wide text-[#ef642e]">Cat Voice Records</h1>
      <button type="button" class="grid h-10 w-10 place-items-center text-[#ef642e]" @click="refresh">
        <van-icon name="setting-o" size="22" />
      </button>
    </header>

    <main class="mt-4 space-y-5">
      <section class="relative overflow-hidden rounded-[24px] bg-[#111] shadow-[0_16px_34px_rgba(0,0,0,0.12)]">
        <div class="absolute inset-0">
          <van-image :src="heroImage" width="100%" height="100%" fit="cover" />
          <div class="absolute inset-0 bg-[linear-gradient(90deg,rgba(0,0,0,0.72)_0%,rgba(0,0,0,0.28)_55%,rgba(0,0,0,0.12)_100%)]"></div>
        </div>
        <div class="relative min-h-[215px] p-5 text-white">
          <div class="inline-flex rounded-full bg-[#ff6b35] px-4 py-2 text-[15px] font-bold shadow-[0_6px_16px_rgba(255,107,53,0.25)]">今日记录</div>
          <h2 class="mt-7 max-w-[78%] text-[28px] font-black leading-[1.08]">{{ selectedCatName }}的日常心声</h2>
          <p class="mt-3 text-[14px] text-white/80">记录每一段音频，识别情绪并追踪变化趋势</p>
        </div>
      </section>

      <div v-if="historyLoading" class="py-10 text-center">
        <van-loading size="24" color="#ef642e" />
      </div>

      <div v-else-if="records.length === 0" class="rounded-[18px] border border-[#e8eaf3] bg-white p-6 text-center text-sm text-[#6f7790]">
        暂无音频记录，去喵喵台录一段音频试试吧。
      </div>

      <section v-else class="space-y-6">
        <div v-for="group in groupedRecords" :key="group.dateKey">
          <div class="mb-3 text-[18px] font-black tracking-[0.12em] text-[#a7a2a0] uppercase">{{ group.title }}</div>

          <div class="space-y-3">
            <article
              v-for="record in group.items"
              :key="record.id"
              class="rounded-[18px] bg-white px-4 py-4 shadow-[0_2px_10px_rgba(15,23,42,0.04)]"
            >
              <div class="flex items-center gap-4">
                <button
                  type="button"
                  class="grid h-16 w-16 place-items-center rounded-full bg-[#ff6b35] text-white shadow-[0_10px_20px_rgba(255,107,53,0.22)]"
                  @click="toggleAudio(record.id)"
                >
                  <van-icon :name="playingId === record.id ? 'pause' : 'play'" size="24" />
                </button>

                <div class="min-w-0 flex-1">
                  <div class="flex items-start justify-between gap-3">
                    <div class="min-w-0">
                      <span class="inline-flex rounded-full px-3 py-1 text-[13px] font-black" :class="emotionBadgeClass(record.emotionTag)">
                        {{ record.emotionTag || '未识别情绪' }}
                      </span>
                      <div class="mt-2 text-[18px] font-black text-[#1f2432]">{{ shortEmotionDescription(record.emotionDescription) }}</div>
                    </div>
                    <div class="text-right text-[13px] text-[#655850]">
                      <div>{{ formatClock(record.createdAt) }}</div>
                      <div class="mt-1">{{ formatDuration(record.audioUrl) }}</div>
                    </div>
                  </div>

                  <div class="mt-3 flex items-center gap-3">
                    <div class="h-1.5 flex-1 rounded-full bg-[#e5e7ef]">
                      <div class="h-full rounded-full bg-[#ef642e]" :style="{ width: `${Math.max(20, record.confidence * 100)}%` }"></div>
                    </div>
                    <span class="text-[13px] font-bold text-[#ef642e]">{{ (record.confidence * 100).toFixed(1) }}%</span>
                  </div>

                  <div class="mt-2 text-[13px] leading-relaxed text-[#6a7082]">{{ record.audioUrl ? '点击左侧按钮即可播放这段音频。' : '这段记录暂时没有可播放音频，但情绪结果已保存。' }}</div>

                  <audio
                    v-if="record.audioUrl"
                    :ref="(el) => setAudioRef(record.id, el as HTMLAudioElement | null)"
                    :src="record.audioUrl"
                    class="hidden"
                    preload="none"
                    @ended="onAudioEnded(record.id)"
                  ></audio>
                </div>
              </div>
            </article>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useEmotionAnalysis } from '@/composables/useEmotionAnalysis';
import { useCatsStore, useCurrentCatStore } from '@/stores';

type RecordItem = {
  id: string;
  catId: string;
  userId: string;
  audioUrl: string;
  emotionTag: string;
  confidence: number;
  emotionDescription: string;
  createdAt: string;
};

const { fetchEmotionRecords, getCurrentRecords, isLoading: historyLoading } = useEmotionAnalysis();
const catsStore = useCatsStore();
const currentCatStore = useCurrentCatStore();

const records = computed(() => getCurrentRecords.value as RecordItem[]);
const selectedCatId = computed(() => currentCatStore.getCurrentCatId || catsStore.getAllCats[0]?.id || '');
const selectedCatName = computed(() => {
  const cat = selectedCatId.value ? catsStore.getCatById(selectedCatId.value) : null;
  return cat?.name || '小猫';
});

const heroImage = computed(() => {
  const cat = selectedCatId.value ? catsStore.getCatById(selectedCatId.value) : null;
  return cat?.avatarUrl || 'https://images.unsplash.com/photo-1513245543132-31f507417b26?w=1200&h=700&fit=crop';
});

const groupedRecords = computed(() => {
  const groups = new Map<string, { dateKey: string; title: string; items: RecordItem[] }>();

  records.value.forEach((record) => {
    const date = new Date(record.createdAt);
    const dateKey = Number.isNaN(date.getTime()) ? 'unknown' : `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
    const title = formatGroupTitle(date);
    if (!groups.has(dateKey)) {
      groups.set(dateKey, { dateKey, title, items: [] });
    }
    groups.get(dateKey)!.items.push(record);
  });

  return Array.from(groups.values());
});

const playingId = ref('');
const audioRefs = new Map<string, HTMLAudioElement>();

const setAudioRef = (id: string, el: HTMLAudioElement | null) => {
  if (el) {
    audioRefs.set(id, el);
  } else {
    audioRefs.delete(id);
  }
};

const toggleAudio = async (id: string) => {
  const audio = audioRefs.get(id);
  if (!audio) return;

  if (playingId.value === id && !audio.paused) {
    audio.pause();
    playingId.value = '';
    return;
  }

  audioRefs.forEach((otherAudio, otherId) => {
    if (otherId !== id) {
      otherAudio.pause();
    }
  });

  try {
    await audio.play();
    playingId.value = id;
  } catch {
    playingId.value = '';
  }
};

const onAudioEnded = (id: string) => {
  if (playingId.value === id) {
    playingId.value = '';
  }
};

const refresh = async () => {
  await catsStore.fetchAllCats();
  if (!selectedCatId.value && catsStore.getAllCats[0]?.id) {
    currentCatStore.setCurrentCat(catsStore.getAllCats[0].id);
  }
  if (selectedCatId.value) {
    await fetchEmotionRecords({ page: 1, pageSize: 50, catId: selectedCatId.value });
  }
};

const formatGroupTitle = (date: Date) => {
  if (Number.isNaN(date.getTime())) {
    return 'UNKNOWN DATE';
  }

  const today = new Date();
  const isToday = date.toDateString() === today.toDateString();
  if (isToday) {
    return `TODAY, ${date.getDate()} ${date.toLocaleString('en-US', { month: 'long' }).toUpperCase()}`;
  }

  const yesterday = new Date();
  yesterday.setDate(today.getDate() - 1);
  if (date.toDateString() === yesterday.toDateString()) {
    return `YESTERDAY, ${date.getDate()} ${date.toLocaleString('en-US', { month: 'long' }).toUpperCase()}`;
  }

  return `${date.getDate()} ${date.toLocaleString('en-US', { month: 'long' }).toUpperCase()}`;
};

const formatClock = (value: string) => {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '';
  const hours = date.getHours();
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const suffix = hours >= 12 ? 'PM' : 'AM';
  const normalized = hours % 12 === 0 ? 12 : hours % 12;
  return `${String(normalized).padStart(2, '0')}:${minutes} ${suffix}`;
};

const formatDuration = (audioUrl: string) => {
  if (!audioUrl) return '0:03';
  return '0:04';
};

const shortEmotionDescription = (value: string) => {
  if (!value) return '系统已记录该段音频的情绪';
  return value.length > 24 ? `${value.slice(0, 24)}...` : value;
};

const emotionBadgeClass = (emotionTag: string) => {
  if (/警|焦虑|异常|悲|愤怒/i.test(emotionTag)) {
    return 'bg-[#ffe5df] text-[#c24a18]';
  }
  if (/开心|平静|轻松|愉快|满足/i.test(emotionTag)) {
    return 'bg-[#eaf7ff] text-[#1782a8]';
  }
  return 'bg-[#eef2fb] text-[#626b82]';
};

onMounted(async () => {
  await refresh();
});
</script>