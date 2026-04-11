<template>
  <div class="min-h-[100dvh] bg-[#f4f5fb] px-4 pt-3 pb-6">
    <div v-if="pageError" class="rounded-2xl border border-surface-container-high bg-surface-container-lowest px-4 py-10 text-center text-sm text-on-surface-variant">
      <div class="text-base font-semibold text-on-background">消息中心加载失败</div>
      <div class="mt-2">{{ pageError }}</div>
      <van-button class="mt-4" type="primary" @click="reload">重试</van-button>
    </div>

    <template v-else>
      <header class="sticky top-0 z-20 -mx-4 min-h-[54px] bg-[#f4f5fb]/95 px-4 py-2.5 backdrop-blur-md">
        <div class="flex items-center gap-3">
          <h1 class="text-[23px] font-extrabold text-[#FF6B35]">消息</h1>
          <div class="flex h-9 flex-1 items-center gap-2 rounded-full bg-[#e6e9fa] px-3 text-[#8f97a9]">
            <van-icon name="search" />
            <span class="text-[14px]">搜索聊天记录</span>
          </div>
          <button type="button" class="text-[#ff6b35]" @click="router.push({ name: 'AddFriend' })">
            <van-icon name="plus" size="20" />
          </button>
        </div>
      </header>

      <nav class="mt-1 flex border-b border-[#e7eaf4] text-[14px]">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="relative px-3 py-2.5 font-semibold"
          :class="activeTab === tab.key ? 'text-[#FF6B35]' : 'text-[#6f6662]'"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
          <span v-if="activeTab === tab.key" class="absolute bottom-0 left-0 h-[2px] w-full rounded-full bg-[#FF6B35]"></span>
        </button>
        <button class="ml-auto py-3 text-on-surface-variant" @click="refresh">
          <van-icon name="replay" />
        </button>
      </nav>

      <section class="mt-3 space-y-2.5">
        <div v-if="loading" class="py-10 text-center">
          <van-loading size="24" />
          <div class="mt-3 text-sm text-on-surface-variant">正在加载会话...</div>
        </div>

        <div v-else-if="activeTab === 'private' && conversations.length === 0" class="rounded-2xl border border-surface-container-high bg-surface-container-lowest p-6 text-center">
          <div class="text-3xl">💬</div>
          <div class="mt-3 text-base font-semibold text-on-background">暂无会话</div>
          <div class="mt-1 text-sm text-on-surface-variant">你可以先在广场互动，或添加好友后开始聊天</div>
        </div>

        <div v-else-if="activeTab === 'private'" class="space-y-3">
          <article
            v-for="conv in conversations"
            :key="conv.id"
            class="flex cursor-pointer items-center gap-3 rounded-[18px] bg-white px-3.5 py-3"
            @click="openConversation(conv)"
          >
            <div class="relative">
              <van-image :src="conv.avatar || defaultAvatar" fit="cover" width="54" height="54" round />
              <div v-if="conv.isOnline" class="absolute bottom-0 right-0 h-3 w-3 rounded-full border-2 border-white bg-[#32c65f]"></div>
            </div>
            <div class="min-w-0 flex-1">
              <div class="flex items-center justify-between gap-2">
                <div class="truncate text-[18px] font-bold text-[#12182a]">{{ conv.nickname || conv.targetUserId }}</div>
                <div class="text-[14px] text-[#9a9798]">{{ formatTime(conv.updatedAt) }}</div>
              </div>
              <div class="mt-0.5 flex items-center gap-2">
                <div class="truncate text-[14px] text-[#6f6662]">{{ previewMessage(conv.lastMessage, conv.lastMessageType) }}</div>
                <div v-if="conv.unreadCount > 0" class="h-2.5 w-2.5 rounded-full bg-[#ff6b35]"></div>
              </div>
            </div>
          </article>
        </div>

        <div v-else-if="activeTab === 'comments'" class="space-y-3">
          <article
            v-for="item in commentItems"
            :key="item.id"
            class="flex cursor-pointer items-center gap-3 rounded-[18px] bg-white px-3.5 py-3"
            @click="openDynamic(item.dynamicId)"
          >
            <div class="grid h-12 w-12 place-items-center rounded-full bg-[#ffeade] text-[#ff6b35]">
              <van-icon name="chat-o" size="20" />
            </div>
            <div class="min-w-0 flex-1">
              <div class="truncate text-[16px] font-bold text-[#12182a]">有人评论了你的动态</div>
              <div class="mt-0.5 truncate text-[14px] text-[#6f6662]">{{ item.preview }}</div>
            </div>
            <div class="text-[14px] text-[#9a9798]">{{ formatTime(item.updatedAt) }}</div>
          </article>

          <div v-if="commentItems.length === 0" class="rounded-2xl border border-surface-container-high bg-surface-container-lowest p-6 text-center text-sm text-on-surface-variant">
            暂无评论动态
          </div>
        </div>

        <div v-else-if="activeTab === 'likes'" class="space-y-3">
          <article
            v-for="item in likeItems"
            :key="item.id"
            class="flex cursor-pointer items-center gap-3 rounded-[18px] bg-white px-3.5 py-3"
            @click="openDynamic(item.dynamicId)"
          >
            <div class="grid h-12 w-12 place-items-center rounded-full bg-[#ffeade] text-[#ff6b35]">
              <van-icon name="like-o" size="20" />
            </div>
            <div class="min-w-0 flex-1">
              <div class="truncate text-[16px] font-bold text-[#12182a]">你的动态收到了赞</div>
              <div class="mt-0.5 truncate text-[14px] text-[#6f6662]">{{ item.preview }}</div>
            </div>
            <div class="text-[14px] text-[#9a9798]">{{ formatTime(item.updatedAt) }}</div>
          </article>

          <div v-if="likeItems.length === 0" class="rounded-2xl border border-surface-container-high bg-surface-container-lowest p-6 text-center text-sm text-on-surface-variant">
            暂无点赞动态
          </div>
        </div>

        <div v-else class="space-y-3">
          <article
            v-for="friend in fans"
            :key="friend.id"
            class="flex cursor-pointer items-center gap-3 rounded-[18px] bg-white px-3.5 py-3"
            @click="openFanChat(friend.userId, friend.nickname, friend.avatar)"
          >
            <div class="relative">
              <van-image :src="friend.avatar || defaultAvatar" fit="cover" width="54" height="54" round />
              <div v-if="friend.isOnline" class="absolute bottom-0 right-0 h-3 w-3 rounded-full border-2 border-white bg-[#32c65f]"></div>
            </div>
            <div class="min-w-0 flex-1">
              <div class="truncate text-[17px] font-bold text-[#12182a]">{{ friend.nickname }}</div>
              <div class="mt-0.5 truncate text-[14px] text-[#6f6662]">点击开始聊天</div>
            </div>
          </article>

          <div v-if="fans.length === 0" class="rounded-2xl border border-surface-container-high bg-surface-container-lowest p-6 text-center text-sm text-on-surface-variant">
            暂无粉丝
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onActivated, onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';
import { useMessaging } from '@/composables/useMessaging';
import type { Conversation } from '@/types/message';
import type { DynamicResponse } from '@/types/social';
import { useSocialFeatures } from '@/composables/useSocialFeatures';

