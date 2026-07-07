<template>
  <div class="relative min-h-[100dvh] overflow-hidden bg-[linear-gradient(165deg,#f3f5fb_0%,#f9ecdf_52%,#f4f6ff_100%)] px-7 pt-16 pb-10 text-[#172033]">
    <div class="pointer-events-none absolute -top-16 -left-8 h-48 w-48 rounded-full bg-[#f97316]/15 blur-2xl"></div>
    <div class="pointer-events-none absolute top-1/3 -right-12 h-40 w-40 rounded-full bg-[#e8f0ff]/80 blur-2xl"></div>
    <div class="pointer-events-none absolute bottom-[-80px] left-1/2 h-[240px] w-[240px] -translate-x-1/2 rounded-full border-[20px] border-[#f1e4d8]/70"></div>

    <button
      type="button"
      class="absolute top-8 right-6 z-10 rounded-full bg-white/70 px-4 py-1.5 text-sm font-semibold text-[#748094] backdrop-blur"
      @click="enterApp"
    >
      跳过
    </button>

    <section class="relative z-10 mt-16 text-center">
      <div class="mx-auto mb-6 grid h-[112px] w-[112px] place-items-center rounded-[30px] bg-white/70 shadow-[0_14px_34px_rgba(249,115,22,0.18)] backdrop-blur overflow-hidden">
        <img src="/logo.png" alt="猫村" class="h-full w-full object-cover" />
      </div>
      <h1 class="text-[36px] font-black tracking-tight text-[#172033]">欢迎来到猫村</h1>
      <p class="mt-4 text-[20px] font-semibold text-[#748094]">记录每只猫咪的情绪、健康和日常点滴</p>
    </section>

    <section class="relative z-10 mt-14 space-y-4">
      <div class="rounded-3xl border border-white/70 bg-white/65 p-5 backdrop-blur">
        <div class="flex items-center gap-3 text-[#172033]">
          <van-icon name="chat-o" size="22" />
          <span class="text-base font-bold">养护陪伴问诊</span>
        </div>
        <p class="mt-2 text-sm text-[#748094]">实时分析猫咪状态，给出护理建议与风险预警。</p>
      </div>

      <div class="rounded-3xl border border-white/70 bg-white/65 p-5 backdrop-blur">
        <div class="flex items-center gap-3 text-[#172033]">
          <van-icon name="records" size="22" />
          <span class="text-base font-bold">健康时间线</span>
        </div>
        <p class="mt-2 text-sm text-[#748094]">体重趋势、关键事件一目了然，守护更安心。</p>
      </div>
    </section>

    <div class="relative z-10 mt-10">
      <button
        type="button"
        class="h-14 w-full rounded-2xl bg-gradient-to-br from-[#e06912] to-[#f97316] text-lg font-extrabold text-white shadow-[0_12px_28px_rgba(249,115,22,0.28)]"
        @click="enterApp"
      >
        进入猫村
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
let autoEnterTimer: number | null = null;

const enterApp = () => {
  if (autoEnterTimer !== null) {
    window.clearTimeout(autoEnterTimer);
    autoEnterTimer = null;
  }

  localStorage.setItem('welcomeSeen', '1');

  const token = localStorage.getItem('token');
  if (token) {
    router.replace('/social');
  } else {
    router.replace('/login');
  }
};

onMounted(() => {
  // 给足 4 秒阅读欢迎信息后再自动跳转
  autoEnterTimer = window.setTimeout(() => {
    enterApp();
  }, 4000);
});

onUnmounted(() => {
  if (autoEnterTimer !== null) {
    window.clearTimeout(autoEnterTimer);
  }
});
</script>
