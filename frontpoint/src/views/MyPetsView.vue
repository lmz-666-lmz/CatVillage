<template>
  <div class="min-h-[100dvh] bg-[#f6f6f8] pb-6">
    <header class="flex items-center justify-between border-b border-[#ebecef] px-5 py-4">
      <div class="flex items-center gap-3">
        <button type="button" class="grid h-10 w-10 place-items-center" @click="router.push({ name: 'UserProfile' })">
          <van-icon name="arrow-left" size="24" color="#111827" />
        </button>
        <h1 class="text-[24px] font-black tracking-tight text-[#111827]">我的萌宠</h1>
      </div>
      <div class="rounded-full bg-[#fdecc8] px-4 py-1.5 text-[13px] font-bold text-[#d97706]">{{ memberCountText }}</div>
    </header>

    <main class="px-5 pt-7">
      <section class="mb-7 text-center">
        <p class="text-[15px] font-semibold tracking-[0.18em] text-[#8b8b8b]">MEMBERS</p>
        <h2 class="mt-1 text-[30px] font-black tracking-tight text-[#111827]">管理你的村友</h2>
        <div class="mx-auto mt-3 h-2 w-14 rounded-full bg-[#f0d8b4]"></div>
      </section>

      <section class="space-y-5">
        <article
          v-for="cat in petCards"
          :key="cat.id"
          class="flex items-center gap-4 rounded-[24px] border border-[#ece8e3] bg-white px-4 py-4 shadow-[0_2px_10px_rgba(0,0,0,0.02)]"
        >
          <img :src="cat.avatar" :alt="cat.name" class="h-[108px] w-[108px] rounded-[30px] object-cover" />

          <div
            class="flex flex-1 items-center justify-between text-left"
            @click="openCatActions(cat.id)"
          >
            <div class="min-w-0 pr-3">
              <div class="flex items-center gap-2">
                <h3 class="text-[20px] font-black text-[#111827]">{{ cat.name }}</h3>
                <span class="inline-block h-3 w-3 rounded-full bg-[#22c55e]"></span>
              </div>
              <p class="mt-1 text-[14px] leading-[1.55] text-[#595959] clamp-2">{{ cat.description }}</p>
            </div>
            <button
              type="button"
              class="grid h-14 w-14 place-items-center rounded-full bg-[#f3f2f0]"
              @click.stop="openCatActions(cat.id)"
            >
              <van-icon name="arrow" size="24" color="#7d7d7d" />
            </button>
          </div>
        </article>

        <button
          type="button"
          class="mt-2 flex w-full flex-col items-center justify-center rounded-[28px] border-4 border-dashed border-[#e7e0d9] bg-[#fcfcfc] py-14"
          @click="router.push({ name: 'AddCat' })"
        >
          <div class="grid h-16 w-16 place-items-center rounded-full bg-[#f7efe5]">
            <van-icon name="plus" size="30" color="#d97706" />
          </div>
          <div class="mt-5 text-[22px] font-black text-[#111827]">添加新成员</div>
        </button>
      </section>
    </main>

    <van-action-sheet v-model:show="showCatActionSheet" title="猫咪操作" class="cat-action-sheet">
      <div class="p-4">
        <div class="mb-4 rounded-2xl bg-[#f3f4fa] px-4 py-3 text-[18px] text-[#545d6e]">
          当前成员：{{ selectedCatName || '未选择' }}
        </div>

        <div class="space-y-2">
          <button
            type="button"
            class="flex w-full items-center justify-between rounded-2xl bg-[#eef1fb] px-5 py-4 text-left"
            @click="viewSelectedCat"
          >
              <span class="text-[16px] font-bold text-[#1f2937]">查看档案</span>
            <van-icon name="arrow" size="24" color="#8c95a8" />
          </button>

          <button
            type="button"
            class="flex w-full items-center justify-between rounded-2xl bg-[#eef1fb] px-5 py-4 text-left"
            @click="editSelectedCat"
          >
              <span class="text-[16px] font-bold text-[#1f2937]">编辑信息</span>
            <van-icon name="arrow" size="24" color="#8c95a8" />
          </button>

          <button
            type="button"
            class="flex w-full items-center justify-between rounded-2xl bg-[#fff1ef] px-5 py-4 text-left"
            @click="deleteSelectedCat"
          >
              <span class="text-[16px] font-bold text-[#d92d20]">删除成员</span>
            <van-icon name="delete-o" size="22" color="#ff3b30" />
          </button>
        </div>
      </div>
    </van-action-sheet>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { closeToast, showConfirmDialog, showToast } from 'vant';
