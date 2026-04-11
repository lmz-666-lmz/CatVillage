<template>
  <div class="min-h-[100dvh] bg-[#f4f5fb] px-4 pt-3 pb-8">
    <header class="flex min-h-[54px] items-center justify-between">
      <h1 class="text-[23px] font-extrabold tracking-tight text-[#ff6b35]">我的</h1>
      <div class="flex items-center gap-4">
        <button type="button" class="grid h-10 w-10 place-items-center rounded-full text-[#594139]" @click="toggleThemeHint">
          <van-icon name="moon-o" size="20" />
        </button>
        <button type="button" class="grid h-10 w-10 place-items-center rounded-full text-[#594139]" @click="openSettings">
          <van-icon name="setting-o" size="20" />
        </button>
      </div>
    </header>

    <section class="mt-6 text-center">
      <button type="button" class="mx-auto block" @click="openSettings">
        <div class="relative mx-auto h-28 w-28">
          <div class="h-full w-full overflow-hidden rounded-full border-4 border-white bg-surface-container-high shadow-md grid place-items-center">
            <van-image :src="avatarUrl" fit="cover" width="112" height="112" />
          </div>
          <div class="absolute bottom-1 right-0 grid h-11 w-11 place-items-center rounded-full border-2 border-white bg-[#ff6b35] text-white shadow-md">
            <van-icon name="edit" size="18" />
          </div>
        </div>

        <h2 class="mt-4 text-[26px] font-black tracking-tight text-[#12182a]">{{ nickname }}</h2>
        <p class="mt-2 text-[14px] text-[#7d7774]">点击头像或用户名修改资料</p>
      </button>
      <p class="mt-2 text-[14px] text-[#837c78]">喵村号：{{ miaoId }}</p>
      <p class="mt-2 text-[16px] text-[#594139]">{{ bio || '村里的一只普通巡逻官 🐾' }}</p>
    </section>

    <section class="mt-6 rounded-[18px] bg-white px-3 py-4 shadow-sm">
      <div class="grid grid-cols-3 divide-x divide-slate-200 text-center">
        <div>
          <div class="text-[28px] font-extrabold text-[#12182a]">{{ formatCount(stats.following) }}</div>
          <div class="mt-1 text-[18px] text-[#594139]">关注</div>
        </div>
        <div>
          <div class="text-[28px] font-extrabold text-[#12182a]">{{ formatCount(stats.followers) }}</div>
          <div class="mt-1 text-[18px] text-[#594139]">粉丝</div>
        </div>
        <div>
          <div class="text-[28px] font-extrabold text-[#12182a]">{{ formatCount(stats.likes) }}</div>
          <div class="mt-1 text-[18px] text-[#594139]">获赞</div>
        </div>
      </div>
    </section>

    <section class="mt-6 grid grid-cols-2 gap-3.5">
      <button type="button" class="rounded-[18px] bg-[#f7d8cf] p-5 text-left" @click="goMyCats">
        <div class="grid h-12 w-12 place-items-center rounded-2xl bg-[#fbe8e1] text-[#8a2a00] shadow-[inset_0_0_0_1px_rgba(179,53,0,0.08)]">
          <svg class="h-7 w-7" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M8.5 7.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zm7 0a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zM4 11.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zm16 0a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zM12 11c-2.3 0-5.1.7-6.5 2.8C4 16.1 5.4 20 12 20s8-3.9 6.5-6.2C17.1 11.7 14.3 11 12 11z"/>
          </svg>
        </div>
        <div class="mt-7 text-[26px] font-extrabold text-[#7b2400]">我的萌宠</div>
        <div class="mt-2 text-[17px] text-[#a55a46]">{{ catsCountText }}</div>
      </button>

      <div class="grid grid-rows-2 gap-3.5">
      <button type="button" class="flex items-center justify-between rounded-[18px] bg-white px-5" @click="goMyFavorites">
          <div class="flex items-center gap-3">
            <div class="grid h-9 w-9 place-items-center rounded-xl bg-[#fff2e9] text-[#ff6b35] shadow-[inset_0_0_0_1px_rgba(255,107,53,0.15)]">
              <svg class="h-5 w-5" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                <path d="M12 3.5l2.6 5.2 5.7.8-4.1 4 1 5.7-5.2-2.7-5.2 2.7 1-5.7-4.1-4 5.7-.8L12 3.5z"/>
              </svg>
            </div>
            <span class="text-[24px] font-bold text-[#12182a]">我的收藏</span>
          </div>
          <van-icon name="arrow" color="#b0a8a5" />
        </button>

        <button type="button" class="flex items-center justify-between rounded-[18px] bg-white px-5" @click="goCreatePost">
          <div class="flex items-center gap-3">
            <div class="grid h-9 w-9 place-items-center rounded-xl bg-[#e8f8ff] text-[#00a7cb] shadow-[inset_0_0_0_1px_rgba(0,167,203,0.15)]">
              <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path d="M4 17.2V20h2.8L17.9 8.9l-2.8-2.8L4 17.2z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
                <path d="M13.9 7.1l2.8 2.8" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
              </svg>
            </div>
            <span class="text-[24px] font-bold text-[#12182a]">村内笔记</span>
          </div>
          <van-icon name="arrow" color="#b0a8a5" />
        </button>
      </div>
    </section>

    <section class="mt-5 rounded-[18px] bg-[#eef0ff] p-3">
      <div class="space-y-1 rounded-[14px] bg-white">
        <button type="button" class="flex w-full items-center justify-between px-4 py-4 text-left" @click="openMarket">
          <div class="flex items-center gap-3">
            <div class="grid h-11 w-11 place-items-center rounded-xl bg-orange-50">
              <van-icon name="shopping-cart-o" color="#ff6b35" />
            </div>
            <div>
              <div class="text-[24px] font-bold text-[#12182a]">喵村市集</div>
              <div class="text-[16px] text-[#594139]">领券买罐罐更划算</div>
            </div>
          </div>
          <van-icon name="arrow" color="#b0a8a5" />
        </button>

        <button type="button" class="flex w-full items-center justify-between border-t border-slate-100 px-4 py-4 text-left" @click="openHealthArchive">
          <div class="flex items-center gap-3">
            <div class="grid h-11 w-11 place-items-center rounded-xl bg-[#e0f2fe] text-[#0284c7] shadow-[inset_0_0_0_1px_rgba(2,132,199,0.12)]">
              <svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <circle cx="12" cy="12" r="8.5" stroke="currentColor" stroke-width="1.8" />
                <path d="M12 8v8M8 12h8" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
              </svg>
            </div>
            <div>
              <div class="text-[24px] font-bold text-[#12182a]">健康档案</div>
              <div class="text-[16px] text-[#594139]">记录疫苗与体检</div>
            </div>
          </div>
          <van-icon name="arrow" color="#b0a8a5" />
        </button>

        <button type="button" class="flex w-full items-center justify-between border-t border-slate-100 px-4 py-4 text-left" @click="openFeedingRecord">
          <div class="flex items-center gap-3">
            <div class="grid h-11 w-11 place-items-center rounded-xl bg-[#f3ebff] text-[#9554e5] shadow-[inset_0_0_0_1px_rgba(149,84,229,0.14)]">
              <svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path d="M7 9.5h10l-1 8H8l-1-8z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
                <path d="M9 9.5a3 3 0 0 1 6 0" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
              </svg>
            </div>
            <div>
              <div class="text-[24px] font-bold text-[#12182a]">投喂记录</div>
              <div class="text-[16px] text-[#594139]">记录口味偏好与每日食量</div>
            </div>
          </div>
          <van-icon name="arrow" color="#b0a8a5" />
        </button>
      </div>
    </section>

    <section class="mt-6 overflow-hidden rounded-[18px] bg-[#b83a00] px-6 py-5 text-white">
      <div class="flex items-center justify-between">
        <div>
          <div class="flex items-center gap-2 text-[28px] font-extrabold">
            <svg class="h-7 w-7 text-[#ffd8b8]" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <path d="M4 18h16l-1.6-8.2a1 1 0 0 0-1.6-.6L13 12 9.2 9.2a1 1 0 0 0-1.6.6L4 18zm3.2-2h9.6l.9-4.6-3.1 2.3a1 1 0 0 1-1.2 0l-2.4-1.8-2.4 1.8a1 1 0 0 1-1.2 0l-3.1-2.3.9 4.6zM7 20h10a1 1 0 1 1 0 2H7a1 1 0 1 1 0-2z"/>
            </svg>
            <span>喵村VIP</span>
          </div>
          <div class="mt-1 text-[16px] text-white/85">解锁专属挂件与勋章</div>
        </div>
        <button
          type="button"
          class="inline-flex min-w-[152px] items-center justify-center gap-1 rounded-full px-5 py-2 text-[16px] font-extrabold shadow-[0_2px_10px_rgba(120,40,0,0.12)]"
          style="background:#fff6ec;color:#8f2d00;"
          @click="openVip"
        >
          <span class="leading-none">立即开启</span>
          <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M8 6l8 6-8 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </section>

    <div class="mt-6 space-y-3">
      <button
        type="button"
        class="h-11 w-full rounded-[10px] bg-primary text-on-primary font-semibold shadow-cta active:scale-[0.99]"
        @click="openSettings"
      >
        编辑个人资料
      </button>

      <button
        type="button"
        class="h-11 w-full rounded-[10px] border border-outline-variant bg-surface-container-lowest text-on-background font-semibold active:scale-[0.99]"
        @click="logout"
      >
        退出登录
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';
import { useCatsStore } from '@/stores';
import { globalProfile } from '@/utils/userProfile';
import { useMessaging } from '@/composables/useMessaging';
import { useSocialFeatures } from '@/composables/useSocialFeatures';

