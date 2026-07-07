<template>
  <div class="meow-page">
    <AppTopBar title="喵喵台" subtitle="上传叫声，识别猫咪情绪" kicker="Meow Studio">
      <template #actions>
        <button class="topbar-action" type="button" aria-label="选择猫咪" @click="showCatSheet = true">
          <van-icon name="apps-o" size="20" />
        </button>
      </template>
    </AppTopBar>

    <main class="meow-content">
      <section v-if="hasCats" class="cat-status-card" @click="showCatSheet = true">
        <div class="cat-avatar">
          <img :src="selectedCatAvatar" alt="" @error="handleImageError" />
          <i />
        </div>
        <div class="cat-copy">
          <strong>{{ selectedCatName }}</strong>
          <span>{{ selectedCatBreed }} · {{ selectedCatAge || '年龄未知' }} · 监测中</span>
        </div>
        <van-icon name="arrow" color="#98a3b4" />
      </section>

      <section v-else class="empty-panel">
        <div class="empty-illustration">
          <span class="empty-emoji">🐱</span>
          <div class="empty-paws"><span>🐾</span><span>🐾</span><span>🐾</span></div>
        </div>
        <strong>还没有猫咪伙伴</strong>
        <span>添加猫咪后，就能识别猫叫情绪并记录历史</span>
        <button type="button" @click="router.push({ name: 'AddCat' })">
          <van-icon name="plus" size="17" />
          添加猫咪
        </button>
      </section>

      <section class="listen-panel">
        <input ref="audioInputRef" type="file" accept="audio/*" class="hidden" @change="onAudioSelected" />
        <div class="listen-header">
          <span class="listen-badge">喵语识别</span>
          <strong>录音与上传双通道识别</strong>
          <p>{{ recordingHint }}</p>
        </div>

        <div class="recognition-grid">
          <div class="recognition-card record-card" :class="{ unavailable: !recordingSupport.canRecord }">
            <div class="recognition-card-head">
              <div>
                <span>录音识别</span>
                <strong>{{ recordingStatus }}</strong>
              </div>
              <van-icon name="volume-o" size="22" />
            </div>
            <div v-if="!recordingSupport.canRecord" class="capability-warning">{{ recordingSupport.message }}</div>
            <div class="record-disc-wrap">
              <div class="record-disc-stage" :class="{ recording: isRecording, analyzing: analyzing }">
                <div class="disc-aura aura-1" />
                <div class="disc-aura aura-2" />
                <div class="disc-aura aura-3" />
                <div class="disc-glow" />
                <button
                  v-if="recordingSupport.canRecord"
                  class="record-disc-btn"
                  :class="{ recording: isRecording, analyzing, disabled: !hasCats || analyzing }"
                  :disabled="!hasCats || analyzing"
                  @pointerdown.prevent="startRecording"
                  @pointerup.prevent="stopRecording"
                  @pointercancel.prevent="stopRecording"
                  @pointerleave.prevent="stopRecording"
                >
                  <div class="disc-inner-face">
                    <span class="disc-emoji">{{ discEmoji }}</span>
                    <van-icon v-if="!isRecording && !analyzing" name="volume-o" size="28" class="disc-icon" />
                    <van-icon v-else-if="analyzing" name="clock-o" size="28" class="disc-icon spinning" />
                    <span class="disc-label">{{ discLabel }}</span>
                  </div>
                </button>
                <button v-else class="record-disc-btn disabled" type="button" @click="showRecordingUnavailable">
                  <div class="disc-inner-face">
                    <span class="disc-emoji">!</span>
                    <van-icon name="warning-o" size="28" class="disc-icon" />
                    <span class="disc-label">录音不可用</span>
                  </div>
                </button>
              </div>
              <div class="disc-footer-hint">
                {{ recordingSupport.canRecord ? '按住录音 · 松手识别' : '当前环境请使用上传识别' }}
              </div>
            </div>
          </div>

          <div class="recognition-card upload-card">
            <div class="recognition-card-head">
              <div>
                <span>上传音频识别</span>
                <strong>{{ uploadStatus }}</strong>
              </div>
              <van-icon name="upgrade" size="22" />
            </div>
            <p>支持手机录音文件、聊天里的猫叫音频或本地音频文件。</p>
            <button type="button" class="upload-audio-btn" :disabled="analyzing" @click="openAudioPicker">
              <van-icon name="music-o" size="18" />
              {{ analyzing ? '上传识别中...' : '上传猫叫音频' }}
            </button>
          </div>
        </div>
      </section>

      <section class="emotion-panel">
        <div class="section-head">
          <div>
            <span>当前情绪</span>
            <h2>{{ latestRecord?.emotionTag || '暂无记录' }}</h2>
          </div>
          <b v-if="latestRecord">{{ ((latestRecord.confidence || 0) * 100).toFixed(0) }}%</b>
        </div>

        <template v-if="latestRecord">
          <div class="emotion-insight">
            <div class="emotion-symbol" :class="emotionColor(latestRecord.emotionTag)">
              {{ emotionIcon(latestRecord.emotionTag) }}
            </div>
            <p>{{ latestRecord.emotionDescription || '猫咪状态良好，正在享受当下的时光。' }}</p>
          </div>
          <div class="emotion-meter">
            <span>平稳</span>
            <div><i :style="{ width: emotionPercent(latestRecord) + '%' }" /></div>
            <span>强烈</span>
          </div>
        </template>

        <div v-else class="emotion-placeholder">
          <van-icon name="music-o" size="30" />
          <span>完成一次识别后，这里会展示最新情绪</span>
        </div>
      </section>

      <section class="doctor-card" @click="router.push({ name: 'ProfessionalDoctors' })">
        <div>
          <van-icon name="service-o" size="22" />
        </div>
        <div>
          <strong>专业医生咨询</strong>
          <span>模拟养护建议，仅供参考</span>
        </div>
        <van-icon name="arrow" color="#98a3b4" />
      </section>

      <section class="records-section">
        <div class="section-head compact">
          <div>
            <span>最近记录</span>
            <h2>音频历史</h2>
          </div>
          <button v-if="historyItems.length" type="button" @click="router.push({ name: 'AudioHistory' })">
            全部 <van-icon name="arrow" size="12" />
          </button>
        </div>

        <div v-if="historyItems.length === 0" class="records-empty">
          <van-icon name="music-o" size="32" />
          <strong>暂无音频记录</strong>
          <span>完成一次识别后会显示在这里</span>
        </div>

        <div v-else class="records-list">
          <article v-for="item in historyItems" :key="item.id" class="record-item">
            <button class="record-play-btn" :class="{ playing: playingId === item.id }" :disabled="!item.audioUrl" @click="toggleAudio(item.id)">
              <van-icon :name="playingId === item.id ? 'pause' : 'play'" size="16" />
            </button>
            <audio :ref="(el) => setAudioRef(item.id, el as HTMLAudioElement | null)" :src="audioObjectUrls.get(item.id) || ''" class="hidden" @ended="onAudioEnded(item.id)" />
            <div class="record-body">
              <div class="record-top-row">
                <span class="record-tag" :class="emotionColor(item.emotionTag)">{{ item.emotionTag || '未知' }}</span>
                <div class="record-inline-actions">
                  <time>{{ formatClock(item.createdAt) }}</time>
                  <button type="button" class="record-delete-mini" @click="deleteRecord(item.id)">
                    <van-icon name="delete-o" size="13" />
                  </button>
                </div>
              </div>
              <div class="record-bar"><i :style="{ width: ((item.confidence || 0) * 100).toFixed(0) + '%' }" /></div>
              <small>置信度 {{ ((item.confidence || 0) * 100).toFixed(0) }}%</small>
            </div>
          </article>
        </div>
      </section>
    </main>

    <!-- ====== Cat Switcher Sheet ====== -->
    <van-action-sheet v-model:show="showCatSheet" title="选择猫咪" :round="true">
      <div class="sheet-wrap">
        <div v-if="cats.length === 0" class="sheet-empty-state">
          <span>🐱</span>
          <p>还没有猫咪，先去添加吧</p>
        </div>
        <div v-else class="sheet-cat-list">
          <button
            v-for="cat in cats"
            :key="cat.id"
            class="sheet-cat-item"
            :class="{ active: cat.id === selectedCatId }"
            @click="switchCat(cat.id)"
          >
            <div class="sheet-cat-avatar">
              <img :src="getSafeImageUrl(cat.avatarUrl, defaultAvatar)" alt="" @error="handleImageError" />
            </div>
            <div class="sheet-cat-info">
              <span class="sheet-cat-name">{{ cat.name }}</span>
              <span class="sheet-cat-meta">{{ cat.breed || '猫咪' }} · {{ catAgeText(cat) }}</span>
            </div>
            <van-icon v-if="cat.id === selectedCatId" name="success" size="20" />
            <div v-else class="sheet-cat-radio" />
          </button>
        </div>
        <div class="sheet-footer">
          <button class="sheet-footer-btn outline" @click="showCatSheet = false; router.push({ name: 'AddCat' })">
            <van-icon name="plus" size="16" /> 添加猫咪
          </button>
          <button v-if="selectedCatId" class="sheet-footer-btn primary" @click="showCatSheet = false; router.push({ name: 'EditCat', params: { id: selectedCatId } })">
            <van-icon name="edit" size="16" /> 编辑当前
          </button>
        </div>
      </div>
    </van-action-sheet>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { closeToast, showConfirmDialog, showToast } from 'vant';
