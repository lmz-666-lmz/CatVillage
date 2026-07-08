<template>
  <div class="relative min-h-[100dvh] overflow-hidden bg-[#f5f7fb] px-5 pt-2 pb-6">
    <!-- 背景装饰 -->
    <div class="pointer-events-none absolute -top-20 -right-16 h-48 w-48 rounded-full bg-[#ffe7d1]/50 blur-2xl"></div>
    <div class="pointer-events-none absolute bottom-0 -left-20 h-56 w-56 rounded-full bg-[#e8f0ff]/60 blur-2xl"></div>

    <header class="relative z-10 flex items-center py-2">
      <button type="button" class="grid h-10 w-10 place-items-center text-[#748094]" @click="router.back()">
        <van-icon name="arrow-left" size="22" />
      </button>
    </header>

    <div class="relative z-10">
      <!-- Logo -->
      <div class="mx-auto mb-3 grid h-[64px] w-[64px] place-items-center rounded-[18px] bg-white/70 shadow-[0_10px_24px_rgba(249,115,22,0.14)] backdrop-blur overflow-hidden">
        <img src="/logo.png" alt="猫村" class="h-full w-full object-cover" />
      </div>

      <h1 class="text-center text-[22px] font-black text-[#172033] tracking-tight">注册账号</h1>
      <p class="mt-1 text-center text-[13px] leading-5 text-[#748094]">加入猫村，记录健康档案与猫咪日常</p>

      <van-form class="mt-4 space-y-4 rounded-[26px] border border-white/80 bg-white/80 p-4 shadow-[0_20px_46px_rgba(23,32,51,0.09)] backdrop-blur" @submit="onSubmit">
        <div>
          <div class="mb-3 text-[15px] font-bold text-[#172033]">用户名</div>
          <div class="flex h-12 items-center rounded-2xl border border-[rgba(226,232,240,0.92)] bg-white px-4">
            <van-icon name="user-o" class="text-[#748094]" size="22" />
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
          <div class="mb-3 text-[15px] font-bold text-[#172033]">设置密码</div>
          <div class="flex h-12 items-center rounded-2xl border border-[rgba(226,232,240,0.92)] bg-white px-4">
            <van-icon name="lock" class="text-[#748094]" size="22" />
            <input
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              class="ml-4 h-full flex-1 bg-transparent text-[15px] text-[#172033] outline-none placeholder:text-[#748094]"
              placeholder="6-32位密码"
              autocomplete="new-password"
            />
            <button type="button" class="text-[#748094]" @click="togglePassword">
              <van-icon :name="showPassword ? 'eye-o' : 'closed-eye'" size="22" />
            </button>
          </div>
        </div>

        <div>
          <div class="mb-3 text-[15px] font-bold text-[#172033]">确认密码</div>
          <div class="flex h-12 items-center rounded-2xl border border-[rgba(226,232,240,0.92)] bg-white px-4">
            <van-icon name="replay" class="text-[#748094]" size="22" />
            <input
              v-model="confirmPassword"
              :type="showPassword ? 'text' : 'password'"
              class="ml-4 h-full flex-1 bg-transparent text-[15px] text-[#172033] outline-none placeholder:text-[#748094]"
              placeholder="请再次输入密码"
              autocomplete="new-password"
            />
          </div>
        </div>

        <label class="mt-1 flex cursor-pointer items-center gap-2.5 text-[13px] text-[#748094] select-none" @click.prevent="openAgreementDialog">
          <input :checked="agree" type="checkbox" class="h-5 w-5 accent-[#f97316] cursor-pointer" readonly />
          我已阅读并同意用户协议与隐私政策
        </label>

        <div v-if="errorText" class="rounded-2xl bg-[#fff7ed] px-4 py-2.5 text-[13px] font-bold text-[#ea580c]">
          {{ errorText }}
        </div>

        <button
          type="submit"
          class="mt-2 h-[52px] w-full rounded-[22px] bg-[linear-gradient(135deg,#ff8a4c,#f97316,#e06912)] text-[17px] font-black text-white shadow-[0_16px_34px_rgba(249,115,22,0.32)] active:scale-[0.985]"
        >
          立即注册
        </button>
      </van-form>
    </div>

    <van-dialog
      v-model:show="showAgreement"
      title="用户协议与隐私政策"
      show-cancel-button
      cancel-button-text="不同意"
      confirm-button-text="我已阅读并同意"
      confirm-button-color="#f97316"
      @confirm="confirmAgreement"
      @cancel="rejectAgreement"
      @close="rejectAgreement"
    >
      <div class="px-5 pb-3 pt-1 text-[14px] leading-7 text-[#40506a]">
        <p class="mb-2">请确认你已了解以下内容：</p>
        <ul class="list-disc space-y-1 pl-5">
          <li>账号注册与使用</li>
          <li>宠物资料与上传内容</li>
          <li>AI/情绪识别结果仅供参考</li>
          <li>不构成兽医诊断</li>
          <li>隐私数据仅用于项目功能展示</li>
        </ul>
      </div>
    </van-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { closeToast, showToast } from 'vant';
import { registerUser } from '@/api/apiService';

const router = useRouter();

const username = ref('');
const password = ref('');
const confirmPassword = ref('');
const agree = ref(false);
const showPassword = ref(false);
const showAgreement = ref(false);
const errorText = ref('');

const validatePassword = (value: string) => value.length >= 6 && value.length <= 32;

const togglePassword = () => {
  showPassword.value = !showPassword.value;
};

const openAgreementDialog = () => {
  if (agree.value) {
    agree.value = false;
    return;
  }
  showAgreement.value = true;
};

const confirmAgreement = () => {
  agree.value = true;
};

const rejectAgreement = () => {
  if (!agree.value) {
    agree.value = false;
  }
};

const onSubmit = async () => {
  errorText.value = '';
  if (!agree.value) {
    errorText.value = '请先阅读并同意用户协议与隐私政策';
    showToast({ type: 'fail', message: '请先阅读并同意用户协议与隐私政策' });
    return;
  }
  if (!username.value.trim()) {
    errorText.value = '请输入用户名';
    showToast({ type: 'fail', message: '请输入用户名' });
    return;
  }
  if (username.value.trim().length < 3) {
    errorText.value = '用户名至少3个字符';
    showToast({ type: 'fail', message: '用户名至少3个字符' });
    return;
  }
  if (!validatePassword(password.value)) {
    errorText.value = '密码需为6-32位';
    showToast({ type: 'fail', message: '密码需为6-32位' });
    return;
  }
  if (password.value !== confirmPassword.value) {
    errorText.value = '两次输入密码不一致';
    showToast({ type: 'fail', message: '两次输入密码不一致' });
    return;
  }

  showToast({ type: 'loading', message: '正在注册...', forbidClick: true, duration: 0 });
  try {
    await registerUser(username.value.trim(), password.value);
    closeToast();
    showToast({ type: 'success', message: '注册成功，欢迎加入猫村' });
    router.replace({ name: 'Login' });
  } catch (error: any) {
    closeToast();
    const friendly = String(error?.message || '').trim() || '注册失败，请稍后重试';
    errorText.value = friendly;
    showToast({ type: 'fail', message: friendly });
  }
};
</script>
