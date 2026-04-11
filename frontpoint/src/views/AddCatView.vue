<template>
  <div class="min-h-[100dvh] bg-[#f4f5fb] px-5 pt-4 pb-8">
    <div v-if="loading" class="rounded-2xl border border-surface-container-high bg-surface-container-lowest px-4 py-10 text-center text-sm text-on-surface-variant">
      <van-loading size="20" />
      <div class="mt-3">正在准备添加猫咪表单...</div>
    </div>

    <div v-else-if="error" class="rounded-2xl border border-surface-container-high bg-surface-container-lowest px-4 py-10 text-center text-sm text-on-surface-variant">
      <div class="text-base font-semibold text-on-background">组件加载失败</div>
      <div class="mt-2">{{ error }}</div>
      <van-button class="mt-4" type="primary" @click="reload">重试</van-button>
    </div>

    <div v-else>
    <header class="sticky top-0 z-20 -mx-5 flex items-center justify-between bg-[#f4f5fb]/95 px-5 py-3 backdrop-blur">
      <button type="button" class="grid h-10 w-10 place-items-center text-[#837974]" @click="router.back()">
        <van-icon name="arrow-left" size="20" />
      </button>
      <h1 class="text-[20px] font-extrabold tracking-tight text-[#f05d23]">添加猫咪档案</h1>
      <button type="button" class="grid h-10 w-10 place-items-center text-[#837974]">
        <van-icon name="bell" size="20" />
      </button>
    </header>

    <section class="mt-6 text-center">
      <div class="flex items-center justify-center">
        <input ref="avatarInputRef" type="file" accept="image/*" class="hidden" @change="onAvatarChange" />
        <button
          type="button"
          class="relative grid h-[160px] w-[160px] place-items-center overflow-hidden bg-[#ececf3]"
          @click="openAvatarPicker"
        >
          <div class="relative h-[130px] w-[130px] overflow-hidden rounded-full border-[4px] border-white shadow-sm">
            <img
              v-if="avatarPreviewUrl"
              :src="avatarPreviewUrl"
              class="h-full w-full object-cover"
              alt="猫咪头像"
            />
            <img
              v-else
              src="https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg"
              class="h-full w-full object-cover opacity-60"
              alt="猫咪头像"
            />
          </div>

          <div class="absolute inset-0 grid place-items-center text-white">
            <div class="grid h-11 w-11 place-items-center rounded-xl bg-black/45">
              <van-icon name="photo-o" size="23" />
            </div>
          </div>

          <div class="absolute bottom-[14px] right-[14px] grid h-[58px] w-[58px] place-items-center rounded-full border-[3px] border-white bg-[#ff6b35] text-white shadow">
            <van-icon name="edit" size="18" />
          </div>
        </button>
      </div>

      <p class="mt-4 text-[17px] text-[#594139]">点击上传猫咪头像</p>
    </section>

    <section class="mt-10">
      <div class="space-y-5">
        <div>
          <label class="mb-3 block text-[15px] font-bold text-[#594139]">猫咪名字</label>
          <input
            v-model="form.name"
            type="text"
            placeholder="输入超可爱的名字"
            class="h-12 w-full rounded-[20px] border border-[#dbe2f4] bg-white px-6 text-[14px] text-on-background outline-none placeholder:text-[#8f9aab]"
          />
        </div>

        <div>
          <label class="mb-3 block text-[15px] font-bold text-[#594139]">品种选择</label>
          <div class="relative">
            <select
              v-model="form.breed"
              class="h-12 w-full appearance-none rounded-[20px] border border-[#dbe2f4] bg-white px-6 pr-14 text-[14px] text-on-background outline-none"
            >
              <option disabled value="">选择猫咪品种</option>
              <option v-for="option in breedOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
            </select>
            <van-icon name="arrow-down" class="absolute right-5 top-1/2 -translate-y-1/2 text-[#594139]" />
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="mb-3 block text-[15px] font-bold text-[#594139]">年龄/生日</label>
            <input
              v-model="form.ageBirthdayText"
              type="text"
              placeholder="2岁 / 2022-05"
              class="h-[58px] w-full rounded-[20px] border border-[#dbe2f4] bg-white px-5 text-[14px] text-on-background outline-none placeholder:text-[#8f9aab]"
            />
          </div>

          <div>
            <label class="mb-3 block text-[15px] font-bold text-[#594139]">体重 (kg)</label>
            <input
              v-model="form.weightKg"
              type="number"
              placeholder="4.5"
              class="h-[58px] w-full rounded-[20px] border border-[#dbe2f4] bg-white px-5 text-[14px] text-on-background outline-none placeholder:text-[#8f9aab]"
            />
          </div>
        </div>
      </div>
    </section>

    <section class="mt-7">
      <div class="text-[15px] font-bold text-[#594139]">疫苗情况</div>
      <div class="mt-3 flex flex-wrap gap-3">
        <button
          v-for="tag in vaccineTags"
          :key="tag"
          type="button"
          class="rounded-full px-5 py-2 text-[14px] font-medium transition-all active:scale-95"
          :class="isVaccineSelected(tag)
            ? 'bg-[#ff6b35] text-white'
            : 'bg-[#dfe4f8] text-[#594139]'"
          @click="toggleVaccine(tag)"
        >
          {{ tag }}
        </button>

        <button
          type="button"
          class="rounded-full border border-dashed border-[#e3c4b9] px-5 py-2 text-[14px] font-medium text-[#594139]"
        >
          + 自定义
        </button>
      </div>
    </section>

    <div class="mt-8">
      <button
        type="button"
        class="h-[66px] w-full rounded-[20px] bg-gradient-to-br from-[#b83a00] to-[#ff6b35] text-[18px] font-bold text-white shadow-[0_12px_30px_rgba(255,107,53,0.3)] disabled:opacity-60 active:scale-[0.99]"
        :disabled="saving"
        @click="onSave"
      >
        {{ saving ? '保存中...' : '保存' }}
      </button>
    </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import { closeToast, showToast } from 'vant';
