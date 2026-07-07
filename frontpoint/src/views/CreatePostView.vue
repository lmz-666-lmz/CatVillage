<template>
  <div class="create-page">
    <div v-if="loading" class="state-card">
      <van-loading size="22" color="#ff6b35" />
      <div class="state-text">正在加载发布页面...</div>
    </div>

    <div v-else-if="error" class="state-card">
      <div class="state-title">页面加载失败</div>
      <div class="state-text">{{ error }}</div>
      <van-button class="retry-btn" type="primary" @click="reload">重试</van-button>
    </div>

    <div v-else>
      <!-- Header -->
      <header class="create-header">
        <button type="button" class="cancel-btn" @click="router.back()">取消</button>
        <h1 class="create-title">发布动态</h1>
        <button
          type="button"
          class="publish-btn"
          :disabled="publishing || !hasCats || !content.trim()"
          @click="publish"
        >
          {{ publishing ? '发布中' : '发布' }}
        </button>
      </header>

      <!-- Identity Card -->
      <section class="identity-card">
        <div class="identity-label">发布身份</div>
        <div class="identity-row">
          <span class="identity-emoji">🐾</span>
          <span class="identity-name">{{ selectedCatName }}</span>
        </div>

        <!-- No cat empty state -->
        <div v-if="!hasCats" class="no-cat-block">
          <div class="no-cat-visual">
            <span class="no-cat-emoji">🐱</span>
            <div class="no-cat-paws">
              <span>🐾</span><span>🐾</span><span>🐾</span>
            </div>
          </div>
          <h3 class="no-cat-title">还没有猫咪档案</h3>
          <p class="no-cat-desc">添加猫咪后即可发布动态，和村友们分享日常</p>
          <button class="no-cat-btn" @click="router.push({ name: 'AddCat' })">
            <van-icon name="plus" size="16" />
            添加猫咪
          </button>
        </div>
      </section>

      <!-- Content Editor -->
      <section class="editor-card">
        <textarea
          v-model="content"
          class="editor-textarea"
          maxlength="500"
          placeholder="分享关于猫咪的日常或是新的发现..."
        ></textarea>
        <div class="editor-footer">
          <span class="char-count">{{ content.length }}/500</span>
        </div>

        <!-- Image Grid -->
        <div class="image-section">
          <input ref="imageInputRef" type="file" accept="image/*" multiple class="hidden" @change="onPickImages" />
          <div class="image-grid">
            <template v-for="(slot, index) in imageSlots" :key="index">
              <!-- Existing image -->
              <button
                v-if="slot"
                type="button"
                class="image-item image-item--filled"
                @click="removeImage(slot.id)"
              >
                <img :src="slot.previewUrl" class="image-preview" alt="已选择图片" />
                <span class="image-remove">×</span>
              </button>

              <!-- Add button -->
              <button
                v-else-if="index === imageAssets.length && imageAssets.length < MAX_IMAGES"
                type="button"
                class="image-item image-item--add"
                @click="openImagePicker"
              >
                <van-icon name="plus" size="28" />
                <span class="image-add-text">添加图片</span>
              </button>

              <!-- Empty slot -->
              <div v-else class="image-item image-item--empty"></div>
            </template>
          </div>
          <div v-if="imageAssets.length > 0" class="image-hint">已选 {{ imageAssets.length }}/{{ MAX_IMAGES }} 张，点击图片可移除</div>
        </div>
      </section>

      <!-- Audio / Emotion Section -->
      <section class="audio-card">
        <div class="audio-header">
          <div class="audio-header-left">
            <span class="audio-dot"></span>
            <span class="audio-title">添加猫语</span>
          </div>
          <span class="audio-badge">AI 情绪识别</span>
        </div>

        <div class="audio-actions">
          <button type="button" class="audio-action-btn" :disabled="!hasCats || audioBusy || !selectedCatId" @click="toggleRecording">
            <div class="audio-action-icon" :class="{ recording: isRecording }">
              <van-icon :name="isRecording ? 'pause-circle-o' : 'volume-o'" size="22" />
            </div>
            <span class="audio-action-label">{{ isRecording ? '停止录音' : '现场录音' }}</span>
            <span class="audio-action-hint">{{ isRecording ? '点击停止' : '录制猫叫声' }}</span>
          </button>
          <button type="button" class="audio-action-btn" :disabled="!hasCats || audioBusy || !selectedCatId" @click="openAudioPicker">
            <div class="audio-action-icon">
              <van-icon name="replay" size="22" />
            </div>
            <span class="audio-action-label">历史导入</span>
            <span class="audio-action-hint">选择音频文件</span>
          </button>
        </div>

        <input ref="audioInputRef" type="file" accept="audio/*" class="hidden" @change="onPickAudioFile" />

        <!-- Recording Status -->
        <div v-if="recordStatusText" class="audio-status">
          {{ recordStatusText }}
        </div>

        <!-- Emotion Result -->
        <div v-if="lastAudioResult" class="emotion-result">
          <div class="emotion-result-row">
            <div>
              <div class="emotion-tag">{{ lastAudioResult.emotionTag }}</div>
              <div class="emotion-confidence">置信度 {{ Math.round(lastAudioResult.confidence * 100) }}%</div>
            </div>
            <button type="button" class="emotion-insert-btn" @click="appendEmotionToContent">
              插入文案
            </button>
          </div>
          <div class="emotion-desc">{{ lastAudioResult.emotionDescription || '暂无描述' }}</div>
        </div>

        <div class="audio-footer-hint">系统会整理情绪结果与热词推荐，帮你找到合适话题。</div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from 'vue';
