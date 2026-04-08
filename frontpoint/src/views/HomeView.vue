<template>
  <div class="px-6 pt-6 pb-6">
    <header class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold tracking-tight text-on-background">猫村</h1>
        <p class="mt-1 text-sm text-on-surface-variant">社交 · 健康 · AI 翻译</p>
      </div>

      <van-button size="small" plain type="primary" @click="refresh">刷新</van-button>
    </header>

    <section class="mt-6 rounded-2xl border border-surface-container-high bg-surface-container-lowest p-4">
      <div class="flex items-center justify-between gap-3">
        <div>
          <div class="text-sm text-on-surface-variant">当前猫咪</div>
          <div class="mt-1 text-base font-semibold text-on-background">
            {{ currentCatTitle }}
          </div>
        </div>
        <van-button size="small" type="primary" @click="router.push({ name: 'Cats' })">去管理</van-button>
      </div>
    </section>

    <section class="mt-6 grid grid-cols-2 gap-3">
      <button
        type="button"
        class="rounded-2xl border border-surface-container-high bg-surface-container-lowest p-4 text-left active:scale-[0.99]"
        @click="router.push({ name: 'AIAssistant' })"
      >
        <div class="text-sm font-semibold text-on-background">AI 助理</div>
        <div class="mt-1 text-xs text-on-surface-variant">猫语翻译与建议</div>
      </button>

      <button
        type="button"
        class="rounded-2xl border border-surface-container-high bg-surface-container-lowest p-4 text-left active:scale-[0.99]"
        @click="router.push({ name: 'Emotions' })"
      >
        <div class="text-sm font-semibold text-on-background">情绪识别</div>
        <div class="mt-1 text-xs text-on-surface-variant">上传音频 · 查看记录</div>
      </button>

      <button
        type="button"
        class="rounded-2xl border border-surface-container-high bg-surface-container-lowest p-4 text-left active:scale-[0.99]"
        @click="router.push({ name: 'Social' })"
      >
        <div class="text-sm font-semibold text-on-background">社交广场</div>
        <div class="mt-1 text-xs text-on-surface-variant">看动态 · 发动态</div>
      </button>

      <button
        type="button"
        class="rounded-2xl border border-surface-container-high bg-surface-container-lowest p-4 text-left active:scale-[0.99]"
        @click="router.push({ name: 'Messages' })"
      >
        <div class="text-sm font-semibold text-on-background">消息中心</div>
        <div class="mt-1 text-xs text-on-surface-variant">会话列表 · 历史消息</div>
      </button>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';
import { useCatsStore, useCurrentCatStore } from '@/stores';

const router = useRouter();
const catsStore = useCatsStore();
const currentCatStore = useCurrentCatStore();

const refreshing = ref(false);

const currentCat = computed(() => {
  const selectedId = currentCatStore.getCurrentCatId;
  if (selectedId) {
    return catsStore.getCatById(selectedId);
  }
  return catsStore.getAllCats[0];
});

const currentCatTitle = computed(() => {
  const cat = currentCat.value;
  if (!cat) {
    return '未选择（请先添加猫咪档案）';
  }
  const years = Math.floor((cat.age || 0) / 12);
  const months = (cat.age || 0) % 12;
  const ageText = years > 0 ? `${years}岁${months}个月` : `${months}个月`;
  return `${cat.name} · ${cat.breed || '未填写品种'} · ${ageText}`;
});

const refresh = async () => {
  if (refreshing.value) {
    return;
  }

  refreshing.value = true;
  try {
    await catsStore.fetchAllCats();
    const first = catsStore.getAllCats[0];
    if (!currentCatStore.getCurrentCatId && first) {
      currentCatStore.setCurrentCat(first.id);
    }
  } catch {
    showToast({ type: 'fail', message: '刷新失败，请检查登录状态或后端服务' });
  } finally {
    refreshing.value = false;
  }
};

onMounted(refresh);
</script>