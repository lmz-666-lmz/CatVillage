<template>
  <div class="flex min-h-[100dvh] flex-col items-center justify-center bg-[#f5f7fb] px-6">
    <div class="text-5xl font-black text-[#172033]">404</div>
    <p class="mt-3 text-sm text-[#748094]">页面未找到</p>
    <button
      type="button"
      class="mt-6 h-14 rounded-2xl bg-gradient-to-br from-[#e06912] to-[#f97316] px-8 text-lg font-extrabold text-white shadow-[0_12px_28px_rgba(249,115,22,0.28)]"
      @click="$router.push('/')"
    >
      返回首页
    </button>
  </div>
</template>

<script setup lang="ts">
// NotFoundView 组件
</script>