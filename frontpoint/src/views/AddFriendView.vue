<template>
  <div class="add-friend-page">
    <AppTopBar title="添加好友" subtitle="通过猫村号或昵称找到村民" kicker="FRIENDS" back @back="router.back()">
      <template #actions>
        <button class="topbar-action" type="button" aria-label="搜索" @click="searchNow">
          <van-icon name="search" size="20" />
        </button>
      </template>
    </AppTopBar>

    <!-- My Miao ID -->
    <section class="miao-id-card">
      <div class="miao-id-label">我的喵村号：{{ myMiaoId }}</div>
      <div class="miao-id-tip">通过猫村号或手机号快速找到好友</div>
    </section>

    <!-- Search -->
    <section class="search-card">
      <div class="search-row">
        <van-icon name="search" class="search-icon" size="19" />
        <input
          v-model="keyword"
          type="text"
          class="search-input"
          placeholder="搜索猫村号/手机号"
          @keyup.enter="searchNow"
        />
        <button type="button" class="search-btn" @click="searchNow">
          搜索
        </button>
      </div>
    </section>

    <!-- Section Header: 可能感兴趣的人 -->
    <div class="section-header">
      <h2 class="section-title">可能感兴趣的人</h2>
      <button
        type="button"
        class="section-more"
        :disabled="!hasMore || loading"
        @click="loadMore"
      >
        查看更多
      </button>
    </div>

    <!-- User List -->
    <div class="user-list">
      <div v-if="loading && users.length === 0" class="empty-state">
        <van-loading size="24" />
      </div>

      <div
        v-else-if="users.length === 0"
        class="empty-card"
      >
        暂无匹配用户，换个关键词试试
      </div>

      <article
        v-for="user in users"
        :key="user.id"
        class="user-card"
      >
        <div class="user-card-row">
          <van-image :src="resolveAvatar(user)" fit="cover" width="66" height="66" round>
            <template #error>
              <img :src="getDefaultUserAvatar(user.userId || user.username || user.id)" alt="" width="66" height="66" class="avatar-fallback-img" />
            </template>
          </van-image>

          <div class="user-info">
            <div class="user-name">{{ user.nickname || user.username }}</div>
            <div class="user-tags">
              <span class="tag tag-warm">{{ resolveCatSummary(user) }}</span>
              <span class="tag tag-cool">猫村号: {{ resolveMiaoId(user) }}</span>
            </div>
          </div>

          <button
            type="button"
            class="follow-btn"
            :class="user.isFollowing ? 'follow-btn--following' : 'follow-btn--follow'"
            :disabled="followingUserId === user.userId"
            @click="toggleFollow(user)"
          >
            {{ user.isFollowing ? '已关注' : '关注' }}
          </button>
        </div>

        <button
          type="button"
          class="msg-btn"
          @click="startChat(user)"
        >
          发消息
        </button>
      </article>

      <div v-if="loading && users.length > 0" class="loading-more">加载中...</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';
import AppTopBar from '@/components/AppTopBar.vue';
import { toggleFollowUser } from '@/api/social';
import { useMessaging } from '@/composables/useMessaging';
import type { Friend } from '@/types/message';
import { getUserDisplayProfile } from '@/utils/userProfile';
import { getDefaultUserAvatar, getSafeAvatarUrl } from '@/utils/image';

const router = useRouter();
const { fetchFriendList } = useMessaging();

const keyword = ref('');
const users = ref<Friend[]>([]);
const loading = ref(false);
const page = ref(1);
const pageSize = 12;
const total = ref(0);
const followingUserId = ref('');
const myMiaoId = ref('');

const hasMore = computed(() => users.value.length < total.value);

const mergeUsers = (base: Friend[], extra: Friend[]) => {
  const map = new Map<string, Friend>();
  base.forEach((item) => map.set(item.userId, item));
  extra.forEach((item) => map.set(item.userId, item));
  return Array.from(map.values());
};

