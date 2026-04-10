<template>
  <div class="min-h-[100dvh] bg-[#f4f5fb] px-4 pt-4 pb-8">
    <header class="flex items-center gap-2">
      <button type="button" class="grid h-10 w-10 place-items-center text-[#b33500]" @click="router.back()">
        <van-icon name="arrow-left" size="22" />
      </button>
      <h1 class="text-[20px] font-black text-[#12182a]">浏览历史</h1>
    </header>

    <section class="mt-4 rounded-[18px] bg-white p-4 shadow-[0_4px_14px_rgba(20,27,43,0.05)]">
      <div v-if="items.length === 0" class="py-8 text-center text-[14px] text-[#8d95a8]">暂无浏览历史</div>
      <div v-else class="space-y-2">
        <div v-for="item in items" :key="item" class="rounded-[12px] bg-[#f6f7fc] px-3 py-2 text-[14px] text-[#3e465b]">
          {{ item }}
        </div>
      </div>

      <button type="button" class="mt-4 w-full rounded-[12px] border border-[#e1e5f0] py-2 text-[14px] font-semibold text-[#5d657a]" @click="clearHistory">
        清空历史
      </button>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';

const router = useRouter();
const STORAGE_KEY = 'settings-browse-history';
const items = ref<string[]>(JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'));

const clearHistory = () => {
  items.value = [];
  localStorage.setItem(STORAGE_KEY, '[]');
  showToast({ message: '已清空历史' });
};
</script>