import { useRouter } from 'vue-router';
import { closeToast, showToast } from 'vant';
import type { RecognizeEmotionResponse } from '@/types/emotion';
import { useSocialFeatures } from '@/composables/useSocialFeatures';
import { useEmotionAnalysis } from '@/composables/useEmotionAnalysis';
import { useCatsStore, useCurrentCatStore } from '@/stores';

const router = useRouter();
const { publishNewDynamic } = useSocialFeatures();
const { analyzeEmotion } = useEmotionAnalysis();
const catsStore = useCatsStore();
const currentCatStore = useCurrentCatStore();

const publishing = ref(false);
const content = ref('');
const loading = ref(true);
const error = ref<string | null>(null);
const imageInputRef = ref<HTMLInputElement | null>(null);
const audioInputRef = ref<HTMLInputElement | null>(null);
const imageAssets = ref<Array<{ id: string; file: File; previewUrl: string }>>([]);
const MAX_IMAGES = 9;

const audioBusy = ref(false);
const isRecording = ref(false);
const recordStatusText = ref('');
const lastAudioResult = ref<RecognizeEmotionResponse | null>(null);
const recorder = ref<MediaRecorder | null>(null);
const recordingChunks = ref<Blob[]>([]);
const recordingStream = ref<MediaStream | null>(null);

const selectedCatId = computed(() => currentCatStore.getCurrentCatId || catsStore.getAllCats[0]?.id || '');
const hasCats = computed(() => catsStore.getAllCats.length > 0);
const selectedCatName = computed(() => {
  const id = selectedCatId.value;
  if (!id) return '未选择猫咪';
  const cat = catsStore.getCatById(id);
  return cat?.name || '未选择猫咪';
});

const imageSlots = computed(() => Array.from({ length: MAX_IMAGES }, (_, index) => imageAssets.value[index] || null));

const initData = async () => {
  loading.value = true;
  error.value = null;
  try {
    await catsStore.fetchAllCats();
    const first = catsStore.getAllCats[0];
    if (!currentCatStore.getCurrentCatId && first) {
      currentCatStore.setCurrentCat(first.id);
    }
  } catch {
    error.value = '页面加载失败，请检查网络后重试';
  } finally {
    loading.value = false;
  }
};

const reload = () => initData();

const openImagePicker = () => imageInputRef.value?.click();
const openAudioPicker = () => audioInputRef.value?.click();

const revokePreview = (url: string) => {
  if (url.startsWith('blob:')) URL.revokeObjectURL(url);
};

const onPickImages = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const files = Array.from(target.files || []);
  if (!files.length) return;

  const availableCount = MAX_IMAGES - imageAssets.value.length;
  const nextFiles = files.slice(0, availableCount).map((file) => ({
    id: `${file.name}-${file.size}-${file.lastModified}-${Math.random().toString(36).slice(2)}`,
    file,
    previewUrl: URL.createObjectURL(file)
  }));

  imageAssets.value = [...imageAssets.value, ...nextFiles];
  target.value = '';
};

const removeImage = (id: string) => {
  const item = imageAssets.value.find((entry) => entry.id === id);
  if (item) revokePreview(item.previewUrl);
  imageAssets.value = imageAssets.value.filter((entry) => entry.id !== id);
};

const cleanupRecorder = () => {
  recorder.value?.stream.getTracks().forEach((track) => track.stop());
  recorder.value = null;
  recordingStream.value = null;
  recordingChunks.value = [];
  isRecording.value = false;
};

