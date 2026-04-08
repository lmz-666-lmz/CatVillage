<template>
  <div class="px-6 pt-6 pb-6">
    <header class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold tracking-tight text-on-background">我的猫咪</h1>
        <p class="mt-1 text-sm text-on-surface-variant">选择一只猫咪用于 AI 与情绪分析</p>
      </div>
      <div class="flex items-center gap-2">
        <van-button size="small" plain type="primary" @click="refresh">刷新</van-button>
        <van-button size="small" type="primary" @click="router.push({ name: 'AddCat' })">添加</van-button>
      </div>
    </header>

    <section class="mt-6 rounded-2xl border border-surface-container-high bg-surface-container-lowest p-4">
      <div class="text-sm text-on-surface-variant">当前选择</div>
      <div class="mt-1 text-base font-semibold text-on-background">
        {{ currentCatTitle }}
      </div>
    </section>

    <section class="mt-4">
      <div v-if="loading" class="py-10 text-center">
        <van-loading size="24" />
        <div class="mt-3 text-sm text-on-surface-variant">正在加载猫咪档案...</div>
      </div>

      <div v-else-if="cats.length === 0" class="mt-6 rounded-2xl border border-surface-container-high bg-surface-container-lowest p-6 text-center">
        <div class="text-3xl">🐱</div>
        <div class="mt-3 text-base font-semibold text-on-background">还没有猫咪档案</div>
        <div class="mt-1 text-sm text-on-surface-variant">先添加一只猫咪，才能使用 AI 助理与情绪记录</div>
        <button
          type="button"
          class="mt-5 h-11 w-full rounded-xl bg-primary text-on-primary font-semibold shadow-cta active:scale-[0.99]"
          @click="router.push({ name: 'AddCat' })"
        >
          添加猫咪
        </button>
      </div>

      <div v-else class="mt-4 space-y-3">
        <article
          v-for="cat in cats"
          :key="cat.id"
          class="rounded-2xl border border-surface-container-high bg-surface-container-lowest p-4"
        >
          <div class="flex items-center gap-3">
            <van-image
              :src="cat.avatarUrl || defaultAvatar"
              fit="cover"
              width="52"
              height="52"
              round
            />

            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <h3 class="truncate text-base font-semibold text-on-background">{{ cat.name }}</h3>
                <van-tag v-if="cat.id === selectedCatId" type="primary">已选中</van-tag>
              </div>
              <p class="mt-0.5 text-xs text-on-surface-variant">
                {{ cat.breed || '未填写品种' }} · {{ formatAge(cat.age) }}
              </p>
            </div>
          </div>

          <div class="mt-3 grid grid-cols-2 gap-2">
            <van-button size="small" plain type="primary" @click="selectCat(cat.id)">设为当前</van-button>
            <van-button size="small" type="primary" @click="router.push({ name: 'EditCat', params: { id: cat.id } })">
              编辑
            </van-button>
          </div>
        </article>
      </div>
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

const loading = ref(false);
const defaultAvatar = 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg';

const cats = computed(() => catsStore.getAllCats);
const selectedCatId = computed(() => currentCatStore.getCurrentCatId || '');

const formatAge = (ageInMonths: number) => {
  const years = Math.floor((ageInMonths || 0) / 12);
  const months = (ageInMonths || 0) % 12;
  if (years <= 0) {
    return `${months}个月`;
  }
  return `${years}岁${months}个月`;
};

const currentCatTitle = computed(() => {
  const id = currentCatStore.getCurrentCatId;
  if (!id) {
    return cats.value[0] ? '未选择（可点击“设为当前”）' : '未选择（请先添加猫咪）';
  }
  const cat = catsStore.getCatById(id);
  return cat ? `${cat.name} · ${cat.breed || '未填写品种'} · ${formatAge(cat.age)}` : '未选择（当前猫咪不存在）';
});

const selectCat = (catId: string) => {
  currentCatStore.setCurrentCat(catId);
  showToast({ type: 'success', message: '已切换当前猫咪' });
};

const refresh = async () => {
  if (loading.value) {
    return;
  }
  loading.value = true;
  try {
    await catsStore.fetchAllCats();
    const first = catsStore.getAllCats[0];
    if (!currentCatStore.getCurrentCatId && first) {
      currentCatStore.setCurrentCat(first.id);
    }
  } catch {
    showToast({ type: 'fail', message: '加载失败，请检查登录状态或后端服务' });
  } finally {
    loading.value = false;
  }
};

onMounted(refresh);
</script>