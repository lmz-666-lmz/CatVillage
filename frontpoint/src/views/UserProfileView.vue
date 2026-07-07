<template>
  <div class="profile-page">
    <AppTopBar title="我的" subtitle="资料、猫咪和健康记录" kicker="Profile">
      <template #actions>
        <button class="topbar-action" type="button" aria-label="设置" @click="openSettings">
          <van-icon name="setting-o" size="18" />
        </button>
      </template>
    </AppTopBar>

    <!-- Avatar + Name -->
    <section class="profile-hero">
      <button type="button" class="profile-hero-tap" @click="openSettings">
        <div class="profile-avatar-wrap">
          <van-image :src="safeAvatarUrl" fit="cover" width="88" height="88" round class="profile-avatar">
            <template #error>
              <img :src="getDefaultUserAvatar(getCurrentUserId())" alt="" width="88" height="88" class="avatar-fallback-img" />
            </template>
          </van-image>
          <div class="profile-avatar-edit">
            <van-icon name="edit" size="14" />
          </div>
        </div>
        <h2 class="profile-name">{{ nickname }}</h2>
        <p class="profile-hint">点击头像或用户名修改资料</p>
      </button>
      <p class="profile-miao-id">喵村号：{{ miaoId }}</p>
      <p class="profile-bio">{{ bio || '村里的一只普通巡逻官 🐾' }}</p>
    </section>

    <!-- Stats -->
    <section class="profile-stats">
      <div class="profile-stat">
        <span class="profile-stat-num">{{ formatCount(stats.following) }}</span>
        <span class="profile-stat-label">关注</span>
      </div>
      <div class="profile-stat">
        <span class="profile-stat-num">{{ formatCount(stats.followers) }}</span>
        <span class="profile-stat-label">粉丝</span>
      </div>
      <div class="profile-stat">
        <span class="profile-stat-num">{{ formatCount(stats.likes) }}</span>
        <span class="profile-stat-label">获赞</span>
      </div>
    </section>

    <!-- Quick Actions -->
    <section class="profile-quick">
      <button class="profile-quick-card primary" @click="goMyCats">
        <div class="profile-quick-icon-wrap warm">
          <span class="profile-quick-emoji">🐱</span>
        </div>
        <div class="profile-quick-text">
          <span class="profile-quick-title">我的萌宠</span>
          <span class="profile-quick-sub">{{ catsCountText }}</span>
        </div>
        <van-icon name="arrow" size="16" class="profile-quick-arrow" />
      </button>

      <button class="profile-quick-card" @click="goMyFavorites">
        <div class="profile-quick-icon-wrap orange">
          <van-icon name="star-o" size="20" />
        </div>
        <span class="profile-quick-title">我的收藏</span>
        <van-icon name="arrow" size="16" class="profile-quick-arrow" />
      </button>

      <button class="profile-quick-card" @click="goCreatePost">
        <div class="profile-quick-icon-wrap blue">
          <van-icon name="edit" size="20" />
        </div>
        <span class="profile-quick-title">村内笔记</span>
        <van-icon name="arrow" size="16" class="profile-quick-arrow" />
      </button>
    </section>

    <!-- Menu -->
    <section class="profile-menu">
      <button class="profile-menu-item" @click="openMarket">
        <div class="profile-menu-icon-wrap shop">
          <van-icon name="shopping-cart-o" size="20" />
        </div>
        <div class="profile-menu-text">
          <span class="profile-menu-title">喵村市集</span>
          <span class="profile-menu-sub">领券买罐罐更划算</span>
        </div>
        <van-icon name="arrow" size="16" class="profile-menu-arrow" />
      </button>

      <button class="profile-menu-item" @click="openHealthArchive">
        <div class="profile-menu-icon-wrap health">
          <van-icon name="add-o" size="20" />
        </div>
        <div class="profile-menu-text">
          <span class="profile-menu-title">健康档案</span>
          <span class="profile-menu-sub">记录疫苗与体检</span>
        </div>
        <van-icon name="arrow" size="16" class="profile-menu-arrow" />
      </button>

      <button class="profile-menu-item" @click="openFeedingRecord">
        <div class="profile-menu-icon-wrap feed">
          <van-icon name="smile-comment-o" size="20" />
        </div>
        <div class="profile-menu-text">
          <span class="profile-menu-title">投喂记录</span>
          <span class="profile-menu-sub">记录口味偏好与每日食量</span>
        </div>
        <van-icon name="arrow" size="16" class="profile-menu-arrow" />
      </button>
    </section>

    <!-- VIP Banner -->
    <section class="profile-vip">
      <div class="profile-vip-left">
        <span class="profile-vip-icon">👑</span>
        <div>
          <div class="profile-vip-title">喵村VIP</div>
          <div class="profile-vip-sub">解锁专属挂件与勋章</div>
        </div>
      </div>
      <button class="profile-vip-btn" @click="openVip">立即开启 <van-icon name="arrow" size="14" /></button>
    </section>

    <!-- Footer -->
    <div class="profile-footer">
      <button class="profile-footer-primary" @click="openSettings">编辑个人资料</button>
      <button class="profile-footer-secondary" @click="logout">退出登录</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';
