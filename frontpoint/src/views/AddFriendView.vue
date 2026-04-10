<template>
  <div class="min-h-[100dvh] bg-[#f2f4f8] px-4 pt-4 pb-6">
    <header class="rounded-[22px] bg-white/95 px-4 py-3 shadow-[0_1px_4px_rgba(16,24,40,0.06)]">
      <div class="flex items-center justify-between">
        <button type="button" class="grid h-10 w-10 place-items-center text-[#0b1736]" @click="router.back()">
          <van-icon name="arrow-left" size="24" />
        </button>
        <h1 class="text-[22px] font-black tracking-tight text-[#0b1736]">添加好友</h1>
        <button type="button" class="grid h-10 w-10 place-items-center text-[#ff6b35]" @click="searchNow">
          <van-icon name="search" size="23" />
        </button>
      </div>
    </header>

    <section class="mt-4 rounded-[18px] bg-white px-4 py-3 shadow-[0_1px_4px_rgba(16,24,40,0.05)]">
      <div class="text-[12px] text-[#7d869b]">我的喵村号：{{ myMiaoId }}</div>
      <div class="mt-2 rounded-xl bg-[#fff4ef] px-3 py-2 text-[13px] text-[#cc5f36]">通过猫村号或手机号快速找到好友</div>
    </section>

    <section class="mt-5 flex items-center justify-between px-1">
      <h2 class="text-[18px] font-black text-[#071233]">可能感兴趣的人</h2>
      <button
        type="button"
        class="text-[14px] font-extrabold text-[#ff6b35] disabled:text-[#c7ccd8]"
        :disabled="!hasMore || loading"
        @click="loadMore"
      >
        查看更多
      </button>
    </section>

    <section class="mt-3 rounded-[18px] border border-[#e4eaf4] bg-white px-3 py-3 shadow-[0_2px_8px_rgba(16,24,40,0.04)]">
      <div class="flex h-11 items-center gap-2 rounded-[12px] bg-[#f1f4fa] px-3">
        <van-icon name="search" class="text-[#8895ab]" size="19" />
        <input
          v-model="keyword"
          type="text"
          class="h-full flex-1 bg-transparent text-[15px] text-[#22314f] outline-none placeholder:text-[#9aa8c0]"
          placeholder="搜索猫村号/手机号"
          @keyup.enter="searchNow"
        />
        <button type="button" class="rounded-lg bg-[#ff6b35] px-3 py-1.5 text-[12px] font-bold text-white" @click="searchNow">
          搜索
        </button>
      </div>
    </section>

    <section class="mt-3 space-y-3">
      <div v-if="loading && users.length === 0" class="py-12 text-center">
        <van-loading size="24" />
      </div>

      <div
        v-else-if="users.length === 0"
        class="rounded-[18px] border border-[#e2e8f2] bg-white px-4 py-10 text-center text-[15px] text-[#6f7b92]"
      >
        暂无匹配用户，换个关键词试试
      </div>

      <article
        v-for="user in users"
        :key="user.id"
        class="rounded-[22px] border border-[#e5e9f2] bg-white px-4 py-4 shadow-[0_2px_8px_rgba(16,24,40,0.04)]"
      >
        <div class="flex items-center gap-3">
          <van-image :src="resolveAvatar(user.avatar)" fit="cover" width="66" height="66" round />

          <div class="min-w-0 flex-1">
            <div class="truncate text-[18px] font-black text-[#111a33]">{{ user.nickname || user.username }}</div>
            <div class="mt-1 flex flex-wrap items-center gap-2">
              <span class="rounded-full bg-[#ffe9df] px-2.5 py-1 text-[12px] font-bold text-[#d84a1b]">{{ resolveStyleTag(user) }}</span>
              <span class="rounded-full bg-[#eef2f8] px-2.5 py-1 text-[12px] font-bold text-[#66718a]">猫村号: {{ resolveMiaoId(user) }}</span>
            </div>
          </div>

          <button
            type="button"
            class="h-11 min-w-[84px] rounded-[14px] px-4 text-[14px] font-black text-white shadow-[0_8px_18px_rgba(255,107,53,0.24)] disabled:opacity-60"
            :class="user.isFollowing ? 'bg-[#97a2b6]' : 'bg-[#ff6b35]'"
            :disabled="followingUserId === user.userId"
            @click="toggleFollow(user)"
          >
            {{ user.isFollowing ? '已关注' : '关注' }}
          </button>
        </div>

        <button
          type="button"
          class="mt-3 w-full rounded-xl bg-[#f5f7fc] py-2 text-[14px] font-semibold text-[#4f5c79]"
          @click="startChat(user)"
        >
          发消息
        </button>
      </article>

      <div v-if="loading && users.length > 0" class="py-4 text-center text-[13px] text-[#8a94aa]">加载中...</div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';
import { toggleFollowUser } from '@/api/social';
import { useMessaging } from '@/composables/useMessaging';
import type { Friend } from '@/types/message';
import { getUserDisplayProfile } from '@/utils/userProfile';

const router = useRouter();
const { fetchFriendList } = useMessaging();

const defaultAvatar = 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg';

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
      avatar: resolveAvatar(user.avatar)
    }
  });
};

const resolveMiaoId = (user: Friend) => {
  const username = (user.username || '').trim();
  if (username) {
    return username;
  }
  const userId = (user.userId || user.id || '').trim();
  return userId ? userId.slice(0, 10) : '未设置';
};

const resolveAvatar = (value?: string) => value || defaultAvatar;

const resolveStyleTag = (user: Friend) => {
  const styles = ['英短蓝猫', '中华田园猫', '暹罗猫', '缅因猫', '布偶猫'];
  const seed = (user.userId || user.id || '').split('').reduce((acc, cur) => acc + cur.charCodeAt(0), 0);
  return styles[seed % styles.length] || '猫村居民';
};

onMounted(() => {
  myMiaoId.value = getUserDisplayProfile().miaoId;
  void loadUsers(true);
});
</script>
