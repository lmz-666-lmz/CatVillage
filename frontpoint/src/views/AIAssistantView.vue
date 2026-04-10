<template>
  <div class="min-h-screen bg-[#f8f9fc] pb-[100px] flex flex-col font-sans relative">
    <!-- Header -->
    <header class="flex items-center justify-between px-4 py-3 bg-[#f8f9fc] sticky top-0 z-50">
      <div class="w-6 flex justify-start">
        <van-icon name="arrow-left" size="20" class="text-gray-800 font-bold" @click="handleBack" />
      </div>
      <h1 class="text-[18px] font-bold text-gray-900 tracking-wide">AI 助理</h1>
      <button class="text-[12px] font-semibold text-[#b92c0b]" @click="handleClearHistory">清空</button>
    </header>

    <main class="flex-1 px-4 pt-4 pb-4">
      <!-- Pet Info Card -->
      <section class="mb-6 rounded-[18px] border border-gray-50 bg-white p-4 shadow-[0_2px_12px_rgba(0,0,0,0.03)]">
        <button type="button" class="flex w-full items-start justify-between text-left" @click="openCatArchive">
          <div class="flex items-center gap-3">
            <div class="w-[56px] h-[56px] rounded-full overflow-hidden border-[2.5px] border-[#ff6b35]">
              <img :src="petInfo.avatar" class="w-full h-full object-cover" />
            </div>
            <div class="flex flex-col justify-center">
              <div class="flex items-center gap-2">
                <h2 class="text-[17px] font-bold text-gray-900 leading-tight">{{ petInfo.name }}</h2>
                <span class="rounded-full bg-[#eef2ff] px-2 py-0.5 text-[11px] font-semibold text-[#4f64a6]">点进档案</span>
              </div>
              <div class="flex items-center gap-1.5 mt-1">
                <span class="w-1.5 h-1.5 rounded-full bg-[#10b981]"></span>
                <span class="text-[12px] text-gray-600 font-medium tracking-wide">健康状态：{{ petInfo.status }}</span>
              </div>
            </div>
          </div>
          <div class="bg-[#fff5f2] rounded-xl px-2.5 py-1.5 flex flex-col items-center justify-center min-w-[48px]">
            <span class="text-[#b92c0b] text-[20px] font-extrabold leading-none mb-0.5">{{ petInfo.score }}</span>
            <span class="text-[#ff8a6a] text-[10px] font-bold tracking-widest scale-90 transform origin-center">健康分</span>
          </div>
        </button>

        <div class="mt-3 flex items-center justify-between border-t border-gray-100/80 pt-3.5 text-[13px]">
          <button type="button" class="flex items-center gap-2 text-gray-600" @click="openCatSwitcher">
            <van-icon name="exchange" class="text-[#ff4e2a]" />
            <span>切换猫咪</span>
          </button>
          <button type="button" class="flex items-center gap-1 text-[#ff4e2a]" @click="openCatArchive">
            <span>查看详细报告</span>
            <van-icon name="arrow" />
          </button>
        </div>
      </section>

      <!-- Chat Area -->
      <section class="space-y-5 mb-8">
        <div
          v-for="msg in messages"
          :key="msg.id"
          :class="msg.role === 'user' ? 'flex gap-3 justify-end items-end' : 'flex gap-3'"
        >
          <template v-if="msg.role !== 'user'">
            <div class="flex-shrink-0 w-9 h-9 rounded-full bg-[#ff6b35] flex items-center justify-center text-white shadow-sm mt-0.5">
              <van-icon name="service" size="20" />
            </div>
            <div v-if="msg.type === 'consult_card'" class="max-w-[84%] rounded-tr-2xl rounded-bl-2xl rounded-br-2xl border border-[#ffd9c8] bg-[linear-gradient(135deg,#fff5ef_0%,#fffaf7_100%)] px-4 py-3.5 shadow-[0_8px_20px_rgba(255,107,53,0.10)]">
              <div class="flex items-center gap-2">
                <span class="inline-flex rounded-full bg-[#ff6b35] px-2.5 py-1 text-[11px] font-bold tracking-wide text-white">AI 养猫助手</span>
                <span class="text-[11px] text-[#8e5f4f]">已为你准备好</span>
              </div>
              <p class="mt-2 text-[14px] leading-[1.7] text-[#6a4b40] whitespace-pre-line">{{ msg.content }}</p>
              <button
                type="button"
                class="mt-3 rounded-full bg-[#ff6b35] px-4 py-1.5 text-[12px] font-bold text-white"
                @click="focusConsultInput"
              >
                去下方输入咨询
              </button>
            </div>

            <div v-else class="max-w-[84%] bg-[#eef2ff] border border-[#dde5ff] rounded-tr-2xl rounded-bl-2xl rounded-br-2xl px-4 py-3.5 shadow-[0_6px_16px_rgba(87,105,177,0.08)]">
              <div class="mb-2 flex items-center gap-2">
                <span class="rounded-full bg-[#dce5ff] px-2.5 py-1 text-[11px] font-bold tracking-wide text-[#3550a1]">AI 分析</span>
                <span class="text-[11px] text-[#6a769d]">结构化建议</span>
              </div>
              <div class="space-y-2.5">
                <div
                  v-for="(section, sectionIndex) in buildAssistantSections(msg.content)"
                  :key="`${msg.id}-section-${sectionIndex}`"
                  class="rounded-xl bg-white/85 border border-[#d7e1ff] px-3 py-2.5"
                >
                  <h4 class="text-[12px] font-bold text-[#2f3a64] mb-1">{{ section.title }}</h4>
                  <p
                    class="text-[14px] text-gray-800 leading-[1.75] whitespace-pre-line break-words"
                    v-html="highlightKeywords(section.content)"
                  ></p>
                </div>
              </div>
            </div>
          </template>

          <template v-else>
            <div class="bg-[#ff6b35] rounded-tl-[20px] rounded-bl-[20px] rounded-br-[4px] rounded-tr-[20px] px-4 py-3 text-[14px] text-white leading-[1.6] max-w-[80%] shadow-sm">
              {{ msg.content }}
            </div>
            <div class="flex-shrink-0 w-9 h-9 rounded-full bg-[#dee2f1] flex items-center justify-center text-gray-500 mb-0.5">
              <van-icon name="contact" size="22" />
            </div>
          </template>
        </div>

        <div v-if="sending" class="flex gap-3">
          <div class="flex-shrink-0 w-9 h-9 rounded-full bg-[#ff6b35] flex items-center justify-center text-white shadow-sm mt-0.5">
            <van-icon name="service" size="20" />
          </div>
          <div class="bg-[#f0f3ff] rounded-tr-2xl rounded-bl-2xl rounded-br-2xl px-4 py-3 text-[14px] text-gray-600 leading-[1.6] max-w-[80%]">
            AI 正在思考中...
          </div>
        </div>
      </section>

      <!-- Grid Cards -->
      <section class="grid grid-cols-2 gap-3 mb-4">
        <div 
          v-for="(item, index) in actionCards" 
          :key="index" 
          class="bg-white rounded-[20px] py-5 px-2 flex flex-col items-center justify-center gap-3 shadow-[0_2px_8px_rgba(0,0,0,0.02)] active:scale-95 transition-transform"
          @click="handleActionClick(item)"
        >
          <!-- Icon circle container -->
          <div :class="['w-[44px] h-[44px] rounded-full flex items-center justify-center', item.bgClass]">
            <van-icon :name="item.icon" size="24" :class="item.colorClass" />
          </div>
          <span class="text-[14px] font-bold text-gray-900">{{ item.name }}</span>
        </div>
      </section>
      
    </main>

    <!-- Bottom Input Area (Fixed above bottom tabs) -->
    <div class="fixed bottom-16 left-0 right-0 w-full bg-white/95 backdrop-blur-md px-4 py-3 z-40 border-t border-gray-50 pb-safe">
      <div class="bg-[#edf0f9] rounded-full flex items-center px-4 py-2.5 gap-2 shadow-inner">
        <van-icon name="volume-o" size="24" class="text-gray-700 font-bold active:scale-90 transition-transform cursor-pointer" />
        <input
          ref="consultInputRef"
          v-model="inputText"
          @keyup.enter="handleSend"
          type="text" 
          placeholder="咨询你的 AI 宠物助手..." 
          class="flex-1 bg-transparent border-none text-[15px] outline-none text-gray-800 placeholder-gray-500 min-w-0" 
        />
        <button
          class="text-[#b92c0b] font-bold text-[15px] px-2 active:opacity-70 transition-opacity tracking-wider flex-shrink-0 disabled:opacity-40"
          @click="handleSend"
          :disabled="sending || !inputText.trim()"
        >
          发送
        </button>
      </div>
    </div>
    <van-action-sheet v-model:show="showCatSheet" title="切换猫咪">
      <div class="p-4">
        <div class="mb-3 text-xs text-gray-500">选择后会同步切换 AI 助理所服务的猫咪</div>
        <div class="space-y-2">
          <button
            v-for="cat in cats"
            :key="cat.id"
            type="button"
            class="flex w-full items-center justify-between rounded-xl px-3 py-3"
            :class="cat.id === selectedCat?.id ? 'bg-orange-50 text-orange-600' : 'bg-[#f5f7ff] text-[#1f2937]'"
            @click="selectCat(cat.id)"
          >
            <span class="text-sm font-semibold">{{ cat.name }} · {{ cat.breed || '未填写品种' }}</span>
            <van-icon v-if="cat.id === selectedCat?.id" name="success" />
          </button>
        </div>
      </div>
    </van-action-sheet>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, nextTick, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';
