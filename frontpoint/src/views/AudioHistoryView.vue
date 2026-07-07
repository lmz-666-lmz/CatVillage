<template>
  <div class="audio-page">
    <!-- Header -->
    <header class="audio-header">
      <button type="button" class="audio-back" @click="$router.back()">
        <van-icon name="arrow-left" size="20" />
      </button>
      <div>
        <h1 class="audio-title">音频历史</h1>
        <p class="audio-sub">{{ selectedCatName }}的情绪音频档案</p>
      </div>
      <button type="button" class="audio-refresh" @click="refresh">
        <van-icon name="replay" size="18" />
      </button>
    </header>

    <!-- Hero Card -->
    <section class="hero-card">
      <div class="hero-bg">
        <van-image :src="heroImage" width="100%" height="100%" fit="cover" />
        <div class="hero-overlay"></div>
      </div>
      <div class="hero-content">
        <span class="hero-badge">今日记录</span>
        <h2 class="hero-text">{{ selectedCatName }}的日常心声</h2>
        <p class="hero-desc">记录每一段音频，识别情绪并追踪变化趋势</p>
      </div>
    </section>

    <!-- Loading / Empty -->
    <div v-if="historyLoading" class="audio-loading">
      <van-loading size="24" color="#ff6b35" />
      <div class="audio-loading-text">正在加载音频记录...</div>
    </div>

    <div v-else-if="records.length === 0" class="audio-empty">
      <span class="audio-empty-icon">🎙️</span>
      <div class="audio-empty-title">暂无音频记录</div>
      <div class="audio-empty-text">去喵喵台录一段音频试试吧</div>
    </div>

    <!-- Records List -->
    <section v-else class="records-section">
      <div v-for="group in groupedRecords" :key="group.dateKey" class="record-group">
        <div class="group-title">{{ group.title }}</div>

        <div class="record-list">
          <article
            v-for="record in group.items"
            :key="record.id"
            class="record-card"
          >
            <div class="record-row">
              <button
                type="button"
                class="play-btn"
                :class="{ playing: playingId === record.id }"
                @click="toggleAudio(record.id)"
              >
                <van-icon :name="playingId === record.id ? 'pause' : 'play'" size="22" />
              </button>

              <div class="record-info">
                <div class="record-top">
                  <span class="emotion-badge" :class="emotionBadgeClass(record.emotionTag)">
                    {{ record.emotionTag || '未识别情绪' }}
                  </span>
                  <div class="record-actions">
                    <span class="record-time">{{ formatClock(record.createdAt) }}</span>
                    <button type="button" class="delete-record-btn" @click="deleteRecord(record.id)">
                      <van-icon name="delete-o" size="15" />
                    </button>
                  </div>
                </div>
                <div class="record-desc">{{ shortEmotionDescription(record.emotionDescription) }}</div>

                <div class="confidence-bar-wrap">
                  <div class="confidence-bar">
                    <div class="confidence-fill" :style="{ width: `${Math.max(20, record.confidence * 100)}%` }"></div>
                  </div>
                  <span class="confidence-text">{{ (record.confidence * 100).toFixed(1) }}%</span>
                </div>

                <div class="record-hint">{{ record.audioUrl ? '点击左侧按钮即可播放这段音频' : '这段记录暂时没有可播放音频，但情绪结果已保存' }}</div>

                <audio
                  v-if="record.audioUrl"
                  :ref="(el) => setAudioRef(record.id, el as HTMLAudioElement | null)"
                  :src="audioObjectUrls.get(record.id) || ''"
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
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { showConfirmDialog, showToast } from 'vant';
import { useEmotionAnalysis } from '@/composables/useEmotionAnalysis';
import { useCatsStore, useCurrentCatStore } from '@/stores';
import { createAuthorizedAudioObjectUrl } from '@/api/emotion';

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

const { fetchEmotionRecords, getCurrentRecords, isLoading: historyLoading, removeEmotionRecord } = useEmotionAnalysis();
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
    if (!groups.has(dateKey)) groups.set(dateKey, { dateKey, title, items: [] });
    groups.get(dateKey)!.items.push(record);
  });
  return Array.from(groups.values());
});

