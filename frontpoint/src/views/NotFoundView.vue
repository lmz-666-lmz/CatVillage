<template>
  <div class="not-found">
    <h1>404 - 页面未找到</h1>
    <p>抱歉，您访问的页面不存在。</p>
    <router-link to="/">返回首页</router-link>
  </div>
</template>

<script setup lang="ts">
// NotFoundView 组件
</script>

<style scoped>
.not-found {
  padding: 40px;
  text-align: center;
}

.not-found h1 {
  color: #ff0000;
}
</style>