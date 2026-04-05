<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router';
import { onMounted } from 'vue';
import { useUserStore } from '@/stores/user';

const userStore = useUserStore();

// 应用启动时恢复登录状态
onMounted(() => {
  userStore.restoreLoginState();
});
</script>

<template>
  <div id="app">
    <header>
      <nav>
        <RouterLink to="/"><span>🏠</span> 首页</RouterLink>
        <RouterLink v-if="userStore.isLoggedIn" to="/cats"><span>🐱</span> 我的猫咪</RouterLink>
        <RouterLink v-if="userStore.isLoggedIn" to="/social"><span>👥</span> 社交广场</RouterLink>
        <RouterLink v-if="userStore.isLoggedIn" to="/messages"><span>💬</span> 消息中心</RouterLink>
        <RouterLink v-if="userStore.isLoggedIn" to="/emotions"><span>😊</span> 情绪识别</RouterLink>
        <RouterLink v-if="userStore.isLoggedIn" to="/ai-assistant"><span>🤖</span> AI助理</RouterLink>
        <RouterLink v-if="userStore.isLoggedIn" to="/profile"><span>👤</span> 个人资料</RouterLink>
        <RouterLink v-if="!userStore.isLoggedIn" to="/login"><span>🔐</span> 登录</RouterLink>
        <button v-if="userStore.isLoggedIn" @click="userStore.logout()">登出</button>
      </nav>
    </header>
    <main>
      <RouterView />
    </main>
  </div>
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

nav {
  padding: 20px;
  text-align: center;
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
  margin: 0 10px;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 4px;
}

nav a.router-link-exact-active {
  color: #42b983;
  background-color: rgba(66, 185, 131, 0.1);
}

nav button {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 10px;
}

main {
  padding: 20px;
  min-height: calc(100vh - 100px);
}
</style>