import AppTopBar from '@/components/AppTopBar.vue';
import { useEmotionAnalysis } from '@/composables/useEmotionAnalysis';
import { useCatsStore, useCurrentCatStore } from '@/stores';
import { createAuthorizedAudioObjectUrl } from '@/api/emotion';
import type { CatProfile } from '@/types';
import { DEFAULT_CAT_AVATAR, getSafeImageUrl, handleImageError as replaceBrokenImage } from '@/utils/image';
import { detectAudioRecordingSupport, type AudioRecordingSupport } from '@/utils/media';
import { formatCatAge } from '@/utils/age';

const router = useRouter();
const catsStore = useCatsStore();
const currentCatStore = useCurrentCatStore();
const { analyzeEmotion, fetchEmotionRecords, getCurrentRecords, removeEmotionRecord } = useEmotionAnalysis();

const showCatSheet = ref(false);
const audioInputRef = ref<HTMLInputElement | null>(null);
const analyzing = ref(false);
const isRecording = ref(false);
const recordDuration = ref(0);
let recordTimer: ReturnType<typeof setInterval> | null = null;
const recorder = ref<MediaRecorder | null>(null);
const recordingChunks = ref<Blob[]>([]);
const recordingStream = ref<MediaStream | null>(null);
const defaultAvatar = DEFAULT_CAT_AVATAR;
const recordingSupport = ref<AudioRecordingSupport>(detectAudioRecordingSupport());
const cats = computed(() => catsStore.getAllCats);
const hasCats = computed(() => cats.value.length > 0);
const recordingStatus = computed(() => {
  if (analyzing.value) return '正在解读喵星语...';
  if (isRecording.value) return `小耳朵竖起中 ${recordDuration.value}s`;
  return '准备好听猫咪说说话';
});
const recordingHint = computed(() => {
  if (!hasCats.value) return '先添加一只小猫咪，才能开始倾听喔 🐱';
  if (analyzing.value) return 'AI 正在努力理解主子的心思，请稍等一下～';
  if (isRecording.value) return '主子的每一声喵都在被认真记录中...';
  if (!recordingSupport.value.canRecord) return recordingSupport.value.message;
  return '把猫咪的叫声录下来，我来帮你翻译它在说什么 ✨';
});
const uploadStatus = computed(() => {
  if (!hasCats.value) return '请先添加猫咪';
  if (analyzing.value) return '正在识别';
  return '随时可用';
});
const discEmoji = computed(() => {
  if (analyzing.value) return '🤔';
  if (isRecording.value) return '🎤';
  return '🐱';
});
const discLabel = computed(() => {
  if (analyzing.value) return '破译中';
  if (isRecording.value) return '松手听听';
  return '按住喵一声';
});

const selectedCatId = computed(() => currentCatStore.getCurrentCatId || catsStore.getAllCats[0]?.id || '');
const selectedCat = computed(() => selectedCatId.value ? catsStore.getCatById(selectedCatId.value) : null);
const selectedCatName = computed(() => selectedCat.value?.name || '未选择');
const selectedCatAvatar = computed(() => getSafeImageUrl(selectedCat.value?.avatarUrl, defaultAvatar));
const selectedCatBreed = computed(() => selectedCat.value?.breed || '猫咪');
const selectedCatAge = computed(() => formatCatAge(selectedCat.value?.age));
const catAgeText = (cat: CatProfile) => formatCatAge(cat.age);

const records = computed(() => getCurrentRecords.value);
const latestRecord = computed(() => records.value[0] || null);
const historyItems = computed(() => records.value.slice(0, 4));

const playingId = ref('');
const audioObjectUrls = ref(new Map<string, string>());
const audioRefs = new Map<string, HTMLAudioElement>();

