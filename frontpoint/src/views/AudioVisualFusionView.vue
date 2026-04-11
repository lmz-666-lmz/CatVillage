<template>
  <div class="min-h-[100dvh] bg-[#f3f4fb] px-5 pt-4 pb-28">
    <header class="flex min-h-[54px] items-center justify-between">
      <button type="button" class="grid h-10 w-10 place-items-center text-[#222734]" @click="router.back()">
        <van-icon name="arrow-left" size="22" />
      </button>
      <h1 class="text-[22px] font-black text-[#202533]">视听融合</h1>
      <button type="button" class="grid h-10 w-10 place-items-center text-[#222734]" @click="showCatSheet = true">
        <van-icon name="exchange" size="22" />
      </button>
    </header>

    <!-- 功能介绍卡片 -->
    <section class="mt-5 rounded-[24px] bg-gradient-to-br from-[#667eea] to-[#764ba2] p-5 text-white">
      <div class="flex items-start justify-between gap-3">
        <div>
          <h2 class="text-[34px] font-black leading-[1.06]">视听融合</h2>
          <p class="mt-1 text-[13px] text-white/90">多模态 AI 深度学习融合</p>
          <p v-if="selectedCatName" class="mt-2 text-[12px] text-white/80">当前猫咪：{{ selectedCatName }}</p>
        </div>
        <div class="grid h-14 w-14 place-items-center rounded-2xl bg-white/22 shadow-[0_8px_20px_rgba(24,31,52,0.12)]">
          <span class="text-[18px] leading-none">🐱</span>
        </div>
      </div>
    </section>

    <!-- 实时分析区域 -->
    <section class="mt-7">
      <div class="mb-3 flex items-center gap-2">
        <span class="h-6 w-1 rounded-full bg-[#764ba2]" />
        <h3 class="text-[24px] font-black text-[#1d2333]">实时分析演示</h3>
      </div>

      <!-- 分析面板 -->
      <div class="rounded-[20px] bg-gradient-to-br from-[#f0edff] to-[#f7f5ff] p-5 shadow-[0_6px_18px_rgba(20,27,43,0.06)]">
        <!-- 音频和视觉输入指示器 -->
        <div class="grid grid-cols-2 gap-3">
          <div class="relative rounded-[14px] bg-white p-4 text-center">
            <div class="absolute top-3 right-3 h-8 w-8 rounded-full bg-[#667eea] flex items-center justify-center text-white text-sm font-bold">
              📷
            </div>
            <van-icon name="photo" size="32" color="#667eea" />
            <p class="mt-3 text-[12px] font-bold text-[#141a2c]">视觉特征</p>
            <p class="mt-1 text-[10px] text-[#8f94a3]">图像识别接口</p>
          </div>
          <div class="relative rounded-[14px] bg-white p-4 text-center">
            <div class="absolute top-3 right-3 h-8 w-8 rounded-full bg-[#764ba2] flex items-center justify-center text-white text-sm font-bold">
              🔊
            </div>
            <van-icon name="volume" size="32" color="#764ba2" />
            <p class="mt-3 text-[12px] font-bold text-[#141a2c]">音频特征</p>
            <p class="mt-1 text-[10px] text-[#8f94a3]">MFCC 提取</p>
          </div>
        </div>

        <!-- 融合过程可视化 -->
        <div class="mt-4 rounded-[12px] bg-white p-3">
          <p class="text-[12px] font-bold text-[#141a2c]">融合进度</p>
          <div class="mt-2 space-y-2">
            <div>
              <p class="text-[11px] text-[#5f7790]">特征对齐中...</p>
              <div class="mt-1 h-2 overflow-hidden rounded-full bg-[#e8eaf3]">
                <div class="h-full rounded-full bg-[#667eea] transition-all duration-500" :style="{ width: fusionProgress[0] + '%' }"></div>
              </div>
            </div>
            <div>
              <p class="text-[11px] text-[#5f7790]">注意力融合中...</p>
              <div class="mt-1 h-2 overflow-hidden rounded-full bg-[#e8eaf3]">
                <div class="h-full rounded-full bg-[#764ba2] transition-all duration-500" :style="{ width: fusionProgress[1] + '%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- 分析按钮 -->
        <button
          v-if="!isAnalyzing"
          type="button"
          class="mt-4 h-10 w-full rounded-[12px] bg-gradient-to-r from-[#667eea] to-[#764ba2] text-[14px] font-bold text-white transition-all active:scale-95"
          @click="startAnalysis"
        >
          开始分析
        </button>
        <div v-else class="mt-4 flex items-center justify-center gap-2 rounded-[12px] bg-white p-3">
          <van-loading size="20" color="#667eea" />
          <span class="text-[14px] font-bold text-[#667eea]">分析中...</span>
        </div>
      </div>
    </section>

    <!-- 分析结果 -->
    <section v-if="analysisResult" class="mt-7">
      <div class="mb-3 flex items-center gap-2">
        <span class="h-6 w-1 rounded-full bg-[#667eea]" />
        <h3 class="text-[24px] font-black text-[#1d2333]">情绪标签</h3>
      </div>

      <div class="space-y-2">
        <!-- 当前主要情绪 -->
        <article class="rounded-[18px] border-l-4 border-[#667eea] bg-white px-4 py-3 shadow-[0_2px_10px_rgba(15,23,42,0.04)]">
          <div class="flex items-start justify-between">
            <div>
              <div class="text-[16px] font-bold text-[#141a2c]">{{ analysisResult.primaryEmotion.label }}</div>
              <p class="mt-1 text-[12px] text-[#8f94a3]">{{ analysisResult.primaryEmotion.description }}</p>
              <div class="mt-2 flex items-center gap-2">
                <div class="h-2 w-32 overflow-hidden rounded-full bg-[#e8eaf3]">
                  <div class="h-full rounded-full bg-[#667eea]" :style="{ width: analysisResult.primaryEmotion.confidence + '%' }"></div>
                </div>
                <span class="text-[11px] font-bold text-[#667eea]">{{ analysisResult.primaryEmotion.confidence }}%</span>
              </div>
            </div>
            <div class="grid h-8 w-8 place-items-center rounded-full bg-[#f0edff] text-[#667eea]">
              <van-icon name="check" size="16" />
            </div>
          </div>
        </article>

        <!-- 其他情绪维度 -->
        <article
          v-for="item in analysisResult.otherEmotions"
          :key="item.label"
          class="rounded-[18px] border-l-4 bg-white px-4 py-3 shadow-[0_2px_10px_rgba(15,23,42,0.04)]"
          :style="{ borderLeftColor: item.color }"
        >
          <div class="flex items-start justify-between">
            <div>
              <div class="text-[14px] font-bold text-[#141a2c]">{{ item.label }}</div>
              <p class="mt-1 text-[12px] text-[#8f94a3]">{{ item.description }}</p>
              <div class="mt-2 flex items-center gap-2">
                <div class="h-1.5 w-24 overflow-hidden rounded-full bg-[#e8eaf3]">
                  <div class="h-full rounded-full transition-all duration-500" :style="{ width: item.confidence + '%', backgroundColor: item.color }"></div>
                </div>
                <span class="text-[10px] font-bold" :style="{ color: item.color }">{{ item.confidence }}%</span>
              </div>
            </div>
          </div>
        </article>
      </div>

      <!-- 融合过程详解 -->
      <article class="mt-5 rounded-[18px] bg-gradient-to-br from-[#f0edff] to-[#f7f5ff] p-5">
        <h4 class="text-[15px] font-bold text-[#141a2c]">融合过程</h4>
        <div class="mt-3 space-y-2">
          <div v-for="(step, idx) in analysisResult.fusionSteps" :key="idx" class="flex gap-2">
            <div class="grid h-6 w-6 flex-shrink-0 place-items-center rounded-full bg-[#667eea] text-[11px] font-bold text-white">
              {{ idx + 1 }}
            </div>
            <div class="min-w-0 flex-1">
              <p class="text-[12px] font-semibold text-[#141a2c]">{{ step.name }}</p>
              <p class="mt-0.5 text-[11px] text-[#8f94a3]">{{ step.detail }}</p>
            </div>
          </div>
        </div>
      </article>

      <!-- 重新分析按钮 -->
      <button
        type="button"
        class="mt-5 h-10 w-full rounded-[12px] border border-[#667eea] bg-white text-[14px] font-bold text-[#667eea] transition-all hover:bg-[#f0edff]"
        @click="resetAnalysis"
      >
        重新分析
      </button>
    </section>

    <!-- 核心原理 -->
    <section v-if="!analysisResult" class="mt-7">
      <div class="mb-3 flex items-center gap-2">
        <span class="h-6 w-1 rounded-full bg-[#764ba2]" />
        <h3 class="text-[24px] font-black text-[#1d2333]">融合机制</h3>
      </div>

      <article class="rounded-[20px] bg-gradient-to-br from-[#f0edff] to-[#f7f5ff] p-4">
        <div class="flex gap-3">
          <div class="grid h-14 w-14 place-items-center rounded-full bg-gradient-to-br from-[#667eea] to-[#764ba2] text-white shadow-[0_4px_12px_rgba(102,126,234,0.2)]">
            <van-icon name="cluster-o" size="22" />
          </div>
          <div class="min-w-0 flex-1">
            <div class="text-[16px] font-bold text-[#141a2c]">注意力机制融合</div>
            <p class="mt-2 text-[13px] leading-relaxed text-[#5f7790]">通过注意力机制，将视觉特征（表情、姿态）与音频特征（叫声）在特征空间完全融合，消除信息孤岛</p>
          </div>
        </div>
      </article>
    </section>

    <!-- 工作流程 -->
    <section v-if="!analysisResult" class="mt-7">
      <div class="mb-3 flex items-center gap-2">
        <span class="h-6 w-1 rounded-full bg-[#8f94a3]" />
        <h3 class="text-[24px] font-black text-[#1d2333]">分析流程</h3>
      </div>

      <div class="space-y-2">
        <div class="flex gap-3">
          <div class="flex flex-col items-center gap-2">
            <div class="grid h-9 w-9 place-items-center rounded-full bg-[#667eea] text-white text-[12px] font-bold">1</div>
            <div class="h-4 w-0.5 bg-[#dde3f2]" />
          </div>
          <div class="flex-1 rounded-[14px] bg-white px-3 py-3">
            <div class="text-[14px] font-bold text-[#141a2c]">视觉提取</div>
            <p class="mt-1 text-[12px] text-[#8f94a3]">ViT 图像编码器提取 2048 维视觉特征</p>
          </div>
        </div>

        <div class="flex gap-3">
          <div class="flex flex-col items-center gap-2">
            <div class="grid h-9 w-9 place-items-center rounded-full bg-[#667eea] text-white text-[12px] font-bold">2</div>
            <div class="h-4 w-0.5 bg-[#dde3f2]" />
          </div>
          <div class="flex-1 rounded-[14px] bg-white px-3 py-3">
            <div class="text-[14px] font-bold text-[#141a2c]">音频提取</div>
            <p class="mt-1 text-[12px] text-[#8f94a3]">MelSpectrogram + MFCC 提取音频特征</p>
          </div>
        </div>

        <div class="flex gap-3">
          <div class="flex flex-col items-center gap-2">
            <div class="grid h-9 w-9 place-items-center rounded-full bg-[#667eea] text-white text-[12px] font-bold">3</div>
            <div class="h-4 w-0.5 bg-[#dde3f2]" />
          </div>
          <div class="flex-1 rounded-[14px] bg-white px-3 py-3">
            <div class="text-[14px] font-bold text-[#141a2c]">特征融合</div>
            <p class="mt-1 text-[12px] text-[#8f94a3]">Cross-Modal Attention 跨模态融合</p>
          </div>
        </div>

        <div class="flex gap-3">
          <div class="flex flex-col items-center">
            <div class="grid h-9 w-9 place-items-center rounded-full bg-[#667eea] text-white text-[12px] font-bold">4</div>
          </div>
          <div class="flex-1 rounded-[14px] bg-white px-3 py-3">
            <div class="text-[14px] font-bold text-[#141a2c]">情绪分类</div>
            <p class="mt-1 text-[12px] text-[#8f94a3]">输出精准的综合情绪标签与置信度</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 猫咪切换弹窗 -->
    <van-action-sheet v-model:show="showCatSheet" title="选择猫咪">
      <div class="p-4">
        <div class="mb-3 text-xs text-on-surface-variant">当前：{{ selectedCatName || '未选择' }}</div>
        <div class="space-y-2">
          <button
            v-for="cat in catList"
            :key="cat.id"
            type="button"
            class="flex w-full items-center justify-between rounded-xl px-3 py-3"
            :class="cat.id === selectedCatId ? 'bg-purple-100 text-purple-600' : 'bg-surface-container-low text-on-background'"
            @click="selectCat(cat)"
          >
            <span class="text-sm font-semibold">{{ cat.name }}</span>
            <van-icon v-if="cat.id === selectedCatId" name="success" />
          </button>
        </div>
      </div>
    </van-action-sheet>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';
