<template>
  <div class="chat-page">
    <AppTopBar :title="nickname" subtitle="最近互动" back @back="router.back()">
      <template #actions>
        <button class="topbar-action" type="button" aria-label="清空聊天" @click="clearConversationOnlyMine">
          <van-icon name="delete-o" size="18" />
        </button>
        <button class="topbar-action" type="button" aria-label="发送喵喵卡" @click="showMeowCardSheet = true">
          <van-icon name="plus" size="20" />
        </button>
      </template>
    </AppTopBar>

    <main ref="chatMainRef" class="chat-main" @scroll="handleThreadScroll">
      <section v-if="loading" class="chat-state">
        <van-loading size="26" color="#f97316" />
        <span>正在加载消息...</span>
      </section>

      <section v-else-if="messages.length === 0" class="chat-state">
        <van-icon name="chat-o" size="38" />
        <strong>还没有消息</strong>
        <span>发一句“喵”开启对话</span>
      </section>

      <section v-else class="message-thread">
        <time class="thread-time">{{ todayTimeLabel }}</time>
        <article v-for="msg in messages" :key="msg.id" class="message-row" :class="{ mine: !isTargetMessage(msg) }">
          <time class="message-time">{{ formatSentTime(msg.sentAt) }}</time>
          <div class="message-line">
            <van-image :src="isTargetMessage(msg) ? avatar : myAvatar" fit="cover" width="36" height="36" round>
              <template #error>
                <img :src="getDefaultUserAvatar(isTargetMessage(msg) ? targetUserId : getCurrentUserId())" alt="" width="36" height="36" class="avatar-fallback-img" />
              </template>
            </van-image>

            <template v-if="resolveMeowCard(msg)">
              <div class="meow-card">
                <div class="meow-card-head">
                  <van-image :src="resolveMeowCardAvatar(resolveMeowCard(msg))" width="48" height="48" radius="14" fit="cover" />
                  <div>
                    <strong>{{ resolveMeowCard(msg)?.name }}</strong>
                    <span>{{ meowCardMeta(resolveMeowCard(msg)) }}</span>
                  </div>
                </div>
                <div class="meow-card-section">
                  <b>基本信息</b>
                  <span v-if="resolveMeowCard(msg)?.genderText">性别：{{ resolveMeowCard(msg)?.genderText }}</span>
                  <span v-if="resolveMeowCard(msg)?.recentWeightText">体重：{{ resolveMeowCard(msg)?.recentWeightText }}</span>
                  <span v-if="resolveMeowCard(msg)?.vaccineStatus">疫苗：{{ resolveMeowCard(msg)?.vaccineStatus }}</span>
                  <span v-if="resolveMeowCard(msg)?.medicalHistory">病史：{{ resolveMeowCard(msg)?.medicalHistory }}</span>
                  <span v-if="!hasMeowCardBasicInfo(resolveMeowCard(msg))">主人还没有补充更多资料</span>
                </div>
                <div v-if="resolveMeowCard(msg)?.recentMood || resolveMeowCard(msg)?.recentNote" class="meow-card-section warm">
                  <b>最近情绪</b>
                  <span v-if="resolveMeowCard(msg)?.recentMood">{{ resolveMeowCard(msg)?.recentMood }}</span>
                  <span v-if="resolveMeowCard(msg)?.recentNote">{{ resolveMeowCard(msg)?.recentNote }}</span>
                </div>
                <button type="button" @click="openMeowCard(resolveMeowCard(msg))">
                  查看猫咪档案
                  <van-icon name="arrow" />
                </button>
              </div>
            </template>

            <div v-else class="bubble">
              {{ msg.content }}
            </div>
          </div>
        </article>
      </section>

      <button v-if="hasNewMessages" type="button" class="new-message-btn" @click="scrollToBottom(true)">
        有新消息
      </button>
    </main>

    <footer class="chat-input-bar">
      <button type="button" class="attach-btn" aria-label="发送喵喵卡" @click="showMeowCardSheet = true">
        <van-icon name="plus" size="18" />
      </button>
      <input v-model="draft" placeholder="输入消息..." @keyup.enter="send" />
      <button type="button" class="send-btn" :disabled="!draft.trim() || sending" @click="send">
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
          <van-image :src="getSafeCatAvatarUrl(cat.avatarUrl)" width="44" height="44" round fit="cover" />
          <div class="min-w-0 flex-1">
            <div class="truncate text-[16px] font-bold text-[#2f2f35]">{{ cat.name }}</div>
            <div class="truncate text-[13px] text-[#7f7773]">{{ catPickerMeta(cat) }}</div>
          </div>
          <van-icon name="arrow" class="text-[#aaa2a0]" />
        </button>

        <div v-if="cats.length === 0" class="rounded-xl bg-[#f6f7fc] p-4 text-center text-[14px] text-[#7f7773]">
          暂无可发送的猫咪卡片
        </div>
      </div>
    </van-action-sheet>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { showConfirmDialog, showToast } from 'vant';