const analyzeAudioBlob = async (blob: Blob, fileName: string) => {
  const catId = selectedCatId.value;
  if (!catId) {
    showToast({ type: 'fail', message: '请先选择猫咪档案' });
    return;
  }

  audioBusy.value = true;
  recordStatusText.value = '正在上传并识别猫叫记录...';
  showToast({ type: 'loading', message: '正在识别...', duration: 0, forbidClick: true });

  try {
    const file = new File([blob], fileName, { type: blob.type || 'audio/webm' });
    lastAudioResult.value = await analyzeEmotion({ catId, audioFile: file });
    recordStatusText.value = `已识别：${lastAudioResult.value.emotionTag}`;
    closeToast();
    showToast({ type: 'success', message: '识别完成' });
  } catch {
    recordStatusText.value = '识别失败，请稍后重试';
    closeToast();
    showToast({ type: 'fail', message: '识别失败，请稍后重试' });
  } finally {
    audioBusy.value = false;
  }
};

const toggleRecording = async () => {
  if (audioBusy.value || !selectedCatId.value) return;

  if (isRecording.value && recorder.value) {
    recorder.value.stop();
    isRecording.value = false;
    recordStatusText.value = '正在处理录音...';
    return;
  }

  if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === 'undefined') {
    showToast({ type: 'fail', message: '当前浏览器不支持录音' });
    return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    recordingStream.value = stream;
    recordingChunks.value = [];
    const mediaRecorder = new MediaRecorder(stream);
    recorder.value = mediaRecorder;

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) recordingChunks.value.push(event.data);
    };

    mediaRecorder.onstop = async () => {
      const blob = new Blob(recordingChunks.value, { type: mediaRecorder.mimeType || 'audio/webm' });
      cleanupRecorder();
      if (blob.size > 0) {
        await analyzeAudioBlob(blob, `meow-record-${Date.now()}.webm`);
      } else {
        recordStatusText.value = '未录到有效音频';
      }
    };

    mediaRecorder.start();
    isRecording.value = true;
    recordStatusText.value = '正在录音，点击可停止';
  } catch {
    showToast({ type: 'fail', message: '无法开启录音权限' });
    cleanupRecorder();
  }
};

const onPickAudioFile = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  target.value = '';
  if (!file) return;
  if (!file.type.startsWith('audio/')) {
    showToast({ type: 'fail', message: '请选择音频文件' });
    return;
  }
  await analyzeAudioBlob(file, file.name || `meow-import-${Date.now()}.webm`);
};

const appendEmotionToContent = () => {
  if (!lastAudioResult.value) return;
  const text = `【${lastAudioResult.value.emotionTag}】${lastAudioResult.value.emotionDescription}`;
  content.value = content.value ? `${content.value}\n${text}` : text;
};

const publish = async () => {
  const text = content.value.trim();
  if (!text) {
    showToast({ type: 'fail', message: '请填写内容' });
    return;
  }

  if (!hasCats.value || !selectedCatId.value) {
    await catsStore.fetchAllCats();
    const first = catsStore.getAllCats[0];
    if (!currentCatStore.getCurrentCatId && first) currentCatStore.setCurrentCat(first.id);
  }

  if (!hasCats.value || !selectedCatId.value) {
    showToast({ type: 'fail', message: '请先添加并选择一只猫咪' });
    return;
  }

  const images = imageAssets.value.map((item) => item.file);

  publishing.value = true;
  showToast({ type: 'loading', message: '正在发布...', duration: 0, forbidClick: true });
  try {
    await publishNewDynamic({ catId: selectedCatId.value, content: text, images });
    closeToast();
    showToast({ type: 'success', message: '发布成功' });
    router.replace({ name: 'Social' });
  } catch {
    closeToast();
    showToast({ type: 'fail', message: '发布失败，请稍后重试' });
  } finally {
    publishing.value = false;
  }
};

onBeforeUnmount(() => {
  imageAssets.value.forEach((item) => revokePreview(item.previewUrl));
  cleanupRecorder();
});

void initData();
</script>

<style scoped>
/* ========== PAGE ========== */
.create-page {
  min-height: 100dvh;
  padding: 0 16px 104px;
  background: #fff7f0;
}

/* ========== STATE CARD ========== */
.state-card {
  border-radius: 24px;
  background: #ffffff;
  padding: 48px 20px;
  text-align: center;
  box-shadow: 0 2px 14px rgba(16, 32, 51, 0.04);
  margin-top: 24px;
}

.state-title {
  font-size: 16px;
  font-weight: 800;
  color: #102033;
  margin-bottom: 6px;
}

.state-text {
  font-size: 14px;
  color: #7a8494;
  margin-top: 8px;
}

