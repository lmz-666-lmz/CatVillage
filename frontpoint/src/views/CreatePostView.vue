<template>
  <div class="min-h-[100dvh] bg-[#f4f5fb] px-4 pt-3 pb-8">
    <div v-if="loading" class="rounded-2xl border border-surface-container-high bg-surface-container-lowest px-4 py-10 text-center text-sm text-on-surface-variant">
      <van-loading size="20" />
      <div class="mt-3">正在加载发布页面...</div>
    </div>

    <div v-else-if="error" class="rounded-2xl border border-surface-container-high bg-surface-container-lowest px-4 py-10 text-center text-sm text-on-surface-variant">
      <div class="text-base font-semibold text-on-background">组件加载失败</div>
      <div class="mt-2">{{ error }}</div>
      <van-button class="mt-4" type="primary" @click="reload">重试</van-button>
    </div>

    <div v-else>
      <header class="sticky top-0 z-20 -mx-4 flex min-h-[54px] items-center justify-between bg-[#f4f5fb]/95 px-4 py-2.5 backdrop-blur-md">
        <button type="button" class="text-[14px] font-semibold text-[#8b8480]" @click="router.back()">取消</button>
        <h1 class="text-[21px] font-extrabold tracking-tight text-[#12182a]">发布动态</h1>
        <button
          type="button"
          class="h-9 rounded-full bg-[#ff6b35] px-4 text-[14px] font-bold text-white shadow-sm"
          :disabled="publishing || !hasCats || !content.trim()"
          @click="publish"
        >
          {{ publishing ? '发布中' : '发布' }}
        </button>
      </header>

      <section class="mt-3 rounded-[18px] border border-[#e3e7f2] bg-white p-3.5">
        <div class="text-[14px] text-[#9a97a0]">发布身份</div>
        <div class="mt-1 flex items-center gap-2">
          <span class="text-xl">🐾</span>
          <span class="text-[15px] font-semibold text-[#12182a]">
            {{ selectedCatName }}
          </span>
        </div>
        <div v-if="!hasCats" class="mt-3 text-sm text-on-surface-variant">
          需要先添加一只猫咪档案才能发布动态。
        </div>
        <van-button v-if="!hasCats" class="mt-4" block type="primary" @click="router.push({ name: 'AddCat' })">
          去添加猫咪
        </van-button>
      </section>

      <section class="mt-3 rounded-[18px] bg-white p-3.5">
        <textarea
          v-model="content"
          class="min-h-[96px] w-full resize-none bg-transparent text-[15px] leading-relaxed text-[#12182a] outline-none placeholder:text-[#b1adb5]"
          maxlength="500"
          placeholder="分享关于猫咪的日常或是新的发现..."
        ></textarea>

        <div class="mt-2">
          <input ref="imageInputRef" type="file" accept="image/*" multiple class="hidden" @change="onPickImages" />
          <div class="grid grid-cols-3 gap-3">
            <template v-for="(slot, index) in imageSlots" :key="index">
              <button
                v-if="slot"
                type="button"
                class="relative h-[94px] overflow-hidden rounded-[14px] bg-[#eef1fb]"
                @click="removeImage(slot.id)"
              >
                <img :src="slot.previewUrl" class="h-full w-full object-cover" alt="已选择图片" />
                <span class="absolute right-1 top-1 grid h-5 w-5 place-items-center rounded-full bg-black/60 text-white">×</span>
              </button>

              <button
                v-else-if="index === imageAssets.length && imageAssets.length < MAX_IMAGES"
                type="button"
                class="grid h-[94px] place-items-center rounded-[14px] bg-[#e9ecfb] text-[#afadb0]"
                @click="openImagePicker"
              >
                <van-icon name="photo-o" size="26" />
              </button>

              <div
                v-else
                class="h-[94px] rounded-[14px] border border-dashed border-[#e1e3ea] bg-[#fafafa]"
              ></div>
            </template>
          </div>
        </div>
      </section>

      <section class="mt-4 rounded-[18px] bg-[#e9ecfb] p-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2 text-[#131b2a]">
            <span class="inline-block h-5 w-1.5 rounded-full bg-[#ff6b35]"></span>
            <span class="text-[15px] font-bold">添加猫语</span>
          </div>
          <div class="text-[12px] font-bold text-[#ff6b35]">NEW VILLAGE AI</div>
        </div>

        <div class="mt-4 grid grid-cols-2 gap-3">
          <button type="button" class="rounded-2xl bg-white py-4 text-center disabled:opacity-60" :disabled="!hasCats || audioBusy || !selectedCatId" @click="toggleRecording">
            <div class="mx-auto grid h-9 w-9 place-items-center rounded-full bg-[#fff1e8] text-[#ff6b35]">
              <van-icon :name="isRecording ? 'pause-circle-o' : 'volume-o'" size="20" />
            </div>
            <div class="mt-2 text-[14px] font-semibold text-[#3f3632]">{{ isRecording ? '停止录音' : '现场录音' }}</div>
          </button>
          <button type="button" class="rounded-2xl bg-white py-4 text-center disabled:opacity-60" :disabled="!hasCats || audioBusy || !selectedCatId" @click="openAudioPicker">
            <div class="mx-auto grid h-9 w-9 place-items-center rounded-full bg-[#fff1e8] text-[#ff6b35]">
              <van-icon name="replay" size="20" />
            </div>
            <div class="mt-2 text-[14px] font-semibold text-[#3f3632]">历史导入</div>
          </button>
        </div>

        <input ref="audioInputRef" type="file" accept="audio/*" class="hidden" @change="onPickAudioFile" />

        <div v-if="recordStatusText" class="mt-3 rounded-2xl bg-white px-3 py-3 text-[13px] text-[#5f4f48]">
          {{ recordStatusText }}
        </div>

        <div v-if="lastAudioResult" class="mt-3 rounded-2xl bg-white px-3 py-3">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-[14px] font-bold text-[#12182a]">{{ lastAudioResult.emotionTag }}</div>
              <div class="text-[12px] text-[#8d8580]">置信度 {{ Math.round(lastAudioResult.confidence * 100) }}%</div>
            </div>
            <button type="button" class="rounded-full bg-[#ff6b35] px-3 py-1 text-[12px] font-bold text-white" @click="appendEmotionToContent">
              插入文案
            </button>
          </div>
          <div class="mt-2 text-[12px] text-[#5f4f48]">{{ lastAudioResult.emotionDescription || '暂无描述' }}</div>
        </div>

        <div class="mt-3 text-[11px] text-[#b0acb1]">AI 会分析并生成配文与热词推荐，并帮你找到合适话题。</div>
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
  if (!id) {
    return '未选择猫咪';
  }
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
    error.value = '组件加载失败，请检查后端服务';
  } finally {
    loading.value = false;
  }
};

