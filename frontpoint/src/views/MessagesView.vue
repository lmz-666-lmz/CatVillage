<template>
  <div class="messages-page">
    <AppTopBar title="消息中心" subtitle="私信、互动和粉丝都在这里" kicker="Inbox">
      <template #actions>
        <button class="topbar-action" type="button" aria-label="添加好友" @click="router.push({ name: 'AddFriend' })">
          <van-icon name="add-o" size="20" />
        </button>
      </template>

      <div class="message-search" :class="{ focused: isSearching }">
        <van-icon name="search" size="16" />
        <input
          v-model="searchKeyword"
          type="text"
          placeholder="搜索聊天、昵称或消息内容"
          @focus="isSearching = true"
          @blur="onSearchBlur"
        />
        <button v-if="searchKeyword" type="button" @click="searchKeyword = ''">
          <van-icon name="clear" size="14" />
        </button>
      </div>
    </AppTopBar>

    <nav class="message-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        type="button"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
        <span v-if="badgeForTab(tab.key)">{{ badgeForTab(tab.key) }}</span>
      </button>
      <button class="refresh-btn" type="button" aria-label="刷新" @click="refresh">
        <van-icon name="replay" size="16" />
      </button>
    </nav>

    <main class="messages-content">
      <section v-if="pageError" class="message-state">
        <van-icon name="warning-o" size="34" />
        <strong>消息中心加载失败</strong>
        <span>{{ pageError }}</span>
        <button type="button" @click="reload">重新加载</button>
      </section>

      <section v-else-if="loading" class="message-state">
        <van-loading size="28" color="#f97316" />
        <span>正在加载...</span>
      </section>

      <template v-else>
        <section v-if="activeTab === 'private'" class="message-list">
          <div v-if="searchLoading" class="empty-card">
            <van-loading size="26" color="#f97316" />
            <strong>正在搜索消息</strong>
            <span>会同时匹配昵称和会话内容</span>
          </div>
          <div v-else-if="!searchingPrivate && conversations.length === 0" class="empty-card">
            <van-icon name="chat-o" size="38" />
            <strong>暂无会话</strong>
            <span>在广场互动或添加好友后开始聊天</span>
          </div>
          <div v-else-if="searchingPrivate && visibleConversations.length === 0" class="empty-card">
            <van-icon name="search" size="38" />
            <strong>无搜索结果</strong>
            <span>未找到匹配的昵称或消息内容</span>
          </div>
          <article v-for="conv in visibleConversations" :key="conv.id" class="conversation-card" @click="openConversation(conv)">
            <div class="avatar-wrap">
              <van-image :src="getSafeAvatarUrl(conv.avatar, conv.targetUserId)" fit="cover" width="54" height="54" round>
                <template #error>
                  <img :src="getDefaultUserAvatar(conv.targetUserId)" alt="" width="54" height="54" class="avatar-fallback-img" />
                </template>
              </van-image>
              <b v-if="conv.unreadCount > 0">{{ conv.unreadCount > 99 ? '99+' : conv.unreadCount }}</b>
            </div>
            <div class="conversation-body">
              <div class="conversation-top">
                <strong>{{ conv.nickname || conv.targetUserId }}</strong>
                <time>{{ formatTime(conv.updatedAt) }}</time>
              </div>
              <p>{{ previewMessage(conv.lastMessage, conv.lastMessageType) }}</p>
              <p v-if="searchingPrivate && conv.matchSnippet" class="match-snippet">匹配：{{ conv.matchSnippet }}</p>
            </div>
            <van-icon name="arrow" color="#b6bfcc" />
            <button type="button" class="conversation-delete" @click.stop="deleteConversationOnlyMine(conv)">
              <van-icon name="delete-o" size="16" />
            </button>
          </article>
        </section>

        <section v-else-if="activeTab === 'comments'" class="message-list">
          <div v-if="commentItems.length === 0" class="empty-card">
            <van-icon name="comment-o" size="38" />
            <strong>暂无评论</strong>
            <span>有人评论你的动态时会显示在这里</span>
          </div>
          <article v-for="item in commentItems" :key="item.id" class="notice-card" @click="openDynamic(item.dynamicId)">
            <p class="notice-source">{{ item.content || '查看你的动态' }}</p>
            <div v-if="item.latestComment" class="notice-main">
              <van-image :src="getSafeAvatarUrl(item.latestComment.avatar, item.latestComment.userId)" fit="cover" width="38" height="38" round>
                <template #error>
                  <img :src="getDefaultUserAvatar(item.latestComment.userId)" alt="" width="38" height="38" class="avatar-fallback-img" />
                </template>
              </van-image>
              <div>
                <div class="notice-title">
                  <strong>{{ item.latestComment.username }}</strong>
                  <time>{{ formatTime(item.latestComment.createdAt) }}</time>
                </div>
                <p>{{ item.latestComment.content }}</p>
                <span v-if="item.commentCount > 1">查看全部 {{ item.commentCount }} 条评论</span>
              </div>
            </div>
          </article>
        </section>

        <section v-else-if="activeTab === 'likes'" class="message-list">
          <div v-if="likeItems.length === 0" class="empty-card">
            <van-icon name="like-o" size="38" />
            <strong>暂无赞</strong>
            <span>有人赞你的动态时会显示在这里</span>
          </div>
          <article v-for="item in likeItems" :key="item.id" class="notice-card" @click="openDynamic(item.dynamicId)">
            <p class="notice-source">{{ item.content || '查看你的动态' }}</p>
            <div class="notice-main">
              <div class="avatar-stack">
                <van-image
                  v-for="(liker, idx) in (item.recentLikers || []).slice(0, 4)"
                  :key="liker.userId"
                  :src="getSafeAvatarUrl(liker.avatar, liker.userId)"
                  width="34"
                  height="34"
                  round
                  fit="cover"
                  :style="{ marginLeft: idx > 0 ? '-10px' : '0', zIndex: 4 - idx }"
                >
                  <template #error>
                    <img :src="getDefaultUserAvatar(liker.userId)" alt="" width="34" height="34" class="avatar-fallback-img" />
                  </template>
                </van-image>
              </div>
              <div>
                <p>
                  <template v-for="(liker, idx) in (item.recentLikers || []).slice(0, 2)" :key="liker.userId">
                    <strong>{{ liker.username }}</strong><template v-if="idx < Math.min((item.recentLikers || []).length, 2) - 1">、</template>
                  </template>
                  <template v-if="item.likeCount > 2"> 等 {{ item.likeCount }} 人</template>
                  赞了你的动态
                </p>
                <time>{{ formatTime(item.updatedAt) }}</time>
              </div>
            </div>
          </article>
        </section>

        <section v-else class="message-list">
          <div v-if="fans.length === 0" class="empty-card">
            <van-icon name="friends-o" size="38" />
            <strong>暂无粉丝</strong>
            <span>发布精彩内容，吸引更多村民关注你</span>
          </div>
          <article v-for="friend in fans" :key="friend.id" class="conversation-card" @click="openFanChat(friend.userId, friend.nickname, friend.avatar)">
            <div class="avatar-wrap">
              <van-image :src="getSafeAvatarUrl(friend.avatar, friend.userId)" fit="cover" width="54" height="54" round>
                <template #error>
                  <img :src="getDefaultUserAvatar(friend.userId)" alt="" width="54" height="54" class="avatar-fallback-img" />
                </template>
              </van-image>
            </div>
            <div class="conversation-body">
              <div class="conversation-top">
                <strong>{{ friend.nickname }}</strong>
                <em v-if="friend.isFollowing">已关注</em>
              </div>
              <p>点击开始聊天</p>
            </div>
            <van-icon name="arrow" color="#b6bfcc" />
          </article>
        </section>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onActivated, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { showConfirmDialog, showToast } from 'vant';