const playingId = ref('');
const audioObjectUrls = ref(new Map<string, string>());
const audioRefs = new Map<string, HTMLAudioElement>();

const setAudioRef = (id: string, el: HTMLAudioElement | null) => {
  if (el) audioRefs.set(id, el);
  else audioRefs.delete(id);
};

const toggleAudio = async (id: string) => {
  const audio = audioRefs.get(id);
  if (!audio) return;
  const record = records.value.find((item) => item.id === id);
  if (record?.audioUrl && !audioObjectUrls.value.has(id)) {
    const objectUrl = await createAuthorizedAudioObjectUrl(record.audioUrl);
    audioObjectUrls.value.set(id, objectUrl);
    audio.src = objectUrl;
  }
  if (playingId.value === id && !audio.paused) { audio.pause(); playingId.value = ''; return; }
  audioRefs.forEach((otherAudio, otherId) => { if (otherId !== id) otherAudio.pause(); });
  try { await audio.play(); playingId.value = id; } catch { playingId.value = ''; }
};

const onAudioEnded = (id: string) => { if (playingId.value === id) playingId.value = ''; };

const refresh = async () => {
  await catsStore.fetchAllCats();
  if (!selectedCatId.value && catsStore.getAllCats[0]?.id) currentCatStore.setCurrentCat(catsStore.getAllCats[0].id);
  if (selectedCatId.value) await fetchEmotionRecords({ page: 1, pageSize: 50, catId: selectedCatId.value });
};

const deleteRecord = async (recordId: string) => {
  try {
    await showConfirmDialog({
      title: '删除音频记录',
      message: '确认删除这条情绪/叫声记录吗？'
    });
  } catch {
    return;
  }
  try {
    await removeEmotionRecord(recordId);
    await refresh();
    showToast({ type: 'success', message: '记录已删除' });
  } catch {
    showToast({ type: 'fail', message: '删除失败，请稍后重试' });
  }
};

