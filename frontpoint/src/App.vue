<template>
  <div class="min-h-[100dvh] bg-background text-on-background antialiased">
    <div class="mx-auto w-full max-w-[393px] min-h-[100dvh] flex flex-col">
      <main class="flex-1" :class="showTabbar ? 'pb-16' : ''">
        <router-view />
      </main>

      <van-tabbar v-if="showTabbar" route safe-area-inset-bottom>
        <van-tabbar-item icon="home-o" to="/">首页</van-tabbar-item>
        <van-tabbar-item icon="apps-o" to="/cats">猫咪</van-tabbar-item>
        <van-tabbar-item icon="chat-o" to="/ai-assistant">AI助理</van-tabbar-item>
        <van-tabbar-item icon="smile-o" to="/social">广场</van-tabbar-item>
        <van-tabbar-item icon="user-o" to="/profile">我的</van-tabbar-item>
      </van-tabbar>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();

// 判断逻辑：如果是登录页，就不显示底部导航栏
const showTabbar = computed(() => {
  const routeName = route?.name ? String(route.name) : '';
  const hiddenRoutes = new Set(['Login', 'Register']);
  if (hiddenRoutes.has(routeName)) {
    return false;
  }
  return !route.meta?.hideTabbar;
});
</script>