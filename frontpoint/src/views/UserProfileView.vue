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
        <div class="text-2xl">
          <van-icon name="paw-o" size="36" color="#b33500" />
        </div>
        <div class="mt-7 text-[26px] font-extrabold text-[#7b2400]">我的萌宠</div>
        <div class="mt-2 text-[17px] text-[#a55a46]">{{ catsCountText }}</div>
      </button>

      <div class="grid grid-rows-2 gap-3.5">
      <button type="button" class="flex items-center justify-between rounded-[18px] bg-white px-5" @click="goMyFavorites">
          <div class="flex items-center gap-3">
            <van-icon name="star" size="22" color="#ff6b35" />
            <span class="text-[24px] font-bold text-[#12182a]">我的收藏</span>
          </div>
          <van-icon name="arrow" color="#b0a8a5" />
        </button>

        <button type="button" class="flex items-center justify-between rounded-[18px] bg-white px-5" @click="goCreatePost">
          <div class="flex items-center gap-3">
            <van-icon name="edit" size="22" color="#00a7cb" />
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
            <div class="grid h-11 w-11 place-items-center rounded-xl" style="background-color: #e0f2fe;">
              <van-icon name="medical-o" color="#0284c7" size="22" />
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
            <div class="grid h-11 w-11 place-items-center rounded-xl bg-purple-50">
              <van-icon name="shop-o" color="#a855f7" />
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
          <div class="text-[28px] font-extrabold">喵村VIP</div>
          <div class="mt-1 text-[16px] text-white/85">解锁专属挂件与勋章</div>
        </div>
        <button type="button" class="rounded-full bg-white px-5 py-2 text-[16px] font-bold text-[#b83a00]" @click="openVip">立即开启</button>
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
import { getUserDisplayProfile } from '@/utils/userProfile';
import { useMessaging } from '@/composables/useMessaging';
import { useSocialFeatures } from '@/composables/useSocialFeatures';

const router = useRouter();
const catsStore = useCatsStore();
const { fetchFollowerList, fetchFriendList } = useMessaging();
const { fetchMyDynamicsList } = useSocialFeatures();

const avatarUrl = ref('');
const nickname = ref('');
const miaoId = ref('');
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

const openHealthArchive = () => {
  const firstCat = catsStore.getAllCats[0];
  if (!firstCat) {
    showToast({ type: 'fail', message: '请先添加猫咪档案' });
    router.push({ name: 'AddCat' });
    return;
  }
  router.push({ name: 'CatArchive', params: { id: firstCat.id } });
};

const openFeedingRecord = () => {
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
  const profile = getUserDisplayProfile();
  avatarUrl.value = profile.avatarUrl;
  nickname.value = profile.nickname;
  miaoId.value = profile.miaoId;
  void catsStore.fetchAllCats();
  void loadProfileStats();
});
</script>
