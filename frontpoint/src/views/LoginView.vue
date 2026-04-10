<template>
  <div class="relative min-h-[100dvh] overflow-hidden bg-[#f6f7fb] px-6 pt-16 pb-10">
    <div class="pointer-events-none absolute inset-x-0 bottom-0 h-80 bg-[radial-gradient(ellipse_at_bottom,_rgba(201,72,0,0.07),_transparent_70%)]"></div>
    <div class="pointer-events-none absolute -bottom-24 right-[-80px] h-[320px] w-[320px] rounded-full border-[28px] border-[#f3eaf2]/70"></div>
    <div class="pointer-events-none absolute -bottom-8 right-[-20px] h-[220px] w-[220px] rounded-full border-[20px] border-[#f1e7f0]/80"></div>

    <header class="relative z-10 mt-8 text-center">
      <div class="mx-auto mb-5 grid h-[96px] w-[96px] place-items-center rounded-[24px] bg-[#fceee9] text-[#ff6b35]">
        <van-icon name="paw" size="40" />
      </div>
      <h1 class="text-[38px] font-black tracking-tight text-[#111a32]">猫村</h1>
      <p class="mt-1 text-[14px] text-[#5f453b]">Mao Village</p>
    </header>

    <van-form class="relative z-10 mt-12 space-y-7" @submit="onSubmit">
      <div>
        <div class="mb-3 text-[16px] font-bold text-[#4f3f38]">手机号码</div>
        <div class="flex h-[72px] items-center rounded-[20px] bg-[#e5e9fa] px-5">
          <span class="text-[22px] font-bold text-[#5d4037]">+86</span>
          <input
            v-model="phone"
            type="tel"
            maxlength="11"
            class="ml-4 h-full flex-1 bg-transparent text-[18px] text-[#5d4037] outline-none placeholder:text-[#9ea4b2]"
            placeholder="请输入您的手机号"
          />
        </div>
      </div>

      <div>
        <div class="mb-3 text-[16px] font-bold text-[#4f3f38]">密码</div>
        <div class="flex h-[72px] items-center rounded-[20px] bg-[#e5e9fa] px-5">
          <van-icon name="lock" class="text-[#5d4037]" size="24" />
          <input
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            class="ml-4 h-full flex-1 bg-transparent text-[18px] text-[#5d4037] outline-none placeholder:text-[#9ea4b2]"
            placeholder="请输入密码"
            autocomplete="current-password"
          />
          <button type="button" class="text-[#9ea4b2]" @click="togglePassword">
            <van-icon :name="showPassword ? 'eye-o' : 'closed-eye'" size="24" />
          </button>
        </div>
      </div>

      <button
        type="submit"
        class="mt-4 h-[56px] w-full rounded-[16px] bg-gradient-to-r from-[#b93100] to-[#ff652f] text-[20px] font-black text-white shadow-[0_12px_26px_rgba(201,72,0,0.3)] active:scale-[0.99]"
      >
        登录 →
      </button>
    </van-form>

    <div class="relative z-10 mt-14 flex items-center gap-3 text-[#c6c1c4]">
      <div class="h-px flex-1 bg-[#dce1f0]"></div>
      <div class="text-[14px] font-semibold">第三方登录</div>
      <div class="h-px flex-1 bg-[#dce1f0]"></div>
    </div>

    <div class="relative z-10 mt-6 flex items-center justify-center gap-5">
      <button type="button" class="grid h-16 w-16 place-items-center rounded-[18px] bg-[#eceffd] text-[#6b5249]">
        <van-icon name="chat-o" size="28" />
      </button>
      <button type="button" class="grid h-16 w-16 place-items-center rounded-[18px] bg-[#eceffd] text-[#6b5249]">
        <van-icon name="service-o" size="28" />
      </button>
    </div>

    <div class="relative z-10 mt-20 text-center text-[18px] text-[#5f514b]">
      还没有账号？
      <router-link class="ml-2 font-black text-[#ea580c]" to="/register">立即注册</router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import { closeToast, showToast } from 'vant';
import { loginUser } from '@/api/apiService';

const router = useRouter();

const phone = ref('');
const password = ref('');
const showPassword = ref(false);

const isValidPhone = computed(() => /^1\d{10}$/.test(phone.value));

const togglePassword = () => {
  showPassword.value = !showPassword.value;
};

// 点击按钮后触发的真实逻辑！
const onSubmit = async () => {
  if (!isValidPhone.value) {
    showToast({ type: 'fail', message: '请输入正确手机号' });
    return;
  }
  if (!password.value.trim()) {
    showToast({ type: 'fail', message: '请输入密码' });
    return;
  }

  try {
    showToast({ type: 'loading', message: '正在进入猫村...', forbidClick: true });
    const res = await loginUser(phone.value.trim(), password.value.trim());

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
</script>