<template>
  <div class="relative min-h-[100dvh] overflow-hidden bg-[#f5f7fb] px-5 pt-3 pb-6">
    <div class="pointer-events-none absolute inset-x-0 bottom-0 h-80 bg-[radial-gradient(ellipse_at_bottom,_rgba(201,72,0,0.07),_transparent_70%)]"></div>
    <div class="pointer-events-none absolute -bottom-16 -right-12 h-[200px] w-[200px] rounded-full border-[20px] border-[#f3eaf2]/70"></div>
    <div class="pointer-events-none absolute -bottom-4 -right-4 h-[140px] w-[140px] rounded-full border-[14px] border-[#f1e7f0]/80"></div>

    <header class="relative z-10 mt-2 text-center">
      <div class="mx-auto mb-2 grid h-[62px] w-[62px] place-items-center rounded-[18px] bg-[#fceee9] shadow-[0_10px_24px_rgba(249,115,22,0.14)] overflow-hidden">
        <img src="/logo.png" alt="猫村" class="h-full w-full object-cover" />
      </div>
      <h1 class="text-xl font-black text-[#172033] tracking-tight">猫村</h1>
      <p class="mt-0.5 text-[13px] text-[#748094]">登录后继续照顾你的猫咪伙伴</p>
    </header>

    <van-form class="relative z-10 mt-5 space-y-4 rounded-[26px] border border-white/80 bg-white/80 p-4 shadow-[0_20px_46px_rgba(23,32,51,0.09)] backdrop-blur" @submit="onSubmit">
      <div>
        <div class="mb-3 text-[15px] font-bold text-[#172033]">用户名</div>
        <div class="flex h-12 items-center rounded-2xl border border-[rgba(226,232,240,0.92)] bg-white px-4">
          <van-icon name="user-o" class="text-[#748094]" size="24" />
          <input
            v-model="username"
            type="text"
            maxlength="50"
            class="ml-4 h-full flex-1 bg-transparent text-[15px] text-[#172033] outline-none placeholder:text-[#748094]"
            placeholder="请输入用户名"
          />
        </div>
      </div>

      <div>
        <div class="mb-3 text-[15px] font-bold text-[#172033]">密码</div>
        <div class="flex h-12 items-center rounded-2xl border border-[rgba(226,232,240,0.92)] bg-white px-4">
          <van-icon name="lock" class="text-[#748094]" size="24" />
          <input
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            class="ml-4 h-full flex-1 bg-transparent text-[15px] text-[#172033] outline-none placeholder:text-[#748094]"
            placeholder="请输入密码"
            autocomplete="current-password"
          />
          <button type="button" class="text-[#748094]" @click="togglePassword">
            <van-icon :name="showPassword ? 'eye-o' : 'closed-eye'" size="24" />
          </button>
        </div>
      </div>

      <div v-if="errorText" class="rounded-2xl bg-[#fff7ed] px-4 py-2.5 text-[13px] font-bold text-[#ea580c]">
        {{ errorText }}
      </div>

      <button
        type="submit"
        class="mt-2 h-[52px] w-full rounded-[22px] bg-[linear-gradient(135deg,#ff8a4c,#f97316,#e06912)] text-[17px] font-black text-white shadow-[0_16px_34px_rgba(249,115,22,0.32)] active:scale-[0.985]"
      >
        登录 →
      </button>
    </van-form>

    <div class="relative z-10 mt-4 text-right text-[13px]">
      <button type="button" class="font-bold text-[#748094]" @click="showToast({ message: '忘记密码功能稍后上线', duration: 1500 })">
        忘记密码？
      </button>
    </div>

    <div class="relative z-10 mt-5 text-center text-[15px] text-[#748094]">
      还没有账号？
      <router-link class="ml-2 font-black text-[#f97316]" to="/register">立即注册</router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { closeToast, showToast } from 'vant';
import { loginUser } from '@/api/apiService';
import { getMe } from '@/api/auth';
import { clearAccountRuntimeState, setCurrentUserIdentity } from '@/utils/userProfile';
import { useCatsStore, useCurrentCatStore } from '@/stores';

const router = useRouter();
const catsStore = useCatsStore();
const currentCatStore = useCurrentCatStore();

const username = ref('');
const password = ref('');
const showPassword = ref(false);
const errorText = ref('');

const togglePassword = () => {
  showPassword.value = !showPassword.value;
};

// 点击按钮后触发的真实逻辑！
const onSubmit = async () => {
  errorText.value = '';
  if (!username.value.trim()) {
    errorText.value = '请输入用户名';
    showToast({ type: 'fail', message: '请输入用户名' });
    return;
  }
  if (!password.value.trim()) {
    errorText.value = '请输入密码';
    showToast({ type: 'fail', message: '请输入密码' });
    return;
  }

  try {
    showToast({ type: 'loading', message: '正在进入猫村...', forbidClick: true });
    const res = await loginUser(username.value.trim(), password.value.trim());

    clearAccountRuntimeState();
    catsStore.clearCats();
    currentCatStore.clearCurrentCat();

    const token = res.access_token;
    localStorage.setItem('token', token);

    const meRes = await getMe();
    const userInfo = meRes.data;
    localStorage.setItem('is_admin', String(!!userInfo.is_admin));
    setCurrentUserIdentity(userInfo);
    currentCatStore.loadCurrentCat();
    await catsStore.fetchAllCats(true);
    const storedCat = currentCatStore.getCurrentCatId
      ? catsStore.getCatById(currentCatStore.getCurrentCatId)
      : null;
    if (!storedCat && catsStore.getAllCats[0]?.id) {
      currentCatStore.setCurrentCat(catsStore.getAllCats[0].id);
    }
    closeToast();
    showToast({ type: 'success', message: '登录成功！' });

    // 登录后进入主广场
    router.push('/social');
    
  } catch (error: any) {
    closeToast();
    const friendly = String(error?.message || '').trim() || '登录失败，请稍后重试';
    errorText.value = friendly;
    showToast({ type: 'fail', message: friendly });
  }
};
</script>
