<template>
  <div class="bg-background text-on-background antialiased">
    <div class="mx-auto w-full max-w-[393px] relative flex flex-col overflow-hidden bg-background min-h-[100dvh] font-body">
      <!-- TopAppBar -->
      <header class="fixed top-0 left-1/2 -translate-x-1/2 w-full max-w-[393px] z-50 bg-white/70 backdrop-blur-xl flex items-center justify-between px-6 py-4">
        <button type="button" class="transition-all duration-200 active:scale-95 text-stone-500" @click="router.back()">
          <van-icon name="arrow-left" size="20" />
        </button>
        <h1 class="font-headline font-semibold text-lg tracking-tight text-orange-600">添加猫咪档案</h1>
        <button type="button" class="transition-all duration-200 active:scale-95 text-stone-500" @click="onNotificationsClick">
          <van-icon name="bell-o" size="20" />
        </button>
      </header>

      <!-- Main Content -->
      <main class="flex-1 overflow-y-auto pt-24 pb-32 px-6 no-scrollbar">
        <!-- Avatar Upload Section -->
        <div class="flex flex-col items-center mb-10">
          <input
            ref="avatarInputRef"
            type="file"
            accept="image/*"
            class="hidden"
            @change="onAvatarChange"
          />
          <button type="button" class="flex flex-col items-center" @click="openAvatarPicker">
            <div class="relative group">
              <div
                class="w-28 h-28 rounded-full bg-surface-container-high flex items-center justify-center border-4 border-white shadow-sm overflow-hidden"
              >
                <img
                  v-if="avatarPreviewUrl"
                  class="w-full h-full object-cover"
                  :src="avatarPreviewUrl"
                  alt="猫咪头像"
                />
                <div v-else class="w-full h-full flex items-center justify-center opacity-80">
                  <van-icon name="photo-o" size="34" class="text-on-surface-variant" />
                </div>
                <div class="absolute inset-0 bg-black/5 flex items-center justify-center">
                  <van-icon name="photograph" size="28" class="text-on-surface-variant" />
                </div>
              </div>
              <div class="absolute bottom-1 right-1 bg-primary-container text-white p-1.5 rounded-full shadow-lg border-2 border-white">
                <van-icon name="edit" size="14" />
              </div>
            </div>
            <p class="mt-4 text-label-md text-on-surface-variant font-medium">点击上传猫咪头像</p>
          </button>
        </div>

        <!-- Form Fields -->
        <div class="space-y-6">
          <!-- Field: Name -->
          <div class="space-y-2">
            <label class="text-label-md font-semibold text-on-surface-variant ml-1">猫咪名字</label>
            <div class="relative">
              <input
                v-model="form.name"
                class="w-full h-14 px-4 bg-surface-container-lowest rounded-xl border-none ring-1 ring-surface-container-high focus:ring-2 focus:ring-primary-container/30 transition-all outline-none text-body-md"
                placeholder="输入超可爱的名字"
                type="text"
              />
            </div>
          </div>

          <!-- Field: Breed -->
          <div class="space-y-2">
            <label class="text-label-md font-semibold text-on-surface-variant ml-1">品种选择</label>
            <div class="relative">
              <select
                v-model="form.breed"
                class="w-full h-14 px-4 bg-surface-container-lowest rounded-xl border-none ring-1 ring-surface-container-high focus:ring-2 focus:ring-primary-container/30 transition-all outline-none text-body-md appearance-none"
              >
                <option disabled value="">选择猫咪品种</option>
                <option v-for="option in breedOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
              </select>
              <van-icon name="arrow-down" class="absolute right-4 top-4 text-on-surface-variant pointer-events-none" />
            </div>
          </div>

          <!-- Horizontal Group -->
          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <label class="text-label-md font-semibold text-on-surface-variant ml-1">年龄/生日</label>
              <input
                v-model="form.ageBirthdayText"
                class="w-full h-14 px-4 bg-surface-container-lowest rounded-xl border-none ring-1 ring-surface-container-high focus:ring-2 focus:ring-primary-container/30 transition-all outline-none text-body-md"
                placeholder="2岁 / 2022-05"
                type="text"
                inputmode="numeric"
              />
            </div>
            <div class="space-y-2">
              <label class="text-label-md font-semibold text-on-surface-variant ml-1">体重 (kg)</label>
              <input
                v-model="form.weightKg"
                class="w-full h-14 px-4 bg-surface-container-lowest rounded-xl border-none ring-1 ring-surface-container-high focus:ring-2 focus:ring-primary-container/30 transition-all outline-none text-body-md"
                placeholder="4.5"
                type="number"
                inputmode="decimal"
                min="0"
                step="0.1"
              />
            </div>
          </div>

          <!-- Multi-select Tags: Vaccine -->
          <div class="space-y-3">
            <label class="text-label-md font-semibold text-on-surface-variant ml-1">疫苗情况</label>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="tag in vaccineTags"
                :key="tag"
                type="button"
                class="px-4 py-2 rounded-full text-xs font-medium transition-all active:scale-95"
                :class="isVaccineSelected(tag)
                  ? 'bg-primary-container text-white'
                  : 'bg-surface-container-high text-on-surface-variant hover:bg-surface-container-highest'"
                @click="toggleVaccine(tag)"
              >
                {{ tag }}
              </button>
              <button
                type="button"
                class="px-4 py-2 rounded-full text-xs font-medium border border-dashed border-outline-variant text-on-surface-variant flex items-center gap-1"
                @click="onAddCustomVaccine"
              >
                <van-icon name="plus" size="14" />
                自定义
              </button>
            </div>
          </div>
        </div>
      </main>

      <!-- Bottom CTA -->
      <div class="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-[393px] px-6 pb-10 pt-4 bg-gradient-to-t from-background via-background to-transparent">
        <button
          type="button"
          class="w-full h-14 bg-gradient-to-br from-primary to-primary-container text-white font-bold rounded-xl shadow-cta transition-all active:scale-[0.98] flex items-center justify-center gap-2 disabled:opacity-60"
          :disabled="saving"
          @click="onSave"
        >
          保存
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
import type { CreateCatProfileRequest } from '@/types/cat';

