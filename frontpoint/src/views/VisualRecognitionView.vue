<template>
  <div class="min-h-[100dvh] bg-[#f3f4fb] px-5 pt-4 pb-28">
    <header class="flex min-h-[54px] items-center justify-between">
      <button type="button" class="grid h-10 w-10 place-items-center text-[#222734]" @click="router.back()">
        <van-icon name="arrow-left" size="22" />
      </button>
      <h1 class="text-[22px] font-black text-[#202533]">视觉识别</h1>
      <div class="h-10 w-10" />
    </header>

    <!-- 功能介绍卡片 -->
    <section class="mt-5 rounded-[24px] bg-gradient-to-br from-[#ff8c42] to-[#ff6b35] p-5 text-white">
      <div class="flex items-start justify-between gap-3">
        <div>
          <h2 class="text-[34px] font-black leading-[1.06]">视觉识别</h2>
          <p class="mt-1 text-[13px] text-white/90">ViT 深度学习解析猫咪行为</p>
        </div>
        <div class="grid h-14 w-14 place-items-center rounded-2xl bg-white/20">
          <van-icon name="photo-o" size="26" color="#fff" />
        </div>
      </div>
    </section>

    <!-- 上传区域 -->
    <section class="mt-7">
      <div class="mb-3 flex items-center gap-2">
        <span class="h-6 w-1 rounded-full bg-[#ff6b35]" />
        <h3 class="text-[24px] font-black text-[#1d2333]">上传图片</h3>
      </div>

      <van-uploader
        :max-count="1"
        :preview-image="false"
        :after-read="onImageRead"
        class="w-full"
      >
        <div class="rounded-[20px] border-2 border-dashed border-[#ffc8a3] bg-[#fff7f2] p-6 text-center transition-all hover:border-[#ff6b35] hover:bg-[#ffede4]">
          <van-icon name="photograph" size="32" color="#ff6b35" />
          <div class="mt-3 text-[16px] font-bold text-[#141a2c]">点击上传猫咪照片</div>
          <p class="mt-1 text-[12px] text-[#8f94a3]">支持 JPG、PNG 格式，建议使用高清晰度照片</p>
        </div>
      </van-uploader>
    </section>

    <!-- 上传的图片预览 -->
    <section v-if="uploadedImage" class="mt-7">
      <div class="mb-3 flex items-center gap-2">
        <span class="h-6 w-1 rounded-full bg-[#ff6b35]" />
        <h3 class="text-[24px] font-black text-[#1d2333]">识别结果</h3>
      </div>

      <div class="rounded-[20px] overflow-hidden bg-white shadow-[0_6px_18px_rgba(20,27,43,0.06)]">
        <van-image :src="uploadedImage" fit="cover" width="100%" height="300" />
      </div>

      <!-- 识别进度 -->
      <div v-if="analyzing" class="mt-5 rounded-[18px] bg-white p-5 text-center">
        <van-loading size="28" color="#ff6b35" />
        <div class="mt-3 text-[14px] font-semibold text-[#141a2c]">AI 正在深度分析中...</div>
        <p class="mt-1 text-[12px] text-[#8f94a3]">正在提取面部特征和肢体体态...</p>
      </div>

      <!-- 识别结果 -->
      <div v-else-if="recognitionResult" class="mt-5 space-y-4">
        <!-- 面部微表情 -->
        <article class="rounded-[18px] border-l-4 border-[#ff6b35] bg-white px-4 py-4 shadow-[0_2px_10px_rgba(15,23,42,0.04)]">
          <div class="flex items-start justify-between">
            <div>
              <div class="text-[15px] font-bold text-[#141a2c]">面部微表情</div>
              <div class="mt-2 space-y-1">
                <p class="text-[13px] text-[#5f7790]">眼睛状态：{{ recognitionResult.facialExpression.eyes }}</p>
                <p class="text-[13px] text-[#5f7790]">耳朵位置：{{ recognitionResult.facialExpression.ears }}</p>
                <p class="text-[13px] text-[#5f7790]">嘴部开合：{{ recognitionResult.facialExpression.mouth }}</p>
              </div>
            </div>
            <div class="grid h-10 w-10 place-items-center rounded-full bg-[#fff0e8] text-[#ff6b35]">
              <van-icon name="smile-o" size="18" />
            </div>
          </div>
        </article>

        <!-- 肢体体态 -->
        <article class="rounded-[18px] border-l-4 border-[#4a90e2] bg-white px-4 py-4 shadow-[0_2px_10px_rgba(15,23,42,0.04)]">
          <div class="flex items-start justify-between">
            <div>
              <div class="text-[15px] font-bold text-[#141a2c]">肢体体态</div>
              <div class="mt-2 space-y-1">
                <p class="text-[13px] text-[#5f7790]">身体姿态：{{ recognitionResult.bodyPosture.posture }}</p>
                <p class="text-[13px] text-[#5f7790]">尾巴动作：{{ recognitionResult.bodyPosture.tail }}</p>
                <p class="text-[13px] text-[#5f7790]">放松指数：{{ recognitionResult.bodyPosture.relaxLevel }}%</p>
              </div>
            </div>
            <div class="grid h-10 w-10 place-items-center rounded-full bg-[#f0f8ff] text-[#4a90e2]">
              <van-icon name="gem-o" size="18" />
            </div>
          </div>
        </article>

        <!-- 行为分析 -->
        <article class="rounded-[18px] border-l-4 border-[#4fb233] bg-white px-4 py-4 shadow-[0_2px_10px_rgba(15,23,42,0.04)]">
          <div class="flex items-start justify-between">
            <div>
              <div class="text-[15px] font-bold text-[#141a2c]">行为分析</div>
              <p class="mt-2 text-[13px] leading-relaxed text-[#5f7790]">{{ recognitionResult.behaviorAnalysis }}</p>
            </div>
            <div class="grid h-10 w-10 place-items-center rounded-full bg-[#f0fff0] text-[#4fb233]">
              <van-icon name="video-o" size="18" />
            </div>
          </div>
        </article>

        <!-- 情绪评分 -->
        <article class="rounded-[18px] bg-gradient-to-br from-[#ff8d2a] to-[#ff6b35] p-4 text-white">
          <div class="flex items-center justify-between">
            <div>
              <div class="text-[16px] font-bold">情绪评分</div>
              <p class="mt-1 text-[13px] text-white/90">{{ recognitionResult.emotionScore }}/100</p>
            </div>
            <div class="text-right">
              <div class="text-[28px] font-black">{{ recognitionResult.emotionLabel }}</div>
              <p class="mt-1 text-[12px] text-white/90" v-if="recognitionResult.emotionScore >= 75">状态良好</p>
              <p class="mt-1 text-[12px] text-white/90" v-else-if="recognitionResult.emotionScore >= 50">状态一般</p>
              <p class="mt-1 text-[12px] text-white/90" v-else>需关注</p>
            </div>
          </div>
        </article>

        <!-- 重新分析按钮 -->
        <button
          type="button"
          class="mt-4 h-10 w-full rounded-[12px] border border-[#ff6b35] bg-white text-[14px] font-bold text-[#ff6b35] transition-all hover:bg-[#fff7f2]"
          @click="resetAnalysis"
        >
          重新分析
        </button>
      </div>
    </section>

    <!-- 技术特点 -->
    <section v-if="!uploadedImage" class="mt-7">
      <div class="mb-3 flex items-center gap-2">
        <span class="h-6 w-1 rounded-full bg-[#ff6b35]" />
        <h3 class="text-[24px] font-black text-[#1d2333]">识别能力</h3>
      </div>

      <div class="space-y-3">
        <!-- 面部微表情识别 -->
        <article class="rounded-[20px] bg-gradient-to-br from-[#fff0e8] to-[#fff7f0] p-4">
          <div class="flex gap-3">
            <div class="grid h-12 w-12 place-items-center rounded-full bg-white text-[#ff6b35] shadow-[0_2px_8px_rgba(255,107,53,0.12)]">
              <van-icon name="smile-o" size="20" />
            </div>
            <div class="min-w-0 flex-1">
              <div class="text-[16px] font-bold text-[#141a2c]">面部微表情识别</div>
              <p class="mt-1 text-[13px] leading-relaxed text-[#5f7790]">毫秒级解析眼睛、耳朵、嘴角等细微变化，捕捉猫咪的真实情绪</p>
            </div>
          </div>
        </article>

        <!-- 肢体体态分析 -->
        <article class="rounded-[20px] bg-gradient-to-br from-[#f0f8ff] to-[#f5faff] p-4">
          <div class="flex gap-3">
            <div class="grid h-12 w-12 place-items-center rounded-full bg-white text-[#4a90e2] shadow-[0_2px_8px_rgba(74,144,226,0.12)]">
              <van-icon name="gem-o" size="20" />
            </div>
            <div class="min-w-0 flex-1">
              <div class="text-[16px] font-bold text-[#141a2c]">肢体体态分析</div>
              <p class="mt-1 text-[13px] leading-relaxed text-[#5f7790]">识别坐、卧、站等姿态，以及尾巴、胡须的动作，判断警惕度与放松程度</p>
            </div>
          </div>
        </article>

        <!-- 行为拍摄 -->
        <article class="rounded-[20px] bg-gradient-to-br from-[#f0fff0] to-[#f5fff5] p-4">
          <div class="flex gap-3">
            <div class="grid h-12 w-12 place-items-center rounded-full bg-white text-[#4fb233] shadow-[0_2px_8px_rgba(79,178,51,0.12)]">
              <van-icon name="video-o" size="20" />
            </div>
            <div class="min-w-0 flex-1">
              <div class="text-[16px] font-bold text-[#141a2c]">视频行为拍摄</div>
              <p class="mt-1 text-[13px] leading-relaxed text-[#5f7790]">支持上传猫咪照片或视频，AI 自动检测与建档，形成每只猫的行为基线数据库</p>
            </div>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';
