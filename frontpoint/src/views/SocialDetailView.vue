<template>
  <div class="min-h-[100dvh] bg-[#f4f5fb] pb-24">
    <header class="sticky top-0 z-20 flex min-h-[54px] items-center justify-between bg-white px-3.5 py-2.5">
      <button type="button" class="grid h-10 w-10 place-items-center text-[#12182a]" @click="router.back()">
        <van-icon name="arrow-left" size="20" />
      </button>
      <div class="text-[19px] font-extrabold text-[#12182a]">{{ detail?.catName || 'Momo的守护者' }}</div>
      <button
        v-if="detail?.isOwner"
        type="button"
        class="grid h-10 w-10 place-items-center text-[#12182a]"
        :disabled="deleteBusy"
        @click="deleteCurrentDynamic"
      >
        <van-icon name="delete-o" size="20" />
      </button>
      <div v-else class="w-10"></div>
    </header>

    <section v-if="loading" class="py-10 text-center">
      <van-loading size="24" />
      <div class="mt-3 text-sm text-on-surface-variant">正在加载动态详情...</div>
    </section>

    <section v-else-if="error" class="mt-4 rounded-2xl border border-surface-container-high bg-surface-container-lowest p-6 text-center">
      <div class="text-base font-semibold text-on-background">加载失败</div>
      <div class="mt-2 text-sm text-on-surface-variant">{{ error }}</div>
      <van-button class="mt-4" type="primary" @click="loadDetail">重试</van-button>
    </section>

    <section v-else-if="detail" class="pb-4">
      <div class="relative bg-black">
        <van-image :src="detail.images?.[0] || fallbackImage" fit="cover" width="100%" height="300" />
        <div class="absolute right-3 top-3 rounded-full bg-black/40 px-2 py-1 text-[12px] text-white">1/{{ detail.images?.length || 1 }}</div>
      </div>

      <article class="-mt-2 rounded-t-[22px] bg-white px-4 pt-4 pb-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <van-image :src="detail.avatar || fallbackAvatar" fit="cover" width="44" height="44" round />
            <div>
              <div class="text-[18px] font-extrabold text-[#12182a]">{{ detail.username || '金毛Momo' }}</div>
              <div class="text-[13px] text-[#8b8380]">{{ formatRelativeTime(detail.createdAt) }}发布</div>
            </div>
          </div>
          <button
            type="button"
            class="h-9 w-[108px] rounded-[10px] text-[15px] font-bold transition-colors disabled:opacity-60"
            :class="detail.isFollowing ? 'bg-[#f4f5fb] text-[#8b8380]' : 'bg-[#ff6b35] text-white'"
            :disabled="followBusy || detail.isOwner"
            @click="toggleFollow"
          >
            {{ detail.isOwner ? '作者' : detail.isFollowing ? '已关注' : '关注' }}
          </button>
        </div>

        <p class="mt-4 whitespace-pre-wrap text-[15px] leading-relaxed text-[#2d2522]">{{ detail.content }}</p>

        <div class="mt-4 flex items-center justify-around rounded-[14px] bg-[#f4f5fb] py-3">
          <div class="text-center">
            <button type="button" class="text-[#8f4628]" :disabled="likeBusy" @click="toggleLike">
              <van-icon :name="detail.isLiked ? 'like' : 'like-o'" size="20" />
            </button>
            <div class="mt-2 text-[16px] text-[#3f3632]">{{ formatCount(detail.likeCount) }}</div>
          </div>
          <div class="text-center">
            <button type="button" class="text-[#1a2437]" :disabled="favoriteBusy" @click="toggleFavorite">
              <van-icon :name="detail.isFavorited ? 'star' : 'star-o'" size="20" :class="detail.isFavorited ? 'text-[#ff6b35]' : ''" />
            </button>
            <div class="mt-2 text-[16px] text-[#3f3632]">{{ formatCount(detail.favoriteCount) }}</div>
          </div>
          <div class="text-center">
            <div class="text-[#1a2437]"><van-icon name="chat" size="20" /></div>
            <div class="mt-2 text-[16px] text-[#3f3632]">{{ detail.commentCount || comments.length }}</div>
          </div>
        </div>
      </article>

      <section class="mt-2 bg-white px-4 py-4">
        <div class="text-[22px] font-black text-[#12182a]">评论 ({{ detail.commentCount || comments.length }})</div>

        <div v-if="comments.length === 0" class="mt-3 text-[16px] text-[#726966]">还没有评论，来抢沙发吧。</div>

        <div v-else class="mt-3 space-y-4">
          <div v-for="item in comments" :key="item.id" class="flex items-start gap-3">
            <van-image :src="item.avatar || fallbackAvatar" width="34" height="34" round fit="cover" />
            <div class="flex-1 border-b border-[#eef0f5] pb-3">
              <div class="flex items-center justify-between">
                <div class="text-[15px] font-bold text-[#2f2724]">{{ item.username }}</div>
                <button
                  type="button"
                  class="flex items-center gap-1 text-[14px]"
                  :class="item.isLiked ? 'text-[#ff6b35]' : 'text-[#8b8380]'"
                  :disabled="commentLikeBusyId === item.id"
                  @click.stop="toggleCommentLike(item)"
                >
                  <van-icon :name="item.isLiked ? 'good-job' : 'good-job-o'" size="14" />
                  <span>{{ item.likeCount || 0 }}</span>
                </button>
              </div>
              <div class="mt-1 text-[14px] text-[#544b47]">{{ item.content }}</div>
            </div>
          </div>
        </div>
      </section>
    </section>

    <footer class="fixed bottom-0 left-1/2 z-30 flex w-full max-w-[430px] -translate-x-1/2 items-center gap-2 border-t border-[#edf0f6] bg-white px-3 py-2.5">
      <input
        v-model="draft"
        class="h-10 flex-1 rounded-[10px] bg-[#e8ecfb] px-3 text-[15px] text-[#5b534f] outline-none"
        placeholder="说点什么吧..."
        @keyup.enter="submitComment"
      />
      <button type="button" class="grid h-10 w-10 place-items-center rounded-[10px] bg-[#f4f5fb] text-[#1a2437]">
        <van-icon name="like-o" size="20" />
      </button>
      <button type="button" class="grid h-10 w-10 place-items-center rounded-[10px] bg-[#f4f5fb] text-[#1a2437]" :disabled="favoriteBusy" @click="toggleFavorite">
        <van-icon :name="detail?.isFavorited ? 'star' : 'star-o'" size="20" :class="detail?.isFavorited ? 'text-[#ff6b35]' : ''" />
      </button>
      <button
        type="button"
        class="h-10 w-14 rounded-[10px] bg-[#ff6b35] text-[16px] font-semibold text-white shadow-cta disabled:opacity-60"
        :disabled="commentBusy || !draft.trim()"
        @click="submitComment"
      >
        ➤
      </button>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { closeToast, showConfirmDialog, showToast } from 'vant';
