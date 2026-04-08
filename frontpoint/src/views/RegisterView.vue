<template>
  <div class="px-6 pt-10 pb-10">
    <van-nav-bar title="加入猫村" left-arrow @click-left="router.back()" />

    <header class="mt-6 text-center">
      <div class="mx-auto grid h-14 w-14 place-items-center rounded-2xl bg-primary-container text-on-primary shadow-cta">
        <span class="text-2xl">🐾</span>
      </div>
      <p class="mt-3 text-sm text-on-surface-variant">
        已有账号？
        <router-link class="font-semibold text-primary" to="/login">去登录</router-link>
      </p>
    </header>

    <van-form class="mt-8" @submit="onSubmit">
      <van-cell-group inset>
        <van-field
          v-model="phone"
          name="phone"
          type="tel"
          label="手机号"
          placeholder="请输入手机号"
          autocomplete="tel"
          :rules="[
            { required: true, message: '请输入手机号' },
            { validator: validatePhone, message: '手机号格式不正确' }
          ]"
        />

        <van-field
          v-model="code"
          name="code"
          label="验证码"
          placeholder="输入验证码"
          :rules="[{ required: true, message: '请输入验证码' }]"
        >
          <template #button>
            <van-button
              size="small"
              native-type="button"
              :disabled="codeCooldown > 0 || !phone"
              type="primary"
              @click="onSendCode"
            >
              {{ codeCooldown > 0 ? `${codeCooldown}s后重试` : '获取验证码' }}
            </van-button>
          </template>
        </van-field>

        <van-field
          v-model="password"
          name="password"
          :type="showPassword ? 'text' : 'password'"
          label="设置密码"
          placeholder="6-16位字母、数字组合"
          autocomplete="new-password"
          :rules="[
            { required: true, message: '请输入密码' },
            { validator: validatePassword, message: '密码需为6-16位字母或数字组合' }
          ]"
          @click-right-icon="togglePassword"
        >
          <template #right-icon>
            <van-icon :name="showPassword ? 'eye-o' : 'closed-eye'" />
          </template>
        </van-field>
      </van-cell-group>

      <div class="mt-5 rounded-2xl border border-surface-container-high bg-surface-container-lowest p-4">
        <van-checkbox v-model="agree" icon-size="18px">
          <span class="text-sm text-on-surface-variant">阅读并同意</span>
          <span class="mx-1 text-sm font-semibold text-primary" @click.stop="onViewTerms">《用户服务协议》</span>
          <span class="text-sm text-on-surface-variant">与</span>
          <span class="ml-1 text-sm font-semibold text-primary" @click.stop="onViewPrivacy">《隐私政策》</span>
        </van-checkbox>
      </div>

      <button
        type="submit"
        class="mt-6 h-12 w-full rounded-xl bg-primary text-on-primary font-semibold shadow-cta active:scale-[0.99]"
      >
        立即注册
      </button>
    </van-form>
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
