<template>
  <div class="px-6 pt-6 pb-6">
    <div v-if="pageError" class="rounded-2xl border border-surface-container-high bg-surface-container-lowest px-4 py-10 text-center text-sm text-on-surface-variant">
      <div class="text-base font-semibold text-on-background">消息中心加载失败</div>
      <div class="mt-2">{{ pageError }}</div>
      <van-button class="mt-4" type="primary" @click="reload">重试</van-button>
    </div>

    <template v-else>
    <template v-if="!activeConversation">
      <header class="flex items-center justify-between">
        <div>
          <h1 class="text-xl font-semibold tracking-tight text-on-background">消息中心</h1>
          <p class="mt-1 text-sm text-on-surface-variant">会话列表与历史消息</p>
        </div>
        <van-button size="small" plain type="primary" @click="refresh">刷新</van-button>
      </header>

      <section class="mt-6">
        <div v-if="loading" class="py-10 text-center">
          <van-loading size="24" />
          <div class="mt-3 text-sm text-on-surface-variant">正在加载会话...</div>
        </div>

        <div v-else-if="conversations.length === 0" class="rounded-2xl border border-surface-container-high bg-surface-container-lowest p-6 text-center">
          <div class="text-3xl">💬</div>
          <div class="mt-3 text-base font-semibold text-on-background">暂无会话</div>
          <div class="mt-1 text-sm text-on-surface-variant">你可以先在广场互动，或添加好友后开始聊天</div>
        </div>

        <div v-else class="space-y-3">
          <article
            v-for="conv in conversations"
            :key="conv.id"
            class="rounded-2xl border border-surface-container-high bg-surface-container-lowest p-4"
            @click="openConversation(conv)"
          >
            <div class="flex items-center gap-3">
              <van-image :src="conv.avatar" fit="cover" width="44" height="44" round />
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between gap-2">
                  <div class="truncate text-base font-semibold text-on-background">{{ conv.nickname }}</div>
                  <van-badge v-if="conv.unreadCount > 0" :content="conv.unreadCount" />
                </div>
                <div class="mt-0.5 truncate text-xs text-on-surface-variant">{{ conv.lastMessage }}</div>
              </div>
            </div>
          </article>
        </div>
      </section>
    </template>

    <template v-else>
      <van-nav-bar
        :title="activeConversation.nickname"
        left-arrow
        @click-left="closeConversation"
      />

      <section class="mt-4 space-y-3">
        <div v-if="messagesLoading" class="py-10 text-center">
          <van-loading size="24" />
          <div class="mt-3 text-sm text-on-surface-variant">正在加载消息...</div>
        </div>

        <div v-else-if="messages.length === 0" class="rounded-2xl border border-surface-container-high bg-surface-container-lowest p-6 text-center">
          <div class="text-3xl">🐾</div>
          <div class="mt-3 text-base font-semibold text-on-background">还没有消息</div>
          <div class="mt-1 text-sm text-on-surface-variant">发一句“喵”开启对话</div>
        </div>

        <div v-else class="space-y-2">
          <div
            v-for="msg in messages"
            :key="msg.id"
            class="rounded-2xl border border-surface-container-high bg-surface-container-lowest p-3 text-sm text-on-background"
          >
            {{ msg.content }}
          </div>
        </div>
      </section>

      <div class="mt-5 flex items-center gap-2">
        <input
          v-model="draft"
          class="h-11 flex-1 rounded-xl border border-surface-container-high bg-surface-container-lowest px-3 text-sm text-on-background outline-none"
          placeholder="输入消息..."
          @keyup.enter="send"
        />
        <button
          type="button"
          class="h-11 w-20 rounded-xl bg-primary text-on-primary font-semibold shadow-cta disabled:opacity-60"
          :disabled="!draft.trim()"
          @click="send"
        >
          发送
        </button>
      </div>
    </template>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { showToast } from 'vant';
import { useMessaging } from '@/composables/useMessaging';
import type { Conversation, Message } from '@/types/message';

const { fetchConversationList, fetchConversationMessages, sendNewMessage, getCurrentConversations } = useMessaging();

const loading = ref(false);
const messagesLoading = ref(false);
const pageError = ref<string | null>(null);

const conversations = computed(() => getCurrentConversations.value);

const activeConversation = ref<Conversation | null>(null);
const messages = ref<Message[]>([]);
const draft = ref('');

const refresh = async () => {
  if (loading.value) {
    return;
  }
  loading.value = true;
  try {
    await fetchConversationList({ page: 1, pageSize: 20 });
  } catch {
    showToast({ type: 'fail', message: '加载会话失败，请稍后重试' });
  } finally {
    loading.value = false;
  }
};

const reload = async () => {
  pageError.value = null;
  await refresh();
};

const openConversation = async (conv: Conversation) => {
  activeConversation.value = conv;
  messages.value = [];
  messagesLoading.value = true;
  pageError.value = null;
  try {
    const res = await fetchConversationMessages(conv.targetUserId, { page: 1, pageSize: 30 });
    messages.value = res.list;
  } catch {
    pageError.value = '加载消息失败，请稍后重试';
  } finally {
    messagesLoading.value = false;
  }
};

const closeConversation = () => {
  activeConversation.value = null;
  draft.value = '';
};

const send = async () => {
  const conv = activeConversation.value;
  const text = draft.value.trim();
  if (!conv || !text) {
    return;
  }

  draft.value = '';
  try {
    const sent = await sendNewMessage({
      receiverId: conv.targetUserId,
      content: text,
      messageType: 'text'
    });
    messages.value = [...messages.value, sent];
  } catch {
    pageError.value = '发送失败，请稍后重试';
  }
};

onMounted(refresh);
</script>
