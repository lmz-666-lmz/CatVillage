<template>
  <div class="fav-page">
    <!-- Header -->
    <header class="fav-header">
      <button type="button" class="fav-back" @click="router.push({ name: 'UserProfile' })">
        <van-icon name="arrow-left" size="20" />
      </button>
      <div>
        <h1 class="fav-title">我的收藏</h1>
        <p class="fav-sub">珍藏每一份感动与美好</p>
      </div>
      <button type="button" class="refresh-btn" @click="refresh">
        <van-icon name="replay" size="18" />
      </button>
    </header>

    <!-- Tabs -->
    <nav class="fav-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        type="button"
        class="fav-tab"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </nav>

    <!-- Content -->
    <section class="fav-list">
      <div v-if="loading" class="fav-empty">
        <van-loading size="24" color="#ff6b35" />
        <div class="fav-empty-text">正在加载收藏内容...</div>
      </div>

      <div v-else-if="visibleFavorites.length === 0" class="fav-empty">
        <div class="fav-empty-icon">🐾</div>
        <div class="fav-empty-title">这里还是空的</div>
        <div class="fav-empty-text">去广场收藏你喜欢的猫咪动态，收藏后会自动出现在这里</div>
        <button type="button" class="fav-empty-btn" @click="router.push({ name: 'Social' })">
          去广场看看
        </button>
      </div>

      <article
        v-for="item in visibleFavorites"
        :key="item.id"
        class="fav-card"
      >
        <div class="fav-card-header">
          <button type="button" class="fav-author" @click="openDetail(item.id)">
            <van-image :src="getSafeAvatarUrl(item.avatar, item.userId || item.username)" fit="cover" width="44" height="44" round />
            <div class="fav-author-info">
              <div class="fav-author-name">{{ item.username || '猫村村民' }}</div>
              <div class="fav-author-meta">
                <span class="fav-cat-chip">{{ item.categoryLabel }}</span>
                <span>收藏于 {{ formatRelativeTime(item.createdAt) }}</span>
              </div>
            </div>
          </button>

          <button type="button" class="fav-unstar" @click="toggleFavorite(item)">
            <van-icon name="star" size="20" />
          </button>
        </div>

        <button type="button" class="fav-content" @click="openDetail(item.id)">
          <p class="fav-text">{{ item.content }}</p>

          <div v-if="item.images && item.images.length" class="fav-image-wrap">
            <van-image :src="item.previewImage" fit="cover" width="100%" height="220" radius="16" />
          </div>
        </button>

        <div class="fav-card-footer">
          <div class="fav-stats">
            <div class="fav-stat" :class="{ liked: item.isLiked }">
              <van-icon :name="item.isLiked ? 'like' : 'like-o'" size="18" />
              <span>{{ formatSocialCount(item.likeCount) }}</span>
            </div>
            <div class="fav-stat starred">
              <van-icon name="star" size="18" />
              <span>{{ formatSocialCount(item.favoriteCount) }}</span>
            </div>
            <div class="fav-stat">
              <van-icon name="chat-o" size="18" />
              <span>{{ item.commentCount || 0 }}</span>
            </div>
          </div>

          <button type="button" class="fav-remove-btn" @click="toggleFavorite(item)">
            取消收藏
          </button>
        </div>
      </article>

      <div v-if="!loading && visibleFavorites.length > 0" class="fav-end">
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
import { getSafeAvatarUrl } from '@/utils/image';

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
const defaultAvatar = '';

const formatSocialCount = (value?: number) => {
  const num = value || 0;
  if (num >= 10000) return `${(num / 10000).toFixed(1)}w`;
  if (num >= 1000) return `${(num / 1000).toFixed(1)}k`;
  return String(num);
};

const inferCategory = (item: SocialDynamic): { key: FavoriteCategoryKey; label: string } => {
  const text = `${item.content || ''} ${item.catName || ''}`.toLowerCase();
  if (/[图照摄拍美萌]/.test(text) || (item.images?.length || 0) > 0 && text.includes('日常') === false)
    return { key: 'photo', label: '萌图摄影' };
  if (/(攻略|喂养|护理|疫苗|体检|饲养|新手)/.test(text))
    return { key: 'guide', label: '养宠攻略' };
  return { key: 'diary', label: '喵村日记' };
};

const getPreviewImage = (item: SocialDynamic) => {
  if (item.images && item.images.length > 0) return item.images[0] || defaultAvatar;
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
          return { ...normalized, categoryKey: category.key, categoryLabel: category.label, previewImage: getPreviewImage(normalized) };
        });
      collected.push(...favoritesFromPage);
      if (list.length < pageSize) break;
    }
    favorites.value = collected.sort((left, right) => new Date(right.createdAt).getTime() - new Date(left.createdAt).getTime());
  } catch (error) {
    console.error('加载收藏列表失败:', error);
    showToast({ type: 'fail', message: '收藏列表加载失败' });
  } finally {
    loading.value = false;
  }
};

const refresh = async () => { await loadAllFavorites(); };