const router = useRouter();
const catsStore = useCatsStore();
const { fetchFollowerList, fetchFriendList } = useMessaging();
const { fetchMyDynamicsList } = useSocialFeatures();

const avatarUrl = computed(() => globalProfile.avatarUrl);
const nickname = computed(() => globalProfile.nickname);
const miaoId = computed(() => globalProfile.miaoId);
const bio = ref('');
const stats = ref({ following: 0, followers: 0, likes: 0 });

const catsCountText = computed(() => `${Math.max(catsStore.getAllCats.length, 0)}只毛孩子已上线`);

const formatCount = (value: number) => {
  if (value >= 10000) {
    return `${(value / 10000).toFixed(1)}w`;
  }
  if (value >= 1000) {
    return `${(value / 1000).toFixed(1)}k`;
  }
  return String(value);
};

const loadProfileStats = async () => {
  try {
    const [followersRes, myDynamicsRes] = await Promise.all([
      fetchFollowerList({ page: 1, pageSize: 50 }),
      fetchMyDynamicsList({ page: 1, pageSize: 100 })
    ]);

    const likes = (myDynamicsRes.list || []).reduce((sum, item) => sum + (item.likeCount || 0), 0);
    stats.value.followers = followersRes.total || (followersRes.list || []).length;
    stats.value.likes = likes;

    let followingCount = 0;
    let page = 1;
    let total = Number.POSITIVE_INFINITY;
    while ((page - 1) * 50 < total) {
      const friendRes = await fetchFriendList({ page, pageSize: 50 });
      total = friendRes.total || 0;
      followingCount += (friendRes.list || []).filter((item) => item.isFollowing).length;
      page += 1;
      if (!(friendRes.list || []).length) {
        break;
      }
    }
    stats.value.following = followingCount;
  } catch {
    showToast({ message: '资料统计同步失败，已显示默认值' });
  }
};

