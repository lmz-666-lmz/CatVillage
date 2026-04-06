<template>
  <div class="app-container">
    <div class="main-content">
      <router-view />
    </div>

    <van-tabbar v-if="!$route.meta.hideTabbar" v-model="activeTab" route>
      <van-tabbar-item icon="home-o" to="/">首页</van-tabbar-item>
      <van-tabbar-item icon="comment-o" to="/ai-assistant">AI助理</van-tabbar-item>
      <van-tabbar-item icon="apps-o" to="/cats">猫咪</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/profile">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
const activeTab = ref(0);
</script>

<style>
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}
.main-content {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 50px; /* 为底部导航留出空间 */
}
</style>