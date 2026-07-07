<template>
  <div class="search-page">
    <AppTopBar title="搜索" subtitle="查找动态、话题和村民" kicker="Search" back @back="router.back()">
      <div class="search-box" :class="{ active: keyword }">
        <van-icon name="search" size="18" />
        <input
          v-model="keyword"
          type="text"
          placeholder="搜索动态、村民..."
          @keyup.enter="commitKeyword"
        />
        <button v-if="keyword" type="button" class="search-clear" @click="keyword = ''">
          <van-icon name="clear" size="16" />
        </button>
      </div>
    </AppTopBar>

    <main class="search-main">
      <!-- Loading -->
      <div v-if="loading" class="search-loading">
        <van-loading size="28" color="#ff6b35" />
        <div class="search-loading-text">正在加载...</div>
      </div>

      <div v-else>
        <!-- Idle: History + Hot Topics + Recommended -->
          <template v-if="!keyword.trim()">
          <!-- Search History -->
          <section v-if="searchHistory.length" class="search-section">
            <div class="section-header">
              <h2 class="section-title">历史搜索</h2>
              <button type="button" class="section-action" @click="clearHistory">清空</button>
            </div>
            <div class="history-tags">
              <button
                v-for="term in searchHistory"
                :key="term"
                type="button"
                class="history-tag"
                @click="applyKeyword(term)"
              >
                {{ term }}
              </button>
            </div>
          </section>

          <!-- Hot Topics -->
          <section class="search-section">
            <div class="section-header">
              <h2 class="section-title">
                <span class="section-icon">🔥</span> 热门话题
              </h2>
            </div>
            <div class="topic-list">
              <button
                v-for="topic in hotTopics"
                :key="topic.topic"
                type="button"
                class="topic-card"
                @click="applyKeyword(topic.topic)"
              >
                <div class="topic-rank" v-if="false"></div>
                <span class="topic-text"># {{ topic.topic }}</span>
                <span class="topic-count">{{ topic.isDefault ? '引导' : `${topic.count}次` }}</span>
                <van-icon name="arrow" class="topic-arrow" />
              </button>
            </div>
          </section>

          <!-- Recommended -->
          <section class="search-section">
            <div class="section-header">
              <h2 class="section-title">推荐内容</h2>
            </div>
            <div class="recommend-grid">
              <article
                v-for="item in recommendedList"
                :key="item.id"
                class="recommend-card"
                @click="router.push({ name: 'SocialDetail', params: { id: item.id } })"
              >
                <div class="recommend-cover">
                  <van-image v-if="getRecommendedImage(item)" :src="getRecommendedImage(item)" fit="cover" width="100%" height="100%">
                    <template #error>
                      <div class="recommend-cover-fallback">
                        <van-icon name="photo-o" size="28" />
                      </div>
                    </template>
                  </van-image>
                  <div v-else class="recommend-cover-empty">
                    <span>🐾</span>
                  </div>
                </div>
                <div class="recommend-body">
                  <p class="recommend-text">{{ item.content }}</p>
                  <div class="recommend-meta">
                    <van-icon name="like-o" size="13" />
                    <span>{{ item.likeCount || 0 }}</span>
                  </div>
                </div>
              </article>
            </div>
          </section>
        </template>

        <!-- Search Results -->
        <template v-else>
          <div v-if="filteredList.length === 0" class="search-empty">
            <span class="search-empty-icon">ฅ</span>
            <div class="search-empty-title">没有找到相关内容</div>
            <div class="search-empty-text">换个关键词试试吧</div>
          </div>

          <div v-else class="result-list">
            <article
              v-for="item in filteredList"
              :key="item.id"
              class="result-card"
              @click="router.push({ name: 'SocialDetail', params: { id: item.id } })"
            >
              <div class="result-author">
                <van-image :src="getSafeAvatarUrl(item.avatar, item.userId)" fit="cover" width="40" height="40" round />
                <div class="result-author-info">
                  <div class="result-author-name">{{ item.username }}</div>
                  <div class="result-author-cat">{{ item.catName || '猫村村民' }}</div>
                </div>
                <div class="result-like">
                  <van-icon name="like-o" size="13" />
                  <span>{{ item.likeCount || 0 }}</span>
                </div>
              </div>
              <p class="result-text">{{ item.content }}</p>
            </article>
          </div>
        </template>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';
import AppTopBar from '@/components/AppTopBar.vue';
import { useSocialFeatures } from '@/composables/useSocialFeatures';
import { getHotTopics, searchDynamics } from '@/api/social';
import { getOptionalImageUrl, getSafeAvatarUrl } from '@/utils/image';
import type { HotTopicItem, SocialDynamic } from '@/types/social';

const router = useRouter();
const { fetchDynamicsList, getCurrentDynamics } = useSocialFeatures();

const loading = ref(false);
const keyword = ref('');
const searchHistory = ref<string[]>([]);
const hotTopics = ref<HotTopicItem[]>([]);
const searchResults = ref<SocialDynamic[]>([]);
let searchTimer: ReturnType<typeof setTimeout> | null = null;