const formatGroupTitle = (date: Date) => {
  if (Number.isNaN(date.getTime())) return '未知日期';
  const today = new Date();
  if (date.toDateString() === today.toDateString()) return '今天';
  const yesterday = new Date(); yesterday.setDate(today.getDate() - 1);
  if (date.toDateString() === yesterday.toDateString()) return '昨天';
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`;
};

const formatClock = (value: string) => {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '';
  const hh = String(date.getHours()).padStart(2, '0');
  const mm = String(date.getMinutes()).padStart(2, '0');
  return `${hh}:${mm}`;
};

const shortEmotionDescription = (value: string) => {
  if (!value) return '系统已记录该段音频的情绪';
  return value.length > 28 ? `${value.slice(0, 28)}...` : value;
};

const emotionBadgeClass = (emotionTag: string) => {
  if (/警|焦虑|异常|悲|愤怒/i.test(emotionTag)) return 'badge-alert';
  if (/开心|平静|轻松|愉快|满足/i.test(emotionTag)) return 'badge-happy';
  return 'badge-neutral';
};

onMounted(async () => { await refresh(); });
</script>

<style scoped>
.audio-page { min-height: 100dvh; padding: 0 16px 32px; background: #fff7f0; }

/* Header */
.audio-header { display: flex; align-items: flex-start; gap: 12px; padding: 14px 0 10px; }
.audio-back { width: 38px; height: 38px; flex-shrink: 0; border: none; border-radius: 14px; background: #fff; display: grid; place-items: center; color: #ff6b35; cursor: pointer; box-shadow: 0 2px 8px rgba(16,32,51,0.06); }
.audio-back:active { transform: scale(.93); }
.audio-title { margin: 0; font-size: 22px; font-weight: 900; color: #102033; }
.audio-sub { margin: 2px 0 0; font-size: 12px; font-weight: 600; color: #7a8494; }
.audio-refresh { width: 38px; height: 38px; flex-shrink: 0; border: none; border-radius: 14px; background: #fff; display: grid; place-items: center; color: #7a8494; cursor: pointer; box-shadow: 0 2px 8px rgba(16,32,51,0.06); margin-left: auto; }
.audio-refresh:active { transform: scale(.93); }

/* Hero Card */
.hero-card { margin-top: 10px; position: relative; border-radius: 22px; overflow: hidden; min-height: 190px; }
.hero-bg { position: absolute; inset: 0; }
.hero-overlay { position: absolute; inset: 0; background: linear-gradient(135deg, rgba(0,0,0,0.65) 0%, rgba(0,0,0,0.25) 55%, rgba(0,0,0,0.08) 100%); }
.hero-content { position: relative; padding: 22px 20px; color: #fff; }
.hero-badge { display: inline-block; border-radius: 999px; background: #ff6b35; padding: 5px 14px; font-size: 13px; font-weight: 700; box-shadow: 0 4px 12px rgba(255,107,53,0.3); }
.hero-text { margin: 14px 0 0; font-size: 24px; font-weight: 900; line-height: 1.15; max-width: 80%; }
.hero-desc { margin: 8px 0 0; font-size: 13px; opacity: 0.8; }

/* Loading & Empty */
.audio-loading { padding: 48px 0; text-align: center; }
.audio-loading-text { margin-top: 10px; font-size: 14px; color: #7a8494; }
.audio-empty { padding: 48px 20px; text-align: center; }
.audio-empty-icon { font-size: 48px; display: block; margin-bottom: 10px; }
.audio-empty-title { font-size: 17px; font-weight: 800; color: #102033; margin-bottom: 4px; }
.audio-empty-text { font-size: 14px; color: #7a8494; }

/* Records */
.records-section { margin-top: 16px; }
.record-group { margin-bottom: 20px; }
.group-title { font-size: 13px; font-weight: 800; color: #7a8494; letter-spacing: 0.06em; margin-bottom: 10px; padding-left: 2px; }
.record-list { display: flex; flex-direction: column; gap: 10px; }

/* Record Card */
.record-card { border-radius: 22px; background: #fff; padding: 16px; box-shadow: 0 2px 12px rgba(16,32,51,0.04); }
.record-row { display: flex; gap: 14px; }

/* Play Button */
.play-btn { width: 56px; height: 56px; flex-shrink: 0; border: none; border-radius: 50%; background: #ff6b35; color: #fff; display: grid; place-items: center; cursor: pointer; box-shadow: 0 6px 18px rgba(255,107,53,0.24); transition: transform .14s; }
.play-btn:active { transform: scale(.92); }
.play-btn.playing { background: #102033; }

/* Record Info */
.record-info { min-width: 0; flex: 1; }
.record-top { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 6px; }
.record-time { font-size: 12px; font-weight: 600; color: #7a8494; }
.record-actions { display: inline-flex; flex-shrink: 0; align-items: center; gap: 7px; }
.delete-record-btn { display: grid; width: 28px; height: 28px; place-items: center; border: 0; border-radius: 999px; background: #fff1f2; color: #e11d48; }
.record-desc { font-size: 15px; font-weight: 700; color: #102033; line-height: 1.4; margin-bottom: 10px; }

/* Emotion Badge */
.emotion-badge { display: inline-block; border-radius: 999px; padding: 3px 10px; font-size: 12px; font-weight: 700; }
.badge-alert { background: #ffe8e4; color: #c13b1f; }
.badge-happy { background: #ecfdf5; color: #0f8a44; }
.badge-neutral { background: #fdfaf6; color: #7a8494; }

/* Confidence Bar */
.confidence-bar-wrap { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.confidence-bar { flex: 1; height: 5px; border-radius: 3px; background: #ede8e0; overflow: hidden; }
.confidence-fill { height: 100%; border-radius: 3px; background: linear-gradient(90deg, #ff8a4c, #ff6b35); transition: width .3s ease; }
.confidence-text { font-size: 12px; font-weight: 700; color: #ff6b35; white-space: nowrap; }

.record-hint { font-size: 12px; color: #7a8494; }
</style>