const loadUsers = async (reset = false) => {
  if (loading.value) {
    return;
  }

  loading.value = true;
  try {
    if (reset) {
      page.value = 1;
    }

    const res = await fetchFriendList({
      page: page.value,
      pageSize,
      keyword: keyword.value.trim() || undefined
    });

    total.value = res.total || 0;
    const list = res.list || [];
    users.value = reset ? list : mergeUsers(users.value, list);
  } catch {
    showToast({ type: 'fail', message: '加载候选好友失败' });
  } finally {
    loading.value = false;
  }
};

const loadMore = async () => {
  if (!hasMore.value || loading.value) {
    return;
  }
  page.value += 1;
  await loadUsers();
};

const searchNow = async () => {
  await loadUsers(true);
};

const toggleFollow = async (user: Friend) => {
  if (followingUserId.value) {
    return;
  }

  followingUserId.value = user.userId;
  try {
    const res = await toggleFollowUser(user.userId);
    user.isFollowing = !!res.data.isFollowing;
    showToast({ type: 'success', message: user.isFollowing ? `已关注 ${user.nickname}` : `已取消关注 ${user.nickname}` });
  } catch {
    showToast({ type: 'fail', message: '操作失败，请稍后重试' });
  } finally {
    followingUserId.value = '';
  }
};

const startChat = (user: Friend) => {
  router.push({
    name: 'ChatDetail',
    params: { targetUserId: user.userId },
    query: {
      nickname: user.nickname || user.username,
      avatar: resolveAvatar(user)
    }
  });
};

const resolveMiaoId = (user: Friend) => {
  const username = (user.miaoId || user.username || '').trim();
  if (username) {
    return username;
  }
  const userId = (user.userId || user.id || '').trim();
  return userId ? userId.slice(0, 10) : '未设置';
};

const resolveAvatar = (user: Friend) => getSafeAvatarUrl(user.avatar, user.userId || user.username || user.id);

const resolveCatSummary = (user: Friend) => {
  if (user.catSummary) {
    return user.catSummary;
  }
  const names = user.catNames || [];
  if (names.length === 0) {
    return 'TA 的猫咪：暂无公开猫咪';
  }
  if (names.length <= 2) {
    return `TA 的猫咪：${names.join('、')}`;
  }
  return `TA 的猫咪：${names.slice(0, 2).join('、')}等 ${names.length} 只`;
};

onMounted(() => {
  myMiaoId.value = getUserDisplayProfile().miaoId;
  void loadUsers(true);
});
</script>

<style scoped>
.avatar-fallback-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 999px;
}

/* ========== Page ========== */
.add-friend-page {
  min-height: 100dvh;
  padding: 0 16px 104px;
  background: #fff7f0;
}