.retry-btn {
  margin-top: 16px;
}

/* ========== HEADER ========== */
.create-header {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  min-height: 56px;
  align-items: center;
  justify-content: space-between;
  margin: 0 -16px;
  padding: 8px 16px;
  background: linear-gradient(180deg, rgba(255, 247, 240, 0.96) 0%, rgba(255, 247, 240, 0.88) 100%);
  backdrop-filter: blur(14px);
}

.cancel-btn {
  border: none;
  background: none;
  font-size: 15px;
  font-weight: 600;
  color: #7a8494;
  cursor: pointer;
  padding: 8px 4px;
}

.create-title {
  margin: 0;
  font-size: 20px;
  font-weight: 900;
  color: #102033;
}

.publish-btn {
  height: 42px;
  border: none;
  border-radius: 16px;
  background: linear-gradient(135deg, #ff8a4c, #ff6b35);
  padding: 0 22px;
  font-size: 15px;
  font-weight: 800;
  color: #ffffff;
  cursor: pointer;
  box-shadow: 0 6px 18px rgba(255, 107, 53, 0.24);
  transition: opacity 0.14s ease, transform 0.14s ease;
}

.publish-btn:active {
  transform: scale(0.95);
}

.publish-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  transform: none;
}

/* ========== IDENTITY CARD ========== */
.identity-card {
  margin-top: 16px;
  border-radius: 22px;
  background: #ffffff;
  padding: 16px 18px;
  box-shadow: 0 2px 12px rgba(16, 32, 51, 0.04);
}

.identity-label {
  font-size: 12px;
  font-weight: 700;
  color: #7a8494;
  margin-bottom: 6px;
}

.identity-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.identity-emoji {
  font-size: 22px;
}

.identity-name {
  font-size: 16px;
  font-weight: 800;
  color: #102033;
}

/* ========== NO CAT BLOCK ========== */
.no-cat-block {
  margin-top: 16px;
  border-radius: 18px;
  border: 2px dashed #ffe0cc;
  background: linear-gradient(135deg, #fff8f4 0%, #fff 50%, #fef5ff 100%);
  padding: 28px 20px;
  text-align: center;
}

.no-cat-visual {
  display: inline-block;
  margin-bottom: 10px;
}

.no-cat-emoji {
  font-size: 52px;
  display: block;
  animation: catBounce 3s ease-in-out infinite;
}

@keyframes catBounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.no-cat-paws {
  display: flex;
  justify-content: center;
  gap: 6px;
  margin-top: -6px;
}

.no-cat-paws span {
  font-size: 13px;
  animation: pawPop 1.5s ease-in-out infinite;
}

.no-cat-paws span:nth-child(2) { animation-delay: 0.2s; }
.no-cat-paws span:nth-child(3) { animation-delay: 0.4s; }

@keyframes pawPop {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.2); opacity: 1; }
}

.no-cat-title {
  margin: 0 0 4px;
  font-size: 17px;
  font-weight: 800;
  color: #102033;
}

.no-cat-desc {
  margin: 0 0 16px;
  font-size: 13px;
  color: #7a8494;
  line-height: 1.5;
}

.no-cat-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: none;
  border-radius: 999px;
  background: linear-gradient(135deg, #ff8a4c, #ff6b35);
  padding: 11px 24px;
  font-size: 14px;
  font-weight: 700;
  color: #ffffff;
  cursor: pointer;
  box-shadow: 0 6px 18px rgba(255, 107, 53, 0.24);
  transition: transform 0.14s ease;
}

.no-cat-btn:active {
  transform: scale(0.95);
}

/* ========== EDITOR CARD ========== */
.editor-card {
  margin-top: 14px;
  border-radius: 22px;
  background: #ffffff;
  padding: 16px 18px 18px;
  box-shadow: 0 2px 12px rgba(16, 32, 51, 0.04);
}

.editor-textarea {
  width: 100%;
  min-height: 120px;
  box-sizing: border-box;
  resize: none;
  border: none;
  border-radius: 16px;
  background: #fdfaf6;
  padding: 14px 16px;
  font-size: 15px;
  font-weight: 500;
  line-height: 1.7;
  color: #102033;
  outline: none;
  transition: background 0.2s ease;
}

.editor-textarea::placeholder {
  color: #b0b8c4;
}

.editor-textarea:focus {
  background: #fffaf5;
}

.editor-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 6px;
}

.char-count {
  font-size: 12px;
  font-weight: 600;
  color: #b0b8c4;
}