const router = useRouter();

const { fetchConversationList, fetchFollowerList, getCurrentConversations, getCurrentFollowers } = useMessaging();
const { fetchMyDynamicsList, getCurrentDynamics } = useSocialFeatures();

const loading = ref(false);
const pageError = ref<string | null>(null);
const activeTab = ref<'private' | 'comments' | 'likes' | 'fans'>('private');
const loadedState = ref({
  private: false,
  comments: false,
  likes: false,
  fans: false
});

const tabs = [
  { key: 'private', label: '私信' },
  { key: 'comments', label: '评论' },
  { key: 'likes', label: '赞' },
  { key: 'fans', label: '粉丝' }
] as const;

const defaultAvatar = 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg';

const conversations = computed(() => getCurrentConversations.value);
const fans = computed(() => getCurrentFollowers.value);

interface DynamicNoticeItem {
  id: string;
  dynamicId: string;
  preview: string;
  updatedAt: string;
}

const mapDynamicPreview = (item: DynamicResponse): string => {
  const content = item.content?.trim();
  if (!content) {
    return '查看你的动态互动';
  }
  return content.length > 28 ? `${content.slice(0, 28)}...` : content;
};

const commentItems = computed<DynamicNoticeItem[]>(() => {
  return getCurrentDynamics.value
    .filter((item) => (item.commentCount || 0) > 0)
    .map((item) => ({
      id: `comment-${item.id}`,
      dynamicId: item.id,
      preview: `${item.commentCount} 条评论 · ${mapDynamicPreview(item)}`,
      updatedAt: item.createdAt
    }));
});

