<template>
  <div class="min-h-[100dvh] bg-[#f4f5fb] px-4 pt-4 pb-8">
    <header class="flex items-center gap-2">
      <button type="button" class="grid h-10 w-10 place-items-center text-[#b33500]" @click="router.back()">
        <van-icon name="arrow-left" size="22" />
      </button>
      <h1 class="text-[20px] font-black text-[#12182a]">隐私协议与条款</h1>
    </header>

    <section class="mt-4 rounded-[18px] bg-white p-4 shadow-[0_4px_14px_rgba(20,27,43,0.05)]">
      <p class="text-[14px] leading-relaxed text-[#4b556d]">
        猫村仅收集提供服务所必需的数据，包括账号信息、互动内容与健康记录。我们不会在未经授权的情况下向第三方出售个人数据。
      </p>
      <p class="mt-3 text-[14px] leading-relaxed text-[#4b556d]">
        使用本应用即表示你同意在产品功能范围内处理相关数据。你可在设置中随时调整隐私选项。
      </p>
    </section>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
const router = useRouter();
</script>
