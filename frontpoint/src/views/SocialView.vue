<template>
  <div class="social-page">
    <AppTopBar title="猫村广场" subtitle="看看村民们今天在分享什么" kicker="Village Feed" logo="/logo.png">
      <template #actions>
        <button class="topbar-action" type="button" aria-label="搜索" @click="router.push({ name: 'SocialSearch' })">
          <van-icon name="search" size="19" />
        </button>
      </template>

      <div class="feed-switch">
        <button type="button" :class="{ active: activeTab === 'recommend' }" @click="activeTab = 'recommend'">
          <van-icon name="fire-o" size="15" />
          发现
        </button>
        <button type="button" :class="{ active: activeTab === 'follow' }" @click="activeTab = 'follow'">
          <van-icon name="friends-o" size="15" />
          关注
        </button>
      </div>
    </AppTopBar>

    <main class="feed-main">
      <section v-if="error" class="state-card">
        <van-icon name="warning-o" size="34" />
        <strong>广场加载失败</strong>
        <span>{{ error }}</span>
        <button type="button" @click="reload">重新加载</button>
      </section>

      <section v-else-if="loading" class="state-card">
        <van-loading size="28" color="#f97316" />
        <span>正在加载动态...</span>
      </section>

      <section v-else-if="dynamics.length === 0" class="empty-feed">
        <div class="empty-visual">
          <van-icon name="photo-o" size="40" />
        </div>
        <strong>还没有动态</strong>
        <span>成为第一个分享猫咪日常的村民吧</span>
        <button type="button" @click="router.push({ name: 'CreatePost' })">
          <van-icon name="plus" size="17" />
          发布动态
        </button>
      </section>

      <section v-else class="feed-list">
        <article v-for="item in dynamics" :key="item.id" class="feed-card" :class="{ recommended: item.isRecommended }" @click="openDetail(item.id)">
          <div class="feed-author">
            <van-image :src="getSafeAvatarUrl(item.avatar, item.userId)" fit="cover" width="44" height="44" round>
              <template #error>
                <img :src="getDefaultUserAvatar(item.userId)" alt="" width="44" height="44" class="avatar-fallback-img" />
              </template>
            </van-image>
            <div class="author-text">
              <strong>
                {{ item.username || '猫村村民' }}
                <span v-if="item.isRecommended" class="chief-badge">村长推荐</span>
              </strong>
              <span>{{ formatRelativeTime(item.createdAt) }} · {{ resolveLocation(item) }}</span>
            </div>
            <button class="more-btn" type="button" aria-label="更多" @click.stop="openCardMenu(item)">
              <van-icon name="ellipsis" size="18" />
            </button>
          </div>

          <p class="feed-content" @click.stop="openDetail(item.id)">{{ cleanDynamicContent(item.content) }}</p>
          <button v-if="isLongContent(cleanDynamicContent(item.content))" type="button" class="expand-content-btn" @click.stop="openDetail(item.id)">
            展开全文
          </button>

          <div v-if="item.images?.length" class="image-grid" :class="`count-${Math.min(item.images.length, 4)}`">
            <van-image
              v-for="(img, index) in item.images.slice(0, 4)"
              :key="img + index"
              :src="img"
              fit="cover"
              radius="14"
            >
              <template #error>
                <div class="image-error"><van-icon name="photo-o" size="26" /></div>
              </template>
            </van-image>
          </div>

          <div class="feed-meta">
            <span v-if="item.catName" class="cat-chip"><van-icon name="smile-o" size="13" />{{ item.catName }}</span>
            <span v-if="parseEmotionSnapshot(item.content)" class="cat-chip emotion-chip">本喵{{ parseEmotionSnapshot(item.content)?.tag }}中</span>
            <span v-if="!item.catName && !parseEmotionSnapshot(item.content)" class="cat-chip muted">猫村日常</span>
            <span>{{ item.commentCount || 0 }} 条评论</span>
          </div>

          <div class="feed-actions">
            <button type="button" :class="{ active: item.isLiked }" :disabled="likingId === item.id" @click.stop="toggleLike(item)">
              <van-icon :name="item.isLiked ? 'like' : 'like-o'" size="19" />
              {{ formatSocialCount(item.likeCount) }}
            </button>
            <button type="button" :class="{ active: item.isFavorited }" :disabled="favoriteId === item.id" @click.stop="toggleFavorite(item)">
              <van-icon :name="item.isFavorited ? 'star' : 'star-o'" size="19" />
              {{ formatSocialCount(item.favoriteCount) }}
            </button>
            <button type="button" @click.stop="openDetail(item.id)">
              <van-icon name="chat-o" size="19" />
              评论
            </button>
          </div>
        </article>

        <button v-if="hasMore" class="load-more" type="button" :disabled="loadingMore" @click="loadMore">
          {{ loadingMore ? '加载中...' : '查看更多动态' }}
        </button>
        <div v-else class="feed-end">已经到底了</div>
      </section>
    </main>

    <button class="compose-fab" type="button" aria-label="发布动态" @click="router.push({ name: 'CreatePost' })">
      <van-icon name="plus" size="27" />
    </button>

    <van-action-sheet v-model:show="showEditSheet" title="编辑动态">
      <div class="edit-sheet">
        <textarea v-model="editDraft" maxlength="2000" placeholder="更新你想说的话..." />
        <div class="edit-footer">
          <span>{{ editDraft.trim().length }}/2000</span>
          <button type="button" :disabled="savingEdit || !editDraft.trim()" @click="saveEdit">
            {{ savingEdit ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </van-action-sheet>

    <van-action-sheet
      v-model:show="showMenuSheet"
      :actions="menuActions"
      cancel-text="取消"
      close-on-click-action
      @select="handleMenuSelect"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { showConfirmDialog, showToast } from 'vant';
import AppTopBar from '@/components/AppTopBar.vue';
import { useSocialFeatures } from '@/composables/useSocialFeatures';
import { formatRelativeTime } from '@/utils/date';
import { applyDisplayProfileToDynamic } from '@/utils/userProfile';
import { getDefaultUserAvatar, getSafeAvatarUrl } from '@/utils/image';
import type { SocialDynamic } from '@/types/social';

const router = useRouter();
const activeTab = ref<'follow' | 'recommend'>('recommend');

const {
  fetchDynamicsList,
  likeADynamic,
  unlikeADynamic,
  toggleFavoriteADynamic,
  editDynamic,
  removeDynamic
} = useSocialFeatures();

const loading = ref(false);
const likingId = ref('');
const favoriteId = ref('');
const loadingMore = ref(false);
const error = ref<string | null>(null);
const dynamics = ref<SocialDynamic[]>([]);
const currentPage = ref(1);
const pageSize = 8;
const hasMore = ref(true);
const showEditSheet = ref(false);
const showMenuSheet = ref(false);
const savingEdit = ref(false);
const editingItem = ref<SocialDynamic | null>(null);
const menuItem = ref<SocialDynamic | null>(null);
const editDraft = ref('');
const menuActions = ref<Array<{ name: string; color?: string }>>([]);

const resolveLocation = (item: SocialDynamic) => {
  const source = item as SocialDynamic & { location?: string; address?: string; locationName?: string };
  if (source.location || source.address || source.locationName) return source.location || source.address || source.locationName;
  const locations = ['上海', '杭州', '成都', '北京', '深圳', '重庆', '广州', '苏州'];
  const idx = item.id.split('').reduce((acc, ch) => acc + ch.charCodeAt(0), 0) % locations.length;
  return locations[idx] || '猫村';
};

const isLongContent = (content?: string) => {
  const text = content || '';
  return text.length > 92 || text.split(/\r?\n/).length > 4;
};

const parseEmotionSnapshot = (content?: string) => {
  const match = String(content || '').match(/\[CV_EMOTION\s+id="([^"]*)"\s+tag="([^"]*)"\s+audio="([^"]*)"\]/);
  return match ? { id: match[1], tag: match[2], audio: match[3] } : null;
};

const cleanDynamicContent = (content?: string) => String(content || '').replace(/\n?\[CV_EMOTION[^\]]+\]/g, '').trim();

const formatSocialCount = (value?: number) => {
  const num = value || 0;
  if (num >= 10000) return `${(num / 10000).toFixed(1)}w`;
  if (num >= 1000) return `${(num / 1000).toFixed(1)}k`;
  return String(num);
};

const refresh = async () => {
  if (loading.value) return;
  loading.value = true;
  error.value = null;
  try {
    const res = await fetchDynamicsList({ page: 1, pageSize, scope: activeTab.value === 'follow' ? 'following' : 'all' });
    dynamics.value = (res.list || []).map((item: Record<string, unknown>) => applyDisplayProfileToDynamic(item as any));
    currentPage.value = 1;
    hasMore.value = dynamics.value.length < (res.total || 0);
  } catch (err: unknown) {
    const status = typeof err === 'object' && err !== null && 'response' in err
      ? (err as { response?: { status?: number } }).response?.status
      : undefined;
    error.value = status === 401 ? '登录已过期，请重新登录后查看广场' : '加载失败，请稍后重试';
  } finally {
    loading.value = false;
  }
};

const loadMore = async () => {
  if (loadingMore.value || loading.value || !hasMore.value) return;
  loadingMore.value = true;
  try {
    const nextPage = currentPage.value + 1;
    const res = await fetchDynamicsList({ page: nextPage, pageSize, scope: activeTab.value === 'follow' ? 'following' : 'all' });
    const list = (res.list || []).map((item: Record<string, unknown>) => applyDisplayProfileToDynamic(item as any));
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
const openDetail = (id: string) => router.push({ name: 'SocialDetail', params: { id } });

const openCardMenu = (item: SocialDynamic) => {
  menuItem.value = item;
  menuActions.value = item.isOwner
    ? [{ name: '编辑动态' }, { name: '删除动态', color: '#ee0a24' }, { name: '查看详情' }]
    : [{ name: '查看详情' }];
  showMenuSheet.value = true;
};

const handleMenuSelect = async (action: { name: string }) => {
  const item = menuItem.value;
  if (!item) return;
  if (action.name === '编辑动态') {
    editingItem.value = item;
    editDraft.value = item.content || '';
    showEditSheet.value = true;
    return;
  }
  if (action.name === '删除动态') {
    try {
      await showConfirmDialog({
        title: '删除动态',
        message: '删除后无法恢复，确认删除吗？'
      });
    } catch {
      return;
    }
    try {
      await removeDynamic(item.id);
      dynamics.value = dynamics.value.filter(d => d.id !== item.id);
      showToast({ type: 'success', message: '动态已删除' });
    } catch {
      showToast({ type: 'fail', message: '删除失败，请稍后重试' });
    }
    return;
  }
  openDetail(item.id);
};

const saveEdit = async () => {
  const target = editingItem.value;
  const content = editDraft.value.trim();
  if (!target || !content || savingEdit.value) return;
  savingEdit.value = true;
  try {
    const updated = await editDynamic(target.id, content);
    const index = dynamics.value.findIndex((item) => item.id === target.id);
    if (index !== -1) {
      dynamics.value[index] = applyDisplayProfileToDynamic(updated as any) as SocialDynamic;
    }
    showEditSheet.value = false;
    showToast({ type: 'success', message: '动态已更新' });
  } catch {
    showToast({ type: 'fail', message: '编辑失败，请稍后重试' });
  } finally {
    savingEdit.value = false;
  }
};

const toggleLike = async (dynamic: SocialDynamic) => {
  if (likingId.value) return;
  likingId.value = dynamic.id;
  const previousLiked = !!dynamic.isLiked;
  const previousCount = dynamic.likeCount || 0;
  dynamic.isLiked = !previousLiked;
  dynamic.likeCount = Math.max(0, previousCount + (previousLiked ? -1 : 1));
  try {
    const res = previousLiked ? await unlikeADynamic(dynamic.id) : await likeADynamic(dynamic.id);
    const serverCount = (res as any)?.like_count ?? (res as any)?.likeCount;
    if (typeof serverCount === 'number') dynamic.likeCount = serverCount;
  } catch {
    dynamic.isLiked = previousLiked;
    dynamic.likeCount = previousCount;
    showToast({ type: 'fail', message: '操作失败，请稍后重试' });
  } finally {
    likingId.value = '';
  }
};

const toggleFavorite = async (dynamic: SocialDynamic) => {
  if (favoriteId.value) return;
  favoriteId.value = dynamic.id;
  const previousFavorited = !!dynamic.isFavorited;
  const previousCount = dynamic.favoriteCount || 0;
  dynamic.isFavorited = !previousFavorited;
  dynamic.favoriteCount = Math.max(0, previousCount + (previousFavorited ? -1 : 1));
  try {
    const response = await toggleFavoriteADynamic(dynamic.id);
    dynamic.isFavorited = response.isFavorited;
    dynamic.favoriteCount = response.favoriteCount;
  } catch {
    dynamic.isFavorited = previousFavorited;
    dynamic.favoriteCount = previousCount;
    showToast({ type: 'fail', message: '收藏失败，请稍后重试' });
  } finally {
    favoriteId.value = '';
  }
};

onMounted(refresh);
watch(activeTab, () => { void refresh(); });
</script>

<style scoped>
.social-page {
  min-height: 100dvh;
  padding: 0 16px 104px;
  background: var(--cv-page-gradient);
}

.feed-switch {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
  border: 1px solid rgba(226, 232, 240, 0.88);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.7);
  padding: 4px;
}

.feed-switch button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  border: 0;
  border-radius: 12px;
  background: transparent;
  color: var(--cv-muted);
  padding: 9px;
  font-size: 14px;
  font-weight: 900;
}

.feed-switch button.active {
  background: var(--cv-ink);
  color: #fff;
  box-shadow: 0 10px 22px rgba(23, 32, 51, 0.14);
}

.feed-main,
.feed-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.feed-main {
  padding-top: 12px;
}

.state-card,
.empty-feed {
  display: grid;
  min-height: 220px;
  place-items: center;
  gap: 8px;
  border: 1px solid var(--cv-card-border);
  border-radius: var(--cv-card-radius);
  background: var(--cv-card-bg);
  padding: 26px;
  text-align: center;
  color: var(--cv-muted);
  box-shadow: var(--cv-card-shadow);
}

.state-card strong,
.empty-feed strong {
  color: var(--cv-ink);
  font-size: 17px;
  font-weight: 900;
}

.state-card button,
.empty-feed button,
.load-more {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border: 0;
  border-radius: 14px;
  background: linear-gradient(135deg, #f97316, #14b8a6);
  color: #fff;
  padding: 11px 16px;
  font-size: 14px;
  font-weight: 900;
}

.empty-visual {
  display: grid;
  width: 74px;
  height: 74px;
  place-items: center;
  border-radius: 24px;
  background: rgba(249,115,22,0.08);
  color: var(--cv-accent);
}

.feed-card {
  overflow: hidden;
  border: 1px solid var(--cv-card-border);
  border-radius: var(--cv-card-radius);
  background: var(--cv-card-bg);
  padding: 14px;
  box-shadow: var(--cv-card-shadow);
}

.feed-card.recommended {
  border-color: rgba(249, 115, 22, 0.34);
  box-shadow: 0 18px 38px rgba(249, 115, 22, 0.13);
}

.feed-author {
  display: flex;
  align-items: center;
  gap: 10px;
}

.avatar-fallback-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 999px;
}

.author-text {
  min-width: 0;
  flex: 1;
}

.author-text strong {
  display: block;
  overflow: hidden;
  color: var(--cv-ink);
  font-size: 15px;
  font-weight: 900;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.author-text span,
.feed-meta,
.feed-end {
  color: var(--cv-muted);
  font-size: 12px;
  font-weight: 700;
}

.author-text .chief-badge {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  margin-left: 6px;
  padding: 3px 8px;
  border-radius: 999px;
  background: linear-gradient(135deg, #fff7ed, #ffedd5);
  color: #ea580c;
  font-size: 11px;
  font-weight: 900;
  vertical-align: middle;
  box-shadow: inset 0 0 0 1px rgba(249, 115, 22, 0.14);
}

.author-text .chief-badge::before {
  content: '♛';
  font-size: 11px;
}

.emotion-chip {
  background: #ecfdf5;
  color: #0f766e;
}

.more-btn {
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;
  border: 0;
  border-radius: 12px;
  background: #f4f7fb;
  color: #748094;
}

.feed-content {
  margin: 12px 0;
  display: -webkit-box;
  overflow: hidden;
  color: var(--cv-ink);
  font-size: 15px;
  line-height: 1.68;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 4;
  white-space: pre-line;
  word-break: break-word;
}

.expand-content-btn {
  margin: -4px 0 10px;
  border: 0;
  background: transparent;
  color: var(--cv-accent);
  padding: 0;
  font-size: 13px;
  font-weight: 900;
}

.image-grid {
  display: grid;
  gap: 7px;
  overflow: hidden;
  margin-top: 10px;
}

.image-grid.count-1 {
  grid-template-columns: 1fr;
}

.image-grid.count-1 :deep(.van-image) {
  height: 248px;
}

.image-grid.count-2,
.image-grid.count-3,
.image-grid.count-4 {
  grid-template-columns: repeat(2, 1fr);
}

.image-grid.count-2 :deep(.van-image),
.image-grid.count-3 :deep(.van-image),
.image-grid.count-4 :deep(.van-image) {
  height: 148px;
}

.image-error {
  display: grid;
  width: 100%;
  height: 100%;
  place-items: center;
  background: rgba(249,115,22,0.08);
  color: var(--cv-accent);
}

.feed-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-top: 12px;
}

.cat-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  border-radius: 999px;
  background: rgba(249,115,22,0.08);
  color: var(--cv-accent);
  padding: 5px 9px;
  font-weight: 900;
}

.cat-chip.muted {
  background: #eef3f8;
  color: #748094;
}

.feed-actions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-top: 12px;
  border-top: 1px solid #edf2f7;
  padding-top: 12px;
}