import { useSocialFeatures } from '@/composables/useSocialFeatures';
import { formatRelativeTime } from '@/utils/date';
import type { CommentResponse, SocialDynamic } from '@/types/social';

const props = defineProps<{ id: string }>();
const router = useRouter();

const {
  fetchDynamicDetail,
  likeADynamic,
  unlikeADynamic,
  toggleFavoriteADynamic,
  toggleFollowAUser,
  toggleCommentLikeById,
  postNewComment,
  removeDynamic
} = useSocialFeatures();

const loading = ref(false);
const likeBusy = ref(false);
const favoriteBusy = ref(false);
const followBusy = ref(false);
const commentLikeBusyId = ref('');
const commentBusy = ref(false);
const deleteBusy = ref(false);
const error = ref<string | null>(null);
const detail = ref<SocialDynamic | null>(null);
const draft = ref('');
const comments = ref<CommentResponse[]>([]);
const fallbackAvatar = 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg';
const fallbackImage = 'https://images.unsplash.com/photo-1518791841217-8f162f1e1131?auto=format&fit=crop&w=1200&q=80';

const normalizeComments = (input: unknown) => {
  if (!Array.isArray(input)) {
    return [] as CommentResponse[];
  }
  return input.map((item, idx) => {
    const row = item as Record<string, unknown>;
    return {
      id: String(row.id || `tmp-${idx}`),
      userId: String(row.userId || ''),
      username: String(row.username || '猫村用户'),
      avatar: String(row.avatar || ''),
      dynamicId: String(row.dynamicId || props.id),
      content: String(row.content || ''),
      createdAt: String(row.createdAt || new Date().toISOString()),
      likeCount: Number(row.likeCount || 0),
      isLiked: Boolean(row.isLiked || false),
      isOwner: Boolean(row.isOwner || false)
    };
  });
};