import { useCatManagement } from '@/composables/useCatManagement';
import { useCatsStore, useCurrentCatStore } from '@/stores';
import type { CreateCatProfileRequest } from '@/types/cat';
import { CAT_BREED_OPTIONS } from '@/constants/catBreeds';

interface AddCatFormState {
  name: string;
  breed: string;
  ageBirthdayText: string;
  weightKg: string;
}

const router = useRouter();
const { createCat } = useCatManagement();
const catsStore = useCatsStore();
const currentCatStore = useCurrentCatStore();

const saving = ref<boolean>(false);
const avatarInputRef = ref<HTMLInputElement | null>(null);
const avatarPreviewUrl = ref<string>('');
const loading = ref(true);
const error = ref<string | null>(null);

const form = ref<AddCatFormState>({
  name: '',
  breed: '',
  ageBirthdayText: '',
  weightKg: ''
});

const breedOptions = CAT_BREED_OPTIONS.map((option) => ({
  label: option.label,
  value: option.label
}));

const vaccineTags = ['三联疫苗', '狂犬疫苗', '体内驱虫', '体外驱虫'] as const;
type VaccineTag = (typeof vaccineTags)[number];
const selectedVaccines = ref<VaccineTag[]>(['三联疫苗']);

const isVaccineSelected = (tag: VaccineTag): boolean => selectedVaccines.value.includes(tag);

const toggleVaccine = (tag: VaccineTag): void => {
  if (selectedVaccines.value.includes(tag)) {
    selectedVaccines.value = selectedVaccines.value.filter((t) => t !== tag);
    return;
  }
  selectedVaccines.value = [...selectedVaccines.value, tag];
};

const parseBirthdayMonth = (value: string): { year: number; month: number } | null => {
  const match = value.match(/(\d{4})-(\d{1,2})/);
  if (!match) {
    return null;
  }

  const year = Number(match[1]);
  const month = Number(match[2]);
  if (!Number.isFinite(year) || !Number.isFinite(month) || month < 1 || month > 12) {
    return null;
  }
  return { year, month };
};

const ageInMonths = computed<number>(() => {
  const parsed = parseBirthdayMonth(form.value.ageBirthdayText);
  if (!parsed) {
    return 1;
  }
  const now = new Date();
  const months = (now.getFullYear() - parsed.year) * 12 + (now.getMonth() + 1 - parsed.month);
  return Math.max(1, months);
});

const weightNumber = computed<number | undefined>(() => {
  const raw = String(form.value.weightKg || '').trim();
  if (!raw) {
    return undefined;
  }
  const num = Number(raw);
  if (!Number.isFinite(num) || num <= 0) {
    return undefined;
  }
  return num;
});

const openAvatarPicker = (): void => {
  avatarInputRef.value?.click();
};

const initData = async () => {
  loading.value = true;
  error.value = null;
  try {
    await catsStore.fetchAllCats();
  } catch {
    error.value = '组件加载失败，请检查后端服务';
  } finally {
    loading.value = false;
  }
};

const reload = () => initData();

const onAvatarChange = (event: Event): void => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) {
    return;
  }

  const reader = new FileReader();
  reader.onload = () => {
    if (typeof reader.result === 'string') {
      avatarPreviewUrl.value = reader.result;
    }
  };
  reader.readAsDataURL(file);
};

const onSave = async (): Promise<void> => {
  if (!form.value.name.trim()) {
    showToast({ type: 'fail', message: '请输入猫咪名字' });
    return;
  }
  if (!form.value.breed) {
    showToast({ type: 'fail', message: '请选择猫咪品种' });
    return;
  }

  const payload: CreateCatProfileRequest = {
    name: form.value.name.trim(),
    breed: form.value.breed,
    age: ageInMonths.value,
    gender: 1,
    weight: weightNumber.value,
    vaccineStatus: selectedVaccines.value.join('、'),
    avatarUrl: avatarPreviewUrl.value || undefined
  };

  saving.value = true;
  showToast({ type: 'loading', message: '正在保存...', forbidClick: true, duration: 0 });

  try {
    // 复用现有 composable：会调用 Pinia + API 并同步本地列表
    const createdCat = await createCat(payload);
    closeToast();
    showToast({ type: 'success', message: '猫咪档案创建成功' });
    if (createdCat?.id) {
      currentCatStore.setCurrentCat(createdCat.id);
      router.replace({ name: 'CatArchive', params: { id: createdCat.id } });
      return;
    }
    router.replace({ name: 'MyPets' });
  } catch {
    closeToast();
    showToast({ type: 'fail', message: '创建失败，请稍后再试' });
  } finally {
    saving.value = false;
  }
};

void initData();
</script>

<style scoped>
/* No extra styles beyond prototype utility classes */
</style>