const reload = () => initData();

const openImagePicker = () => {
  imageInputRef.value?.click();
};

const openAudioPicker = () => {
  audioInputRef.value?.click();
};

const revokePreview = (url: string) => {
  if (url.startsWith('blob:')) {
    URL.revokeObjectURL(url);
  }
};

const onPickImages = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const files = Array.from(target.files || []);
  if (!files.length) {
    return;
  }

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
  if (item) {
    revokePreview(item.previewUrl);
  }
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
  if (audioBusy.value || !selectedCatId.value) {
    return;
  }

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
      if (event.data.size > 0) {
        recordingChunks.value.push(event.data);
      }
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
  if (!file) {
    return;
  }
  if (!file.type.startsWith('audio/')) {
    showToast({ type: 'fail', message: '请选择音频文件' });
    return;
  }
  await analyzeAudioBlob(file, file.name || `meow-import-${Date.now()}.webm`);
};

const appendEmotionToContent = () => {
  if (!lastAudioResult.value) {
    return;
  }
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
    if (!currentCatStore.getCurrentCatId && first) {
      currentCatStore.setCurrentCat(first.id);
    }
  }

  if (!hasCats.value || !selectedCatId.value) {
    showToast({ type: 'fail', message: '请先添加并选择一只猫咪' });
    return;
  }

  const images = imageAssets.value.map((item) => item.file);

  publishing.value = true;
  showToast({ type: 'loading', message: '正在发布...', duration: 0, forbidClick: true });
  try {
    await publishNewDynamic({
      catId: selectedCatId.value,
      content: text,
      images
    });
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