const HISTORY_KEY = 'social_search_history';
const DEFAULT_TOPICS: HotTopicItem[] = [
  { topic: '猫咪', count: 0, isDefault: true },
  { topic: '新手养猫', count: 0, isDefault: true },
  { topic: '喵喵台', count: 0, isDefault: true }
];

const list = computed(() => getCurrentDynamics.value);

const filteredList = computed(() => keyword.value.trim() ? searchResults.value : list.value);

const recommendedList = computed(() => list.value.slice(0, 6));

const getRecommendedImage = (item: SocialDynamic) => {
  const first = Array.isArray(item.images) ? item.images[0] : '';
  return getOptionalImageUrl(first);
};

const loadHistory = () => {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    if (!raw) { searchHistory.value = []; return; }
    const arr = JSON.parse(raw) as unknown;
    if (!Array.isArray(arr)) { searchHistory.value = []; return; }
    searchHistory.value = arr.filter((s): s is string => typeof s === 'string').slice(0, 10);
  } catch { searchHistory.value = []; }
};

const saveHistory = () => {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(searchHistory.value.slice(0, 10)));
};

const pushHistory = (term: string) => {
  const value = term.trim();
  if (!value) return;
  searchHistory.value = [value, ...searchHistory.value.filter((s) => s !== value)].slice(0, 10);
  saveHistory();
};

const applyKeyword = (term: string) => {
  const value = term.replace(/^#\s*/, '').trim();
  keyword.value = value;
  pushHistory(value);
};

const commitKeyword = () => { pushHistory(keyword.value); void runSearch(); };
const clearHistory = () => { searchHistory.value = []; saveHistory(); };

const runSearch = async () => {
  const q = keyword.value.trim();
  if (!q) {
    searchResults.value = [];
    return;
  }
  loading.value = true;
  try {
    const res = await searchDynamics({ q, page: 1, pageSize: 30 });
    searchResults.value = res.data.list || [];
  } catch {
    searchResults.value = [];
    showToast({ type: 'fail', message: '搜索失败，请稍后重试' });
  } finally {
    loading.value = false;
  }
};

const initData = async () => {
  loading.value = true;
  try {
    await Promise.all([
      fetchDynamicsList({ page: 1, pageSize: 50 }),
      (async () => {
        try {
          const res = await getHotTopics({ limit: 8, sampleSize: 500 });
          hotTopics.value = (res.data.list || []).filter((item) => !!item.topic);
          if (!hotTopics.value.length) hotTopics.value = DEFAULT_TOPICS;
        } catch { hotTopics.value = DEFAULT_TOPICS; }
      })(),
    ]);
    loadHistory();
  } catch {
    showToast({ type: 'fail', message: '搜索内容加载失败' });
    if (!hotTopics.value.length) hotTopics.value = DEFAULT_TOPICS;
  } finally { loading.value = false; }
};

onMounted(initData);
watch(keyword, () => {
  if (searchTimer) clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    if (keyword.value.trim()) void runSearch();
    else searchResults.value = [];
  }, 320);
});
onBeforeUnmount(() => {
  if (searchTimer) clearTimeout(searchTimer);
});
</script>

<style scoped>
/* ========== PAGE ========== */
.search-page {
  min-height: 100dvh;
  padding: 0 16px 104px;
  background:
    radial-gradient(circle at 12% 0%, rgba(249, 115, 22, 0.14), transparent 28%),
    linear-gradient(180deg, #fff8f3 0%, #f5f7fb 48%, #eef6f5 100%);
}

.search-main {
  padding-top: 8px;
}

/* ========== SEARCH BOX (inside AppTopBar extra) ========== */
.search-box {
  display: flex;
  align-items: center;
  gap: 9px;
  height: 42px;
  border: 1.5px solid rgba(249, 115, 22, 0.18);
  border-radius: 18px;
  background: rgba(255,255,255,0.94);
  color: #ff6b35;
  padding: 0 14px;
  box-shadow: 0 10px 24px rgba(23, 32, 51, 0.05);
  transition: border-color .15s, box-shadow .15s, transform .15s;
}

.search-box.active {
  border-color: #ff6b35;
  box-shadow: 0 4px 16px rgba(255, 107, 53, 0.1);
  transform: translateY(-1px);
}

.search-box input {
  min-width: 0;
  flex: 1;
  border: 0;
  background: transparent;
  color: #102033;
  outline: none;
  font-size: 14px;
  font-weight: 600;
}

.search-box input::placeholder {
  color: #b0b8c4;
}

.search-clear {
  display: grid;
  width: 24px;
  height: 24px;
  place-items: center;
  border: 0;
  background: transparent;
  color: #7a8494;
  cursor: pointer;
}

/* ========== LOADING ========== */
.search-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 54px 0;
}

.search-loading-text {
  margin-top: 12px;
  font-size: 14px;
  color: #7a8494;
}

.search-loading::before {
  content: '...';
  width: 54px;
  height: 34px;
  border-radius: 999px;
  background: #fff;
  color: #f97316;
  display: grid;
  place-items: center;
  margin-bottom: 10px;
  font-weight: 900;
  letter-spacing: 2px;
  animation: floatSoft 2.4s ease-in-out infinite;
}

