<template>
  <div class="app-stage min-h-[100dvh] bg-background text-on-background antialiased">
    <div class="app-shell mx-auto w-full min-h-[100dvh] flex flex-col">
      <main class="flex-1" :class="showTabbar ? 'pb-16' : ''">
        <router-view />
      </main>

      <van-tabbar v-if="showTabbar" route safe-area-inset-bottom active-color="#ff6b35" inactive-color="#594139">
        <van-tabbar-item icon="smile-o" to="/social">广场</van-tabbar-item>
        <van-tabbar-item icon="chat-o" to="/ai-assistant">AI助理</van-tabbar-item>
        <van-tabbar-item icon="apps-o" to="/cats">喵喵台</van-tabbar-item>
        <van-tabbar-item icon="comment-o" to="/messages">消息</van-tabbar-item>
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

<style scoped>
.app-stage {
  padding: 0;
}

.app-shell {
  max-width: 430px;
}

@media (min-width: 768px) {
  .app-stage {
    display: grid;
    place-items: center;
    min-height: 100dvh;
    padding: 12px;
    background: radial-gradient(circle at top, #f8f2eb 0%, #f2f5ff 45%, #eef1fb 100%);
  }

  .app-shell {
    width: min(430px, calc((100dvh - 24px) * 0.462));
    min-height: calc(100dvh - 24px);
    max-height: calc(100dvh - 24px);
    border-radius: 28px;
    overflow: auto;
    background: #f9f9ff;
    border: 1px solid #e6e8f2;
    box-shadow: 0 18px 48px rgba(34, 42, 66, 0.16);
  }
}
</style>