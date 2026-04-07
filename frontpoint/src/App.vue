<template>
  <div class="app-container">
    <div class="main-content">
      <router-view />
    </div>

    <van-tabbar v-if="showTabbar" v-model="activeTab" route safe-area-inset-bottom>
      <van-tabbar-item icon="home-o" to="/">首页</van-tabbar-item>
      <van-tabbar-item icon="apps-o" to="/cats">猫咪</van-tabbar-item>
      <van-tabbar-item icon="chat-o" to="/ai-assistant">AI助理</van-tabbar-item>
      <van-tabbar-item icon="smile-o" to="/social">广场</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/profile">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const activeTab = ref(0);

// 判断逻辑：如果是登录页，就不显示底部导航栏
const showTabbar = computed(() => {
  const hiddenRoutes = ['Login', 'Register'];
  if (hiddenRoutes.includes(route.name as string)) {
    return false;
  }
  return !route.meta.hideTabbar;
});
</script>

<style>
/* 保证全局充满屏幕，没有恶心的白边 */
html, body, #app {
  height: 100%;
  margin: 0;
  padding: 0;
  background-color: #f7f8fa; /* 温柔的浅灰底色 */
}

.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  /* 给底部的 Tabbar 留出空间，防止最下面的内容被挡住 */
  padding-bottom: 50px; 
}
</style>