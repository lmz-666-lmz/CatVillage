<template>
  <div class="relative min-h-[100dvh] overflow-hidden bg-[linear-gradient(165deg,#f3f5fb_0%,#f9ecdf_52%,#f4f6ff_100%)] px-7 pt-16 pb-10 text-[#1f2a44]">
    <div class="pointer-events-none absolute -top-24 -left-12 h-72 w-72 rounded-full bg-[#ffe7d1]/70 blur-2xl"></div>
    <div class="pointer-events-none absolute top-1/3 -right-20 h-64 w-64 rounded-full bg-[#e8f0ff]/80 blur-2xl"></div>
    <div class="pointer-events-none absolute bottom-[-120px] left-1/2 h-[340px] w-[340px] -translate-x-1/2 rounded-full border-[30px] border-[#f1e4d8]/70"></div>

    <button
      type="button"
      class="absolute top-8 right-6 z-10 rounded-full bg-white/70 px-4 py-1.5 text-sm font-semibold text-[#5e6475] backdrop-blur"
      @click="enterApp"
    >
      跳过
    </button>

    <section class="relative z-10 mt-16 text-center">
      <div class="mx-auto mb-6 grid h-[112px] w-[112px] place-items-center rounded-[30px] bg-white/70 text-[#ff6b35] shadow-[0_14px_34px_rgba(255,107,53,0.18)] backdrop-blur">
        <van-icon name="smile-o" size="50" />
      </div>
      <h1 class="text-[36px] font-black tracking-tight text-[#101a34]">欢迎来到猫村</h1>
      <p class="mt-4 text-[20px] font-semibold text-[#5e6475]">记录每只猫咪的情绪、健康和日常点滴</p>
    </section>

    <section class="relative z-10 mt-14 space-y-4">
      <div class="rounded-3xl border border-white/70 bg-white/65 p-5 backdrop-blur">
        <div class="flex items-center gap-3 text-[#21325b]">
          <van-icon name="chat-o" size="22" />
          <span class="text-base font-bold">AI 陪伴问诊</span>
        </div>
        <p class="mt-2 text-sm text-[#62708f]">实时分析猫咪状态，给出护理建议与风险预警。</p>
      </div>

      <div class="rounded-3xl border border-white/70 bg-white/65 p-5 backdrop-blur">
        <div class="flex items-center gap-3 text-[#21325b]">
          <van-icon name="records" size="22" />
          <span class="text-base font-bold">健康时间线</span>
        </div>
        <p class="mt-2 text-sm text-[#62708f]">体重趋势、关键事件一目了然，守护更安心。</p>
      </div>
    </section>

    <div class="relative z-10 mt-10">
      <button
        type="button"
        class="h-14 w-full rounded-2xl bg-gradient-to-r from-[#bb3600] to-[#ff6b35] text-xl font-black text-white shadow-[0_14px_28px_rgba(201,72,0,0.32)]"
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
  autoEnterTimer = window.setTimeout(() => {
    enterApp();
  }, 2200);
});

onUnmounted(() => {
  if (autoEnterTimer !== null) {
    window.clearTimeout(autoEnterTimer);
  }
});
</script>