const formatCount = (value?: number) => {
  const num = value || 0;
  if (num >= 10000) {
    return `${(num / 10000).toFixed(1)}w`;
  }
  if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}k`;
  }
  return String(num);
};

const loadDetail = async () => {
  loading.value = true;
  error.value = null;
  try {
    const data = await fetchDynamicDetail(props.id);
    detail.value = data;
    const raw = data as unknown as Record<string, unknown>;
    comments.value = normalizeComments(raw.comments);
  } catch {
    error.value = '动态详情获取失败，请稍后重试';
  } finally {
    loading.value = false;
  }
};

const toggleFavorite = async () => {
  if (!detail.value || favoriteBusy.value) {
    return;
  }

  favoriteBusy.value = true;
  try {
    const response = await toggleFavoriteADynamic(detail.value.id);
    detail.value.isFavorited = response.isFavorited;
    detail.value.favoriteCount = response.favoriteCount;
  } catch {
    showToast({ type: 'fail', message: '收藏失败，请稍后重试' });
  } finally {
    favoriteBusy.value = false;
  }
};

const toggleFollow = async () => {
  if (!detail.value || followBusy.value || detail.value.isOwner || !detail.value.userId) {
    return;
  }

  followBusy.value = true;
  try {
    const response = await toggleFollowAUser(detail.value.userId);
    detail.value.isFollowing = response.isFollowing;
  } catch {
    showToast({ type: 'fail', message: '关注失败，请稍后重试' });
  } finally {
    followBusy.value = false;
  }
};

const toggleLike = async () => {
  if (!detail.value || likeBusy.value) {
    return;
  }
  likeBusy.value = true;
  try {
    if (detail.value.isLiked) {
      await unlikeADynamic(detail.value.id);
      detail.value.isLiked = false;
      detail.value.likeCount = Math.max(0, (detail.value.likeCount || 0) - 1);
    } else {
      await likeADynamic(detail.value.id);
      detail.value.isLiked = true;
      detail.value.likeCount = (detail.value.likeCount || 0) + 1;
    }
  } catch {
    showToast({ type: 'fail', message: '操作失败，请稍后重试' });
  } finally {
    likeBusy.value = false;
  }
};

const toggleCommentLike = async (comment: CommentResponse) => {
  if (commentLikeBusyId.value) {
    return;
  }

  commentLikeBusyId.value = comment.id;
  try {
    const response = await toggleCommentLikeById(comment.id);
    comment.isLiked = response.isLiked;
    comment.likeCount = response.likeCount;
  } catch {
    showToast({ type: 'fail', message: '评论点赞失败，请稍后重试' });
  } finally {
    commentLikeBusyId.value = '';
  }
};

const submitComment = async () => {
  if (!detail.value) {
    return;
  }
  const text = draft.value.trim();
  if (!text) {
    return;
  }

  commentBusy.value = true;
  showToast({ type: 'loading', message: '发送中...', duration: 0, forbidClick: true });
  try {
    const res = await postNewComment(detail.value.id, { dynamicId: detail.value.id, content: text });
    comments.value = [
      ...comments.value,
      {
        id: res.id,
        userId: res.userId,
        username: res.username,
        avatar: res.avatar,
        dynamicId: res.dynamicId,
        content: res.content,
        createdAt: res.createdAt,
        likeCount: res.likeCount || 0,
        isLiked: res.isLiked || false,
        isOwner: res.isOwner
      }
    ];
    detail.value.commentCount = (detail.value.commentCount || comments.value.length - 1) + 1;
    draft.value = '';
    closeToast();
    showToast({ type: 'success', message: '评论成功' });
  } catch {
    closeToast();
    showToast({ type: 'fail', message: '评论失败，请稍后重试' });
  } finally {
    commentBusy.value = false;
  }
};

const deleteCurrentDynamic = async () => {
  if (!detail.value || deleteBusy.value) {
    return;
  }

  try {
    await showConfirmDialog({
      title: '删除动态',
      message: '删除后无法恢复，确认删除吗？'
    });
  } catch {
    return;
  }

  deleteBusy.value = true;
  try {
    await removeDynamic(detail.value.id);
    showToast({ type: 'success', message: '动态已删除' });
    router.back();
  } catch {
    showToast({ type: 'fail', message: '删除失败，请稍后重试' });
  } finally {
    deleteBusy.value = false;
  }
};

onMounted(loadDetail);
</script>