const setAudioRef = (id: string, el: HTMLAudioElement | null) => { if (el) audioRefs.set(id, el); else audioRefs.delete(id); };
const toggleAudio = async (id: string) => {
  const a = audioRefs.get(id); if (!a) return;
  const r = records.value.find(x => x.id === id);
  if (r?.audioUrl && !audioObjectUrls.value.has(id)) { const u = await createAuthorizedAudioObjectUrl(r.audioUrl); audioObjectUrls.value.set(id, u); a.src = u; }
  if (playingId.value === id && !a.paused) { a.pause(); playingId.value = ''; return; }
  audioRefs.forEach((x, oid) => { if (oid !== id) x.pause(); });
  try { await a.play(); playingId.value = id; } catch { playingId.value = ''; }
};
const onAudioEnded = (id: string) => { if (playingId.value === id) playingId.value = ''; };

const refresh = async () => {
  if (!selectedCatId.value) return;
  try { await fetchEmotionRecords({ page: 1, pageSize: 10, catId: selectedCatId.value }); }
  catch (e: unknown) { if ((e as any)?.status !== 404) showToast({ type: 'fail', message: '数据加载失败，请稍后重试' }); }
};
const switchCat = async (id: string) => { currentCatStore.setCurrentCat(id); showCatSheet.value = false; await refresh(); };

