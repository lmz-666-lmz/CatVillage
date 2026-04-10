<template>
  <div class="min-h-[100dvh] bg-[#f4f5fb] px-4 pt-4 pb-8">
    <header class="flex items-center gap-2">
      <button type="button" class="grid h-10 w-10 place-items-center text-[#b33500]" @click="router.back()">
        <van-icon name="arrow-left" size="22" />
      </button>
      <h1 class="text-[20px] font-black text-[#12182a]">关于猫村</h1>
    </header>

    <section class="mt-4 rounded-[18px] bg-white p-4 shadow-[0_4px_14px_rgba(20,27,43,0.05)]">
      <div class="text-[17px] font-black text-[#12182a]">猫村 CatVillage</div>
      <div class="mt-2 text-[14px] leading-relaxed text-[#5c657d]">猫咪社交与健康管理应用，提供喵喵台翻译、情绪预警、投喂记录和社交互动能力。</div>
      <div class="mt-4 text-[13px] text-[#8d95a8]">当前版本：v2.4.0</div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
const router = useRouter();
</script>
