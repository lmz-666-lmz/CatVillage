<template>
  <div class="min-h-[100dvh] bg-[#f4f5fb] px-4 pt-3 pb-8">
    <header class="sticky top-0 z-20 -mx-4 flex items-center justify-between bg-[#f4f5fb]/95 px-4 py-2 backdrop-blur-md">
      <button type="button" class="grid h-10 w-10 place-items-center text-[#ff6b35]" @click="router.back()">
        <van-icon name="arrow-left" size="22" />
      </button>
      <h1 class="text-[23px] font-extrabold tracking-tight text-[#ff6b35]">我的收藏</h1>
      <button type="button" class="grid h-10 w-10 place-items-center text-[#5e493f]" @click="refresh">
        <van-icon name="ellipsis" size="22" />
      </button>
    </header>

    <section class="mt-4 flex gap-3 overflow-x-auto pb-1">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        type="button"
        class="shrink-0 rounded-full px-4 py-2 text-[15px] font-semibold transition-colors"
        :class="activeTab === tab.key ? 'bg-[#ff6b35] text-white shadow-[0_8px_18px_rgba(255,107,53,0.22)]' : 'bg-[#eeeff6] text-[#55433d]'"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </section>

    <section class="mt-4 space-y-4">
      <div v-if="loading" class="py-16 text-center">
        <van-loading size="26" color="#ff6b35" />
        <div class="mt-3 text-sm text-[#6f7790]">正在加载收藏内容...</div>
      </div>

      <div v-else-if="visibleFavorites.length === 0" class="rounded-[20px] border border-[#e5e7f0] bg-white p-8 text-center">
        <div class="text-4xl">🐾</div>
        <div class="mt-3 text-[18px] font-extrabold text-[#1f2432]">这里还是空的</div>
        <div class="mt-2 text-[14px] leading-relaxed text-[#6f7790]">去广场收藏你喜欢的猫咪动态，收藏后会自动出现在这里。</div>
        <button type="button" class="mt-5 rounded-full bg-[#ff6b35] px-5 py-2 text-[15px] font-bold text-white" @click="router.push({ name: 'Social' })">
          去广场看看
        </button>
      </div>

      <article
        v-for="item in visibleFavorites"
        :key="item.id"
        class="overflow-hidden rounded-[20px] border border-[#e6e8f2] bg-white shadow-[0_4px_12px_rgba(20,27,43,0.05)]"
      >
        <div class="flex items-start justify-between gap-3 px-4 pt-4">
          <button type="button" class="flex min-w-0 flex-1 items-center gap-3 text-left" @click="openDetail(item.id)">
            <div class="h-11 w-11 shrink-0 overflow-hidden rounded-full bg-[#f3ece7]">
              <van-image :src="item.avatar || defaultAvatar" fit="cover" width="44" height="44" round />
            </div>
            <div class="min-w-0">
              <div class="truncate text-[17px] font-black text-[#11192a]">{{ item.username || '橘猫派大星' }}</div>
              <div class="mt-1 flex items-center gap-2 text-[12px] text-[#6b5950]">
                <span class="rounded-full bg-[#fff1ea] px-2 py-0.5 text-[#ff6b35]">{{ item.categoryLabel }}</span>
                <span>收藏于 {{ formatRelativeTime(item.createdAt) }}</span>
              </div>
            </div>
          </button>

          <button type="button" class="grid h-10 w-10 place-items-center text-[#6b5950]" @click="toggleFavorite(item)">
            <van-icon name="star" size="20" class="text-[#ff6b35]" />
          </button>
        </div>

        <button type="button" class="block w-full text-left" @click="openDetail(item.id)">
          <p class="mt-3 px-4 whitespace-pre-wrap text-[15px] leading-relaxed text-[#11192a]">{{ item.content }}</p>

          <div v-if="item.images && item.images.length" class="mt-3 px-4 pb-4">
            <van-image
              :src="item.previewImage"
              fit="cover"
              width="100%"
              height="250"
              radius="16"
            />
          </div>
        </button>

        <div class="flex items-center justify-between px-4 py-3 text-sm">
          <div class="flex items-center gap-6">
            <div class="flex items-center gap-2 text-[#2f2521]">
              <van-icon name="like-o" size="19" />
              <span class="text-[15px]">{{ formatSocialCount(item.likeCount) }}</span>
            </div>
            <div class="flex items-center gap-2 text-[#2f2521]">
              <van-icon name="star" size="19" class="text-[#ff6b35]" />
              <span class="text-[15px]">{{ formatSocialCount(item.favoriteCount) }}</span>
            </div>
            <div class="flex items-center gap-2 text-[#2f2521]">
              <van-icon name="chat-o" size="19" />
              <span class="text-[15px]">{{ item.commentCount || 0 }}</span>
            </div>
          </div>

          <button type="button" class="rounded-full bg-[#fff2ea] px-3 py-1.5 text-[13px] font-bold text-[#ff6b35]" @click="toggleFavorite(item)">
            取消收藏
          </button>
        </div>
      </article>

      <div v-if="!loading && visibleFavorites.length > 0" class="py-3 text-center text-[13px] text-[#9a97a0]">
        没有更多收藏啦，去广场转转吧
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';
import { getDynamicsList, toggleFavoriteDynamic } from '@/api/social';
import type { SocialDynamic } from '@/types/social';
import { formatRelativeTime } from '@/utils/date';
import { applyDisplayProfileToDynamic } from '@/utils/userProfile';

