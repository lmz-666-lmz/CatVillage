<template>
  <div class="px-6 pt-16 pb-10">
    <header class="text-center">
      <div class="mx-auto grid h-14 w-14 place-items-center rounded-2xl bg-primary-container text-on-primary shadow-cta">
        <span class="text-2xl">🐾</span>
      </div>
      <h1 class="mt-4 text-xl font-semibold tracking-tight text-on-background">欢迎回到猫村</h1>
      <p class="mt-1 text-sm text-on-surface-variant">登录后即可管理猫咪档案与 AI 助理</p>
    </header>

    <van-form class="mt-8" @submit="onSubmit">
      <van-cell-group inset>
        <van-field
          v-model="username"
          name="username"
          label="账号"
          placeholder="请输入账号"
          autocomplete="username"
          :rules="[{ required: true, message: '请填写账号' }]"
        />
        <van-field
          v-model="password"
          name="password"
          type="password"
          label="密码"
          placeholder="请输入密码"
          autocomplete="current-password"
          :rules="[{ required: true, message: '请填写密码' }]"
        />
      </van-cell-group>

      <button
        type="submit"
        class="mt-6 h-12 w-full rounded-xl bg-primary text-on-primary font-semibold shadow-cta active:scale-[0.99]"
      >
        登录
      </button>

      <div class="mt-4 text-center text-sm text-on-surface-variant">
        还没有账号？
        <router-link class="font-semibold text-primary" to="/register">立即注册</router-link>
      </div>
    </van-form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { closeToast, showToast } from 'vant';
import { loginUser } from '@/api/apiService';

const router = useRouter();

// 定义前端输入的变量
const username = ref('');
const password = ref('');

// 点击按钮后触发的真实逻辑！
const onSubmit = async () => {
  try {
    showToast({ type: 'loading', message: '正在进入猫村...', forbidClick: true });
    const res = await loginUser(username.value.trim(), password.value);

    // 拿到你刚才看到的那个长长的 token，存起来
    localStorage.setItem('token', res.access_token);
    // 避免切换账号后沿用旧账号的猫咪缓存，导致 AI 使用错误 pet_id
    localStorage.removeItem('cats');
    localStorage.removeItem('currentCatId');
    closeToast();
    showToast({ type: 'success', message: '登录成功！' });

    // 丝滑跳转到首页
    router.push('/');
    
  } catch {
    closeToast();
    showToast({ type: 'fail', message: '账号或密码错啦' });
  }
};
</script>