import type { UploaderFileListItem } from 'vant';

const router = useRouter();

const uploadedImage = ref<string>('');
const analyzing = ref(false);

interface RecognitionResult {
  facialExpression: { eyes: string; ears: string; mouth: string };
  bodyPosture: { posture: string; tail: string; relaxLevel: number };
  behaviorAnalysis: string;
  emotionScore: number;
  emotionLabel: string;
}

const recognitionResult = ref<RecognitionResult | null>(null);

const mockResults: RecognitionResult[] = [
  {
    facialExpression: { eyes: '警惕，瞳孔缩小', ears: '竖起，指向前方', mouth: '微张，呼吸加快' },
    bodyPosture: { posture: '蜷缩坐姿', tail: '卷在身下，偶尔抽动', relaxLevel: 35 },
    behaviorAnalysis: '猫咪处于警惕状态，可能受到惊吓或环境变化影响。建议保持安静环境，给予猫咪安全感。',
    emotionScore: 42,
    emotionLabel: '警惕'
  },
  {
    facialExpression: { eyes: '柔和，瞳孔适中', ears: '自然竖立', mouth: '正常，偶有舔舐' },
    bodyPosture: { posture: '舒适卧姿', tail: '缓慢摆动', relaxLevel: 78 },
    behaviorAnalysis: '猫咪状态放松，处于满足与享受阶段。这是健康的休息状态，说明猫咪对环境很满意。',
    emotionScore: 82,
    emotionLabel: '愉快'
  },
  {
    facialExpression: { eyes: '明亮有神，瞳孔扩张', ears: '转向声源', mouth: '微张，振须' },
    bodyPosture: { posture: '站立或弓形身体', tail: '竖起或快速摆动', relaxLevel: 65 },
    behaviorAnalysis: '猫咪处于活跃兴奋状态，可能是发现了猎物或对某事物感兴趣。这是正常的狩猎本能表现。',
    emotionScore: 71,
    emotionLabel: '兴奋'
  },
  {
    facialExpression: { eyes: '半闭，眯起', ears: '自然放松', mouth: '轻闭，舌头可见' },
    bodyPosture: { posture: '蜷缩球形', tail: '环绕身体', relaxLevel: 88 },
    behaviorAnalysis: '猫咪处于极度放松状态，可能在享受按摩或温暖。这个姿势表示完全信任与安心。',
    emotionScore: 89,
    emotionLabel: '舒适'
  }
];

const onImageRead = async (file: UploaderFileListItem | UploaderFileListItem[]) => {
  const fileItem = Array.isArray(file) ? file[0] : file;
  if (!fileItem) {
    return;
  }

  if (typeof fileItem.content === 'string') {
    uploadedImage.value = fileItem.content;
    recognitionResult.value = null;
    
    // 模拟 AI 分析过程
    analyzing.value = true;
    showToast({ type: 'loading', message: '正在分析猫咪表情...', duration: 0, forbidClick: true });
    
    // 延迟 1.5-2.5 秒以模拟分析过程
    setTimeout(() => {
      const randomIndex = Math.floor(Math.random() * mockResults.length);
      const result = mockResults[randomIndex];
      recognitionResult.value = result as RecognitionResult;
      analyzing.value = false;
      showToast({ type: 'success', message: '分析完成！', duration: 2 });
    }, 1500 + Math.random() * 1000);
  }
};

const resetAnalysis = () => {
  uploadedImage.value = '';
  recognitionResult.value = null;
};
</script>

<style scoped>
/* 自定义上传器样式 */
:deep(.van-uploader) {
  width: 100%;
}
</style>