const deleteRecord = async (recordId: string) => {
  try {
    await showConfirmDialog({ title: '删除记录', message: '确认删除这条情绪/叫声记录吗？' });
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

const cleanupRecorder = () => {
  if (recordTimer) { clearInterval(recordTimer); recordTimer = null; }
  recorder.value?.stream.getTracks().forEach((t) => t.stop());
  recordingStream.value?.getTracks().forEach((t) => t.stop());
  recorder.value = null;
  recordingStream.value = null;
  recordingChunks.value = [];
  isRecording.value = false;
  recordDuration.value = 0;
};

const analyzeAudioBlob = async (blob: Blob, fileName: string) => {
  const catId = selectedCatId.value;
  if (!hasCats.value || !catId) { showToast({ type: 'fail', message: '请先添加猫咪' }); return; }
  analyzing.value = true;
  showToast({ type: 'loading', message: '正在识别猫语...', duration: 0, forbidClick: true });
  try {
    const file = new File([blob], fileName, { type: blob.type || 'audio/webm' });
    await analyzeEmotion({ catId, audioFile: file });
    closeToast();
    showToast({ type: 'success', message: '识别完成' });
    await refresh();
  } catch {
    closeToast();
    showToast({ type: 'fail', message: '识别失败，请稍后重试' });
  } finally { analyzing.value = false; }
};

const startRecording = async () => {
  if (isRecording.value || analyzing.value) return;
  if (!hasCats.value || !selectedCatId.value) { showToast({ type: 'fail', message: '请先添加猫咪' }); return; }
  recordingSupport.value = detectAudioRecordingSupport();
  if (!recordingSupport.value.canRecord) {
    showToast({ type: 'fail', message: recordingSupport.value.message });
    return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    recordingStream.value = stream;
    recordingChunks.value = [];
    const options = recordingSupport.value.supportedMimeType ? { mimeType: recordingSupport.value.supportedMimeType } : undefined;
    const mediaRecorder = new MediaRecorder(stream, options);
    recorder.value = mediaRecorder;

    mediaRecorder.ondataavailable = (e) => { if (e.data.size > 0) recordingChunks.value.push(e.data); };
    mediaRecorder.onstop = async () => {
      const blob = new Blob(recordingChunks.value, { type: mediaRecorder.mimeType || 'audio/webm' });
      cleanupRecorder();
      if (blob.size > 0) {
        await analyzeAudioBlob(blob, `meow-${Date.now()}.webm`);
      }
    };

    mediaRecorder.start();
    isRecording.value = true;
    recordDuration.value = 0;
    recordTimer = setInterval(() => { recordDuration.value += 1; }, 1000);
  } catch (error: unknown) {
    const name = (error as DOMException)?.name || '';
    showToast({
      type: 'fail',
      message: /NotAllowedError|PermissionDeniedError/i.test(name)
        ? '请在浏览器设置中允许麦克风权限，或上传音频文件。'
        : '当前浏览器不支持直接录音，可上传音频文件识别。'
    });
    cleanupRecorder();
  }
};

const stopRecording = async () => {
  if (isRecording.value && recorder.value) {
    recorder.value.stop();
  }
};

const showRecordingUnavailable = () => {
  showToast({ type: 'fail', message: recordingSupport.value.message || '当前浏览器不支持直接录音，可上传音频文件识别。' });
};

const openAudioPicker = () => {
  if (!hasCats.value || !selectedCatId.value) { showToast({ type: 'fail', message: '请先添加猫咪' }); return; }
  if (analyzing.value) return;
  audioInputRef.value?.click();
};

const onAudioSelected = async (event: Event) => {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) return;
  if (!hasCats.value || !selectedCatId.value) {
    input.value = '';
    showToast({ type: 'fail', message: '请先添加猫咪' });
    return;
  }
  analyzing.value = true;
  showToast({ type: 'loading', message: '正在识别猫语...', duration: 0, forbidClick: true });
  try {
    await analyzeEmotion({ catId: selectedCatId.value, audioFile: file });
    closeToast();
    showToast({ type: 'success', message: '识别完成' });
    await refresh();
  } catch {
    closeToast();
    showToast({ type: 'fail', message: '识别失败，请稍后重试' });
  } finally { analyzing.value = false; input.value = ''; }
};

const formatClock = (v: string) => { const d = new Date(v); if (isNaN(d.getTime())) return ''; const h = d.getHours(), m = String(d.getMinutes()).padStart(2, '0'); return `${String(h % 12 || 12).padStart(2, '0')}:${m} ${h >= 12 ? 'PM' : 'AM'}`; };
const emotionIcon = (tag: string) => { if (/开心|愉快|兴奋|满足/i.test(tag)) return '😊'; if (/焦虑|紧张|警惕|害怕/i.test(tag)) return '😰'; if (/生气|愤怒|暴躁/i.test(tag)) return '😾'; if (/悲伤|难过/i.test(tag)) return '😿'; return '😐'; };
const emotionColor = (tag: string) => { if (/开心|愉快|兴奋|满足/i.test(tag)) return 'happy'; if (/焦虑|紧张|警惕|害怕|生气|愤怒|暴躁|悲伤|难过/i.test(tag)) return 'alert'; return 'neutral'; };
const emotionPercent = (r: any) => Math.min(100, Math.max(5, ((r?.confidence || 0.5) * 100)));
const handleImageError = (event: Event) => replaceBrokenImage(event, defaultAvatar);

onMounted(async () => {
  window.scrollTo(0, 0);
  recordingSupport.value = detectAudioRecordingSupport();
  currentCatStore.loadCurrentCat();
  await catsStore.fetchAllCats(true);
  const currentId = currentCatStore.getCurrentCatId;
  const hasCurrent = currentId ? Boolean(catsStore.getCatById(currentId)) : false;
  if (!hasCurrent) { currentCatStore.clearCurrentCat(); if (catsStore.getAllCats[0]?.id) currentCatStore.setCurrentCat(catsStore.getAllCats[0].id); }
  await refresh();
});
onUnmounted(() => cleanupRecorder());
watch(() => selectedCatId.value, async (n, o) => { if (n && n !== o) await refresh(); });
</script>

<style scoped>
/* ========== PAGE ========== */
.meow-page {
  min-height: 100dvh;
  padding-bottom: 104px;
  background: var(--cv-page-gradient);
}

/* ========== HEADER ========== */
.meow-top { padding: 0 20px 24px; }
.meow-nav {
  display: flex; align-items: center; justify-content: space-between;
  height: 52px;
}
.meow-nav-btn {
  width: 40px; height: 40px; display: grid; place-items: center;
  border: none; background: rgba(255,255,255,0.7); backdrop-filter: blur(8px);
  border-radius: 14px; color: #5d4037; cursor: pointer;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04); transition: all .15s;
}
.meow-nav-btn:active { transform: scale(.92); background: #fff; }
.meow-nav-btn--accent { color: var(--cv-accent); background: rgba(249,115,22,0.08); }
.meow-nav-center { display: flex; align-items: center; gap: 8px; }
.meow-nav-icon { font-size: 22px; }
.meow-nav-title { font-size: 20px; font-weight: 800; color: var(--cv-ink); }
.meow-subtitle { margin-top: 6px; font-size: 13px; color: #b0a098; padding: 0 12px; }

/* ========== CAT CARD ========== */
.cat-card {
  margin-top: 16px; display: flex; align-items: center; gap: 14px;
  background: rgba(255,255,255,0.88); backdrop-filter: blur(16px);
  border-radius: 22px; padding: 14px 18px; cursor: pointer;
  border: 1px solid rgba(255,255,255,0.95);
  box-shadow: 0 4px 24px rgba(255,107,53,0.06), 0 1px 3px rgba(0,0,0,0.04);
  transition: transform .15s, box-shadow .15s;
}
.cat-card:active { transform: scale(.98); box-shadow: 0 2px 12px rgba(255,107,53,0.04); }
.cat-avatar-ring { position: relative; flex-shrink: 0; }
.cat-avatar {
  width: 52px; height: 52px; border-radius: 50%; overflow: hidden;
  background: #fce4d6; box-shadow: 0 3px 10px rgba(0,0,0,0.08);
  border: 2.5px solid #fff;
}
.cat-avatar img { width: 100%; height: 100%; object-fit: cover; }
.cat-status-dot {
  position: absolute; bottom: 2px; right: 2px;
  width: 12px; height: 12px; border-radius: 50%;
  background: #22c55e; border: 2.5px solid #fff;
  box-shadow: 0 0 6px rgba(34,197,94,0.4);
  animation: pulse-dot 2s ease-in-out infinite;
}
@keyframes pulse-dot { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(1.3); } }
.cat-info { flex: 1; min-width: 0; }
.cat-name { font-size: 17px; font-weight: 800; color: var(--cv-ink); display: flex; align-items: center; gap: 8px; }
.cat-breed-tag {
  font-size: 11px; font-weight: 700; color: var(--cv-accent);
  background: rgba(249,115,22,0.08); padding: 3px 10px; border-radius: 999px; flex-shrink: 0;
}
.cat-meta { font-size: 12px; color: var(--cv-muted); margin-top: 3px; }
.cat-live-text { color: #22c55e; font-weight: 600; }
.cat-chevron {
  width: 30px; height: 30px; border-radius: 50%;
  background: rgba(249,115,22,0.08); display: grid; place-items: center; color: var(--cv-accent);
}

/* ========== CAT EMPTY ========== */
.cat-empty { margin-top: 16px; text-align: center; padding: 40px 24px; background: rgba(249,115,22,0.08); border-radius: 24px; border: 2px dashed #ffe0cc; }
.cat-empty-illustration { position: relative; display: inline-block; margin-bottom: 12px; }
.cat-empty-emoji { font-size: 64px; display: block; filter: drop-shadow(0 4px 8px rgba(255,107,53,0.15)); animation: catFloat 3s ease-in-out infinite; }
.cat-empty-paws { display: flex; justify-content: center; gap: 8px; margin-top: -8px; }
.cat-empty-paws span { font-size: 18px; animation: pawBounce 1.5s ease-in-out infinite; }
.cat-empty-paws span:nth-child(2) { animation-delay: 0.2s; }
.cat-empty-paws span:nth-child(3) { animation-delay: 0.4s; }
@keyframes catFloat { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
@keyframes pawBounce { 0%, 100% { transform: scale(1); opacity: 0.5; } 50% { transform: scale(1.2); opacity: 1; } }
.cat-empty-title { font-size: 18px; font-weight: 800; color: var(--cv-ink); margin: 0 0 6px; }
.cat-empty-desc { font-size: 14px; color: var(--cv-muted); margin: 0 0 20px; line-height: 1.6; }
.cat-empty-btn {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 12px 32px; border-radius: 999px;
  background: linear-gradient(135deg, #ff7b45, #ff6b35);
  color: #fff; font-size: 16px; font-weight: 700; border: none; cursor: pointer;
  box-shadow: 0 8px 24px rgba(255,107,53,0.3);
  transition: transform .15s, box-shadow .15s;
}
.cat-empty-btn:active { transform: scale(.96); box-shadow: 0 4px 12px rgba(255,107,53,0.25); }

/* ========== LISTEN ZONE ========== */
.listen-zone { display: flex; flex-direction: column; align-items: center; padding: 28px 0 24px; }
.listen-outer-ring {
  width: 180px; height: 180px; border-radius: 50%;
  padding: 12px;
  background: rgba(255,107,53,0.04);
  box-shadow: 0 0 0 1px rgba(255,107,53,0.06), 0 0 0 24px rgba(255,107,53,0.02);
}
.listen-mid-ring {
  width: 100%; height: 100%; border-radius: 50%;
  padding: 10px;
  background: rgba(255,107,53,0.06);
}
.listen-btn {
  width: 100%; height: 100%; border-radius: 50%;
  border: none; cursor: pointer; padding: 0;
  background: linear-gradient(145deg, #ff8a55, #ff5e1a);
  box-shadow: 0 12px 36px rgba(255,107,53,0.35), inset 0 2px 4px rgba(255,255,255,0.2);
  transition: transform .2s, box-shadow .2s;
}
.listen-btn:active { transform: scale(.93); box-shadow: 0 6px 20px rgba(255,107,53,0.25); }
.listen-btn.disabled { opacity: .4; cursor: not-allowed; box-shadow: none; }
.listen-btn.disabled:active { transform: none; }
.listen-btn-inner {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 8px; color: #fff; height: 100%;
}
.listen-btn-inner span { font-size: 14px; font-weight: 700; letter-spacing: 0.5px; }
.listen-hint { margin-top: 14px; font-size: 13px; color: var(--cv-muted); text-align: center; }
.listen-hint.analyzing { color: var(--cv-accent); font-weight: 600; animation: blink 1.2s ease-in-out infinite; }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }

/* ========== EMOTION CARD ========== */
.emotion-card {
  margin: 0 16px; background: #fff; border-radius: 24px; padding: 22px 20px;
  box-shadow: 0 4px 20px rgba(16,24,40,0.04), 0 1px 2px rgba(0,0,0,0.03);
}
.emotion-card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.emotion-card-label { font-size: 12px; font-weight: 700; color: var(--cv-muted); text-transform: uppercase; letter-spacing: 1px; }
.emotion-card-badge { font-size: 11px; font-weight: 700; color: var(--cv-accent); background: rgba(249,115,22,0.08); padding: 2px 10px; border-radius: 999px; }
.emotion-hero { display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 10px; }
.emotion-face { font-size: 52px; line-height: 1; }
.emotion-name { font-size: 24px; font-weight: 800; }
.emotion-name.happy { color: #16a34a; }
.emotion-name.alert { color: #ea580c; }
.emotion-name.neutral { color: #6366f1; }
.emotion-desc { font-size: 14px; color: #6B7280; text-align: center; line-height: 1.7; margin: 0 0 16px; }
.emotion-meter { display: flex; align-items: center; gap: 10px; }
.meter-label { font-size: 11px; color: var(--cv-muted); font-weight: 600; flex-shrink: 0; width: 24px; text-align: center; }
.meter-track { flex: 1; height: 6px; border-radius: 3px; background: #f0f0f5; overflow: hidden; }
.meter-fill {
  height: 100%; border-radius: 3px;
  background: linear-gradient(90deg, #fbbf24 0%, #34d399 50%, #f472b6 100%);
  transition: width .4s ease;
}

/* Emotion empty */
.emotion-empty { text-align: center; padding: 16px 0 4px; }
.emotion-empty-icon { font-size: 48px; display: block; margin-bottom: 10px; }
.emotion-empty-title { font-size: 16px; font-weight: 700; color: #374151; margin: 0 0 4px; }
.emotion-empty-sub { font-size: 13px; color: var(--cv-muted); margin: 0; }

/* ========== ADVICE CARD ========== */
.advice-card {
  margin: 14px 16px 0; display: flex; align-items: center; gap: 14px;
  background: #fff; border-radius: 18px; padding: 16px 18px; cursor: pointer;
  border: 1px solid rgba(255,107,53,0.06);
  box-shadow: 0 2px 12px rgba(0,0,0,0.03);
  transition: all .15s;
}
.advice-card:active { transform: scale(.98); background: #fffbf9; }
.advice-icon-wrap {
  width: 44px; height: 44px; border-radius: 14px;
  background: rgba(249,115,22,0.08);
  display: grid; place-items: center; flex-shrink: 0;
}
.advice-icon { font-size: 22px; }
.advice-content { flex: 1; }
.advice-title { font-size: 15px; font-weight: 700; color: var(--cv-ink); }
.advice-sub { font-size: 12px; color: var(--cv-muted); margin-top: 2px; }
.advice-arrow {
  width: 28px; height: 28px; border-radius: 50%;
  background: #f5f5f5; display: grid; place-items: center; color: #b0a8a5;
}
.advice-disclaimer { margin: 6px 20px 0; font-size: 11px; color: #c4c7d3; line-height: 1.5; }

/* ========== RECORDS ========== */
.records-section { margin: 24px 16px 0; }
.records-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.records-title { font-size: 18px; font-weight: 800; color: var(--cv-ink); margin: 0; }
.records-all {
  font-size: 13px; font-weight: 700; color: var(--cv-accent);
  border: none; background: none; cursor: pointer;
  display: flex; align-items: center; gap: 3px;
  padding: 6px 12px; border-radius: 999px; transition: background .15s;
}
.records-all:active { background: rgba(249,115,22,0.06); }

.records-empty {
  background: #fff; border-radius: 20px; padding: 32px 24px; text-align: center;
  border: 1px dashed #e5e7ef;
}
.records-empty-icon { font-size: 40px; display: block; margin-bottom: 10px; }
.records-empty-title { font-size: 15px; font-weight: 700; color: #374151; margin: 0 0 4px; }
.records-empty-sub { font-size: 13px; color: var(--cv-muted); margin: 0; }

.records-list { display: flex; flex-direction: column; gap: 10px; }
.record-item {
  display: flex; align-items: center; gap: 14px;
  background: #fff; border-radius: 18px; padding: 14px 16px;
  box-shadow: 0 1px 6px rgba(0,0,0,0.03);
  transition: transform .12s;
}
.record-item:active { transform: scale(.99); }
.record-play-btn {
  width: 42px; height: 42px; border-radius: 50%;
  background: linear-gradient(135deg, #ff7b45, #ff6b35);
  color: #fff; border: none; display: grid; place-items: center; cursor: pointer;
  flex-shrink: 0; box-shadow: 0 4px 14px rgba(255,107,53,0.2);
  transition: transform .1s;
}
.record-play-btn:active { transform: scale(.9); }
.record-play-btn.playing { background: #1f2937; box-shadow: 0 4px 14px rgba(0,0,0,0.15); }
.record-play-btn:disabled { opacity: .35; cursor: not-allowed; }
.record-body { flex: 1; min-width: 0; }
.record-top-row { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.record-tag { font-size: 12px; font-weight: 700; padding: 3px 10px; border-radius: 999px; }
.record-tag.happy { background: #dcfce7; color: #16a34a; }
.record-tag.alert { background: #fff7ed; color: #ea580c; }
.record-tag.neutral { background: #eef2ff; color: #6366f1; }
.record-time { font-size: 12px; color: var(--cv-muted); font-weight: 500; }
.record-bar-wrap { margin-top: 6px; }
.record-bar { height: 5px; border-radius: 3px; background: #f0f0f5; overflow: hidden; }
.record-bar-fill { height: 100%; border-radius: 3px; background: linear-gradient(90deg, #ff6b35, #ff8a55); transition: width .4s ease; }
.record-conf { font-size: 11px; color: var(--cv-muted); margin-top: 4px; font-weight: 500; }

/* ========== CAT SWITCHER SHEET ========== */
.sheet-wrap { padding: 8px 16px 20px; }
.sheet-empty-state { text-align: center; padding: 32px 16px; color: var(--cv-muted); font-size: 14px; }
.sheet-empty-state span { font-size: 40px; display: block; margin-bottom: 8px; }
.sheet-cat-list { display: flex; flex-direction: column; gap: 8px; max-height: 50vh; overflow-y: auto; }
.sheet-cat-item {
  display: flex; align-items: center; gap: 14px; padding: 14px 16px;
  border-radius: 16px; border: 2px solid transparent;
  background: #f5f7fb; cursor: pointer; width: 100%; text-align: left;
  transition: all .15s;
}
.sheet-cat-item:active { transform: scale(.98); }
.sheet-cat-item.active { background: rgba(249,115,22,0.08); border-color: var(--cv-accent); }
.sheet-cat-avatar {
  width: 44px; height: 44px; border-radius: 50%; overflow: hidden;
  background: #fce4d6; flex-shrink: 0; border: 2px solid #fff;
  box-shadow: 0 2px 6px rgba(0,0,0,0.06);
}
.sheet-cat-avatar img { width: 100%; height: 100%; object-fit: cover; }
.sheet-cat-info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.sheet-cat-name { font-size: 16px; font-weight: 700; color: var(--cv-ink); }
.sheet-cat-item.active .sheet-cat-name { color: var(--cv-accent); }
.sheet-cat-meta { font-size: 13px; color: var(--cv-muted); }
.sheet-cat-radio { width: 20px; height: 20px; border-radius: 50%; border: 2px solid #d1d5db; flex-shrink: 0; }
.sheet-footer { display: flex; gap: 10px; margin-top: 16px; }
.sheet-footer-btn {
  flex: 1; padding: 13px 0; border-radius: 14px; font-size: 14px; font-weight: 700;
  cursor: pointer; border: none; display: inline-flex; align-items: center; justify-content: center; gap: 6px;
  transition: all .12s;
}
.sheet-footer-btn:active { transform: scale(.97); }
.sheet-footer-btn.outline { background: #fff; border: 1.5px solid #e5e7eb; color: #4B5563; }
.sheet-footer-btn.primary { background: linear-gradient(135deg, var(--cv-accent), #14b8a6); color: #fff; box-shadow: 0 4px 14px rgba(249,115,22,0.25); }
</style>

<style scoped>
.meow-page {
  min-height: 100dvh;
  padding: 0 16px 104px;
  background: var(--cv-page-gradient);
}

.meow-content {
  display: flex;
  flex-direction: column;
  gap: 13px;
  padding-top: 12px;
}

.cat-status-card,
.listen-panel,
.emotion-panel,
.doctor-card,
.records-empty,
.record-item,
.empty-panel {
  border: 1px solid var(--cv-card-border);
  border-radius: var(--cv-card-radius);
  background: var(--cv-card-bg);
  box-shadow: var(--cv-card-shadow);
}

.cat-status-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 13px;
}

.cat-avatar {
  position: relative;
  width: 54px;
  height: 54px;
  flex-shrink: 0;
  overflow: visible;
  border: 0;
  border-radius: 18px;
  background: rgba(249,115,22,0.08);
  box-shadow: none;
}

.cat-avatar img {
  width: 54px;
  height: 54px;
  border-radius: 18px;
  object-fit: cover;
}

.cat-avatar i {
  position: absolute;
  right: -2px;
  bottom: -2px;
  width: 13px;
  height: 13px;
  border: 2px solid #fff;
  border-radius: 999px;
  background: #22c55e;
}

.cat-copy {
  min-width: 0;
  flex: 1;
}

.cat-copy strong {
  display: block;
  overflow: hidden;
  color: var(--cv-ink);
  font-size: 16px;
  font-weight: 900;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.cat-copy span {
  display: block;
  margin-top: 3px;
  overflow: hidden;
  color: var(--cv-muted);
  font-size: 12px;
  font-weight: 700;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty-panel {
  display: grid;
  min-height: 220px;
  place-items: center;
  gap: 8px;
  padding: 36px 24px;
  text-align: center;
  color: var(--cv-muted);
  background: linear-gradient(135deg, #fff8f4 0%, #fff 40%, #fef5ff 100%);
  border: 2px dashed #ffe0cc;
}

.empty-illustration {
  display: inline-block;
  margin-bottom: 4px;
}

.empty-emoji {
  font-size: 60px;
  display: block;
  filter: drop-shadow(0 4px 8px rgba(255,107,53,0.15));
  animation: catFloat 3s ease-in-out infinite;
}

.empty-paws {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: -8px;
}

.empty-paws span {
  font-size: 16px;
  animation: pawBounce 1.5s ease-in-out infinite;
}

.empty-paws span:nth-child(2) { animation-delay: 0.2s; }
.empty-paws span:nth-child(3) { animation-delay: 0.4s; }

@keyframes catFloat { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-8px)} }
@keyframes pawBounce { 0%,100%{transform:scale(1);opacity:.5} 50%{transform:scale(1.2);opacity:1} }

.empty-panel strong,
.records-empty strong {
  color: var(--cv-ink);
  font-size: 18px;
  font-weight: 800;
}

.empty-panel button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 0;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--cv-accent), #14b8a6);
  color: #fff;
  padding: 12px 32px;
  font-size: 16px;
  font-weight: 700;
  box-shadow: 0 8px 24px rgba(249,115,22,0.3);
}

.listen-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 22px 16px 28px;
  text-align: center;
}

.listen-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.listen-badge {
  display: inline-block;
  background: #fff1e8;
  color: #ff6b35;
  font-size: 12px;
  font-weight: 700;
  padding: 4px 14px;
  border-radius: 999px;
  letter-spacing: 0.5px;
}

.listen-header strong {
  display: block;
  margin-top: 2px;
  color: #102033;
  font-size: 22px;
  font-weight: 900;
  line-height: 1.15;
}

.listen-header p {
  margin: 4px 0 0;
  color: #7a8494;
  font-size: 13px;
  font-weight: 600;
  line-height: 1.5;
  max-width: 260px;
}

.section-head span {
  color: #ff6b35;
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.recognition-grid {
  display: grid;
  width: 100%;
  gap: 12px;
}

.recognition-card {
  border: 1px solid #ede8e0;
  border-radius: 22px;
  background: #fffaf6;
  padding: 14px;
  text-align: left;
}

.recognition-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  color: #f97316;
}

.recognition-card-head span {
  display: block;
  color: #f97316;
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.06em;
}

.recognition-card-head strong {
  display: block;
  margin-top: 4px;
  color: var(--cv-ink);
  font-size: 17px;
  font-weight: 900;
}

.recognition-card p,
.capability-warning {
  margin: 10px 0 0;
  color: var(--cv-muted);
  font-size: 12px;
  font-weight: 700;
  line-height: 1.55;
}

.capability-warning {
  border-radius: 14px;
  background: #fff7ed;
  color: #c2410c;
  padding: 10px;
}

.record-card.unavailable {
  background: #f8fafc;
}

.upload-card {
  background: #f6fffb;
}

.upload-audio-btn {
  display: inline-flex;
  width: 100%;
  height: 46px;
  align-items: center;
  justify-content: center;
  gap: 7px;
  margin-top: 12px;
  border: 0;
  border-radius: 15px;
  background: var(--cv-ink);
  color: #fff;
  font-size: 14px;
  font-weight: 900;
}

.upload-audio-btn:disabled {
  opacity: .55;
}

/* ===== RECORDING DISC ===== */
.record-disc-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  margin-top: 12px;
}

.record-disc-stage {
  position: relative;
  width: 210px;
  height: 210px;
  display: grid;
  place-items: center;
}

/* Aura rings */
.disc-aura {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
  transition: all .4s cubic-bezier(.4,0,.2,1);
}

.aura-1 {
  width: 100%; height: 100%;
  border: 2px solid rgba(255, 107, 53, 0.08);
  background: radial-gradient(circle, rgba(255,107,53,0.03) 0%, transparent 70%);
}

.aura-2 {
  width: 88%; height: 88%;
  border: 1.5px solid rgba(255, 107, 53, 0.1);
}

.aura-3 {
  width: 76%; height: 76%;
  border: 1px solid rgba(255, 107, 53, 0.12);
}

/* Glow behind disc */
.disc-glow {
  position: absolute;
  width: 130px; height: 130px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255,107,53,0.18) 0%, transparent 70%);
  pointer-events: none;
  transition: all .4s ease;
}

/* Recording state auras */
.record-disc-stage.recording .aura-1 {
  border-color: rgba(255, 80, 60, 0.25);
  background: radial-gradient(circle, rgba(255,80,60,0.06) 0%, transparent 70%);
  animation: aura-breathe 1.4s ease-in-out infinite;
}
.record-disc-stage.recording .aura-2 {
  border-color: rgba(255, 80, 60, 0.2);
  animation: aura-breathe 1.4s ease-in-out .25s infinite;
}
.record-disc-stage.recording .aura-3 {
  border-color: rgba(255, 80, 60, 0.15);
  animation: aura-breathe 1.4s ease-in-out .5s infinite;
}
.record-disc-stage.recording .disc-glow {
  background: radial-gradient(circle, rgba(255,80,60,0.3) 0%, transparent 70%);
  animation: glow-pulse .8s ease-in-out infinite;
}

@keyframes aura-breathe {
  0%, 100% { transform: scale(1); opacity: .7; }
  50% { transform: scale(1.08); opacity: 1; }
}

@keyframes glow-pulse {
  0%, 100% { transform: scale(1); opacity: .6; }
  50% { transform: scale(1.25); opacity: 1; }
}

/* Analyzing state */
.record-disc-stage.analyzing .aura-1 { border-color: rgba(16, 32, 51, 0.1); }
.record-disc-stage.analyzing .aura-2 { border-color: rgba(16, 32, 51, 0.08); }
.record-disc-stage.analyzing .aura-3 { border-color: rgba(16, 32, 51, 0.06); }
.record-disc-stage.analyzing .disc-glow {
  background: radial-gradient(circle, rgba(16,32,51,0.12) 0%, transparent 70%);
}

/* Main disc button */
.record-disc-btn {
  position: relative;
  z-index: 1;
  width: 136px;
  height: 136px;
  border: none;
  border-radius: 50%;
  background: linear-gradient(155deg, #ff9a65 0%, #ff6b35 40%, #e85d2c 100%);
  box-shadow:
    0 8px 32px rgba(255, 107, 53, 0.28),
    0 2px 8px rgba(255, 107, 53, 0.15),
    inset 0 2px 0 rgba(255, 255, 255, 0.25),
    inset 0 -2px 0 rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transition: transform .2s cubic-bezier(.4,0,.2,1), box-shadow .3s;
  display: grid;
  place-items: center;
  -webkit-tap-highlight-color: transparent;
  user-select: none;
  overflow: hidden;
}

.record-disc-btn::after {
  content: '';
  position: absolute;
  inset: 12px;
  border-radius: 50%;
  border: 1.5px solid rgba(255, 255, 255, 0.2);
  pointer-events: none;
}

.record-disc-btn:active {
  transform: scale(.94);
  box-shadow:
    0 4px 16px rgba(255, 107, 53, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.record-disc-btn.recording {
  background: linear-gradient(155deg, #f05050 0%, #dc2626 40%, #b91c1c 100%);
  box-shadow:
    0 8px 36px rgba(220, 38, 38, 0.35),
    0 2px 8px rgba(220, 38, 38, 0.2),
    inset 0 2px 0 rgba(255, 255, 255, 0.2),
    inset 0 -2px 0 rgba(0, 0, 0, 0.1);
  animation: disc-thump .7s ease-in-out infinite;
}

@keyframes disc-thump {
  0%, 100% { transform: scale(1); }
  40% { transform: scale(1.045); }
}

.record-disc-btn.analyzing {
  background: linear-gradient(155deg, #3a3f55 0%, #1a1f33 40%, #0f1322 100%);
  box-shadow:
    0 8px 32px rgba(16, 32, 51, 0.3),
    inset 0 2px 0 rgba(255, 255, 255, 0.1);
}

.record-disc-btn.analyzing::after {
  border-color: rgba(255, 255, 255, 0.1);
}

.record-disc-btn.disabled {
  opacity: .35;
  cursor: not-allowed;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.record-disc-btn.disabled:active { transform: none; }

/* Inner content */
.disc-inner-face {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  pointer-events: none;
  position: relative;
  z-index: 1;
}

.disc-emoji {
  font-size: 36px;
  line-height: 1;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
  transition: transform .3s ease;
}

.record-disc-btn.recording .disc-emoji {
  animation: emoji-bounce .5s ease-in-out infinite;
}

@keyframes emoji-bounce {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-4px) scale(1.1); }
}

.disc-icon {
  color: rgba(255, 255, 255, 0.8);
  margin-top: -2px;
  transition: all .3s;
}

.disc-icon.spinning {
  animation: icon-spin 2s linear infinite;
  color: rgba(255, 255, 255, 0.6);
}

@keyframes icon-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.disc-label {
  margin-top: 2px;
  font-size: 12px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.85);
  letter-spacing: 0.5px;
}

/* Footer hint */
.disc-footer-hint {
  font-size: 12px;
  font-weight: 600;
  color: #b0a89e;
  text-align: center;
  letter-spacing: 0.3px;
}

.hint-paw {
  font-size: 13px;
  display: inline-block;
  animation: paw-wiggle 2s ease-in-out infinite;
}

.hint-paw:last-child { animation-delay: 1s; }

@keyframes paw-wiggle {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(-12deg); }
  75% { transform: rotate(12deg); }
}

.emotion-panel {
  padding: 16px;
}

.section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.section-head h2 {
  margin: 3px 0 0;
  color: var(--cv-ink);
  font-size: 22px;
  font-weight: 900;
  line-height: 1.1;
}

.section-head b {
  border-radius: 999px;
  background: rgba(249,115,22,0.08);
  color: var(--cv-accent);
  padding: 6px 9px;
  font-size: 12px;
  font-weight: 900;
}

.section-head.compact button {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  border: 0;
  background: transparent;
  color: var(--cv-accent);
  font-size: 13px;
  font-weight: 900;
}

.emotion-insight {
  display: flex;
  align-items: center;
  gap: 13px;
  margin-top: 14px;
}

.emotion-symbol {
  display: grid;
  width: 70px;
  height: 70px;
  flex-shrink: 0;
  place-items: center;
  border-radius: 24px;
  background: #eef2ff;
  font-size: 34px;
}

.emotion-symbol.happy {
  background: #ecfdf5;
}

.emotion-symbol.alert {
  background: #fff7ed;
}

.emotion-insight p {
  margin: 0;
  color: var(--cv-muted);
  font-size: 13px;
  font-weight: 700;
  line-height: 1.6;
}

.emotion-meter {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 9px;
  margin-top: 15px;
  color: var(--cv-muted);
  font-size: 11px;
  font-weight: 900;
}

.emotion-meter div {
  height: 8px;
  overflow: hidden;
  border-radius: 999px;
  background: #edf2f7;
}

.emotion-meter i {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #14b8a6, #f97316);
}

.emotion-placeholder {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 14px;
  border-radius: 16px;
  background: #f4f7fb;
  color: var(--cv-muted);
  padding: 14px;
  font-size: 13px;
  font-weight: 800;
}

.doctor-card {
  display: grid;
  grid-template-columns: 44px 1fr auto;
  align-items: center;
  gap: 12px;
  padding: 14px;
}

.doctor-card > div:first-child {
  display: grid;
  width: 44px;
  height: 44px;
  place-items: center;
  border-radius: 15px;
  background: #ecfdf5;
  color: #0f766e;
}

.doctor-card strong {
  display: block;
  color: var(--cv-ink);
  font-size: 15px;
  font-weight: 900;
}

.doctor-card span {
  display: block;
  margin-top: 2px;
  color: var(--cv-muted);
  font-size: 12px;
  font-weight: 700;
}

.records-section {
  margin: 0;
}

.records-list {
  display: flex;
  flex-direction: column;
  gap: 9px;
  margin-top: 10px;
}

.records-empty {
  display: grid;
  min-height: 154px;
  place-items: center;
  gap: 6px;
  margin-top: 10px;
  color: var(--cv-muted);
  padding: 20px;
}

.record-item {
  padding: 13px;
}

.record-play-btn {
  width: 42px;
  height: 42px;
  border-radius: 15px;
  background: var(--cv-ink);
  box-shadow: none;
}

.record-play-btn.playing {
  background: linear-gradient(135deg, var(--cv-accent), #14b8a6);
}

.record-top-row time,
.record-body small {
  color: var(--cv-muted);
  font-size: 11px;
  font-weight: 800;
}

.record-inline-actions {
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  gap: 6px;
}

.record-delete-mini {
  display: inline-grid;
  width: 26px;
  height: 26px;
  place-items: center;
  border: 0;
  border-radius: 10px;
  background: #fef2f2;
  color: #b91c1c;
}

.record-delete-mini:active {
  transform: scale(0.94);
}

.record-bar {
  height: 7px;
  margin-top: 8px;
  border-radius: 999px;
}

.record-bar i {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #14b8a6, #f97316);
}

.record-tag {
  font-weight: 900;
}

.record-tag.happy {
  background: #ecfdf5;
  color: #047857;
}

.record-tag.alert {
  background: #fff7ed;
  color: #c2410c;
}

.record-tag.neutral {
  background: #eef2ff;
  color: #4f46e5;
}

/* ===== Warm Theme Overrides ===== */
.meow-page {
  background: #fff7f0;
}

.cat-status-card,
.listen-panel,
.emotion-panel,
.doctor-card,
.records-empty,
.record-item,
.empty-panel {
  border-color: #ede8e0;
  background: #fff;
  box-shadow: 0 2px 12px rgba(16, 32, 51, 0.04);
}

.cat-empty {
  background: linear-gradient(135deg, #fff8f4 0%, #fff 40%, #fef5ff 100%);
}

.record-tag.happy {
  background: #ecfdf5;
  color: #0f8a44;
}

.record-tag.neutral {
  background: #fdfaf6;
  color: #7a8494;
}

.emotion-card {
  border-color: #ede8e0;
  background: #fff;
  box-shadow: 0 2px 12px rgba(16, 32, 51, 0.04);
}

.advice-card {
  background: #fff;
  border-color: #ede8e0;
}

.advice-card:active {
  background: #fffaf6;
}

/* Watch badge */
.listening-dot {
  background: #22c55e;
}

/* Meter gradient - warmer */
.meter-fill {
  background: linear-gradient(90deg, #fbbf24 0%, #ff6b35 50%, #f472b6 100%);
}
</style>