type FavoriteCategoryKey = 'all' | 'diary' | 'guide' | 'photo';

type FavoriteItem = SocialDynamic & {
  categoryKey: FavoriteCategoryKey;
  categoryLabel: string;
  previewImage: string;
};

const router = useRouter();

const tabs: Array<{ key: FavoriteCategoryKey; label: string }> = [
  { key: 'all', label: '全部收藏' },
  { key: 'diary', label: '喵村日记' },
  { key: 'guide', label: '养宠攻略' },
  { key: 'photo', label: '萌图摄影' }
];

const activeTab = ref<FavoriteCategoryKey>('all');
const loading = ref(false);
const favorites = ref<FavoriteItem[]>([]);
const defaultAvatar = 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg';

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

const inferCategory = (item: SocialDynamic): { key: FavoriteCategoryKey; label: string } => {
  const text = `${item.content || ''} ${item.catName || ''}`.toLowerCase();
  if (/[图照摄拍美萌]/.test(text) || (item.images?.length || 0) > 0 && text.includes('日常') === false) {
    return { key: 'photo', label: '萌图摄影' };
  }
  if (/(攻略|喂养|护理|疫苗|体检|饲养|新手)/.test(text)) {
    return { key: 'guide', label: '养宠攻略' };
  }
  return { key: 'diary', label: '喵村日记' };
};

const getPreviewImage = (item: SocialDynamic) => {
  if (item.images && item.images.length > 0) {
    return item.images[0] || defaultAvatar;
  }
  return defaultAvatar;
};

const loadAllFavorites = async () => {
  loading.value = true;
  try {
    const pageSize = 20;
    const collected: FavoriteItem[] = [];

    for (let page = 1; page <= 10; page += 1) {
      const response = await getDynamicsList({ page, pageSize });
      const list = (response.data.list || []) as SocialDynamic[];
      const favoritesFromPage = list
        .filter((item) => item.isFavorited)
        .map((item) => {
          const normalized = applyDisplayProfileToDynamic(item);
          const category = inferCategory(item);
          return {
            ...normalized,
            categoryKey: category.key,
            categoryLabel: category.label,
            previewImage: getPreviewImage(normalized)
          };
        });

      collected.push(...favoritesFromPage);
      if (list.length < pageSize) {
        break;
      }
    }

    favorites.value = collected.sort((left, right) => new Date(right.createdAt).getTime() - new Date(left.createdAt).getTime());
  } catch (error) {
    console.error('加载收藏列表失败:', error);
    showToast({ type: 'fail', message: '收藏列表加载失败' });
  } finally {
    loading.value = false;
  }
};

const refresh = async () => {
  await loadAllFavorites();
};

const visibleFavorites = computed(() => {
  if (activeTab.value === 'all') {
    return favorites.value;
  }
  return favorites.value.filter((item) => item.categoryKey === activeTab.value);
});

const openDetail = (id: string) => {
  router.push({ name: 'SocialDetail', params: { id } });
};

const toggleFavorite = async (item: FavoriteItem) => {
  try {
    const response = await toggleFavoriteDynamic(item.id);
    if (!response.data.isFavorited) {
      favorites.value = favorites.value.filter((favorite) => favorite.id !== item.id);
      showToast({ message: '已取消收藏' });
    }
  } catch (error) {
    console.error('收藏切换失败:', error);
    showToast({ type: 'fail', message: '操作失败，请稍后重试' });
  }
};

onMounted(() => {
  void refresh();
});
</script>