import AppTopBar from '@/components/AppTopBar.vue';
import { useCatsStore, useCurrentCatStore } from '@/stores';
import { getMe } from '@/api/auth';
import { clearAccountRuntimeState, getCurrentUserId, globalProfile, setCurrentUserIdentity } from '@/utils/userProfile';
import { useMessaging } from '@/composables/useMessaging';
import { useSocialFeatures } from '@/composables/useSocialFeatures';
import { getDefaultUserAvatar, getSafeAvatarUrl } from '@/utils/image';

const router = useRouter();
const catsStore = useCatsStore();
const currentCatStore = useCurrentCatStore();
const { fetchFollowerList, fetchFriendList } = useMessaging();
const { fetchMyDynamicsList } = useSocialFeatures();

const avatarUrl = computed(() => globalProfile.avatarUrl);
const safeAvatarUrl = computed(() => getSafeAvatarUrl(avatarUrl.value, getCurrentUserId()));
const nickname = computed(() => globalProfile.nickname);
const miaoId = computed(() => globalProfile.miaoId);
const bio = ref('');
const stats = ref({ following: 0, followers: 0, likes: 0 });
const catsCountText = computed(() => `${Math.max(catsStore.getAllCats.length, 0)}只毛孩子已上线`);

const formatCount = (value: number) => {
  if (value >= 10000) return `${(value / 10000).toFixed(1)}w`;
  if (value >= 1000) return `${(value / 1000).toFixed(1)}k`;
  return String(value);
};

const loadProfileStats = async () => {
  try {
    const [followersRes, myDynamicsRes] = await Promise.all([
      fetchFollowerList({ page: 1, pageSize: 50 }),
      fetchMyDynamicsList({ page: 1, pageSize: 100 })
    ]);
    const likes = (myDynamicsRes.list || []).reduce((s: number, i: any) => s + ((i.likeCount as number) || 0), 0);
    stats.value.followers = followersRes.total || (followersRes.list || []).length;
    stats.value.likes = likes;
    let followingCount = 0, page = 1, total = Infinity;
    while ((page - 1) * 50 < total) {
      const friendRes = await fetchFriendList({ page, pageSize: 50 });
      total = friendRes.total || 0;
      followingCount += (friendRes.list || []).filter((i: any) => i.isFollowing).length;
      page++; if (!(friendRes.list || []).length) break;
    }
    stats.value.following = followingCount;
  } catch { showToast({ message: '资料统计同步失败' }); }
};
const hydrateProfile = async () => {
  try { const res = await getMe(); if (res.data?.id) setCurrentUserIdentity(res.data); } catch { /* keep cache */ }
};
const logout = () => { clearAccountRuntimeState({ includeToken: true }); catsStore.clearCats(); currentCatStore.clearCurrentCat(); showToast({ message: '已退出登录' }); router.replace({ name: 'Login' }); };
const openSettings = () => router.push({ name: 'Settings' });
const goMyCats = () => router.push({ name: 'MyPets' });
const goMyFavorites = () => router.push({ name: 'MyFavorites' });
const goCreatePost = () => router.push({ name: 'CreatePost' });
const openMarket = () => showToast({ message: '喵村市集即将开放' });
const openVip = () => showToast({ message: 'VIP 功能即将开放' });
const openHealthArchive = async () => {
  if (!catsStore.getAllCats.length) await catsStore.fetchAllCats();
  const first = catsStore.getAllCats[0];
  if (!first) { showToast({ type: 'fail', message: '请先添加猫咪档案' }); router.push({ name: 'AddCat' }); return; }
  router.push({ name: 'CatArchive', params: { id: first.id } });
};
const openFeedingRecord = async () => {
  if (!catsStore.getAllCats.length) await catsStore.fetchAllCats();
  const first = catsStore.getAllCats[0];
  if (!first) { showToast({ type: 'fail', message: '请先添加猫咪档案' }); router.push({ name: 'AddCat' }); return; }
  router.push({ name: 'FeedRecord', query: { catId: first.id } });
};

