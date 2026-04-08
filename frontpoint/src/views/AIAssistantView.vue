<template>
  <div class="px-6 pt-6 pb-6">
    <header class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold tracking-tight text-on-background">AI 助理</h1>
        <p class="mt-1 text-sm text-on-surface-variant">{{ selectedCatName }}</p>
      </div>
      <van-button size="small" plain type="primary" :disabled="!hasCats" @click="clear">
        清空
      </van-button>
    </header>

    <section v-if="!hasCats" class="mt-6 rounded-2xl border border-surface-container-high bg-surface-container-lowest p-6 text-center">
      <div class="text-3xl">🐱</div>
      <div class="mt-3 text-base font-semibold text-on-background">还没有猫咪档案</div>
      <div class="mt-1 text-sm text-on-surface-variant">先添加猫咪，才能使用 AI 养宠建议与对话</div>
      <van-button class="mt-5" block type="primary" @click="router.push({ name: 'AddCat' })">
        去添加猫咪
      </van-button>
    </section>

    <section v-else class="mt-6">
      <div class="rounded-2xl border border-surface-container-high bg-surface-container-lowest p-4">
        <div class="text-sm text-on-surface-variant">对话记录</div>

        <div v-if="messages.length === 0" class="mt-4 text-sm text-on-surface-variant">
          你可以从“猫咪饮食 / 行为 / 健康 / 情绪”任意方向开始提问。
        </div>

        <div v-else class="mt-4 space-y-3">
          <div
            v-for="item in messages"
            :key="item.id"
            class="flex gap-3"
            :class="item.role === 'user' ? 'flex-row-reverse' : ''"
          >
            <div
              class="h-9 w-9 shrink-0 rounded-2xl grid place-items-center border border-surface-container-high"
              :class="item.role === 'user' ? 'bg-primary text-on-primary' : 'bg-surface-container-high text-on-surface-variant'"
            >
              {{ item.role === 'user' ? '我' : 'AI' }}
            </div>
            <div
              class="max-w-[78%] rounded-2xl p-3 text-sm leading-relaxed"
              :class="item.role === 'user' ? 'bg-primary text-on-primary' : 'bg-surface-container-high text-on-background'"
            >
              {{ item.text }}
            </div>
          </div>
        </div>
      </div>

      <div class="mt-4 flex items-center gap-2">
        <input
          v-model="draft"
          class="h-11 flex-1 rounded-xl border border-surface-container-high bg-surface-container-lowest px-3 text-sm text-on-background outline-none"
          placeholder="问问 AI：比如猫咪一直叫怎么办..."
          @keyup.enter="send"
        />
        <button
          type="button"
          class="h-11 w-20 rounded-xl bg-primary text-on-primary font-semibold shadow-cta disabled:opacity-60"
          :disabled="!draft.trim() || sending"
          @click="send"
        >
          发送
        </button>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';
import { useAIAssistant } from '@/composables/useAIAssistant';
import { useCatsStore, useCurrentCatStore } from '@/stores';

type LocalChatItem = { id: string; role: 'user' | 'assistant'; text: string };

const router = useRouter();
const catsStore = useCatsStore();
const currentCatStore = useCurrentCatStore();
const { sendMessageToAI, fetchChatHistory, clearCurrentSession } = useAIAssistant();

const draft = ref('');
const messages = ref<LocalChatItem[]>([]);
const sending = ref(false);

const selectedCatId = computed(() => currentCatStore.getCurrentCatId || catsStore.getAllCats[0]?.id || '');
const hasCats = computed(() => catsStore.getAllCats.length > 0);
const selectedCatName = computed(() => {
  const id = selectedCatId.value;
  if (!id) {
    return '未选择猫咪';
  }
  const cat = catsStore.getCatById(id);
  return cat?.name ? `当前：${cat.name}` : '未选择猫咪';
});

const ensureCats = async () => {
  await catsStore.fetchAllCats();
  const first = catsStore.getAllCats[0];
  if (!currentCatStore.getCurrentCatId && first) {
    currentCatStore.setCurrentCat(first.id);
  }
};

const loadHistory = async () => {
  const catId = selectedCatId.value;
  if (!catId) {
    return;
  }
  try {
    const res = await fetchChatHistory({ catId, page: 1, pageSize: 10 });
    const items: LocalChatItem[] = res.list.map((it) => ({
      id: it.id,
      role: 'assistant',
      text: it.message
    }));
    messages.value = [{ id: 'init', role: 'assistant', text: '我在这里，随时可以帮你一起照顾猫咪。' }, ...items];
  } catch {
    messages.value = [{ id: 'init', role: 'assistant', text: '我在这里，随时可以帮你一起照顾猫咪。' }];
  }
};

const send = async () => {
  const text = draft.value.trim();
  if (!text) {
    return;
  }
  if (!hasCats.value || !selectedCatId.value) {
    showToast({ type: 'fail', message: '请先添加并选择一只猫咪' });
    return;
  }
  if (sending.value) {
    return;
  }

  sending.value = true;
  draft.value = '';
  messages.value = [...messages.value, { id: `u-${Date.now()}`, role: 'user', text }];
  try {
    const reply = await sendMessageToAI({ catId: selectedCatId.value, message: text });
    messages.value = [...messages.value, { id: reply.id, role: 'assistant', text: reply.message }];
  } catch {
    messages.value = [...messages.value, { id: `fallback-${Date.now()}`, role: 'assistant', text: '我建议你先观察食欲、精神与排泄，再结合最近的环境变化做判断。' }];
    showToast({ type: 'fail', message: 'AI 接口暂不可用' });
  } finally {
    sending.value = false;
  }
};

const clear = async () => {
  const catId = selectedCatId.value;
  if (!catId) {
    return;
  }
  try {
    await clearCurrentSession(catId);
  } catch {
    // ignore
  }
  messages.value = [{ id: 'init', role: 'assistant', text: '我在这里，随时可以帮你一起照顾猫咪。' }];
};

onMounted(async () => {
  try {
    await ensureCats();
    await loadHistory();
  } catch {
    showToast({ type: 'fail', message: '加载猫咪档案失败，请检查登录状态' });
  }
});
</script>