.feed-actions button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  border: 0;
  border-radius: 13px;
  background: #f4f7fb;
  color: var(--cv-muted);
  padding: 9px 4px;
  font-size: 13px;
  font-weight: 900;
}

.feed-actions button.active {
  background: rgba(249,115,22,0.08);
  color: var(--cv-accent);
}

.load-more {
  width: 100%;
  background: var(--cv-card-bg);
  color: var(--cv-accent);
  box-shadow: var(--cv-card-shadow);
}

.feed-end {
  padding: 8px 0;
  text-align: center;
}

.compose-fab {
  position: fixed;
  bottom: 82px;
  left: 50%;
  z-index: 28;
  display: grid;
  width: 56px;
  height: 56px;
  place-items: center;
  transform: translateX(-50%);
  border: 0;
  border-radius: 18px;
  background: linear-gradient(135deg, #f97316, #14b8a6);
  color: #fff;
  box-shadow: 0 16px 34px rgba(249, 115, 22, 0.28);
}

.edit-sheet {
  padding: 14px 16px 18px;
}

.edit-sheet textarea {
  width: 100%;
  min-height: 150px;
  box-sizing: border-box;
  resize: none;
  border: 1px solid #dbe4ee;
  border-radius: 16px;
  background: #f8fafc;
  color: var(--cv-ink);
  outline: none;
  padding: 12px;
  font-size: 15px;
  line-height: 1.55;
}

.edit-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 10px;
  color: var(--cv-muted);
  font-size: 12px;
  font-weight: 800;
}

.edit-footer button {
  border: 0;
  border-radius: 13px;
  background: #172033;
  color: #fff;
  padding: 10px 18px;
  font-size: 14px;
  font-weight: 900;
}

.edit-footer button:disabled {
  opacity: 0.45;
}

/* Enlarge the app logo */
.social-page :deep(.app-topbar-logo img) {
  width: 52px;
  height: 52px;
}
</style>