/* ========== SECTIONS ========== */
.search-section {
  margin-bottom: 24px;
  border: 1px solid rgba(226, 232, 240, 0.82);
  border-radius: 22px;
  background: rgba(255,255,255,0.72);
  padding: 14px;
  box-shadow: 0 12px 26px rgba(23,32,51,0.05);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.section-title {
  margin: 0;
  font-size: 17px;
  font-weight: 800;
  color: #102033;
  display: flex;
  align-items: center;
  gap: 6px;
}

.section-icon {
  font-size: 18px;
}

.section-action {
  border: none;
  background: none;
  font-size: 13px;
  font-weight: 600;
  color: #7a8494;
  cursor: pointer;
}

/* ========== HISTORY TAGS ========== */
.history-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.history-tag {
  height: 34px;
  border: 1.5px solid #e8e4df;
  border-radius: 999px;
  background: #fff;
  padding: 0 16px;
  font-size: 13px;
  font-weight: 600;
  color: #7a8494;
  cursor: pointer;
  transition: all .14s;
}

.history-tag:active {
  border-color: #ff6b35;
  background: #fff1e8;
  color: #ff6b35;
  transform: scale(.95);
}

/* ========== TOPICS ========== */
.topic-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.topic-card {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  border: none;
  border-radius: 16px;
  background: #fff;
  padding: 15px 16px;
  cursor: pointer;
  box-shadow: 0 1px 6px rgba(16, 32, 51, 0.03);
  transition: transform .14s, box-shadow .14s;
}

.topic-card:active {
  transform: scale(.98);
  box-shadow: 0 4px 14px rgba(255, 107, 53, 0.08);
}

.topic-text {
  flex: 1;
  text-align: left;
  font-size: 15px;
  font-weight: 700;
  color: #102033;
}

.topic-count {
  flex-shrink: 0;
  border-radius: 999px;
  background: #fff7ed;
  padding: 3px 8px;
  color: #ea580c;
  font-size: 11px;
  font-weight: 800;
}

.topic-arrow {
  color: #d0c8bc;
  font-size: 14px;
}

/* ========== RECOMMENDED ========== */
.recommend-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.recommend-card {
  border-radius: 18px;
  background: #fff;
  overflow: hidden;
  cursor: pointer;
  box-shadow: 0 1px 6px rgba(16, 32, 51, 0.03);
  transition: transform .14s;
}

.recommend-card:active {
  transform: scale(.97);
}

.recommend-cover {
  height: 130px;
  overflow: hidden;
}

.recommend-cover-fallback {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #fff1e8, #fdf6f0);
  color: #ff6b35;
}

.recommend-cover-empty {
  width: 100%;
  height: 100%;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #fff8f4, #fdfaf6, #fef5ff);
  font-size: 36px;
}

.recommend-body {
  padding: 10px 12px 12px;
}

.recommend-text {
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-size: 13px;
  font-weight: 600;
  color: #102033;
  line-height: 1.5;
}

.recommend-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 8px;
  font-size: 12px;
  color: #7a8494;
}

/* ========== EMPTY ========== */
.search-empty {
  margin-top: 40px;
  padding: 48px 20px;
  text-align: center;
  border: 1px dashed #ffd7bf;
  border-radius: 24px;
  background: #fff;
  box-shadow: 0 2px 12px rgba(16, 32, 51, 0.03);
}

.search-empty-icon {
  font-size: 44px;
  display: block;
  margin-bottom: 12px;
  color: #f97316;
  animation: floatSoft 3s ease-in-out infinite;
}

.search-empty-title {
  font-size: 18px;
  font-weight: 800;
  color: #102033;
  margin-bottom: 4px;
}

.search-empty-text {
  font-size: 14px;
  color: #7a8494;
}

/* ========== RESULTS ========== */
.result-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.result-card {
  border: 1px solid rgba(226, 232, 240, 0.92);
  border-radius: 18px;
  background: #fff;
  padding: 15px 16px;
  cursor: pointer;
  box-shadow: 0 1px 6px rgba(16, 32, 51, 0.03);
  transition: transform .14s;
}

@keyframes floatSoft {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

@media (prefers-reduced-motion: reduce) {
  .search-loading::before,
  .search-empty-icon,
  .search-box,
  .result-card,
  .topic-card,
  .recommend-card,
  .history-tag {
    animation: none !important;
    transition: none !important;
  }
}

.result-card:active {
  transform: scale(.98);
}

.result-author {
  display: flex;
  align-items: center;
  gap: 10px;
}

.result-author-info {
  min-width: 0;
  flex: 1;
}

.result-author-name {
  font-size: 14px;
  font-weight: 800;
  color: #102033;
}

.result-author-cat {
  font-size: 12px;
  color: #7a8494;
  margin-top: 1px;
}

.result-like {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 12px;
  color: #7a8494;
}

.result-text {
  margin: 10px 0 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-size: 14px;
  color: #102033;
  line-height: 1.6;
}
</style>