const likeItems = computed<DynamicNoticeItem[]>(() => {
  return getCurrentDynamics.value
    .filter((item) => (item.likeCount || 0) > 0)
    .map((item) => ({
      id: `like-${item.id}`,
      dynamicId: item.id,
      preview: `${item.likeCount} 个赞 · ${mapDynamicPreview(item)}`,
      updatedAt: item.createdAt
    }));
});

const fetchByTab = async (tab: 'private' | 'comments' | 'likes' | 'fans', force = false) => {
  if (loading.value) {
    return;
  }
  if (loadedState.value[tab] && !force) {
    return;
  }

  loading.value = true;
  pageError.value = null;
  try {
    if (tab === 'private') {
      await fetchConversationList({ page: 1, pageSize: 20 });
      loadedState.value.private = true;
      return;
    }

    if (tab === 'comments' || tab === 'likes') {
      await fetchMyDynamicsList({ page: 1, pageSize: 50 });
      loadedState.value.comments = true;
      loadedState.value.likes = true;
      return;
    }

    await fetchFollowerList({ page: 1, pageSize: 50 });
    loadedState.value.fans = true;
  } catch {
    showToast({ type: 'fail', message: '加载失败，请稍后重试' });
  } finally {
    loading.value = false;
  }
};

const refresh = async () => {
  if (loading.value) {
    return;
  }
  await fetchByTab(activeTab.value, true);
};

const reload = async () => {
  pageError.value = null;
  await fetchByTab(activeTab.value, true);
};

const openConversation = (conv: Conversation) => {
  const displayName = conv.nickname || conv.targetUserId;
  router.push({
    name: 'ChatDetail',
    params: { targetUserId: conv.targetUserId },
    query: { nickname: displayName, avatar: conv.avatar || defaultAvatar }
  });
};

const openFanChat = (targetUserId: string, nickname: string, avatar: string) => {
  router.push({
    name: 'ChatDetail',
    params: { targetUserId },
    query: { nickname, avatar: avatar || defaultAvatar }
  });
};

const openDynamic = (dynamicId: string) => {
  router.push({ name: 'SocialDetail', params: { id: dynamicId } });
};

const formatTime = (value: string) => {
  if (!value) {
    return '';
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return '';
  }
  const now = new Date();
  const sameDay = date.toDateString() === now.toDateString();
  if (sameDay) {
    return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
  }
  const diff = now.getTime() - date.getTime();
  if (diff < 1000 * 60 * 60 * 24 * 7) {
    const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
    return weekdays[date.getDay()] || '';
  }
  return `${date.getMonth() + 1}/${date.getDate()}`;
};

const previewMessage = (text: string, type: Conversation['lastMessageType']) => {
  if (type === 'image') {
    return '[图片]';
  }
  if (type === 'audio') {
    return '[语音]';
  }
  if (type === 'quick_meow') {
    return '[喵喵卡]';
  }
  return text;
};

watch(activeTab, (tab) => {
  void fetchByTab(tab);
});

onMounted(() => {
  void fetchByTab('private');
});

onActivated(() => {
  if (activeTab.value === 'private') {
    void fetchByTab('private', true);
  }
});
</script>