import AppTopBar from '@/components/AppTopBar.vue';
import { useMessaging } from '@/composables/useMessaging';
import type { Conversation } from '@/types/message';
import type { DynamicResponse } from '@/types/social';
import { useSocialFeatures } from '@/composables/useSocialFeatures';
import { getDefaultUserAvatar, getSafeAvatarUrl } from '@/utils/image';
import { getUnreadSummary, searchConversations } from '@/api/message';
import {
  applyNotificationSettings,
  formatBadgeCount,
  markNoticeCategorySeen,
  SETTINGS_CHANGED_EVENT,
  type UnreadSummary
} from '@/utils/userSettings';

const router = useRouter();
const { fetchConversationList, fetchFollowerList, removeConversation, getCurrentConversations, getCurrentFollowers } = useMessaging();
const { fetchMyDynamicsList, getCurrentDynamics } = useSocialFeatures();

const loading = ref(false);
const pageError = ref<string | null>(null);
const searchKeyword = ref('');
const isSearching = ref(false);
const activeTab = ref<'private' | 'comments' | 'likes' | 'fans'>('private');
const loadedState = ref({ private: false, comments: false, likes: false, fans: false });
const searchLoading = ref(false);
const searchResults = ref<Conversation[]>([]);
const rawUnreadSummary = ref<UnreadSummary>({ privateMessages: 0, comments: 0, likes: 0, followers: 0, total: 0 });
const displayUnreadSummary = ref<UnreadSummary>({ privateMessages: 0, comments: 0, likes: 0, followers: 0, total: 0 });
let conversationPollingTimer: ReturnType<typeof setInterval> | null = null;
let searchTimer: ReturnType<typeof setTimeout> | null = null;

