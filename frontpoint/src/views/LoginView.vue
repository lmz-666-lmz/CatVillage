<template>
  <div class="relative min-h-[100dvh] overflow-hidden bg-[#f4f5fb] px-7 pt-16 pb-10">
    <div class="pointer-events-none absolute inset-x-0 bottom-0 h-56 bg-[radial-gradient(ellipse_at_bottom,_rgba(255,107,53,0.08),_transparent_65%)]"></div>

    <header class="relative z-10 text-center">
      <div class="mx-auto mb-5 grid h-[92px] w-[92px] place-items-center rounded-3xl bg-[#fceee9] text-[#ff6b35]">
        <van-icon name="paw" size="42" />
      </div>
      <h1 class="text-[52px] font-black tracking-tight text-[#12182a]">猫村</h1>
      <p class="mt-2 text-[18px] font-semibold text-[#6a5b54]">Mao Village</p>
    </header>

    <van-form class="relative z-10 mt-14 space-y-6" @submit="onSubmit">
      <div>
        <div class="mb-2 text-[15px] font-bold text-[#5f4f48]">手机号</div>
        <div class="flex h-16 items-center rounded-2xl bg-[#e6e9fa] px-4">
          <span class="text-[28px] font-bold text-[#5f4f48]">+86</span>
          <input
            v-model="phone"
            type="tel"
            maxlength="11"
            class="ml-4 h-full flex-1 bg-transparent text-[24px] text-[#5f4f48] outline-none placeholder:text-[#99a2b7]"
            placeholder="请输入您的手机号"
          />
        </div>
      </div>

      <div>
        <div class="mb-2 text-[15px] font-bold text-[#5f4f48]">验证码</div>
        <div class="flex items-center gap-3">
          <div class="flex h-16 flex-1 items-center rounded-2xl bg-[#e6e9fa] px-4">
            <van-icon name="lock" class="text-[#5f4f48]" />
            <input
              v-model="code"
              type="text"
              maxlength="6"
              class="ml-3 h-full flex-1 bg-transparent text-[24px] text-[#5f4f48] outline-none placeholder:text-[#99a2b7]"
              placeholder="验证码"
            />
          </div>
          <button
            type="button"
            class="h-16 rounded-2xl bg-[#fceee9] px-5 text-[22px] font-bold text-[#ff6b35] disabled:opacity-60"
            :disabled="codeCooldown > 0 || !isValidPhone"
            @click="onSendCode"
          >
            {{ codeCooldown > 0 ? `${codeCooldown}s` : '获取验证码' }}
          </button>
        </div>
      </div>

      <button
        type="submit"
        class="h-[66px] w-full rounded-2xl bg-gradient-to-r from-[#b83a00] to-[#ff6b35] text-[30px] font-bold text-white shadow-[0_10px_22px_rgba(255,107,53,0.26)] active:scale-[0.99]"
      >
        登录 →
      </button>
    </van-form>

    <div class="relative z-10 mt-8 flex items-center gap-4 text-[#b1acb2]">
      <div class="h-px flex-1 bg-[#dce1f0]"></div>
      <div class="text-[13px] font-semibold">第三方登录</div>
      <div class="h-px flex-1 bg-[#dce1f0]"></div>
    </div>

    <div class="relative z-10 mt-6 flex items-center justify-center gap-4">
      <button type="button" class="grid h-14 w-14 place-items-center rounded-2xl bg-[#eceffd] text-[#6b5249]">
        <van-icon name="chat-o" size="26" />
      </button>
      <button type="button" class="grid h-14 w-14 place-items-center rounded-2xl bg-[#eceffd] text-[#6b5249]">
        <van-icon name="service-o" size="26" />
      </button>
    </div>

    <div class="relative z-10 mt-16 text-center text-[16px] text-[#7a706b]">
      还没有账号？
      <router-link class="ml-2 font-bold text-[#ff6b35]" to="/register">立即注册</router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onUnmounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { closeToast, showToast } from 'vant';
import { loginUser } from '@/api/apiService';

const router = useRouter();

const phone = ref('');
const code = ref('');
const codeCooldown = ref(0);
let cooldownTimer: number | null = null;

const isValidPhone = computed(() => /^1\d{10}$/.test(phone.value));

const clearCooldownTimer = () => {
  if (cooldownTimer !== null) {
    window.clearInterval(cooldownTimer);
    cooldownTimer = null;
  }
};

const onSendCode = () => {
  if (!isValidPhone.value || codeCooldown.value > 0) {
    return;
  }
  showToast({ type: 'success', message: '验证码已发送' });
  codeCooldown.value = 60;
  clearCooldownTimer();
  cooldownTimer = window.setInterval(() => {
    codeCooldown.value -= 1;
    if (codeCooldown.value <= 0) {
      codeCooldown.value = 0;
      clearCooldownTimer();
    }
  }, 1000);
};

// 点击按钮后触发的真实逻辑！
const onSubmit = async () => {
  if (!isValidPhone.value) {
    showToast({ type: 'fail', message: '请输入正确手机号' });
    return;
  }
  if (!code.value.trim()) {
    showToast({ type: 'fail', message: '请输入验证码' });
    return;
  }

  try {
    showToast({ type: 'loading', message: '正在进入猫村...', forbidClick: true });
    const res = await loginUser(phone.value.trim(), code.value.trim());

    // 拿到你刚才看到的那个长长的 token，存起来
    localStorage.setItem('token', res.access_token);
    // 避免切换账号后沿用旧账号的猫咪缓存，导致 AI 使用错误 pet_id
    localStorage.removeItem('cats');
    localStorage.removeItem('currentCatId');
    closeToast();
    showToast({ type: 'success', message: '登录成功！' });

    // 登录后进入主广场
    router.push('/social');
    
  } catch {
    closeToast();
    showToast({ type: 'fail', message: '账号或密码错啦' });
  }
};

onUnmounted(() => {
  clearCooldownTimer();
});
</script>