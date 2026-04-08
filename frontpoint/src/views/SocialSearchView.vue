<template>
  <div class="min-h-[100dvh] bg-white px-4 pt-3 pb-6">
    <header class="sticky top-0 z-20 -mx-4 bg-white/85 px-4 py-3 backdrop-blur-md">
      <div class="flex items-center gap-3">
        <button type="button" class="grid h-10 w-10 place-items-center text-on-surface" @click="router.back()">
          <van-icon name="arrow-left" size="20" />
        </button>
        <div class="relative flex-1">
          <van-icon name="search" class="absolute left-3 top-1/2 -translate-y-1/2 text-stone-400" />
          <input
            v-model="keyword"
            class="h-11 w-full rounded-xl bg-surface-container-high pl-10 pr-10 text-sm text-on-background outline-none"
            placeholder="寻找可爱的毛孩子..."
            @keyup.enter="commitKeyword"
          />
          <button
            v-if="keyword"
            type="button"
            class="absolute right-3 top-1/2 grid h-5 w-5 -translate-y-1/2 place-items-center rounded-full bg-stone-300 text-white"
            @click="keyword = ''"
          >
            <van-icon name="cross" size="10" />
          </button>
        </div>
      </div>
    </header>

    <section class="mt-4">
      <div v-if="loading" class="py-10 text-center">
        <van-loading size="24" />
        <div class="mt-3 text-sm text-on-surface-variant">正在加载广场内容...</div>
      </div>

      <div v-else>
        <template v-if="!keyword.trim()">
          <section class="mb-6">
            <div class="mb-3 flex items-center justify-between">
              <h2 class="text-base font-bold text-on-background">历史搜索</h2>
              <button
                v-if="searchHistory.length"
                type="button"
                class="text-xs font-semibold text-on-surface-variant"
                @click="clearHistory"
              >
                清空
              </button>
            </div>

            <div v-if="searchHistory.length" class="flex flex-wrap gap-2">
              <button
                v-for="term in searchHistory"
                :key="term"
                type="button"
                class="rounded-full bg-surface-container-low px-4 py-2 text-xs font-medium text-on-surface-variant"
                @click="applyKeyword(term)"
              >
                {{ term }}
              </button>
            </div>

            <div v-else class="text-sm text-on-surface-variant">暂无历史搜索</div>
          </section>

          <section class="mb-6">
            <div class="mb-3 flex items-center gap-2">
              <van-icon name="fire-o" color="#ab3500" />
              <h2 class="text-base font-bold text-on-background">热门话题</h2>
            </div>

            <div class="space-y-2">
              <button
                v-for="topic in hotTopics"
                :key="topic"
                type="button"
                class="flex w-full items-center justify-between rounded-xl bg-surface-container-low px-3 py-3 text-left"
                @click="applyKeyword(topic)"
              >
                <span class="text-sm font-semibold text-on-background"># {{ topic }}</span>
                <van-icon name="arrow" class="text-on-surface-variant" />
              </button>
            </div>
          </section>

          <section>
            <h2 class="mb-3 text-base font-bold text-on-background">推荐内容</h2>

            <div class="grid grid-cols-2 gap-3">
              <article
                v-for="item in recommendedList"
                :key="item.id"
                class="cursor-pointer overflow-hidden rounded-2xl bg-surface-container-lowest shadow-sm"
                @click="router.push({ name: 'SocialDetail', params: { id: item.id } })"
              >
                <van-image
                  :src="item.images && item.images[0] ? item.images[0] : item.avatar"
                  fit="cover"
                  width="100%"
                  height="132"
                />
                <div class="p-3">
                  <p class="line-clamp-2 text-xs font-semibold leading-relaxed text-on-background">{{ item.content }}</p>
                  <div class="mt-2 text-[11px] text-on-surface-variant">{{ item.likeCount || 0 }} 赞</div>
                </div>
              </article>
            </div>
          </section>
        </template>

        <template v-else>
          <div v-if="filteredList.length === 0" class="rounded-2xl border border-surface-container-high bg-surface-container-lowest p-6 text-center">
            <div class="text-3xl">🔍</div>
            <div class="mt-3 text-base font-semibold text-on-background">没有找到相关内容</div>
            <div class="mt-1 text-sm text-on-surface-variant">换个关键词试试</div>
          </div>

          <div v-else class="space-y-3">
            <article
              v-for="item in filteredList"
              :key="item.id"
              class="cursor-pointer rounded-xl border border-surface-container-high bg-surface-container-lowest p-4"
              @click="router.push({ name: 'SocialDetail', params: { id: item.id } })"
            >
              <div class="flex items-center gap-3">
                <van-image :src="item.avatar" fit="cover" width="42" height="42" round />
                <div class="min-w-0 flex-1">
                  <div class="truncate text-sm font-bold text-on-background">{{ item.username }}</div>
                  <div class="truncate text-xs text-on-surface-variant">{{ item.catName || '猫村用户' }}</div>
                </div>
                <div class="text-xs text-on-surface-variant">{{ item.likeCount || 0 }} 赞</div>
              </div>

              <p class="mt-3 line-clamp-2 text-sm leading-relaxed text-on-background">{{ item.content }}</p>
            </article>
          </div>
        </template>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';
