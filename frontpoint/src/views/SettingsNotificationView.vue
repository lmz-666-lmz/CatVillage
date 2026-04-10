<template>
  <div class="min-h-[100dvh] bg-[#f4f5fb] px-4 pt-4 pb-8">
    <header class="flex items-center gap-2">
      <button type="button" class="grid h-10 w-10 place-items-center text-[#b33500]" @click="router.back()">
        <van-icon name="arrow-left" size="22" />
      </button>
      <h1 class="text-[20px] font-black text-[#12182a]">通知设置</h1>
    </header>

    <section class="mt-4 space-y-3 rounded-[18px] bg-white p-3 shadow-[0_4px_14px_rgba(20,27,43,0.05)]">
      <van-cell title="私信通知" center>
        <template #right-icon>
          <van-switch v-model="config.message" active-color="#b33500" />
        </template>
      </van-cell>
      <van-cell title="评论通知" center>
        <template #right-icon>
          <van-switch v-model="config.comment" active-color="#b33500" />
        </template>
      </van-cell>
      <van-cell title="点赞通知" center>
        <template #right-icon>
          <van-switch v-model="config.like" active-color="#b33500" />
        </template>
      </van-cell>
    </section>
  </div>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const STORAGE_KEY = 'settings-notification';

const defaultValue = { message: true, comment: true, like: true };
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
