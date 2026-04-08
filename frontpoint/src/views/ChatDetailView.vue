<template>
  <div class="min-h-[100dvh] bg-[#f4f5fb] pb-24">
    <header class="sticky top-0 z-20 min-h-[54px] border-b border-[#eceff7] bg-white px-3.5 py-2">
      <div class="flex items-center">
        <button type="button" class="grid h-10 w-10 place-items-center text-[#594139]" @click="router.back()">
          <van-icon name="arrow-left" size="20" />
        </button>
        <div class="mx-auto text-center">
          <div class="flex items-center justify-center gap-2">
            <van-image :src="avatar" fit="cover" width="28" height="28" round />
            <div class="text-[18px] font-bold text-[#12182a]">{{ nickname }}</div>
          </div>
          <div class="mt-0.5 text-[12px] text-[#35c35a]">● 在线</div>
        </div>
        <div class="w-10"></div>
      </div>
    </header>

    <main class="space-y-3 px-4 pt-4">
      <div v-if="loading" class="py-10 text-center">
        <van-loading size="24" />
        <div class="mt-3 text-sm text-on-surface-variant">正在加载消息...</div>
      </div>

      <div v-else-if="messages.length === 0" class="rounded-2xl border border-surface-container-high bg-surface-container-lowest p-6 text-center">
        <div class="text-3xl">🐾</div>
        <div class="mt-3 text-base font-semibold text-on-background">还没有消息</div>
        <div class="mt-1 text-sm text-on-surface-variant">发一句“喵”开启对话</div>
      </div>

      <div v-else class="space-y-3">
        <div class="text-center text-[12px] text-[#b0abb0]">{{ todayTimeLabel }}</div>
        <div v-for="msg in messages" :key="msg.id" class="space-y-1">
          <div class="text-[12px] text-[#b0abb0]" :class="isTargetMessage(msg) ? 'pl-11 text-left' : 'pr-11 text-right'">
            {{ formatSentTime(msg.sentAt) }}
          </div>

          <div class="flex items-start gap-2" :class="isTargetMessage(msg) ? '' : 'flex-row-reverse'">
            <van-image
              :src="isTargetMessage(msg) ? avatar : myAvatar"
              fit="cover"
              width="34"
              height="34"
              round
            />

            <template v-if="resolveMeowCard(msg)">
              <div class="w-[240px] rounded-[18px] border border-[#ebe9e8] bg-[#fffaf7] p-3 shadow-sm" :class="isTargetMessage(msg) ? '' : 'bg-white'">
                <div class="flex items-center gap-2 rounded-[10px] bg-[#fff4eb] px-2 py-2">
                  <div class="grid h-8 w-8 place-items-center rounded-[10px] bg-[#ffe6d5] text-[#ff6b35]">
                    <van-icon name="paw" size="18" />
                  </div>
                  <div>
                    <div class="text-[15px] font-bold text-[#323237]">{{ resolveMeowCard(msg)?.name }}</div>
                    <div class="text-[12px] text-[#8d8580]">{{ resolveMeowCard(msg)?.breed }} · {{ resolveMeowCard(msg)?.ageText }}</div>
                  </div>
                </div>
                <button
                  type="button"
                  class="mt-2 flex w-full items-center justify-between rounded-[10px] px-2 py-2 text-left text-[13px] text-[#6d6561]"
                  @click="openMeowCard(resolveMeowCard(msg))"
                >
                  <span>查看喵咪档案</span>
                  <van-icon name="arrow" />
                </button>
              </div>
            </template>

            <div
              v-else
              class="max-w-[82%] rounded-[18px] px-3 py-2 text-[15px] leading-relaxed"
              :class="isTargetMessage(msg) ? 'bg-[#f1f2f6] text-[#3f3734]' : 'bg-[#ff6b35] text-white'"
            >
              {{ msg.content }}
            </div>
          </div>
        </div>
      </div>
    </main>

    <footer class="fixed bottom-0 left-1/2 z-30 flex w-full max-w-[430px] -translate-x-1/2 items-center gap-2 border-t border-[#e8ebf4] bg-white px-3 py-2.5">
      <button type="button" class="grid h-10 w-10 place-items-center rounded-full bg-[#eceffd] text-[#594139]" @click="showMeowCardSheet = true">
        <van-icon name="plus" size="18" />
      </button>
      <input
        v-model="draft"
        class="h-10 flex-1 rounded-[10px] bg-[#eceffd] px-3 text-[15px] text-[#5f4f48] outline-none"
        placeholder="输入消息..."
        @keyup.enter="send"
      />
      <button
        type="button"
        class="h-10 w-20 rounded-[10px] bg-[#ff6b35] text-[15px] font-semibold text-white shadow-cta disabled:opacity-60"
        :disabled="!draft.trim() || sending"
        @click="send"
      >
        发送
      </button>
    </footer>

    <van-action-sheet v-model:show="showMeowCardSheet" title="发送喵喵卡">
      <div class="max-h-[48dvh] overflow-auto p-3">
        <button
          v-for="cat in cats"
          :key="cat.id"
          type="button"
          class="mb-2 flex w-full items-center gap-3 rounded-xl border border-[#ece8e5] bg-white p-3 text-left"
          @click="sendMeowCard(cat)"
        >
          <van-image :src="cat.avatarUrl || defaultCatAvatar" width="44" height="44" round fit="cover" />
          <div class="min-w-0 flex-1">
            <div class="truncate text-[16px] font-bold text-[#2f2f35]">{{ cat.name }}</div>
            <div class="truncate text-[13px] text-[#7f7773]">{{ cat.breed }} · {{ toAgeText(cat.age) }} · {{ formatWeight(cat.weight) }}</div>
          </div>
          <van-icon name="arrow" class="text-[#aaa2a0]" />
        </button>

        <div v-if="cats.length === 0" class="rounded-xl bg-[#f6f7fc] p-4 text-center text-[14px] text-[#7f7773]">
          暂无猫咪档案，请先去添加猫咪
        </div>
      </div>
    </van-action-sheet>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { showToast } from 'vant';