interface BreedOption {
  label: string;
  value: string;
}

interface AddCatFormState {
  name: string;
  breed: string;
  ageBirthdayText: string;
  weightKg: string;
}

const router = useRouter();
const { createCat } = useCatManagement();

const saving = ref<boolean>(false);
const avatarInputRef = ref<HTMLInputElement | null>(null);
const avatarPreviewUrl = ref<string>('');

const form = ref<AddCatFormState>({
  name: '',
  breed: '',
  ageBirthdayText: '',
  weightKg: ''
});

const breedOptions: BreedOption[] = [
  { label: '英短蓝猫', value: '英短蓝猫' },
  { label: '布偶猫', value: '布偶猫' },
  { label: '田园猫', value: '田园猫' },
  { label: '暹罗猫', value: '暹罗猫' },
  { label: '缅因猫', value: '缅因猫' }
];

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
  const raw = form.value.weightKg.trim();
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

const onNotificationsClick = (): void => {
  // TODO: 可在此接入 useMessaging() / 通知中心路由跳转
};

const onAddCustomVaccine = (): void => {
  // TODO: 原型仅展示入口；如需自定义标签，可后续设计交互（不要在这里直接弹窗以免偏离原型）。
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
    await createCat(payload);
    closeToast();
    showToast({ type: 'success', message: '猫咪档案创建成功' });
    router.replace({ name: 'Cats' });
  } catch {
    closeToast();
    showToast({ type: 'fail', message: '创建失败，请稍后再试' });
  } finally {
    saving.value = false;
  }
};
</script>

<style scoped>
/* No extra styles beyond prototype utility classes */
</style>