import { useAIAssistant } from '@/composables/useAIAssistant';
import { useCatsStore, useCurrentCatStore } from '@/stores';

const router = useRouter();
const catsStore = useCatsStore();
const currentCatStore = useCurrentCatStore();
const { sendMessageToAI, fetchChatHistory, clearCurrentSession, getCurrentChatHistory, isLoading } = useAIAssistant();

interface ChatItem {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  type?: 'default' | 'consult_card';
}

const inputText = ref('');
const consultInputRef = ref<HTMLInputElement | null>(null);
const showCatSheet = ref(false);
const sending = computed(() => isLoading.value);
const messages = ref<ChatItem[]>([
  {
    id: 'default-1',
    role: 'assistant',
    content: '你好！我是你的 AI 宠物管家。大橘今天的胃口看起来不错，建议下午可以加餐一点冻干。有什么我可以帮你的吗？'
  },
  {
    id: 'default-2',
    role: 'user',
    content: '大橘最近总是挠耳朵，是怎么回事？'
  },
  {
    id: 'default-3',
    role: 'assistant',
    content: '频繁挠耳朵可能是耳螨或者过敏。建议检查一下内耳是否有黑色分泌物。你可以点击下方的 AI 医生进行快速诊断。'
  }
]);

const welcomeMessage: ChatItem[] = [
  {
    id: 'welcome-1',
    role: 'assistant',
    content: '你好！我是你的 AI 宠物管家。有什么我可以帮你的吗？'
  }
];

