<template>
  <div class="min-h-[100dvh] bg-[#f4f5fb] px-5 pt-4 pb-10">
    <header class="flex min-h-[54px] items-center justify-between">
      <button type="button" class="grid h-10 w-10 place-items-center text-[#222734]" @click="router.push({ name: 'AIAssistant' })">
        <van-icon name="arrow-left" size="22" />
      </button>
      <h1 class="text-[22px] font-black text-[#202533]">异常预警</h1>
      <button type="button" class="grid h-10 w-10 place-items-center text-[#222734]" @click="showCatSheet = true">
        <van-icon name="exchange" size="20" />
      </button>
    </header>

    <section class="mt-5 rounded-[24px] bg-gradient-to-br from-[#d94a12] to-[#ef642e] p-5 text-white">
      <div class="flex items-start justify-between gap-3">
        <div>
          <h2 class="text-[34px] font-black leading-[1.06]">异常预警</h2>
          <p class="mt-1 text-[13px] text-white/90">预警发布：今日 {{ currentTime }}</p>
        </div>
        <div class="grid h-14 w-14 place-items-center rounded-2xl bg-white/20">
          <van-icon name="warning-o" size="26" color="#fff" />
        </div>
      </div>
      <div class="mt-4 rounded-xl bg-white/12 px-4 py-3 text-[17px] font-bold">🐾 {{ selectedCatLabel }}</div>
    </section>

    <section class="mt-7">
      <div class="mb-3 flex items-center gap-2">
        <span class="h-6 w-1 rounded-full bg-[#bc2f00]" />
        <h3 class="text-[24px] font-black text-[#1d2333]">异常说明</h3>
      </div>

      <article class="rounded-[20px] bg-[#eceffa] p-4">
        <div class="flex gap-3">
          <div class="grid h-14 w-14 place-items-center rounded-2xl bg-[#f8d9cd] text-[#b93a10]">
            <van-icon name="records" size="24" />
          </div>
          <div class="min-w-0">
            <div class="text-[20px] font-black text-[#141a2c]">{{ explanationTitle }}</div>
            <p class="mt-1 text-[14px] leading-relaxed text-[#4f5770]">{{ explanationText }}</p>
          </div>
        </div>
      </article>
    </section>

    <section class="mt-7">
      <div class="mb-3 flex items-center gap-2">
        <span class="h-6 w-1 rounded-full bg-[#bc2f00]" />
        <h3 class="text-[24px] font-black text-[#1d2333]">建议处理方式</h3>
      </div>

      <div class="space-y-3">
        <button type="button" class="flex w-full items-center justify-between rounded-[18px] bg-white px-4 py-4 text-left">
          <div class="flex items-center gap-3">
            <div class="grid h-12 w-12 place-items-center rounded-full bg-[#dde3f2] text-[#5f6a82]"><van-icon name="checked" size="22" /></div>
            <span class="text-[20px] font-black text-[#1b2133]">检查猫砂盆/排泄物</span>
          </div>
          <van-icon name="arrow" color="#b2b8c8" size="20" />
        </button>

        <button type="button" class="flex w-full items-center justify-between rounded-[18px] border-l-4 border-[#b92f00] bg-[#fff2ef] px-4 py-4 text-left" @click="router.push({ name: 'ProfessionalDoctors' })">
          <div class="flex items-center gap-3">
            <div class="grid h-12 w-12 place-items-center rounded-full bg-[#c5400e] text-white"><van-icon name="plus" size="22" /></div>
            <div>
              <div class="text-[20px] font-black text-[#b22f00]">立即咨询兽医</div>
              <div class="text-[14px] font-bold uppercase tracking-wide text-[#8f5f50]">高优先级行动</div>
            </div>
          </div>
          <van-icon name="phone-o" color="#b22f00" size="20" />
        </button>

        <button type="button" class="flex w-full items-center justify-between rounded-[18px] bg-white px-4 py-4 text-left">
          <div class="flex items-center gap-3">
            <div class="grid h-12 w-12 place-items-center rounded-full bg-[#dde3f2] text-[#5f6a82]"><van-icon name="smile-comment-o" size="22" /></div>
            <span class="text-[20px] font-black text-[#1b2133]">监测进食量</span>
          </div>
          <van-icon name="arrow" color="#b2b8c8" size="20" />
        </button>
      </div>
    </section>

    <section class="mt-7">
      <div class="mb-3 flex items-center justify-between gap-3">
        <div class="flex items-center gap-2">
          <span class="h-6 w-1 rounded-full bg-[#b8bcc8]" />
          <h3 class="text-[24px] font-black text-[#1d2333]">音频记录</h3>
        </div>
        <button type="button" class="rounded-full bg-[#fff2e8] px-4 py-2 text-[14px] font-black text-[#bc2f00]" @click="refresh">查看全部</button>
      </div>

      <div v-if="historyItems.length === 0" class="rounded-[18px] border border-[#e8eaf3] bg-white p-6 text-center text-[14px] text-[#6f7790]">
        暂无音频记录，去喵喵台录一段音频试试吧。
      </div>

      <div v-else class="space-y-3">
        <article
          v-for="item in historyItems"
          :key="item.id"
          class="rounded-[18px] bg-white px-4 py-4 shadow-[0_2px_10px_rgba(15,23,42,0.04)]"
        >
          <div class="flex items-center gap-4">
            <button
              type="button"
              class="grid h-16 w-16 place-items-center rounded-full bg-[#ff6b35] text-white shadow-[0_10px_20px_rgba(255,107,53,0.22)]"
              :disabled="!item.audioUrl"
              @click="toggleAudio(item.id)"
            >
              <van-icon :name="playingId === item.id ? 'pause' : 'play'" size="24" />
            </button>

            <div class="min-w-0 flex-1">
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <span class="inline-flex rounded-full px-3 py-1 text-[13px] font-black" :class="emotionBadgeClass(item.emotionTag)">
                    {{ item.emotionTag || '未识别情绪' }}
                  </span>
                  <div class="mt-2 text-[18px] font-black text-[#1f2432]">{{ shortEmotionDescription(item.emotionDescription) }}</div>
                </div>
                <div class="text-right text-[13px] text-[#655850]">
                  <div>{{ formatClock(item.createdAt) }}</div>
                  <div class="mt-1">{{ formatDuration(item.audioUrl) }}</div>
                </div>
              </div>

              <div class="mt-3 flex items-center gap-3">
                <div class="h-1.5 flex-1 rounded-full bg-[#e5e7ef]">
                  <div class="h-full rounded-full bg-[#ef642e]" :style="{ width: `${Math.max(20, item.confidence * 100)}%` }"></div>
                </div>
                <span class="text-[13px] font-bold text-[#ef642e]">{{ (item.confidence * 100).toFixed(1) }}%</span>
              </div>

              <div class="mt-2 text-[13px] leading-relaxed text-[#6a7082]">
                {{ item.audioUrl ? '点击左侧按钮即可播放这段音频。' : '这段记录暂时没有可播放音频，但情绪结果已保存。' }}
              </div>

              <audio
                v-if="item.audioUrl"
                :ref="(el) => setAudioRef(item.id, el as HTMLAudioElement | null)"
                :src="item.audioUrl"
                class="hidden"
                preload="none"
                @ended="onAudioEnded(item.id)"
              ></audio>
            </div>
          </div>
        </article>
      </div>
    </section>

    <section class="mt-8 rounded-[22px] bg-[#dff1ff] p-5 text-[#0e2b45]">
      <p class="text-[15px] font-semibold leading-relaxed">“宠物突然出现的精神萎靡可能是从轻微感染到严重心脏问题的任何征兆。监测饮水量是您的第一道防线。”</p>
      <div class="mt-4 flex items-start gap-3">
        <van-image src="https://images.unsplash.com/photo-1594824388853-f3f1d0f3f4c1?w=80&h=80&fit=crop" width="30" height="30" round />
        <div>
          <p class="text-[14px] leading-relaxed">“宠物突然出现的精神萎靡可能是从轻微感染到严重心脏问题的任何征兆。监测饮水量是您的第一道防线。”</p>
          <p class="mt-1 text-[13px] text-[#1e557f]">AI 兽医主管</p>
        </div>
      </div>
    </section>

    <van-action-sheet v-model:show="showCatSheet" title="切换猫咪">
      <div class="p-4">
        <div class="mb-3 text-xs text-[#7f889d]">切换后将展示对应猫咪的异常预警</div>
        <div class="space-y-2">
          <button
            v-for="cat in cats"
            :key="cat.id"
            type="button"
            class="flex w-full items-center justify-between rounded-xl px-3 py-3"
            :class="cat.id === selectedCatId ? 'bg-orange-50 text-orange-600' : 'bg-[#f5f7ff] text-[#1f2937]'"
            @click="switchCat(cat.id)"
          >
            <span class="text-sm font-semibold">{{ cat.name }} · {{ cat.breed || '未填写品种' }}</span>
            <van-icon v-if="cat.id === selectedCatId" name="success" />
            <van-icon v-else name="arrow" color="#8c95a8" />
          </button>
        </div>
      </div>
    </van-action-sheet>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useEmotionAnalysis } from '@/composables/useEmotionAnalysis';