const tabs = [
  { key: 'private', label: '私信' },
  { key: 'comments', label: '评论' },
  { key: 'likes', label: '赞' },
  { key: 'fans', label: '粉丝' }
] as const;

const conversations = computed(() => getCurrentConversations.value);
const fans = computed(() => getCurrentFollowers.value);
const searchingPrivate = computed(() => activeTab.value === 'private' && !!searchKeyword.value.trim());
const visibleConversations = computed(() => searchingPrivate.value ? searchResults.value : conversations.value);
const totalUnread = computed(() => displayUnreadSummary.value.privateMessages || conversations.value.reduce((s, c) => s + (c.unreadCount || 0), 0));

const onSearchBlur = () => { setTimeout(() => { if (!searchKeyword.value) isSearching.value = false; }, 200); };

const badgeForTab = (tab: 'private' | 'comments' | 'likes' | 'fans') => {
  const value = tab === 'private'
    ? totalUnread.value
    : tab === 'comments'
      ? displayUnreadSummary.value.comments
      : tab === 'likes'
        ? displayUnreadSummary.value.likes
        : displayUnreadSummary.value.followers;
  return formatBadgeCount(value);
};

interface DynamicNoticeItem {
  id: string;
  dynamicId: string;
  content: string;
  commentCount: number;
  likeCount: number;
  recentLikers?: DynamicResponse['recentLikers'];
  latestComment?: DynamicResponse['latestComment'];
  updatedAt: string;
}

const commentItems = computed<DynamicNoticeItem[]>(() =>
  getCurrentDynamics.value
    .filter(i => (i.commentCount || 0) > 0)
    .map(i => ({ id: `c-${i.id}`, dynamicId: i.id, content: i.content || '', commentCount: i.commentCount || 0, likeCount: i.likeCount || 0, latestComment: i.latestComment, recentLikers: i.recentLikers, updatedAt: i.latestComment?.createdAt || i.createdAt }))
);

const likeItems = computed<DynamicNoticeItem[]>(() =>
  getCurrentDynamics.value
    .filter(i => (i.likeCount || 0) > 0)
    .map(i => ({ id: `l-${i.id}`, dynamicId: i.id, content: i.content || '', commentCount: i.commentCount || 0, likeCount: i.likeCount || 0, recentLikers: i.recentLikers, latestComment: i.latestComment, updatedAt: i.createdAt }))
);

const fetchByTab = async (tab: string, force = false) => {
  if (loading.value) return;
  if (loadedState.value[tab as keyof typeof loadedState.value] && !force) return;
  loading.value = true;
  pageError.value = null;
  try {
    if (tab === 'private') {
      await fetchConversationList({ page: 1, pageSize: 20 });
      loadedState.value.private = true;
      await refreshUnreadSummary();
      return;
    }
    if (tab === 'comments' || tab === 'likes') {
      await fetchMyDynamicsList({ page: 1, pageSize: 50 });
      loadedState.value.comments = true;
      loadedState.value.likes = true;
      markNoticeCategorySeen(tab === 'comments' ? 'comments' : 'likes', rawUnreadSummary.value);
      displayUnreadSummary.value = applyNotificationSettings(rawUnreadSummary.value);
      return;
    }
    await fetchFollowerList({ page: 1, pageSize: 50 });
    loadedState.value.fans = true;
    markNoticeCategorySeen('followers', rawUnreadSummary.value);
    displayUnreadSummary.value = applyNotificationSettings(rawUnreadSummary.value);
  } catch {
    showToast({ type: 'fail', message: '加载失败，请稍后重试' });
  } finally {
    loading.value = false;
  }
};

const refreshUnreadSummary = async () => {
  try {
    const response = await getUnreadSummary();
    rawUnreadSummary.value = {
      privateMessages: response.data.privateMessages || 0,
      comments: response.data.comments || 0,
      likes: response.data.likes || 0,
      followers: response.data.followers || 0,
      total: response.data.total || 0
    };
    displayUnreadSummary.value = applyNotificationSettings(rawUnreadSummary.value);
  } catch {
    displayUnreadSummary.value = applyNotificationSettings(rawUnreadSummary.value);
  }
};

