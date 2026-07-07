<template>
  <div class="min-h-[100dvh] bg-[#f5f7fb] px-5 pt-4 pb-8">
    <header class="flex items-center gap-2">
      <button type="button" class="grid h-10 w-10 place-items-center text-[#f97316]" @click="router.back()">
        <van-icon name="arrow-left" size="22" />
      </button>
      <h1 class="text-2xl font-black text-[#172033]">隐私设置</h1>
    </header>

    <section class="mt-4 space-y-3 rounded-[22px] bg-[rgba(255,255,255,0.92)] border border-[rgba(226,232,240,0.92)] p-3 shadow-[0_12px_26px_rgba(23,32,51,0.06)]">
      <van-cell title="允许被搜索到" label="他人可通过喵村号搜索到你" center>
        <template #right-icon>
          <van-switch v-model="config.searchable" active-color="#f97316" />
        </template>
      </van-cell>
      <van-cell title="公开动态互动" label="允许陌生人评论和点赞" center>
        <template #right-icon>
          <van-switch v-model="config.openInteraction" active-color="#f97316" />
        </template>
      </van-cell>
    </section>
  </div>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const STORAGE_KEY = 'settings-privacy';

const defaultValue = { searchable: true, openInteraction: true };
const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null') as typeof defaultValue | null;
const config = reactive(parsed || defaultValue);

watch(
  () => ({ ...config }),
  (value) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(value));
  },
  { deep: true }
);
</script>