const selectedCat = computed(() => {
  const currentId = currentCatStore.getCurrentCatId || catsStore.getAllCats[0]?.id;
  if (!currentId) return null;
  return catsStore.getCatById(currentId) || null;
});

const petInfo = computed(() => ({
  avatar: selectedCat.value?.avatarUrl || 'https://images.unsplash.com/photo-1543852786-1cf6624b9987?w=200&h=200&fit=crop',
  name: selectedCat.value?.name ? `${selectedCat.value.name} (Orange)` : '大橘 (Orange)',
  status: '优秀',
  score: 98
}));

const cats = computed(() => catsStore.getAllCats);

const actionCards = ref([
  {
    name: '猫咪健康报告',
    icon: 'notes-o',
    bgClass: 'bg-[#ffedeb]',
    colorClass: 'text-[#d84315]'
  },
  {
    name: '异常预警',
    icon: 'warning',
    bgClass: 'bg-[#ffe4e6]',
    colorClass: 'text-[#e11d48]' // rose-600
  },
  {
    name: '专业医生',
    icon: 'plus', // van-icon plus works as medical cross
    bgClass: 'bg-[#eff6ff]',
    colorClass: 'text-[#3b82f6]'
  },
  {
    name: 'AI 养猫',
    icon: 'shop-o', 
    bgClass: 'bg-[#fff7ed]',
    colorClass: 'text-[#fb923c]' // orange-400
  }
]);

const handleActionClick = (item: any) => {
  if (item.name === '异常预警') {
    router.push({ name: 'Emotions' });
  } else if (item.name === '猫咪健康报告') {
    openCatArchive();
  } else if (item.name === '专业医生') {
    router.push({ name: 'ProfessionalDoctors' });
  } else if (item.name === 'AI 养猫') {
    pushConsultCard();
    focusConsultInput();
  } else {
    showToast('该功能正在开发中');
  }
};

const pushConsultCard = () => {
  messages.value.push({
    id: `consult-${Date.now()}`,
    role: 'assistant',
    type: 'consult_card',
    content: '你可以直接输入：例如“2岁猫咪一周喂几次罐头？”“最近掉毛多该怎么护理？”“主食和零食比例怎么配？”'
  });
};

const openCatArchive = () => {
  if (!selectedCat.value) {
    showToast('请先添加并选择猫咪');
    return;
  }
  router.push({ name: 'CatArchive', params: { id: selectedCat.value.id } });
};

const openCatSwitcher = () => {
  if (cats.value.length <= 1) {
    showToast('当前只有一只猫咪可切换');
    return;
  }
  showCatSheet.value = true;
};

const selectCat = (catId: string) => {
  currentCatStore.setCurrentCat(catId);
  showCatSheet.value = false;
};

const focusConsultInput = async () => {
  window.scrollTo({ top: document.documentElement.scrollHeight, behavior: 'smooth' });
  await nextTick();
  consultInputRef.value?.focus();
};