onMounted(() => { void hydrateProfile(); void catsStore.fetchAllCats(true); void loadProfileStats(); });
</script>

<style scoped>
/* ========== PAGE ========== */
.profile-page { min-height: 100dvh; padding: 0 16px 40px; background: var(--cv-page-gradient); }

/* ========== HEADER ========== */
.profile-header { display: flex; align-items: center; justify-content: space-between; padding: 12px 0 8px; }
.profile-header-title { font-size: 24px; font-weight: 800; color: var(--cv-accent); margin: 0; }
.profile-header-actions { display: flex; gap: 8px; }
.profile-header-btn { width: 38px; height: 38px; border-radius: 14px; border: none; background: rgba(0,0,0,0.04); color: var(--cv-muted); display: grid; place-items: center; cursor: pointer; transition: all .12s; }
.profile-header-btn:active { transform: scale(.9); }
.profile-header-btn.accent { background: rgba(249,115,22,0.08); color: var(--cv-accent); }

/* ========== HERO ========== */
.profile-hero { text-align: center; padding: 12px 0 16px; }
.profile-hero-tap { background: none; border: none; cursor: pointer; display: block; margin: 0 auto; padding: 0; }
.profile-avatar-wrap { position: relative; display: inline-block; }
.profile-avatar { box-shadow: 0 4px 20px rgba(0,0,0,0.08); border: 3px solid #fff; }
.profile-avatar-edit { position: absolute; bottom: 2px; right: 2px; width: 28px; height: 28px; border-radius: 50%; background: var(--cv-accent); color: #fff; display: grid; place-items: center; border: 2.5px solid #fff; box-shadow: 0 2px 8px rgba(249,115,22,0.3); }
.profile-name { font-size: 20px; font-weight: 800; color: var(--cv-ink); margin: 10px 0 0; }
.profile-hint { font-size: 12px; color: var(--cv-muted); margin: 2px 0 0; }
.profile-miao-id { font-size: 13px; color: var(--cv-muted); margin: 8px 0 0; }
.profile-bio { font-size: 14px; color: var(--cv-muted); margin: 4px 0 0; }

/* ========== STATS ========== */
.profile-stats { display: grid; grid-template-columns: repeat(3, 1fr); background: #fff; border-radius: 20px; padding: 14px 0; margin: 8px 0 16px; box-shadow: 0 1px 8px rgba(0,0,0,0.03); }
.profile-stat { text-align: center; }
.profile-stat:not(:last-child) { border-right: 1px solid #f3f4f6; }
.profile-stat-num { font-size: 20px; font-weight: 800; color: var(--cv-ink); display: block; }
.profile-stat-label { font-size: 12px; color: var(--cv-muted); margin-top: 2px; display: block; }

/* ========== QUICK CARDS ========== */
.profile-quick { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 16px; }
.profile-quick-card { display: flex; align-items: center; gap: 10px; background: #fff; border-radius: 18px; padding: 14px; border: none; cursor: pointer; text-align: left; box-shadow: 0 1px 6px rgba(0,0,0,0.03); transition: transform .12s; }
.profile-quick-card:active { transform: scale(.97); }
.profile-quick-card.primary { grid-column: span 2; background: rgba(249,115,22,0.08); border: 1px solid rgba(249,115,22,0.1); }
.profile-quick-icon-wrap { width: 40px; height: 40px; border-radius: 14px; display: grid; place-items: center; flex-shrink: 0; }
.profile-quick-icon-wrap.warm { background: #fbe8e1; }
.profile-quick-icon-wrap.orange { background: rgba(249,115,22,0.08); color: var(--cv-accent); }
.profile-quick-icon-wrap.blue { background: #eff6ff; color: #3b82f6; }
.profile-quick-emoji { font-size: 22px; }
.profile-quick-text { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.profile-quick-title { font-size: 15px; font-weight: 700; color: var(--cv-ink); }
.profile-quick-sub { font-size: 12px; color: var(--cv-muted); }
.profile-quick-arrow { color: #d1d5db; flex-shrink: 0; margin-left: auto; }

/* ========== MENU ========== */
.profile-menu { display: flex; flex-direction: column; gap: 2px; background: #fff; border-radius: 20px; overflow: hidden; margin-bottom: 16px; box-shadow: 0 1px 8px rgba(0,0,0,0.03); }
.profile-menu-item { display: flex; align-items: center; gap: 12px; padding: 14px 16px; border: none; background: none; cursor: pointer; width: 100%; text-align: left; transition: background .12s; }
.profile-menu-item:active { background: #f9fafb; }
.profile-menu-item:not(:last-child) { border-bottom: 1px solid #f3f4f6; }
.profile-menu-icon-wrap { width: 38px; height: 38px; border-radius: 12px; display: grid; place-items: center; flex-shrink: 0; }
.profile-menu-icon-wrap.shop { background: rgba(249,115,22,0.08); color: var(--cv-accent); }
.profile-menu-icon-wrap.health { background: #eff6ff; color: #3b82f6; }
.profile-menu-icon-wrap.feed { background: #f5f0ff; color: #9554e5; }
.profile-menu-text { display: flex; flex-direction: column; gap: 2px; flex: 1; }
.profile-menu-title { font-size: 15px; font-weight: 700; color: var(--cv-ink); }
.profile-menu-sub { font-size: 13px; color: var(--cv-muted); }
.profile-menu-arrow { color: #d1d5db; flex-shrink: 0; }

/* ========== VIP ========== */
.profile-vip { display: flex; align-items: center; justify-content: space-between; background: linear-gradient(135deg, #1f2937, #374151); border-radius: 20px; padding: 18px 20px; color: #fff; margin-bottom: 24px; }
.profile-vip-left { display: flex; align-items: center; gap: 10px; }
.profile-vip-icon { font-size: 28px; }
.profile-vip-title { font-size: 18px; font-weight: 800; }
.profile-vip-sub { font-size: 13px; color: rgba(255,255,255,0.65); margin-top: 2px; }
.profile-vip-btn { display: inline-flex; align-items: center; gap: 4px; background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.2); color: #fff; font-size: 13px; font-weight: 700; padding: 8px 16px; border-radius: 999px; cursor: pointer; transition: background .12s; }
.profile-vip-btn:active { background: rgba(255,255,255,0.25); }

/* ========== FOOTER ========== */
.profile-footer { display: flex; flex-direction: column; gap: 10px; }
.profile-footer-primary { width: 100%; padding: 13px 0; border-radius: 14px; border: none; background: linear-gradient(135deg, var(--cv-accent), #14b8a6); color: #fff; font-size: 16px; font-weight: 700; cursor: pointer; box-shadow: 0 4px 16px rgba(249,115,22,0.25); transition: transform .12s; }
.profile-footer-primary:active { transform: scale(.98); }
.profile-footer-secondary { width: 100%; padding: 13px 0; border-radius: 14px; border: 1.5px solid #e5e7eb; background: #fff; color: var(--cv-muted); font-size: 15px; font-weight: 600; cursor: pointer; transition: transform .12s; }
.profile-footer-secondary:active { transform: scale(.98); }

</style>

<style scoped>
.avatar-fallback-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 999px;
}

.profile-page {
  padding: 0 16px 104px;
  background: var(--cv-page-gradient);
}

.profile-hero,
.profile-stats,
.profile-quick-card,
.profile-menu,
.profile-vip {
  border: 1px solid var(--cv-card-border);
  box-shadow: var(--cv-card-shadow);
}

.profile-hero {
  margin-top: 12px;
  border-radius: var(--cv-card-radius);
  background: var(--cv-card-bg);
  padding: 18px 14px;
}

.profile-header {
  display: none;
}

.profile-stats,
.profile-menu,
.profile-quick-card {
  background: var(--cv-card-bg);
}

.profile-vip {
  background: linear-gradient(135deg, var(--cv-ink), #2d3b52);
}

.profile-footer-primary {
  background: linear-gradient(135deg, var(--cv-accent), #14b8a6);
}
</style>
