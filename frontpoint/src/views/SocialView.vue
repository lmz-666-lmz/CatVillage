<template>
  <div class="px-6 pt-6 pb-6">
    <header class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold tracking-tight text-on-background">广场</h1>
        <p class="mt-1 text-sm text-on-surface-variant">和大家分享猫咪日常</p>
      </div>
      <div class="flex items-center gap-2">
        <van-button size="small" plain type="primary" @click="refresh">刷新</van-button>
        <van-button size="small" type="primary" @click="router.push({ name: 'CreatePost' })">发布</van-button>
      </div>
    </header>

    <div class="mt-5 grid grid-cols-3 rounded-2xl border border-surface-container-high bg-surface-container-lowest p-1">
      <button
        type="button"
        class="h-9 rounded-xl text-sm font-semibold"
        :class="activeTab === 'follow' ? 'bg-primary text-on-primary shadow-cta' : 'text-on-surface-variant'"
        @click="activeTab = 'follow'"
      >
        关注
      </button>
      <button
        type="button"
        class="h-9 rounded-xl text-sm font-semibold"
        :class="activeTab === 'recommend' ? 'bg-primary text-on-primary shadow-cta' : 'text-on-surface-variant'"
        @click="activeTab = 'recommend'"
      >
        推荐
      </button>
      <button
        type="button"
        class="h-9 rounded-xl text-sm font-semibold"
        :class="activeTab === 'city' ? 'bg-primary text-on-primary shadow-cta' : 'text-on-surface-variant'"
        @click="activeTab = 'city'"
      >
        同城
      </button>
    </div>

    <section class="mt-6">
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
          class="rounded-2xl border border-surface-container-high bg-surface-container-lowest p-4"
        >
          <div class="flex items-center justify-between gap-3">
            <div class="flex items-center gap-3 min-w-0">
              <van-image :src="item.avatar" fit="cover" width="44" height="44" round />
              <div class="min-w-0">
                <div class="truncate text-sm font-semibold text-on-background">{{ item.username }}</div>
                <div class="mt-0.5 text-xs text-on-surface-variant">{{ formatRelativeTime(item.createdAt) }}</div>
              </div>
            </div>
            <van-tag v-if="item.catName" plain type="primary">{{ item.catName }}</van-tag>
          </div>

          <p class="mt-3 whitespace-pre-wrap text-sm leading-relaxed text-on-background">{{ item.content }}</p>

          <div v-if="item.images && item.images.length" class="mt-3 grid grid-cols-3 gap-2">
            <van-image
              v-for="(img, idx) in item.images"
              :key="idx"
              :src="img"
              fit="cover"
              width="100%"
              height="88"
              radius="12"
            />
          </div>

          <div class="mt-4 flex items-center justify-between gap-3 text-sm">
            <button
              type="button"
              class="flex items-center gap-2 text-on-surface-variant"
              :disabled="likingId === item.id"
              @click="toggleLike(item)"
            >
              <van-icon :name="item.isLiked ? 'like' : 'like-o'" />
              <span>{{ item.likeCount || 0 }}</span>
            </button>
            <div class="flex items-center gap-2 text-on-surface-variant">
              <van-icon name="comment-o" />
              <span>{{ item.commentCount || 0 }}</span>
            </div>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';
import { useSocialFeatures } from '@/composables/useSocialFeatures';
import { formatRelativeTime } from '@/utils/date';
import type { SocialDynamic } from '@/types/social';

const router = useRouter();
const activeTab = ref<'follow' | 'recommend' | 'city'>('recommend');

const { fetchDynamicsList, likeADynamic, unlikeADynamic, getCurrentDynamics } = useSocialFeatures();

const loading = ref(false);
const likingId = ref<string>('');
const dynamics = computed(() => getCurrentDynamics.value);

const refresh = async () => {
  if (loading.value) {
    return;
  }
  loading.value = true;
  try {
    await fetchDynamicsList({ page: 1, pageSize: 20 });
  } catch {
    showToast({ type: 'fail', message: '加载失败，请稍后重试' });
  } finally {
    loading.value = false;
  }
};

const toggleLike = async (dynamic: SocialDynamic) => {
  if (likingId.value) {
    return;
  }
  likingId.value = dynamic.id;
  try {
    if (dynamic.isLiked) {
      await unlikeADynamic(dynamic.id);
      return;
    }
    await likeADynamic(dynamic.id);
  } catch {
    showToast({ type: 'fail', message: '操作失败，请稍后重试' });
  } finally {
    likingId.value = '';
  }
};

onMounted(refresh);
</script>