/* ========== AppTopBar Overrides ========== */
.add-friend-page :deep(.app-topbar) {
  background: linear-gradient(180deg, #fff1e8 0%, #fff8f3 70%, #f8f4ef 100%);
  backdrop-filter: blur(18px);
}

.add-friend-page :deep(.app-topbar-kicker) {
  color: #ff6b35;
}

.add-friend-page :deep(.app-topbar-title h1) {
  color: #102033;
}

.add-friend-page :deep(.app-topbar-title p) {
  color: #7a8494;
}

.add-friend-page :deep(.app-topbar-icon),
.add-friend-page :deep(.topbar-action) {
  border-color: rgba(255, 107, 53, 0.14);
  background: rgba(255, 255, 255, 0.88);
  color: #ff6b35;
  box-shadow: 0 4px 14px rgba(255, 107, 53, 0.08);
}

/* ========== My Miao ID Card ========== */
.miao-id-card {
  margin-top: 16px;
  border-radius: 20px;
  background: #fffbf6;
  padding: 14px 18px;
}

.miao-id-label {
  font-size: 12px;
  font-weight: 700;
  color: #7a8494;
}

.miao-id-tip {
  margin-top: 8px;
  border-radius: 12px;
  background: #fff1e8;
  padding: 10px 14px;
  font-size: 13px;
  font-weight: 600;
  color: #cc5f36;
}

/* ========== Search ========== */
.search-card {
  margin-top: 16px;
  border-radius: 20px;
  background: #ffffff;
  padding: 14px 16px;
  box-shadow: 0 2px 12px rgba(255, 107, 53, 0.06);
}

.search-row {
  display: flex;
  height: 46px;
  align-items: center;
  gap: 10px;
  border-radius: 16px;
  background: #fffaf5;
  padding: 0 14px;
}

.search-icon {
  color: #ff6b35;
  flex-shrink: 0;
}

.search-input {
  height: 100%;
  flex: 1;
  min-width: 0;
  background: transparent;
  font-size: 15px;
  font-weight: 600;
  color: #102033;
  outline: none;
  border: none;
}

.search-input::placeholder {
  color: #9aa3b2;
}

.search-btn {
  flex-shrink: 0;
  border: none;
  border-radius: 12px;
  background: linear-gradient(135deg, #ff8a4c, #ff6b35);
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 700;
  color: #ffffff;
  cursor: pointer;
  transition: opacity 0.14s ease;
}

.search-btn:active {
  opacity: 0.84;
}

/* ========== Section Header ========== */
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 24px;
  padding: 0 2px;
}

.section-title {
  margin: 0;
  font-size: 20px;
  font-weight: 900;
  color: #102033;
}

.section-more {
  border: none;
  background: transparent;
  font-size: 14px;
  font-weight: 700;
  color: #ff6b35;
  cursor: pointer;
  transition: opacity 0.14s ease;
}

.section-more:disabled {
  color: #c7ccd8;
  cursor: default;
}

.section-more:not(:disabled):active {
  opacity: 0.7;
}

/* ========== User List ========== */
.user-list {
  margin-top: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* ========== Empty State ========== */
.empty-state {
  padding: 48px 0;
  text-align: center;
  color: #7a8494;
  font-size: 15px;
  font-weight: 600;
}

.empty-card {
  border-radius: 24px;
  background: #ffffff;
  padding: 48px 20px;
  text-align: center;
  font-size: 15px;
  font-weight: 600;
  color: #7a8494;
  box-shadow: 0 2px 12px rgba(16, 32, 51, 0.04);
}

/* ========== User Card ========== */
.user-card {
  border-radius: 24px;
  background: #ffffff;
  padding: 18px 16px 16px;
  box-shadow: 0 2px 14px rgba(16, 32, 51, 0.05);
}

.user-card-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  min-width: 0;
  flex: 1;
}

.user-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 17px;
  font-weight: 900;
  color: #102033;
}

.user-tags {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-top: 6px;
}

/* ========== Tags ========== */
.tag {
  display: inline-block;
  border-radius: 20px;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 700;
  line-height: 1.4;
}

.tag-warm {
  background: #fff1e8;
  color: #ff6b35;
}

.tag-cool {
  background: #f1f3f6;
  color: #7a8494;
}

/* ========== Follow Button ========== */
.follow-btn {
  flex-shrink: 0;
  min-width: 84px;
  height: 42px;
  border: none;
  border-radius: 14px;
  padding: 0 16px;
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
  transition: opacity 0.14s ease, transform 0.14s ease;
}

.follow-btn:disabled {
  opacity: 0.55;
  cursor: default;
}

.follow-btn:not(:disabled):active {
  transform: scale(0.95);
}

.follow-btn--follow {
  background: #ff6b35;
  color: #ffffff;
  box-shadow: 0 6px 16px rgba(255, 107, 53, 0.22);
}

.follow-btn--following {
  background: #f1f3f6;
  color: #7a8494;
}

/* ========== Message Button ========== */
.msg-btn {
  display: block;
  width: 100%;
  height: 44px;
  margin-top: 14px;
  border: none;
  border-radius: 16px;
  background: #fff1e8;
  font-size: 14px;
  font-weight: 700;
  color: #ff6b35;
  cursor: pointer;
  transition: opacity 0.14s ease;
}

.msg-btn:active {
  opacity: 0.76;
}

/* ========== Loading More ========== */
.loading-more {
  padding: 20px 0;
  text-align: center;
  font-size: 13px;
  font-weight: 600;
  color: #7a8494;
}
</style>
