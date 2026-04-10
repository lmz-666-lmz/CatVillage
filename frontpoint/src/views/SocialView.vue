<template>
  <div class="relative min-h-[100dvh] bg-[#f4f5fb] px-4 pt-3 pb-28">
    <div v-if="error" class="rounded-2xl border border-surface-container-high bg-surface-container-lowest px-4 py-10 text-center text-sm text-on-surface-variant">
      <div class="text-base font-semibold text-on-background">广场加载失败</div>
      <div class="mt-2">{{ error }}</div>
      <van-button class="mt-4" type="primary" @click="reload">重试</van-button>
    </div>

    <div v-else>
    <header class="sticky top-0 z-20 -mx-4 flex min-h-[54px] items-center justify-between bg-[#f4f5fb]/95 px-4 py-2.5 backdrop-blur-md">
      <div class="flex items-center gap-4">
        <h1 class="text-[23px] font-black tracking-tight text-[#FF6B35]">猫村</h1>
        <div class="flex gap-5 text-[20px] font-black">
          <button
            type="button"
            class="relative pb-1"
            :class="activeTab === 'follow' ? 'text-[#FF6B35]' : 'text-on-surface'"
            @click="activeTab = 'follow'"
          >
            关注
            <span v-if="activeTab === 'follow'" class="absolute bottom-0 left-1/2 h-[2px] w-4 -translate-x-1/2 rounded-full bg-[#FF6B35]"></span>
          </button>
          <button
            type="button"
            class="relative pb-1"
            :class="activeTab === 'recommend' ? 'text-[#FF6B35]' : 'text-on-surface'"
            @click="activeTab = 'recommend'"
          >
            发现
            <span v-if="activeTab === 'recommend'" class="absolute bottom-0 left-1/2 h-[2px] w-4 -translate-x-1/2 rounded-full bg-[#FF6B35]"></span>
          </button>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button type="button" class="grid h-10 w-10 place-items-center rounded-full text-[#11192a]" @click="router.push({ name: 'SocialSearch' })">
          <van-icon name="search" size="22" />
        </button>
      </div>
    </header>

    <section class="mt-2.5 space-y-4">
      <div v-if="loading" class="py-10 text-center">
        <van-loading size="24" />
        <div class="mt-3 text-sm text-on-surface-variant">正在加载动态...</div>
      </div>

      <div v-else-if="dynamics.length === 0" class="rounded-2xl border border-surface-container-high bg-surface-container-lowest p-6 text-center">
        <div class="text-3xl">📷</div>
        <div class="mt-3 text-base font-semibold text-on-background">暂无动态</div>
        <div class="mt-1 text-sm text-on-surface-variant">成为第一个分享猫咪日常的人</div>
      </div>

      <div v-else class="space-y-4">
        <article
          v-for="item in dynamics"
          :key="item.id"
          class="overflow-hidden rounded-[18px] border border-[#e6e8f2] bg-white shadow-[0_4px_12px_rgba(20,27,43,0.05)]"
          @click="openDetail(item.id)"
        >
          <div class="flex items-center justify-between gap-3 px-3.5 pt-3.5">
            <div class="flex items-center gap-3 min-w-0">
              <div class="relative">
                <van-image :src="item.avatar || defaultAvatar" fit="cover" width="52" height="52" round />
                <button
                  type="button"
                  class="absolute -bottom-1 -right-1 grid h-5 w-5 place-items-center rounded-full bg-[#ff6b35] text-white"
                  @click.stop
                >
                  <van-icon name="plus" size="10" />
                </button>
              </div>
              <div class="min-w-0">
                <div class="truncate text-[18px] font-black text-[#11192a]">{{ item.username || '橘猫派大星' }}</div>
                <div class="mt-0.5 text-[12px] text-[#6b5950]">{{ formatRelativeTime(item.createdAt) }} · {{ randomLocation(item.id) }}</div>
              </div>
            </div>
            <button type="button" class="text-[#11192a]">
              <van-icon name="ellipsis" size="20" />
            </button>
          </div>

          <p class="mt-3 px-3.5 whitespace-pre-wrap text-[15px] leading-relaxed text-[#11192a]">{{ item.content }}</p>

          <div v-if="item.images && item.images.length" class="mt-3 grid grid-cols-2 gap-2 px-3.5 pb-2.5" :class="item.images.length === 1 ? 'grid-cols-1' : 'grid-cols-2'">
            <van-image
              v-for="(img, idx) in item.images"
              :key="idx"
              :src="img"
              fit="cover"
              width="100%"
              :height="item.images.length === 1 ? '260' : '150'"
              radius="16"
            />
          </div>

          <div class="mt-1 flex items-center justify-between px-4 py-3 text-sm">
            <div class="flex items-center gap-6">
              <button
                type="button"
                class="flex items-center gap-2 text-[#2f2521]"
                :disabled="likingId === item.id"
                @click.stop="toggleLike(item)"
              >
                <van-icon :name="item.isLiked ? 'like' : 'like-o'" size="20" />
                <span class="text-[15px]">{{ formatSocialCount(item.likeCount) }}</span>
              </button>

              <button
                type="button"
                class="flex items-center gap-2 text-[#2f2521]"
                :disabled="favoriteId === item.id"
                @click.stop="toggleFavorite(item)"
              >
                <van-icon :name="item.isFavorited ? 'star' : 'star-o'" size="20" :class="item.isFavorited ? 'text-[#ff6b35]' : ''" />
                <span class="text-[15px]">{{ formatSocialCount(item.favoriteCount) }}</span>
              </button>

              <div class="flex items-center gap-2 text-[#2f2521]">
                <van-icon name="chat-o" size="20" />
                <span class="text-[15px]">{{ item.commentCount || 0 }}</span>
              </div>
            </div>

            <div v-if="item.catName" class="truncate text-[14px] text-[#2f2521] max-w-[120px]">
              🐾 {{ item.catName }}
            </div>
          </div>
        </article>

        <div class="py-2 text-center">
          <button
            v-if="hasMore && !loading"
            type="button"
            class="h-10 rounded-[10px] border border-[#dfe3f0] bg-white px-4 text-[14px] font-semibold text-[#5c5552]"
            :disabled="loadingMore"
            @click="loadMore"
          >
            {{ loadingMore ? '加载中...' : '加载更多' }}
          </button>
          <div v-else-if="!hasMore && dynamics.length > 0" class="text-[13px] text-[#9a97a0]">没有更多了</div>
        </div>
      </div>
    </section>

    <button
      type="button"
      class="fixed bottom-24 left-1/2 z-30 grid h-16 w-16 -translate-x-1/2 place-items-center rounded-full bg-[#ff1f10] text-white shadow-[0_10px_22px_rgba(255,31,16,0.35)]"
      @click="router.push({ name: 'CreatePost' })"
    >
      <van-icon name="plus" size="34" />
    </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';