import { useSocialFeatures } from '@/composables/useSocialFeatures';
import { getHotTopics } from '@/api/social';

const router = useRouter();
const { fetchDynamicsList, getCurrentDynamics } = useSocialFeatures();

const loading = ref(false);
const keyword = ref('');
const searchHistory = ref<string[]>([]);
const hotTopics = ref<string[]>([]);

const HISTORY_KEY = 'social_search_history';
const DEFAULT_TOPICS = ['猫咪迷惑行为', '如何科学铲屎', '布偶猫日常', '猫咪健康', '新手养猫'];

const list = computed(() => getCurrentDynamics.value);

const filteredList = computed(() => {
  const key = keyword.value.trim().toLowerCase();
  if (!key) {
    return list.value;
  }
  return list.value.filter((item) => {
    const text = `${item.username} ${item.catName || ''} ${item.content}`.toLowerCase();
    return text.includes(key);
  });
});

const recommendedList = computed(() => list.value.slice(0, 6));

const loadHistory = () => {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    if (!raw) {
      searchHistory.value = [];
      return;
    }
    const arr = JSON.parse(raw) as unknown;
    if (!Array.isArray(arr)) {
      searchHistory.value = [];
      return;
    }
    searchHistory.value = arr.filter((s): s is string => typeof s === 'string').slice(0, 10);
  } catch {
    searchHistory.value = [];
  }
};

const saveHistory = () => {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(searchHistory.value.slice(0, 10)));
};

const pushHistory = (term: string) => {
  const value = term.trim();
  if (!value) {
    return;
  }
  searchHistory.value = [value, ...searchHistory.value.filter((s) => s !== value)].slice(0, 10);
  saveHistory();
};

const applyKeyword = (term: string) => {
  keyword.value = term;
  pushHistory(term);
};

const commitKeyword = () => {
  pushHistory(keyword.value);
};

const clearHistory = () => {
  searchHistory.value = [];
  saveHistory();
};

const initData = async () => {
  loading.value = true;
  try {
    await Promise.all([
      fetchDynamicsList({ page: 1, pageSize: 50 }),
      (async () => {
        try {
          const res = await getHotTopics({ limit: 8, sampleSize: 500 });
          hotTopics.value = (res.data.list || []).map((item) => item.topic).filter((topic) => !!topic);
          if (!hotTopics.value.length) {
            hotTopics.value = DEFAULT_TOPICS;
          }
        } catch {
          hotTopics.value = DEFAULT_TOPICS;
        }
      })(),
    ]);
    loadHistory();
  } catch {
    showToast({ type: 'fail', message: '搜索内容加载失败' });
    if (!hotTopics.value.length) {
      hotTopics.value = DEFAULT_TOPICS;
    }
  } finally {
    loading.value = false;
  }
};

onMounted(initData);
</script>