const normalizeAssistantText = (content: string) => {
  return content
    // 去掉常见 markdown 和列表符号
    .replace(/[\*#>`~\[\]\(\)_|]/g, ' ')
    .replace(/(^|\n)\s*[-+•]\s*/g, '$1')
    .replace(/\s{2,}/g, ' ')
    // 保留句读，压缩空行
    .replace(/\n{3,}/g, '\n\n')
    .trim();
};

const escapeHtml = (raw: string) => {
  return raw
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\"/g, '&quot;')
    .replace(/'/g, '&#39;');
};

const highlightKeywords = (text: string) => {
  const safeText = escapeHtml(text);
  return safeText.replace(
    /(建议|风险|警惕|立即|尽快|就医|观察|下一步|异常|重点)/g,
    '<span class="ai-keyword">$1</span>'
  );
};

const buildAssistantSections = (content: string) => {
  const cleaned = normalizeAssistantText(content);
  const lines = cleaned
    .split('\n')
    .map((item) => item.trim())
    .filter((item) => !!item);

  const headingReg = /^(建议|风险|下一步|处理方式|观察重点|结论|提示|就医建议|异常预警)[：:]\s*(.*)$/;
  const sections: Array<{ title: string; content: string }> = [];
  let current: { title: string; content: string } | null = null;

  lines.forEach((line) => {
    const matched = line.match(headingReg);
    if (matched) {
      if (current) {
        sections.push(current);
      }
      current = {
        title: matched[1] || 'AI 分析',
        content: matched[2] || '请结合猫咪实际状态继续观察。'
      };
      return;
    }

    if (!current) {
      current = {
        title: sections.length === 0 ? '核心判断' : `补充说明 ${sections.length}`,
        content: line
      };
      return;
    }

    current.content = `${current.content}\n${line}`;
  });

  if (current) {
    sections.push(current);
  }

  if (sections.length === 0) {
    return [
      {
        title: 'AI 回复',
        content: cleaned || '暂时没有可展示的内容。'
      }
    ];
  }

  return sections;
};

const handleSend = async () => {
  const message = inputText.value.trim();
  if (!message) return;

  const catId = selectedCat.value?.id;
  if (!catId) {
    showToast('请先添加并选择猫咪');
    return;
  }

  messages.value.push({
    id: `u-${Date.now()}`,
    role: 'user',
    content: message
  });
  inputText.value = '';

  try {
    const result = await sendMessageToAI({
      catId,
      message
    });
    messages.value.push({
      id: result.id || `a-${Date.now()}`,
      role: 'assistant',
      content: result.message || '抱歉，我暂时没有生成有效回复。'
    });
  } catch {
    messages.value.push({
      id: `a-fail-${Date.now()}`,
      role: 'assistant',
      content: '网络有点忙，请稍后重试。'
    });
    showToast('AI 服务暂时不可用，请稍后再试');
  }
};

const handleBack = () => {
  // 返回统一回到广场，避免受历史栈影响跳转到流程页
  router.push({ name: 'Social' });
};

const handleClearHistory = async () => {
  const catId = selectedCat.value?.id;
  if (!catId) {
    showToast('暂无可清空的历史');
    return;
  }

  try {
    await clearCurrentSession(catId);
    messages.value = welcomeMessage;
    showToast('历史已清空');
  } catch {
    showToast('清空失败，请稍后再试');
  }
};

const loadHistory = async () => {
  const catId = selectedCat.value?.id;
  if (!catId) {
    messages.value = welcomeMessage;
    return;
  }

  try {
    await fetchChatHistory({
      catId,
      page: 1,
      pageSize: 20
    });

    const history = [...getCurrentChatHistory.value]
      .sort((left, right) => new Date(left.timestamp).getTime() - new Date(right.timestamp).getTime())
      .map((item) => ({
        id: item.id,
        role: item.role,
        content: item.message
      }));

    messages.value = history.length > 0 ? history : welcomeMessage;
  } catch {
    messages.value = welcomeMessage;
  }
};

onMounted(async () => {
  await catsStore.fetchAllCats();
  if (!currentCatStore.getCurrentCatId && catsStore.getAllCats[0]?.id) {
    currentCatStore.setCurrentCat(catsStore.getAllCats[0].id);
  }
  await loadHistory();
});

watch(
  () => selectedCat.value?.id,
  async (newId, oldId) => {
    if (!newId || newId === oldId) return;
    await loadHistory();
  }
);
</script>

<style scoped>
.pb-safe {
  padding-bottom: calc(env(safe-area-inset-bottom) + 16px);
}

:deep(.ai-keyword) {
  color: #b42318;
  font-weight: 700;
  background: #ffe4dc;
  border-radius: 6px;
  padding: 0 4px;
}
</style>