const runConversationSearch = async () => {
  const q = searchKeyword.value.trim();
  if (!q) {
    searchResults.value = [];
    return;
  }
  searchLoading.value = true;
  try {
    const response = await searchConversations({ q, page: 1, pageSize: 20 });
    searchResults.value = response.data.list || [];
  } catch {
    searchResults.value = [];
    showToast({ type: 'fail', message: '搜索失败，请稍后重试' });
  } finally {
    searchLoading.value = false;
  }
};

const refresh = () => { if (!loading.value) void fetchByTab(activeTab.value, true); };
const reload = () => { pageError.value = null; void fetchByTab(activeTab.value, true); };
const syncDisplayedUnread = () => {
  displayUnreadSummary.value = applyNotificationSettings(rawUnreadSummary.value);
};

const openConversation = (conv: Conversation) => {
  router.push({ name: 'ChatDetail', params: { targetUserId: conv.targetUserId }, query: { nickname: conv.nickname || conv.targetUserId, avatar: getSafeAvatarUrl(conv.avatar, conv.targetUserId) } });
};
const openFanChat = (targetUserId: string, nickname: string, avatar: string) => {
  router.push({ name: 'ChatDetail', params: { targetUserId }, query: { nickname, avatar: getSafeAvatarUrl(avatar, targetUserId) } });
};
const deleteConversationOnlyMine = async (conv: Conversation) => {
  try {
    await showConfirmDialog({
      title: '删除聊天记录',
      message: '仅删除你这边的聊天记录，不会影响对方。'
    });
  } catch {
    return;
  }
  try {
    await removeConversation(conv.targetUserId);
    await fetchByTab('private', true);
    showToast({ type: 'success', message: '聊天记录已删除' });
  } catch {
    showToast({ type: 'fail', message: '删除失败，请稍后重试' });
  }
};
const openDynamic = (dynamicId: string) => router.push({ name: 'SocialDetail', params: { id: dynamicId } });

const formatTime = (value: string) => {
  if (!value) return '';
  const d = new Date(value); if (Number.isNaN(d.getTime())) return '';
  const now = new Date();
  if (d.toDateString() === now.toDateString()) return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
  const diff = now.getTime() - d.getTime();
  if (diff < 604800000) return ['周日','周一','周二','周三','周四','周五','周六'][d.getDay()];
  return `${d.getMonth() + 1}/${d.getDate()}`;
};
const previewMessage = (text: string, type: Conversation['lastMessageType']) => {
  if (type === 'image') return '[图片]';
  if (type === 'audio') return '[语音]';
  if (type === 'quick_meow') return '[喵喵卡]';
  return text || '暂无消息';
};

watch(activeTab, t => { void fetchByTab(t); });
watch(searchKeyword, () => {
  if (searchTimer) clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    if (activeTab.value === 'private') void runConversationSearch();
  }, 300);
});
onMounted(() => {
  void Promise.all([fetchByTab('private'), refreshUnreadSummary()]);
  conversationPollingTimer = setInterval(() => {
    void refreshUnreadSummary();
    if (activeTab.value === 'private' && !loading.value && !searchKeyword.value.trim()) {
      void fetchByTab('private', true);
    }
  }, 5000);
  window.addEventListener(SETTINGS_CHANGED_EVENT, syncDisplayedUnread);
});
onActivated(() => { void refreshUnreadSummary(); if (activeTab.value === 'private') void fetchByTab('private', true); });
onBeforeUnmount(() => {
  if (conversationPollingTimer) {
    clearInterval(conversationPollingTimer);
    conversationPollingTimer = null;
  }
  if (searchTimer) {
    clearTimeout(searchTimer);
    searchTimer = null;
  }
  window.removeEventListener(SETTINGS_CHANGED_EVENT, syncDisplayedUnread);
});
</script>

<style scoped>
.avatar-fallback-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 999px;
}

.messages-page {
  min-height: 100dvh;
  padding: 0 16px 104px;
  background: var(--cv-page-gradient);
}

.message-search {
  display: flex;
  align-items: center;
  gap: 9px;
  height: 44px;
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.84);
  padding: 0 12px;
  color: var(--cv-muted);
  transition: border-color 0.16s ease, box-shadow 0.16s ease;
}

.message-search.focused {
  border-color: var(--cv-accent);
  box-shadow: 0 10px 22px rgba(249, 115, 22, 0.09);
}

.message-search input {
  min-width: 0;
  flex: 1;
  border: 0;
  background: transparent;
  color: var(--cv-ink);
  outline: none;
  font-size: 14px;
  font-weight: 700;
}

.message-search button {
  display: grid;
  width: 24px;
  height: 24px;
  place-items: center;
  border: 0;
  background: transparent;
  color: #9aa5b5;
}