import { useCatsStore } from '@/stores';

const router = useRouter();
const catsStore = useCatsStore();

const isAnalyzing = ref(false);
const fusionProgress = reactive([0, 0]);
const showCatSheet = ref(false);
const selectedCatId = ref<string>('');

interface EmotionItem {
  label: string;
  description: string;
  confidence: number;
  color: string;
}

interface AnalysisResult {
  primaryEmotion: { label: string; description: string; confidence: number };
  otherEmotions: EmotionItem[];
  fusionSteps: Array<{ name: string; detail: string }>;
}

const analysisResult = ref<AnalysisResult | null>(null);

const catList = computed(() => catsStore.getAllCats || []);

const selectedCatName = computed(() => {
  if (!selectedCatId.value) return '';
  const cat = catsStore.getCatById(selectedCatId.value);
  return cat ? cat.name : '';
});

const mockResults: AnalysisResult[] = [
  {
    primaryEmotion: { label: '平静舒适', description: '轻松的呼吸声 × 放松的眼神 融合', confidence: 95 },
    otherEmotions: [
      { label: '警惕紧张', description: '频繁的耳朵转动特征检测', confidence: 22, color: '#ffa500' },
      { label: '不适焦虑', description: '声音尖锐度分析', confidence: 15, color: '#ff6b6b' },
      { label: '愉快兴奋', description: '呼噜声和蜷缩姿态', confidence: 78, color: '#4fb233' }
    ],
    fusionSteps: [
      { name: '视觉编码', detail: '从面部图像提取 2048 维视觉特征向量' },
      { name: '音频编码', detail: '从叫声提取 MFCC 系数和频谱特征' },
      { name: 'Attention 融合', detail: '多头自注意力机制跨模态对齐' },
      { name: '情绪分类', detail: '融合向量通过分类器实时输出情绪概率' }
    ]
  },
  {
    primaryEmotion: { label: '警惕紧张', description: '尖锐的叫声 × 竖起的耳朵 融合', confidence: 78 },
    otherEmotions: [
      { label: '平静舒适', description: '缓慢的眨眼动作', confidence: 12, color: '#667eea' },
      { label: '不适焦虑', description: '身体抖动和躲避信号', confidence: 65, color: '#ff6b6b' },
      { label: '愉快兴奋', description: '狩猎本能被激发', confidence: 45, color: '#4fb233' }
    ],
    fusionSteps: [
      { name: '视觉编码', detail: '检测瞳孔缩小和耳朵竖立的姿态' },
      { name: '音频编码', detail: '分析高频率叫声频率和振幅' },
      { name: 'Attention 融合', detail: '聚焦警惕相关特征的交叉关联' },
      { name: '情绪分类', detail: '综合判定为警怖发出警告信号' }
    ]
  },
  {
    primaryEmotion: { label: '愉快兴奋', description: '呼噜声 × 蜷缩姿态 融合', confidence: 92 },
    otherEmotions: [
      { label: '平静舒适', description: '缓慢眨眼和放松表情', confidence: 88, color: '#667eea' },
      { label: '警惕紧张', description: '偶发的环境响应', confidence: 18, color: '#ffa500' },
      { label: '不适焦虑', description: '无相关特征检测', confidence: 5, color: '#ff6b6b' }
    ],
    fusionSteps: [
      { name: '视觉编码', detail: '识别柔软蜷缩姿态和缓慢眨眼' },
      { name: '音频编码', detail: '检测连续呼噜声频率约 25Hz' },
      { name: 'Attention 融合', detail: '多头注意力加权组合视听信号' },
      { name: '情绪分类', detail: '高置信度判定为极度满足状态' }
    ]
  },
  {
    primaryEmotion: { label: '不适焦虑', description: '刺耳噪音 × 躲避行为 融合', confidence: 81 },
    otherEmotions: [
      { label: '平静舒适', description: '缺乏放松信号', confidence: 8, color: '#667eea' },
      { label: '警惕紧张', description: '升级为焦虑的被动防御状态', confidence: 62, color: '#ffa500' },
      { label: '愉快兴奋', description: '无正面情绪迹象', confidence: 10, color: '#4fb233' }
    ],
    fusionSteps: [
      { name: '视觉编码', detail: '捕捉身体蜷缩和躲藏行为模式' },
      { name: '音频编码', detail: '分析战栗声和低沉的鸣叫' },
      { name: 'Attention 融合', detail: '强调防御相关的跨模态对齐' },
      { name: '情绪分类', detail: '判定为需要立即关注的焦虑状态' }
    ]
  }
];