import { useCatsStore, useCurrentCatStore } from '@/stores';

const router = useRouter();
const catsStore = useCatsStore();
const currentCatStore = useCurrentCatStore();
const showCatActionSheet = ref(false);
const selectedCatActionId = ref<string>('');

const fallbackImages = [
  'https://images.unsplash.com/photo-1519052537078-e6302a4968d4?auto=format&fit=crop&w=500&q=80',
  'https://images.unsplash.com/photo-1511044568932-338cba0ad803?auto=format&fit=crop&w=500&q=80',
  'https://images.unsplash.com/photo-1548247416-ec66f4900b2e?auto=format&fit=crop&w=500&q=80'
];

const makeDescription = (breed?: string, age?: number, gender?: number) => {
  const breedText = breed || '猫咪';
  const ageText = typeof age === 'number' ? `${age}月龄` : '年龄未知';
  const genderText = gender === 1 ? '活力小王子' : gender === 0 ? '温柔小公主' : '可爱成员';
  return `${breedText} · ${genderText}，${ageText}，村里的快乐担当。`;
};

const petCards = computed(() => {
  return catsStore.getAllCats.map((cat, index) => ({
    id: cat.id,
    name: cat.name,
    avatar: cat.avatarUrl || fallbackImages[index % fallbackImages.length],
    description: makeDescription(cat.breed, cat.age, cat.gender)
  }));
});

const memberCountText = computed(() => `${catsStore.getAllCats.length}位成员`);
const selectedCatName = computed(() => {
  const selected = catsStore.getCatById(selectedCatActionId.value);
  return selected?.name || '';
});

const openCat = (id: string) => {
  router.push({ name: 'CatArchive', params: { id } });
};

const openCatActions = (id: string) => {
  selectedCatActionId.value = id;
  showCatActionSheet.value = true;
};

const viewSelectedCat = () => {
  const id = selectedCatActionId.value;
  if (!id) return;
  showCatActionSheet.value = false;
  router.push({ name: 'CatArchive', params: { id } });
};

const editSelectedCat = () => {
  const id = selectedCatActionId.value;
  if (!id) return;
  showCatActionSheet.value = false;
  router.push({ name: 'EditCat', params: { id } });
};

const deleteSelectedCat = async () => {
  const id = selectedCatActionId.value;
  if (!id) return;

  const cat = catsStore.getCatById(id);
  try {
    await showConfirmDialog({
      title: '删除成员',
      message: `确认删除 ${cat?.name || '该成员'} 吗？此操作不可恢复。`,
      confirmButtonText: '确认删除',
      confirmButtonColor: '#d92d20'
    });

    showToast({ type: 'loading', message: '删除中...', duration: 0, forbidClick: true });
    await catsStore.removeCat(id);
    closeToast();

    if (currentCatStore.getCurrentCatId === id) {
      const nextCat = catsStore.getAllCats[0];
      if (nextCat) {
        currentCatStore.setCurrentCat(nextCat.id);
      } else {
        currentCatStore.clearCurrentCat();
      }
    }

    showCatActionSheet.value = false;
    showToast({ type: 'success', message: '已删除成员' });
  } catch {
    closeToast();
  }
};

onMounted(() => {
  void catsStore.fetchAllCats();
});
</script>

<style scoped>
.clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

:deep(.cat-action-sheet .van-action-sheet__header) {
  font-size: 22px;
  font-weight: 800;
  color: #2f3542;
  padding-top: 14px;
}

:deep(.cat-action-sheet .van-action-sheet__content) {
  padding-bottom: 8px;
}

:deep(.cat-action-sheet .van-icon-cross) {
  font-size: 24px;
  color: #c3c7d0;
}
</style>