.message-tabs {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 12px 0 4px;
  overflow-x: auto;
  scrollbar-width: none;
}

.message-tabs::-webkit-scrollbar {
  display: none;
}

.message-tabs button {
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  gap: 5px;
  min-width: 66px;
  border: 1px solid #dde5ee;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.75);
  color: var(--cv-muted);
  padding: 9px 13px;
  font-size: 13px;
  font-weight: 900;
}

.message-tabs button.active {
  border-color: var(--cv-ink);
  background: var(--cv-ink);
  color: #fff;
}

.message-tabs span,
.avatar-wrap b {
  display: inline-flex;
  min-width: 18px;
  height: 18px;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  background: #ef4444;
  color: #fff;
  padding: 0 5px;
  font-size: 10px;
  font-weight: 900;
}

.message-tabs .refresh-btn {
  min-width: 40px;
  width: 40px;
  padding: 9px 0;
}

.messages-content,
.message-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.messages-content {
  padding-top: 10px;
}

.message-state,
.empty-card {
  display: grid;
  min-height: 200px;
  place-items: center;
  gap: 8px;
  border: 1px solid var(--cv-card-border);
  border-radius: var(--cv-card-radius);
  background: var(--cv-card-bg);
  padding: 24px;
  text-align: center;
  color: var(--cv-muted);
  box-shadow: var(--cv-card-shadow);
}

.message-state strong,
.empty-card strong {
  color: var(--cv-ink);
  font-size: 17px;
  font-weight: 900;
}

.message-state button {
  border: 0;
  border-radius: 14px;
  background: var(--cv-ink);
  color: #fff;
  padding: 10px 15px;
  font-weight: 900;
}

.conversation-card,
.notice-card {
  display: flex;
  align-items: center;
  gap: 12px;
  border: 1px solid var(--cv-card-border);
  border-radius: var(--cv-card-radius);
  background: var(--cv-card-bg);
  padding: 13px;
  box-shadow: var(--cv-card-shadow);
}

.conversation-delete {
  display: grid;
  width: 34px;
  height: 34px;
  flex-shrink: 0;
  place-items: center;
  border: 0;
  border-radius: 12px;
  background: #fff1f2;
  color: #e11d48;
}

.avatar-wrap {
  position: relative;
  flex-shrink: 0;
}

.avatar-wrap i {
  position: absolute;
  right: 2px;
  bottom: 2px;
  width: 11px;
  height: 11px;
  border: 2px solid #fff;
  border-radius: 999px;
  background: #cbd5e1;
}

.avatar-wrap i.online {
  background: #22c55e;
}

.avatar-wrap b {
  position: absolute;
  top: -3px;
  right: -6px;
  border: 2px solid #fff;
}

.conversation-body {
  min-width: 0;
  flex: 1;
}

.conversation-top,
.notice-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.conversation-top strong,
.notice-title strong {
  overflow: hidden;
  color: var(--cv-ink);
  font-size: 15px;
  font-weight: 900;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conversation-top time,
.notice-title time,
.notice-main time {
  color: var(--cv-muted);
  font-size: 11px;
  font-weight: 800;
}

.conversation-top em {
  flex-shrink: 0;
  border-radius: 999px;
  background: rgba(249,115,22,0.08);
  color: var(--cv-accent);
  padding: 3px 8px;
  font-size: 11px;
  font-style: normal;
  font-weight: 900;
}

.conversation-body p,
.notice-main p {
  margin: 4px 0 0;
  overflow: hidden;
  color: var(--cv-muted);
  font-size: 13px;
  line-height: 1.45;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.conversation-body .match-snippet {
  margin-top: 5px;
  border-radius: 10px;
  background: #fff7ed;
  color: #c2410c;
  padding: 5px 8px;
  font-size: 12px;
  font-weight: 800;
}

.notice-card {
  display: block;
}

.notice-source {
  display: -webkit-box;
  margin: 0 0 11px;
  overflow: hidden;
  border-radius: 14px;
  background: #f4f7fb;
  color: var(--cv-muted);
  padding: 10px;
  font-size: 13px;
  line-height: 1.45;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.notice-main {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.notice-main > div:last-child {
  min-width: 0;
  flex: 1;
}

.notice-main span {
  display: inline-block;
  margin-top: 5px;
  color: var(--cv-accent);
  font-size: 12px;
  font-weight: 900;
}

.avatar-stack {
  display: flex;
  flex-shrink: 0;
  align-items: center;
  min-width: 42px;
}

.avatar-stack :deep(.van-image) {
  border: 2px solid #fff;
  box-shadow: 0 4px 10px rgba(23, 32, 51, 0.08);
}
</style>