import AppTopBar from '@/components/AppTopBar.vue';
import { useMessaging } from '@/composables/useMessaging';
import type { Message } from '@/types/message';
import type { CatProfile } from '@/types/cat';
import { useCatsStore } from '@/stores';
import { getEmotionRecords } from '@/api/emotion';
import { getWeightRecords } from '@/api/health';
import { getDefaultUserAvatar, getSafeAvatarUrl, getSafeCatAvatarUrl } from '@/utils/image';
import { formatCatAge } from '@/utils/age';
import { getCurrentUserId, globalProfile } from '@/utils/userProfile';

const props = defineProps<{ targetUserId: string }>();
const route = useRoute();
const router = useRouter();
const catsStore = useCatsStore();

const { fetchConversationMessages, sendNewMessage, markAsRead, removeConversation } = useMessaging();

const loading = ref(false);
const sending = ref(false);
const messages = ref<Message[]>([]);
const draft = ref('');
const showMeowCardSheet = ref(false);
const chatMainRef = ref<HTMLElement | null>(null);
const hasNewMessages = ref(false);
let pollingTimer: ReturnType<typeof setInterval> | null = null;

const targetUserId = computed(() => props.targetUserId);
const nickname = computed(() => String(route.query.nickname || '私信聊天'));
const avatar = computed(() => getSafeAvatarUrl(String(route.query.avatar || ''), targetUserId.value));
const myAvatar = computed(() => getSafeAvatarUrl(globalProfile.avatarUrl, getCurrentUserId()));
const cats = computed(() => catsStore.getAllCats);
const todayTimeLabel = computed(() => {
  const now = new Date();
  return `下午 ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
});

const isTargetMessage = (msg: Message) => msg.senderId === targetUserId.value;

const sortMessages = (items: Message[]) =>
  [...items].sort((left, right) => new Date(left.sentAt).getTime() - new Date(right.sentAt).getTime());

const mergeMessages = (base: Message[], incoming: Message[]) => {
  const map = new Map<string, Message>();
  [...base, ...incoming].forEach((item) => map.set(item.id, item));
  return sortMessages(Array.from(map.values()));
};

const isNearBottom = () => {
  const el = chatMainRef.value;
  if (!el) return true;
  return el.scrollHeight - el.scrollTop - el.clientHeight < 96;
};

const scrollToBottom = async (smooth = false) => {
  await nextTick();
  const el = chatMainRef.value;
  if (!el) return;
  el.scrollTo({ top: el.scrollHeight, behavior: smooth ? 'smooth' : 'auto' });
  hasNewMessages.value = false;
};

const handleThreadScroll = () => {
  if (isNearBottom()) {
    hasNewMessages.value = false;
  }
};

const markUnreadFromTarget = async (items: Message[]) => {
  const unreadIds = items.filter((item) => isTargetMessage(item) && item.status !== 'read').map((item) => item.id);
  if (unreadIds.length > 0) {
    await markAsRead(unreadIds);
  }
};

const loadMessages = async (options: { initial?: boolean } = {}) => {
  if (options.initial) {
    loading.value = true;
  }
  const shouldFollow = options.initial || isNearBottom();
  try {
    await catsStore.fetchAllCats();
    const res = await fetchConversationMessages(targetUserId.value, { page: 1, pageSize: 100 });
    const sorted = sortMessages(res.list || []);
    const oldIds = new Set(messages.value.map((item) => item.id));
    const hasIncoming = sorted.some((item) => !oldIds.has(item.id));
    messages.value = mergeMessages(messages.value, sorted);
    await markUnreadFromTarget(sorted);

    if (shouldFollow && !options.initial) {
      await scrollToBottom(!options.initial);
    } else if (hasIncoming) {
      hasNewMessages.value = true;
    }
  } catch {
    if (options.initial) {
      messages.value = [];
      showToast({ type: 'fail', message: '加载消息失败，请稍后重试' });
    }
  } finally {
    if (options.initial) {
      loading.value = false;
      await scrollToBottom();
    }
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
    messages.value = mergeMessages(messages.value, [sent]);
    await scrollToBottom(true);
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
  gender?: number;
  genderText?: string;
  vaccineStatus?: string;
  medicalHistory?: string;
  neutered?: boolean;
  recentMood?: string;
  recentWeightText?: string;
  recentNote?: string;
  createdAt?: string;
  updatedAt?: string;
}

const toAgeText = (ageMonths?: number | null) => formatCatAge(ageMonths);

const formatWeight = (weight?: number) => {
  if (typeof weight !== 'number' || !Number.isFinite(weight) || weight <= 0) {
    return '';
  }
  return `${weight}kg`;
};

const catPickerMeta = (cat: CatProfile) => {
  const parts = [cat.breed || '猫咪', toAgeText(cat.age), formatWeight(cat.weight)].filter(Boolean);
  return parts.join(' · ');
};

const formatDateLabel = (value?: string) => {
  if (!value) {
    return '';
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return '';
  }
  return `${date.getMonth() + 1}/${date.getDate()}`;
};

const buildMeowCardContent = async (cat: CatProfile) => {
  const avatarUrl = getSafeCatAvatarUrl(cat.avatarUrl);
  const genderText = cat.gender === 1 ? '公猫' : cat.gender === 0 ? '母猫' : '';
  const recentWeightText = formatWeight(cat.weight);
  const payload: MeowCardPayload = {
    id: cat.id,
    name: cat.name,
    breed: cat.breed || '猫咪',
    ageText: toAgeText(cat.age),
    weight: cat.weight,
    avatarUrl,
    gender: cat.gender,
    genderText,
    vaccineStatus: cat.vaccineStatus,
    medicalHistory: cat.medicalHistory,
    neutered: cat.isNeutered,
    recentWeightText,
    createdAt: cat.createdAt,
    updatedAt: cat.updatedAt
  };

  const [emotionRes, weightRes] = await Promise.allSettled([
    getEmotionRecords({ page: 1, pageSize: 1, catId: cat.id }),
    getWeightRecords({ petId: cat.id, page: 1, pageSize: 1 })
  ]);

  if (emotionRes.status === 'fulfilled') {
    const latestEmotion = emotionRes.value.data.list?.[0];
    if (latestEmotion) {
      payload.recentMood = latestEmotion.emotionTag || '平稳';
      payload.recentNote = latestEmotion.emotionDescription || '';
    }
  }

  if (weightRes.status === 'fulfilled') {
    const latestWeight = weightRes.value.data.list?.[0];
    if (latestWeight) {
      const dateLabel = formatDateLabel(latestWeight.recordDate);
      payload.recentWeightText = `${latestWeight.weight}kg${dateLabel ? `（${dateLabel}）` : ''}`;
      payload.weight = latestWeight.weight;
    }
  }

  return `MEOW_CARD:${JSON.stringify(payload)}`;
};

const resolveMeowCardAvatar = (payload: MeowCardPayload | null) => getSafeCatAvatarUrl(payload?.avatarUrl);

const meowCardMeta = (payload: MeowCardPayload | null) => {
  if (!payload) return '';
  return [payload.breed || '猫咪', payload.ageText].filter((item) => item && item !== '年龄未知').join(' · ') || '猫咪档案';
};

const hasMeowCardBasicInfo = (payload: MeowCardPayload | null) =>
  Boolean(payload?.genderText || payload?.recentWeightText || payload?.vaccineStatus || payload?.medicalHistory);

const resolveMeowCard = (msg: Message): MeowCardPayload | null => {
  if (msg.messageType !== 'quick_meow' && !msg.content.startsWith('MEOW_CARD:')) {
    return null;
  }
  const raw = msg.content.startsWith('MEOW_CARD:') ? msg.content.slice('MEOW_CARD:'.length) : msg.content;
  try {
    const parsed = JSON.parse(raw) as MeowCardPayload;
    if (!parsed?.name) {
      return null;
    }
    parsed.breed = parsed.breed || '猫咪';
    parsed.avatarUrl = getSafeCatAvatarUrl(parsed.avatarUrl);
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
      content: await buildMeowCardContent(cat),
      messageType: 'quick_meow'
    });
    messages.value = mergeMessages(messages.value, [sent]);
    await scrollToBottom(true);
    showToast({ type: 'success', message: '喵喵卡已发出' });
  } catch {
    showToast({ type: 'fail', message: '喵喵卡发送失败，请稍后再试' });
  } finally {
    sending.value = false;
  }
};

const clearConversationOnlyMine = async () => {
  try {
    await showConfirmDialog({
      title: '清空聊天',
      message: '仅删除你这边的聊天记录，不会影响对方。'
    });
  } catch {
    return;
  }
  try {
    await removeConversation(targetUserId.value);
    messages.value = [];
    hasNewMessages.value = false;
    showToast({ type: 'success', message: '聊天记录已清空' });
  } catch {
    showToast({ type: 'fail', message: '清空失败，请稍后重试' });
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
  void loadMessages({ initial: true });
  pollingTimer = setInterval(() => {
    void loadMessages();
  }, 3000);
});

onBeforeUnmount(() => {
  if (pollingTimer) {
    clearInterval(pollingTimer);
    pollingTimer = null;
  }
});
</script>

<style scoped>
.avatar-fallback-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 999px;
}

.chat-page {
  display: flex;
  height: 100dvh;
  flex-direction: column;
  overflow: hidden;
  padding: 0 16px;
  background: var(--cv-page-gradient);
}

.chat-page :deep(.app-topbar) {
  position: sticky;
  top: 0;
  z-index: 20;
  flex-shrink: 0;
  margin: 0 -16px;
  padding-left: 16px;
  padding-right: 16px;
  padding-top: env(safe-area-inset-top, 0px);
}

.chat-main {
  min-height: 0;
  flex: 1;
  overflow-x: hidden;
  overflow-y: auto;
  padding: 12px 0 86px;
}

.chat-state {
  display: grid;
  min-height: 220px;
  place-items: center;
  gap: 8px;
  border: 1px solid var(--cv-card-border);
  border-radius: var(--cv-card-radius);
  background: var(--cv-card-bg);
  color: var(--cv-muted);
  text-align: center;
  box-shadow: var(--cv-card-shadow);
}

.chat-state strong {
  color: var(--cv-ink);
  font-size: 17px;
  font-weight: 900;
}

.message-thread {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.new-message-btn {
  position: sticky;
  bottom: 12px;
  left: 50%;
  z-index: 4;
  display: block;
  width: fit-content;
  margin: 12px auto 0;
  border: 0;
  border-radius: 999px;
  background: #172033;
  color: #fff;
  padding: 8px 14px;
  font-size: 13px;
  font-weight: 900;
  box-shadow: 0 10px 24px rgba(23, 32, 51, 0.18);
}

.thread-time {
  align-self: center;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.8);
  color: var(--cv-muted);
  padding: 5px 10px;
  font-size: 11px;
  font-weight: 900;
}

.message-row {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
}

.message-row.mine {
  align-items: flex-end;
}

.message-time {
  color: #a0a9b7;
  padding: 0 44px;
  font-size: 11px;
  font-weight: 800;
}

.message-line {
  display: flex;
  max-width: 100%;
  align-items: flex-start;
  gap: 8px;
}

.message-row.mine .message-line {
  flex-direction: row-reverse;
}

.bubble {
  max-width: 260px;
  border-radius: 18px 18px 18px 6px;
  background: #fff;
  color: var(--cv-ink);
  padding: 10px 12px;
  font-size: 15px;
  line-height: 1.58;
  word-break: break-word;
  box-shadow: 0 8px 20px rgba(23, 32, 51, 0.06);
}

.message-row.mine .bubble {
  border-radius: 18px 18px 6px 18px;
  background: linear-gradient(135deg, #f97316, #14b8a6);
  color: #fff;
}

.meow-card {
  width: 252px;
  border: 1px solid var(--cv-card-border);
  border-radius: var(--cv-card-radius);
  background: var(--cv-card-bg);
  padding: 12px;
  box-shadow: var(--cv-card-shadow);
}

.meow-card-head {
  display: flex;
  align-items: center;
  gap: 10px;
  border-radius: 16px;
  background: rgba(249,115,22,0.08);
  padding: 9px;
}

.meow-card-head strong {
  display: block;
  color: var(--cv-ink);
  font-size: 15px;
  font-weight: 900;
}

.meow-card-head span {
  color: var(--cv-muted);
  font-size: 12px;
  font-weight: 700;
}

.meow-card-section {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 9px;
  border-radius: 15px;
  background: #f4f7fb;
  padding: 10px;
  color: var(--cv-muted);
  font-size: 12px;
  line-height: 1.45;
}

.meow-card-section.warm {
  background: rgba(249,115,22,0.08);
}

.meow-card-section b {
  color: var(--cv-ink);
  font-size: 12px;
  font-weight: 900;
}

.meow-card button {
  display: flex;
  width: 100%;
  align-items: center;
  justify-content: space-between;
  margin-top: 8px;
  border: 0;
  border-radius: 14px;
  background: var(--cv-ink);
  color: #fff;
  padding: 10px;
  font-size: 13px;
  font-weight: 900;
}

.chat-input-bar {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 50%;
  z-index: 32;
  display: flex;
  width: 100%;
  max-width: var(--app-mobile-width, 430px);
  box-sizing: border-box;
  align-items: center;
  gap: 8px;
  transform: translateX(-50%);
  border-top: 1px solid rgba(226, 232, 240, 0.9);
  background: rgba(255, 255, 255, 0.94);
  padding: 10px 12px calc(10px + env(safe-area-inset-bottom, 0px));
  backdrop-filter: blur(18px);
}

.attach-btn,
.send-btn {
  border: 0;
  font-weight: 900;
}

.attach-btn {
  display: grid;
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  place-items: center;
  border-radius: 14px;
  background: #eef3f8;
  color: var(--cv-ink);
}

.chat-input-bar input {
  min-width: 0;
  height: 42px;
  flex: 1;
  border: 1px solid #dde5ee;
  border-radius: 14px;
  background: #f8fafc;
  color: var(--cv-ink);
  outline: none;
  padding: 0 12px;
  font-size: 15px;
  font-weight: 700;
}

.send-btn {
  height: 42px;
  flex-shrink: 0;
  border-radius: 14px;
  background: var(--cv-ink);
  color: #fff;
  padding: 0 16px;
  font-size: 14px;
}

.send-btn:disabled {
  opacity: 0.45;
}
</style>
