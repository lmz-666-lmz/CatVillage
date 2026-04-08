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
      <div class="relative mx-auto h-28 w-28">
        <van-uploader
          v-model="avatarList"
          :max-count="1"
          :preview-image="false"
          :after-read="onAvatarRead"
          class="h-full w-full"
        >
          <div class="h-full w-full overflow-hidden rounded-full border-4 border-white bg-surface-container-high shadow-md grid place-items-center">
            <van-image v-if="avatarUrl" :src="avatarUrl" fit="cover" width="112" height="112" />
            <span v-else class="text-4xl">👤</span>
          </div>
        </van-uploader>
        <div class="absolute bottom-1 right-0 grid h-11 w-11 place-items-center rounded-full border-2 border-white bg-[#ff6b35] text-white shadow-md">
          <van-icon name="paw-o" size="18" />
        </div>
      </div>

      <h2 class="mt-4 text-[34px] font-black tracking-tight text-[#12182a]">{{ nickname || '橘猫村长' }}</h2>
      <p class="mt-2 text-[20px] text-[#594139]">{{ bio || '村里的一只普通巡逻官 🐾' }}</p>
    </section>

    <section class="mt-6 rounded-[18px] bg-white px-3 py-4 shadow-sm">
      <div class="grid grid-cols-3 divide-x divide-slate-200 text-center">
        <div>
          <div class="text-[28px] font-extrabold text-[#12182a]">1.2k</div>
          <div class="mt-1 text-[18px] text-[#594139]">关注</div>
        </div>
        <div>
          <div class="text-[28px] font-extrabold text-[#12182a]">5.8k</div>
          <div class="mt-1 text-[18px] text-[#594139]">粉丝</div>
        </div>
        <div>
          <div class="text-[28px] font-extrabold text-[#12182a]">12.4k</div>
          <div class="mt-1 text-[18px] text-[#594139]">获赞</div>
        </div>
      </div>
    </section>

    <section class="mt-6 grid grid-cols-2 gap-3.5">
      <button type="button" class="rounded-[18px] bg-[#f7d8cf] p-5 text-left" @click="goMyCats">
        <div class="text-2xl text-[#7b2400]">
          <van-icon name="paw-o" size="30" />
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
            <div class="grid h-11 w-11 place-items-center rounded-xl bg-blue-50">
              <van-icon name="medical-o" color="#3b82f6" />
            </div>
            <div>
              <div class="text-[24px] font-bold text-[#12182a]">健康档案</div>
              <div class="text-[16px] text-[#594139]">记录疫苗与体检</div>
            </div>
          </div>
          <van-icon name="arrow" color="#b0a8a5" />
        </button>

        <button type="button" class="flex w-full items-center justify-between border-t border-slate-100 px-4 py-4 text-left" @click="openAdoption">
          <div class="flex items-center gap-3">
            <div class="grid h-11 w-11 place-items-center rounded-xl bg-purple-50">
              <van-icon name="gift-o" color="#a855f7" />
            </div>
            <div>
              <div class="text-[24px] font-bold text-[#12182a]">领养信息</div>
              <div class="text-[16px] text-[#594139]">寻找温暖的家</div>
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

    <van-form class="mt-5" @submit="onSubmit">
      <section class="mt-4 hidden">
        <van-cell-group inset>
          <van-field
            v-model="nickname"
            name="nickname"
            label="昵称"
            placeholder="请输入昵称"
            :rules="[{ required: true, message: '请输入昵称' }]"
          />

          <van-field
            v-model="gender"
            name="gender"
            label="性别"
            readonly
            is-link
            placeholder="请选择"
            @click="showGenderPicker = true"
          />

          <van-field
            v-model="bio"
            name="bio"
            label="简介"
            type="textarea"
            rows="3"
            autosize
            placeholder="简单介绍一下你和你的萌宠..."
          />
        </van-cell-group>
      </section>

      <div class="mt-4 space-y-3">
        <button
          type="submit"
          class="h-11 w-full rounded-[10px] bg-primary text-on-primary font-semibold shadow-cta active:scale-[0.99]"
        >
          保存资料
        </button>

        <button
          type="button"
          class="h-11 w-full rounded-[10px] border border-outline-variant bg-surface-container-lowest text-on-background font-semibold active:scale-[0.99]"
          @click="logout"
        >
          退出登录
        </button>
      </div>
    </van-form>

    <van-action-sheet v-model:show="showGenderPicker" title="选择性别">
      <div class="p-4 space-y-2">
        <van-button block type="primary" @click="setGender('女')">女</van-button>
        <van-button block type="primary" plain @click="setGender('男')">男</van-button>
      </div>
    </van-action-sheet>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { closeToast, showToast } from 'vant';
import type { UploaderFileListItem } from 'vant';
import { useCatsStore } from '@/stores';

const router = useRouter();
const catsStore = useCatsStore();

const avatarList = ref<UploaderFileListItem[]>([]);
const avatarUrl = ref('');
const nickname = ref('');
const gender = ref<'男' | '女'>('女');
const bio = ref('');
const showGenderPicker = ref(false);

const catsCountText = computed(() => `${Math.max(catsStore.getAllCats.length, 0)}只毛孩子已上线`);

const onAvatarRead = (file: UploaderFileListItem | UploaderFileListItem[]) => {
  const fileItem = Array.isArray(file) ? file[0] : file;
  if (!fileItem) {
    return;
  }
  if (typeof fileItem.content === 'string') {
    avatarUrl.value = fileItem.content;
  }
};

const setGender = (value: '男' | '女') => {
  gender.value = value;
  showGenderPicker.value = false;
};

const onSubmit = async () => {
  if (!nickname.value.trim()) {
    showToast({ type: 'fail', message: '请填写昵称' });
    return;
  }

  showToast({ type: 'loading', message: '正在保存...', forbidClick: true, duration: 0 });
  await new Promise((resolve) => setTimeout(resolve, 500));
  closeToast();
  showToast({ type: 'success', message: '已保存' });
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
  showToast({ message: '设置中心即将上线' });
};

const goMyCats = () => {
  const firstCat = catsStore.getAllCats[0];
  if (!firstCat) {
    showToast({ type: 'fail', message: '请先添加猫咪档案' });
    router.push({ name: 'AddCat' });
    return;
  }
  router.push({ name: 'CatArchive', params: { id: firstCat.id } });
};

const goMyFavorites = () => {
  router.push({ name: 'Social' });
  showToast({ message: '已进入广场，可在详情页查看收藏状态' });
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

const openAdoption = () => {
  showToast({ message: '领养信息功能即将上线' });
};

const openVip = () => {
  showToast({ message: 'VIP 功能即将开放' });
};

onMounted(() => {
  void catsStore.fetchAllCats();
});
</script>
