<template>
  <div class="min-h-[100dvh] bg-[#f4f5fb] px-4 pt-4 pb-8">
    <header class="flex items-center gap-2">
      <button type="button" class="grid h-10 w-10 place-items-center text-[#b33500]" @click="router.back()">
        <van-icon name="arrow-left" size="22" />
      </button>
      <h1 class="text-[20px] font-black text-[#12182a]">账号与安全</h1>
    </header>

    <section class="mt-4 space-y-3 rounded-[18px] bg-white p-3 shadow-[0_4px_14px_rgba(20,27,43,0.05)]">
      <div class="rounded-[14px] bg-[#f6f7fc] px-4 py-3">
        <div class="text-[13px] text-[#7c8396]">喵村号</div>
        <div class="mt-1 text-[16px] font-bold text-[#12182a]">{{ profile.miaoId }}</div>
      </div>

      <div class="rounded-[14px] bg-[#f6f7fc] px-4 py-3">
        <div class="text-[13px] text-[#7c8396]">用户名</div>
        <div class="mt-1 text-[16px] font-bold text-[#12182a]">{{ profile.nickname }}</div>
      </div>

      <button type="button" class="w-full rounded-[14px] bg-[#b33500] py-3 text-[15px] font-bold text-white" @click="copyMiaoId">
        复制喵村号
      </button>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';
import { getUserDisplayProfile } from '@/utils/userProfile';

const router = useRouter();
const profile = ref(getUserDisplayProfile());

const copyMiaoId = async () => {
  try {
    await navigator.clipboard.writeText(profile.value.miaoId);
    showToast({ type: 'success', message: '喵村号已复制' });
  } catch {
    showToast({ message: '复制失败，请手动复制' });
  }
};
</script>