import { useMessaging } from '@/composables/useMessaging';
import type { Message } from '@/types/message';
import type { CatProfile } from '@/types/cat';
import { useCatsStore } from '@/stores';

const props = defineProps<{ targetUserId: string }>();
const route = useRoute();
const router = useRouter();
const catsStore = useCatsStore();

const { fetchConversationMessages, sendNewMessage, markAsRead } = useMessaging();

const loading = ref(false);
const sending = ref(false);
const messages = ref<Message[]>([]);
const draft = ref('');
const showMeowCardSheet = ref(false);

const defaultCatAvatar = 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg';

const targetUserId = computed(() => props.targetUserId);
const nickname = computed(() => String(route.query.nickname || '私信聊天'));
const avatar = computed(() => String(route.query.avatar || defaultCatAvatar));
const myAvatar = computed(() => {
  const firstCat = catsStore.getAllCats[0];
  return firstCat?.avatarUrl || defaultCatAvatar;
});
const cats = computed(() => catsStore.getAllCats);
const todayTimeLabel = computed(() => {
  const now = new Date();
  return `下午 ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
});

const isTargetMessage = (msg: Message) => msg.senderId === targetUserId.value;

const loadMessages = async () => {
  loading.value = true;
  try {
    await catsStore.fetchAllCats();
    const res = await fetchConversationMessages(targetUserId.value, { page: 1, pageSize: 100 });
    const sorted = [...(res.list || [])].sort((left, right) => new Date(left.sentAt).getTime() - new Date(right.sentAt).getTime());
    messages.value = sorted;

    const unreadIds = sorted.filter((item) => isTargetMessage(item) && item.status !== 'read').map((item) => item.id);
    if (unreadIds.length > 0) {
      await markAsRead(unreadIds);
    }
  } catch {
    messages.value = [];
    showToast({ type: 'fail', message: '加载消息失败，请稍后重试' });
  } finally {
    loading.value = false;
  }
};

const send = async () => {
  const text = draft.value.trim();
  if (!text || sending.value) {
    return;
  }

  sending.value = true;
  draft.value = '';
  try {
    const sent = await sendNewMessage({
      receiverId: targetUserId.value,
      content: text,
      messageType: 'text'
    });
    messages.value = [...messages.value, sent];
  } catch {
    showToast({ type: 'fail', message: '发送失败，请稍后重试' });
  } finally {
    sending.value = false;
  }
};

interface MeowCardPayload {
  id: string;
  name: string;
  breed: string;
  ageText: string;
  weight?: number;
  avatarUrl?: string;
}

const toAgeText = (ageMonths?: number) => {
  if (!ageMonths || ageMonths <= 0) {
    return '年龄未知';
  }
  if (ageMonths < 12) {
    return `${ageMonths}个月`;
  }
  const years = Math.floor(ageMonths / 12);
  const months = ageMonths % 12;
  return months === 0 ? `${years}岁` : `${years}岁${months}个月`;
};

const formatWeight = (weight?: number) => {
  if (!weight || !Number.isFinite(weight)) {
    return '体重未知';
  }
  return `${weight}kg`;
};

const buildMeowCardContent = (cat: CatProfile) => {
  const payload: MeowCardPayload = {
    id: cat.id,
    name: cat.name,
    breed: cat.breed,
    ageText: toAgeText(cat.age),
    weight: cat.weight,
    avatarUrl: cat.avatarUrl
  };
  return `MEOW_CARD:${JSON.stringify(payload)}`;
};

const resolveMeowCard = (msg: Message): MeowCardPayload | null => {
  if (msg.messageType !== 'quick_meow' && !msg.content.startsWith('MEOW_CARD:')) {
    return null;
  }
  const raw = msg.content.startsWith('MEOW_CARD:') ? msg.content.slice('MEOW_CARD:'.length) : msg.content;
  try {
    const parsed = JSON.parse(raw) as MeowCardPayload;
    if (!parsed?.name || !parsed?.breed) {
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
};

const openMeowCard = (payload: MeowCardPayload | null) => {
  if (!payload) {
    return;
  }
  router.push({
    name: 'CatArchive',
    params: { id: payload.id },
    query: {
      shared: JSON.stringify(payload),
      mode: 'shared'
    }
  });
};

const sendMeowCard = async (cat: CatProfile) => {
  if (sending.value) {
    return;
  }
  showMeowCardSheet.value = false;
  sending.value = true;

  try {
    const sent = await sendNewMessage({
      receiverId: targetUserId.value,
      content: buildMeowCardContent(cat),
      messageType: 'quick_meow'
    });
    messages.value = [...messages.value, sent];
    showToast({ type: 'success', message: '喵喵卡已发出' });
  } catch {
    showToast({ type: 'fail', message: '喵喵卡发送失败，请稍后再试' });
  } finally {
    sending.value = false;
  }
};

const formatSentTime = (value: string) => {
  if (!value) {
    return '';
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return '';
  }
  return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
};

onMounted(() => {
  void loadMessages();
});
</script>