const startAnalysis = () => {
  isAnalyzing.value = true;
  analysisResult.value = null;
  
  showToast({ type: 'loading', message: '正在融合视听特征...', duration: 0, forbidClick: true });
  
  // 模拟融合进度
  let progress1 = 0;
  let progress2 = 0;
  
  const progressInterval = setInterval(() => {
    progress1 = Math.min(100, progress1 + Math.random() * 35);
    progress2 = Math.min(100, progress2 + Math.random() * 30);
    
    fusionProgress[0] = Math.floor(progress1);
    fusionProgress[1] = Math.floor(progress2);
    
    if (progress1 >= 100 && progress2 >= 100) {
      clearInterval(progressInterval);
      
      // 延迟后显示结果
      setTimeout(() => {
        const randomIndex = Math.floor(Math.random() * mockResults.length);
        const result = mockResults[randomIndex];
        analysisResult.value = result as AnalysisResult;
        isAnalyzing.value = false;
        showToast({ type: 'success', message: '融合分析完成！', duration: 2 });
      }, 500);
    }
  }, 300);
  
  // 防止无限循环的超时
  setTimeout(() => {
    if (isAnalyzing.value) {
      clearInterval(progressInterval);
      const randomIndex = Math.floor(Math.random() * mockResults.length);
      const result = mockResults[randomIndex];
      analysisResult.value = result as AnalysisResult;
      isAnalyzing.value = false;
      showToast({ type: 'success', message: '融合分析完成！', duration: 2 });
    }
  }, 3000);
};

const resetAnalysis = () => {
  analysisResult.value = null;
  fusionProgress[0] = 0;
  fusionProgress[1] = 0;
};

const selectCat = (cat: any) => {
  selectedCatId.value = cat.id;
  showCatSheet.value = false;
  showToast({ type: 'success', message: `已切换至 ${cat.name}`, duration: 1.5 });
};

// 初始化时选择第一只猫
if (catList.value.length > 0 && !selectedCatId.value) {
  selectedCatId.value = catList.value[0]?.id || '';
}
</script>

<style scoped>
/* 进度条动画 */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
