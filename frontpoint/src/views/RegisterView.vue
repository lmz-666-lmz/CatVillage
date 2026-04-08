<template>
  <div class="min-h-[100dvh] bg-[#f4f5fb] pb-8">
    <header class="flex items-center px-5 py-4">
      <button type="button" class="grid h-9 w-9 place-items-center text-[#7f746f]" @click="router.back()">
        <van-icon name="arrow-left" size="20" />
      </button>
    </header>

    <div class="px-7 pt-2">
      <h1 class="text-[48px] font-black tracking-tight text-[#12182a]">注册账号</h1>
      <p class="mt-2 text-[16px] leading-7 text-[#5f4f48]">欢迎加入 Mao Village，开启你的猫友社区之旅</p>

      <van-form class="mt-10 space-y-6" @submit="onSubmit">
        <div>
          <div class="mb-2 text-[15px] font-bold text-[#5f4f48]">手机号</div>
          <div class="flex h-16 items-center rounded-2xl bg-[#e6e9fa] px-4">
            <van-icon name="idcard" class="text-[#876e63]" />
            <input
              v-model="phone"
              type="tel"
              maxlength="11"
              class="ml-3 h-full flex-1 bg-transparent text-[24px] text-[#5f4f48] outline-none placeholder:text-[#9aa3b5]"
              placeholder="请输入手机号"
            />
          </div>
        </div>

        <div>
          <div class="mb-2 text-[15px] font-bold text-[#5f4f48]">验证码</div>
          <div class="flex items-center gap-3">
            <div class="flex h-16 flex-1 items-center rounded-2xl bg-[#e6e9fa] px-4">
              <van-icon name="shield-o" class="text-[#876e63]" />
              <input
                v-model="code"
                type="text"
                maxlength="6"
                class="ml-3 h-full flex-1 bg-transparent text-[24px] text-[#5f4f48] outline-none placeholder:text-[#9aa3b5]"
                placeholder="六位验证码"
              />
            </div>
            <button
              type="button"
              class="h-16 rounded-2xl bg-[#d9deef] px-5 text-[20px] font-bold text-[#5f4f48] disabled:opacity-60"
              :disabled="codeCooldown > 0 || !validatePhone(phone)"
              @click="onSendCode"
            >
              {{ codeCooldown > 0 ? `${codeCooldown}s` : '获取验证码' }}
            </button>
          </div>
        </div>

        <div>
          <div class="mb-2 text-[15px] font-bold text-[#5f4f48]">设置密码</div>
          <div class="flex h-16 items-center rounded-2xl bg-[#e6e9fa] px-4">
            <van-icon name="lock" class="text-[#876e63]" />
            <input
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              class="ml-3 h-full flex-1 bg-transparent text-[24px] text-[#5f4f48] outline-none placeholder:text-[#9aa3b5]"
              placeholder="请输入密码"
              autocomplete="new-password"
            />
            <button type="button" class="text-[#876e63]" @click="togglePassword">
              <van-icon :name="showPassword ? 'eye-o' : 'closed-eye'" size="20" />
            </button>
          </div>
        </div>

        <div>
          <div class="mb-2 text-[15px] font-bold text-[#5f4f48]">确认密码</div>
          <div class="flex h-16 items-center rounded-2xl bg-[#e6e9fa] px-4">
            <van-icon name="replay" class="text-[#876e63]" />
            <input
              v-model="confirmPassword"
              :type="showPassword ? 'text' : 'password'"
              class="ml-3 h-full flex-1 bg-transparent text-[24px] text-[#5f4f48] outline-none placeholder:text-[#9aa3b5]"
              placeholder="请再次输入密码"
              autocomplete="new-password"
            />
          </div>
        </div>

        <label class="mt-1 flex items-center gap-2 text-[13px] text-[#7f746f]">
          <input v-model="agree" type="checkbox" class="h-4 w-4 accent-[#ff6b35]" />
          我已阅读并同意用户协议与隐私政策
        </label>

        <button
          type="submit"
          class="mt-3 h-[66px] w-full rounded-2xl bg-gradient-to-r from-[#b83a00] to-[#ff6b35] text-[34px] font-bold text-white shadow-[0_10px_22px_rgba(255,107,53,0.26)] active:scale-[0.99]"
        >
          立即注册
        </button>
      </van-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onUnmounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { closeToast, showToast } from 'vant';
import { registerUser } from '@/api/apiService';

const router = useRouter();

const phone = ref('');
const code = ref('');
const password = ref('');
const confirmPassword = ref('');
const agree = ref(false);
const showPassword = ref(false);
const codeCooldown = ref(0);
let cooldownTimer: number | null = null;

const validatePhone = (value: string) => /^1\d{10}$/.test(value);
const validatePassword = (value: string) => /^[A-Za-z\d]{6,16}$/.test(value);

const togglePassword = () => {
  showPassword.value = !showPassword.value;
};

const startCooldown = () => {
  codeCooldown.value = 60;
  cooldownTimer = window.setInterval(() => {
    if (codeCooldown.value <= 1) {
      codeCooldown.value = 0;
      if (cooldownTimer !== null) {
        window.clearInterval(cooldownTimer);
        cooldownTimer = null;
      }
      return;
    }
    codeCooldown.value -= 1;
  }, 1000);
};

const onSendCode = () => {
  if (!validatePhone(phone.value)) {
    showToast({ type: 'fail', message: '请输入正确的手机号' });
    return;
  }
  if (codeCooldown.value > 0) {
    return;
  }
  showToast({ type: 'success', message: '验证码已发送' });
  startCooldown();
};

const onViewTerms = () => {
  showToast({ message: '服务协议稍后上线', duration: 1500 });
};

const onViewPrivacy = () => {
  showToast({ message: '隐私政策稍后上线', duration: 1500 });
};

const onSubmit = async () => {
  if (!agree.value) {
    showToast({ type: 'fail', message: '请先阅读并同意协议' });
    return;
  }
  if (!validatePhone(phone.value)) {
    showToast({ type: 'fail', message: '手机号格式不正确' });
    return;
  }
  if (!code.value.trim()) {
    showToast({ type: 'fail', message: '请输入验证码' });
    return;
  }
  if (!validatePassword(password.value)) {
    showToast({ type: 'fail', message: '密码需为6-16位字母或数字组合' });
    return;
  }
  if (password.value !== confirmPassword.value) {
    showToast({ type: 'fail', message: '两次输入密码不一致' });
    return;
  }

  showToast({ type: 'loading', message: '正在注册...', forbidClick: true, duration: 0 });
  try {
    await registerUser(phone.value, password.value);
    closeToast();
    showToast({ type: 'success', message: '注册成功，欢迎加入猫村' });
    router.replace({ name: 'Login' });
  } catch {
    closeToast();
    showToast({ type: 'fail', message: '注册失败，请稍后重试' });
  }
};

onUnmounted(() => {
  if (cooldownTimer !== null) {
    window.clearInterval(cooldownTimer);
  }
});
</script>