const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('cats');
  localStorage.removeItem('currentCatId');
  showToast({ message: '已退出登录' });
  router.replace({ name: 'Login' });
};

const toggleThemeHint = () => {
  showToast({ message: '夜间模式即将上线' });
};

const openSettings = () => {
  router.push({ name: 'Settings' });
};

const goMyCats = () => {
  router.push({ name: 'MyPets' });
};

const goMyFavorites = () => {
  router.push({ name: 'MyFavorites' });
};

const goCreatePost = () => {
  router.push({ name: 'CreatePost' });
};

const openMarket = () => {
  showToast({ message: '喵村市集即将开放' });
};

const openHealthArchive = async () => {
  if (!catsStore.getAllCats.length) {
    await catsStore.fetchAllCats();
  }
  const firstCat = catsStore.getAllCats[0];
  if (!firstCat) {
    showToast({ type: 'fail', message: '请先添加猫咪档案' });
    router.push({ name: 'AddCat' });
    return;
  }
  router.push({ name: 'CatArchive', params: { id: firstCat.id } });
};

const openFeedingRecord = async () => {
  if (!catsStore.getAllCats.length) {
    await catsStore.fetchAllCats();
  }
  const firstCat = catsStore.getAllCats[0];
  if (!firstCat) {
    showToast({ type: 'fail', message: '请先添加猫咪档案' });
    router.push({ name: 'AddCat' });
    return;
  }
  router.push({ name: 'FeedRecord', query: { catId: firstCat.id } });
};

const openVip = () => {
  showToast({ message: 'VIP 功能即将开放' });
};

onMounted(() => {
  void catsStore.fetchAllCats();
  void loadProfileStats();
});
</script>