/* ========== IMAGE GRID ========== */
.image-section {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f3f0ec;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.image-item {
  aspect-ratio: 1;
  border-radius: 16px;
  overflow: hidden;
}

.image-item--filled {
  position: relative;
  border: none;
  padding: 0;
  cursor: pointer;
}

.image-item--filled:active {
  opacity: 0.85;
}

.image-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-remove {
  position: absolute;
  top: 6px;
  right: 6px;
  display: grid;
  width: 22px;
  height: 22px;
  place-items: center;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.55);
  color: #ffffff;
  font-size: 14px;
  line-height: 1;
}

.image-item--add {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  border: 2px dashed #e0dbd4;
  background: #fdfaf6;
  color: #c0b8ac;
  cursor: pointer;
  transition: border-color 0.14s ease, color 0.14s ease;
}

.image-item--add:hover {
  border-color: #ff6b35;
  color: #ff6b35;
}

.image-add-text {
  font-size: 11px;
  font-weight: 600;
}

.image-item--empty {
  border: 1px dashed #ede8e0;
  background: #fafaf8;
}

.image-hint {
  margin-top: 8px;
  font-size: 12px;
  font-weight: 500;
  color: #b0b8c4;
  text-align: right;
}

/* ========== AUDIO CARD ========== */
.audio-card {
  margin-top: 14px;
  margin-bottom: 20px;
  border-radius: 22px;
  background: #ffffff;
  padding: 18px;
  box-shadow: 0 2px 12px rgba(16, 32, 51, 0.04);
}

.audio-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.audio-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.audio-dot {
  display: inline-block;
  width: 6px;
  height: 20px;
  border-radius: 3px;
  background: #ff6b35;
}

.audio-title {
  font-size: 16px;
  font-weight: 800;
  color: #102033;
}

.audio-badge {
  font-size: 11px;
  font-weight: 700;
  color: #ff6b35;
  background: #fff1e8;
  padding: 4px 10px;
  border-radius: 999px;
}

.audio-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.audio-action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  border: none;
  border-radius: 18px;
  background: #fdfaf6;
  padding: 20px 12px 16px;
  cursor: pointer;
  transition: background 0.14s ease, transform 0.14s ease;
}

.audio-action-btn:active:not(:disabled) {
  transform: scale(0.96);
  background: #fff5ec;
}

.audio-action-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.audio-action-icon {
  display: grid;
  width: 48px;
  height: 48px;
  place-items: center;
  border-radius: 50%;
  background: #fff1e8;
  color: #ff6b35;
  transition: background 0.14s ease, color 0.14s ease;
}

.audio-action-icon.recording {
  background: #ff6b35;
  color: #ffffff;
  animation: pulse-ring 1.2s ease-in-out infinite;
}

@keyframes pulse-ring {
  0%, 100% { box-shadow: 0 0 0 0 rgba(255, 107, 53, 0.35); }
  50% { box-shadow: 0 0 0 12px rgba(255, 107, 53, 0); }
}

.audio-action-label {
  font-size: 14px;
  font-weight: 700;
  color: #102033;
}

.audio-action-hint {
  font-size: 11px;
  font-weight: 500;
  color: #b0b8c4;
}

.audio-status {
  margin-top: 12px;
  border-radius: 14px;
  background: #fdfaf6;
  padding: 12px 14px;
  font-size: 13px;
  font-weight: 500;
  color: #7a8494;
  text-align: center;
}

/* ========== EMOTION RESULT ========== */
.emotion-result {
  margin-top: 12px;
  border-radius: 16px;
  background: linear-gradient(135deg, #fff8f3, #fffdfa);
  border: 1px solid #ffe8d6;
  padding: 14px 16px;
}

.emotion-result-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.emotion-tag {
  font-size: 15px;
  font-weight: 800;
  color: #102033;
}

.emotion-confidence {
  font-size: 12px;
  font-weight: 600;
  color: #7a8494;
  margin-top: 2px;
}

.emotion-insert-btn {
  border: none;
  border-radius: 999px;
  background: linear-gradient(135deg, #ff8a4c, #ff6b35);
  padding: 7px 16px;
  font-size: 12px;
  font-weight: 700;
  color: #ffffff;
  cursor: pointer;
  transition: opacity 0.14s ease;
}

.emotion-insert-btn:active {
  opacity: 0.8;
}

.emotion-desc {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #ffe8d6;
  font-size: 13px;
  font-weight: 500;
  color: #7a8494;
  line-height: 1.5;
}

.audio-footer-hint {
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid #f3f0ec;
  font-size: 11px;
  font-weight: 500;
  color: #b0b8c4;
  text-align: center;
}
</style>