const visibleFavorites = computed(() => {
  if (activeTab.value === 'all') return favorites.value;
  return favorites.value.filter((item) => item.categoryKey === activeTab.value);
});

const openDetail = (id: string) => { router.push({ name: 'SocialDetail', params: { id } }); };

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

onMounted(() => { void refresh(); });
</script>

<style scoped>
.fav-page { min-height: 100dvh; padding: 0 16px 32px; background: #fff7f0; }

/* Header */
.fav-header { display: flex; align-items: flex-start; gap: 12px; padding: 14px 0 8px; }
.fav-back { width: 38px; height: 38px; flex-shrink: 0; border: none; border-radius: 14px; background: #fff; display: grid; place-items: center; color: #ff6b35; cursor: pointer; box-shadow: 0 2px 8px rgba(16,32,51,0.06); }
.fav-back:active { transform: scale(.93); }
.fav-title { margin: 0; font-size: 22px; font-weight: 900; color: #102033; }
.fav-sub { margin: 2px 0 0; font-size: 12px; font-weight: 600; color: #7a8494; }
.refresh-btn { width: 38px; height: 38px; flex-shrink: 0; border: none; border-radius: 14px; background: #fff; display: grid; place-items: center; color: #7a8494; cursor: pointer; box-shadow: 0 2px 8px rgba(16,32,51,0.06); }
.refresh-btn:active { transform: scale(.93); }

/* Tabs */
.fav-tabs { display: flex; gap: 8px; margin-top: 12px; overflow-x: auto; padding-bottom: 4px; }
.fav-tab { flex-shrink: 0; height: 36px; border: none; border-radius: 999px; background: #fff; padding: 0 16px; font-size: 14px; font-weight: 700; color: #7a8494; cursor: pointer; transition: all .14s; }
.fav-tab.active { background: #ff6b35; color: #fff; box-shadow: 0 4px 12px rgba(255,107,53,0.22); }
.fav-tab:active { transform: scale(.95); }

/* List */
.fav-list { margin-top: 14px; display: flex; flex-direction: column; gap: 12px; }

/* Empty */
.fav-empty { padding: 48px 20px; text-align: center; }
.fav-empty-icon { font-size: 48px; margin-bottom: 8px; }
.fav-empty-title { font-size: 18px; font-weight: 800; color: #102033; margin-bottom: 6px; }
.fav-empty-text { font-size: 14px; color: #7a8494; line-height: 1.6; }
.fav-empty-btn { display: inline-block; margin-top: 16px; border: none; border-radius: 999px; background: linear-gradient(135deg, #ff8a4c, #ff6b35); padding: 10px 24px; font-size: 14px; font-weight: 700; color: #fff; cursor: pointer; box-shadow: 0 4px 14px rgba(255,107,53,0.22); }
.fav-empty-btn:active { transform: scale(.95); }

/* Card */
.fav-card { border-radius: 22px; background: #fff; overflow: hidden; box-shadow: 0 2px 12px rgba(16,32,51,0.04); }
.fav-card-header { display: flex; align-items: flex-start; justify-content: space-between; padding: 16px 16px 0; }
.fav-author { display: flex; align-items: center; gap: 10px; min-width: 0; flex: 1; border: none; background: none; cursor: pointer; text-align: left; padding: 0; }
.fav-author-info { min-width: 0; }
.fav-author-name { font-size: 15px; font-weight: 800; color: #102033; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.fav-author-meta { display: flex; align-items: center; gap: 6px; margin-top: 3px; font-size: 12px; color: #7a8494; }
.fav-cat-chip { border-radius: 999px; background: #fff1e8; padding: 2px 8px; font-size: 11px; font-weight: 700; color: #ff6b35; }
.fav-unstar { width: 36px; height: 36px; border: none; border-radius: 12px; background: #fdfaf6; display: grid; place-items: center; color: #ff6b35; cursor: pointer; flex-shrink: 0; }
.fav-unstar:active { transform: scale(.9); }

.fav-content { display: block; width: 100%; border: none; background: none; cursor: pointer; text-align: left; padding: 0 16px; }
.fav-text { margin: 12px 0; font-size: 15px; color: #102033; line-height: 1.7; white-space: pre-wrap; word-break: break-word; }
.fav-image-wrap { margin-bottom: 12px; }

.fav-card-footer { display: flex; align-items: center; justify-content: space-between; border-top: 1px solid #f3f0ec; padding: 12px 16px; }
.fav-stats { display: flex; gap: 20px; }
.fav-stat { display: flex; align-items: center; gap: 4px; font-size: 14px; font-weight: 600; color: #7a8494; }
.fav-stat.liked { color: #ff4f37; }
.fav-stat.starred { color: #ff6b35; }
.fav-remove-btn { border: none; border-radius: 999px; background: #fff1e8; padding: 6px 14px; font-size: 12px; font-weight: 700; color: #ff6b35; cursor: pointer; }
.fav-remove-btn:active { opacity: .7; }

.fav-end { padding: 20px 0; text-align: center; font-size: 13px; color: #b0b8c4; }
</style>
