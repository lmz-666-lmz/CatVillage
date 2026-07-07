<template>
  <div class="min-h-[100dvh] bg-[#f5f7fb] px-5 pt-4 pb-8">
    <header class="flex items-center gap-2">
      <button type="button" class="grid h-10 w-10 place-items-center text-[#f97316]" @click="router.back()">
        <van-icon name="arrow-left" size="22" />
      </button>
      <h1 class="text-2xl font-black text-[#172033]">通知设置</h1>
    </header>

    <section class="mt-4 space-y-3 rounded-[22px] bg-[rgba(255,255,255,0.92)] border border-[rgba(226,232,240,0.92)] p-3 shadow-[0_12px_26px_rgba(23,32,51,0.06)]">
      <van-cell title="私信通知" center>
        <template #right-icon>
          <van-switch v-model="config.message" active-color="#f97316" />
        </template>
      </van-cell>
      <van-cell title="评论通知" center>
        <template #right-icon>
          <van-switch v-model="config.comment" active-color="#f97316" />
        </template>
      </van-cell>
      <van-cell title="点赞通知" center>
        <template #right-icon>
          <van-switch v-model="config.like" active-color="#f97316" />
        </template>
      </van-cell>
      <van-cell title="粉丝通知" label="新关注会计入消息红点" center>
        <template #right-icon>
          <van-switch v-model="config.follower" active-color="#f97316" />
        </template>
      </van-cell>
    </section>
  </div>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue';
import { useRouter } from 'vue-router';
import { DEFAULT_NOTIFICATION_SETTINGS, getNotificationSettings, saveNotificationSettings } from '@/utils/userSettings';

const router = useRouter();

const config = reactive({ ...DEFAULT_NOTIFICATION_SETTINGS, ...getNotificationSettings() });

watch(
  () => ({ ...config }),
  (value) => {
    saveNotificationSettings(value);
  },
  { deep: true }
);
</script>