import { useSocialFeatures } from '@/composables/useSocialFeatures';
import { formatRelativeTime } from '@/utils/date';
import { applyDisplayProfileToDynamic } from '@/utils/userProfile';
import type { SocialDynamic } from '@/types/social';

const router = useRouter();
const activeTab = ref<'follow' | 'recommend'>('recommend');

const { fetchDynamicsList, likeADynamic, unlikeADynamic, toggleFavoriteADynamic } = useSocialFeatures();

const loading = ref(false);
const likingId = ref<string>('');
const favoriteId = ref<string>('');
const loadingMore = ref(false);
const error = ref<string | null>(null);
const dynamics = ref<SocialDynamic[]>([]);
const currentPage = ref(1);
const pageSize = 8;
const hasMore = ref(true);
const defaultAvatar = 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg';

const randomLocation = (seed: string) => {
  const locations = ['上海·滨江公园', '杭州', '成都', '北京', '深圳', '重庆'];
  const idx = seed.split('').reduce((acc, ch) => acc + ch.charCodeAt(0), 0) % locations.length;
  return locations[idx] || '猫村';
};

const formatSocialCount = (value?: number) => {
  const num = value || 0;
  if (num >= 10000) {
    return `${(num / 10000).toFixed(1)}w`;
  }
  if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}k`;
  }
  return String(num);
};

const refresh = async () => {
  if (loading.value) {
    return;
  }
  loading.value = true;
  error.value = null;
  try {
    const res = await fetchDynamicsList({ page: 1, pageSize, scope: activeTab.value === 'follow' ? 'following' : 'all' });
    dynamics.value = (res.list || []).map((item) => applyDisplayProfileToDynamic(item));
    currentPage.value = 1;
    hasMore.value = dynamics.value.length < (res.total || 0);
  } catch (err: unknown) {
    const status = typeof err === 'object' && err !== null && 'response' in err
      ? (err as { response?: { status?: number } }).response?.status
      : undefined;
    error.value = status === 401
      ? '登录已过期，请重新登录后查看广场'
      : '加载失败，请稍后重试';
  } finally {
    loading.value = false;
  }
};

const loadMore = async () => {
  if (loadingMore.value || loading.value || !hasMore.value) {
    return;
  }
  loadingMore.value = true;
  try {
    const nextPage = currentPage.value + 1;
    const res = await fetchDynamicsList({ page: nextPage, pageSize, scope: activeTab.value === 'follow' ? 'following' : 'all' });
    const list = (res.list || []).map((item) => applyDisplayProfileToDynamic(item));
    dynamics.value = [...dynamics.value, ...list];
    currentPage.value = nextPage;
    hasMore.value = dynamics.value.length < (res.total || 0);
  } catch {
    showToast({ type: 'fail', message: '加载更多失败，请稍后重试' });
  } finally {
    loadingMore.value = false;
  }
};

const reload = () => refresh();

const openDetail = (id: string) => {
  router.push({ name: 'SocialDetail', params: { id } });
};

const toggleLike = async (dynamic: SocialDynamic) => {
  if (likingId.value) {
    return;
  }
  likingId.value = dynamic.id;
  try {
    if (dynamic.isLiked) {
      await unlikeADynamic(dynamic.id);
      dynamic.isLiked = false;
      dynamic.likeCount = Math.max(0, (dynamic.likeCount || 0) - 1);
      return;
    }
    await likeADynamic(dynamic.id);
    dynamic.isLiked = true;
    dynamic.likeCount = (dynamic.likeCount || 0) + 1;
  } catch {
    showToast({ type: 'fail', message: '操作失败，请稍后重试' });
  } finally {
    likingId.value = '';
  }
};

const toggleFavorite = async (dynamic: SocialDynamic) => {
  if (favoriteId.value) {
    return;
  }

  favoriteId.value = dynamic.id;
  try {
    const response = await toggleFavoriteADynamic(dynamic.id);
    dynamic.isFavorited = response.isFavorited;
    dynamic.favoriteCount = response.favoriteCount;
  } catch {
    showToast({ type: 'fail', message: '收藏失败，请稍后重试' });
  } finally {
    favoriteId.value = '';
  }
};

onMounted(refresh);

watch(activeTab, () => {
  void refresh();
});
</script>