import { useCatsStore, useCurrentCatStore } from '@/stores';

const router = useRouter();
const catsStore = useCatsStore();
const currentCatStore = useCurrentCatStore();
const { fetchEmotionRecords, getCurrentRecords } = useEmotionAnalysis();

const currentTime = ref('08:42');
const showCatSheet = ref(false);
const cats = computed(() => catsStore.getAllCats);

const selectedCatId = computed(() => currentCatStore.getCurrentCatId || catsStore.getAllCats[0]?.id || '');
const selectedCatLabel = computed(() => {
  const cat = selectedCatId.value ? catsStore.getCatById(selectedCatId.value) : null;
  if (!cat) return '未选择猫咪';
  const ageText = cat.age ? `${Math.max(1, Math.round(cat.age / 12))}岁` : '未知年龄';
  return `${cat.name} · ${ageText}`;
});

const records = computed(() => getCurrentRecords.value);
const latestRecord = computed(() => records.value[0] || null);
const historyItems = computed(() => records.value.slice(0, 4));

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

const explanationTitle = computed(() => {
  if (!latestRecord.value) return '检测到低活跃状态';
  return latestRecord.value.emotionTag || '检测到低活跃状态';
});

const explanationText = computed(() => {
  if (!latestRecord.value) {
    return '过去24小时内活动量下降，建议重点观察饮水、排泄和食欲变化。';
  }
  return latestRecord.value.emotionDescription || '过去24小时内活动量下降，建议重点观察饮水、排泄和食欲变化。';
});

const refresh = async () => {
  if (!selectedCatId.value) return;
  await fetchEmotionRecords({ page: 1, pageSize: 10, catId: selectedCatId.value });
};

const switchCat = async (catId: string) => {
  currentCatStore.setCurrentCat(catId);
  showCatSheet.value = false;
  await refresh();
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
  window.scrollTo({ top: 0, behavior: 'auto' });
  await catsStore.fetchAllCats();
  if (!currentCatStore.getCurrentCatId && catsStore.getAllCats[0]?.id) {
    currentCatStore.setCurrentCat(catsStore.getAllCats[0].id);
  }
  await refresh();

  const now = new Date();
  currentTime.value = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
});

watch(
  () => selectedCatId.value,
  async (newId, oldId) => {
    if (!newId || newId === oldId) return;
    await refresh();
  }
);
</script>
