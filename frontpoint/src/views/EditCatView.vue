<template>
  <div class="min-h-[100dvh] bg-[#f4f5fb] px-5 pt-4 pb-8">
    <header class="sticky top-0 z-20 -mx-5 flex items-center justify-between bg-[#f4f5fb]/95 px-5 py-3 backdrop-blur">
      <button type="button" class="grid h-10 w-10 place-items-center text-[#837974]" @click="router.back()">
        <van-icon name="arrow-left" size="20" />
      </button>
      <h1 class="text-[32px] font-extrabold tracking-tight text-[#1f2431]">编辑猫咪</h1>
      <div class="h-10 w-10"></div>
    </header>

    <div v-if="loading" class="rounded-2xl border border-surface-container-high bg-surface-container-lowest px-4 py-10 text-center text-sm text-on-surface-variant">
      <van-loading size="20" />
      <div class="mt-3">正在加载猫咪档案...</div>
    </div>

    <div v-else-if="error" class="rounded-2xl border border-surface-container-high bg-surface-container-lowest px-4 py-10 text-center text-sm text-on-surface-variant">
      <div class="text-base font-semibold text-on-background">组件加载失败</div>
      <div class="mt-2">{{ error }}</div>
      <van-button class="mt-4" type="primary" @click="reload">重试</van-button>
    </div>

    <div v-else-if="!cat" class="rounded-2xl border border-surface-container-high bg-surface-container-lowest px-4 py-10 text-center text-sm text-on-surface-variant">
      <div class="text-base font-semibold text-on-background">未找到猫咪档案</div>
      <div class="mt-2">可能已被删除或数据未同步</div>
      <van-button class="mt-4" type="primary" @click="router.replace({ name: 'MyPets' })">返回我的萌宠</van-button>
    </div>

    <template v-else>
      <section class="mt-4 rounded-[20px] border border-[#dbe2f4] bg-white p-4">
        <div class="flex items-center gap-4">
          <input ref="avatarInputRef" type="file" accept="image/*" class="hidden" @change="onAvatarChange" />
          <button
            type="button"
            class="grid h-[94px] w-[94px] place-items-center overflow-hidden rounded-[24px] bg-[#dbe2f6]"
            @click="openAvatarPicker"
          >
            <img v-if="avatarPreviewUrl" :src="avatarPreviewUrl" class="h-full w-full object-cover" alt="猫咪头像" />
            <van-icon v-else name="photo-o" size="30" class="text-[#5e6b86]" />
          </button>
          <div>
            <div class="text-[40px] font-black text-[#12182a]">头像</div>
            <div class="mt-1 text-[18px] text-[#594139]">点击左侧图片上传</div>
          </div>
        </div>
      </section>

      <section class="mt-5 rounded-[18px] border border-[#dbe2f4] bg-white px-5 py-1 shadow-[0_2px_10px_rgba(25,42,70,0.04)]">
        <div class="divide-y divide-[#edf0f5]">
          <div class="flex min-h-[70px] items-center gap-3">
            <div class="w-[100px] shrink-0 text-[18px] font-medium text-[#1f2431]">名字</div>
            <input
              v-model="form.name"
              type="text"
              placeholder="请输入猫咪名字"
              class="h-10 flex-1 bg-transparent text-[18px] text-[#12182a] outline-none placeholder:text-[#c2c8d4]"
            />
          </div>

          <div class="flex min-h-[70px] items-center gap-3">
            <div class="w-[100px] shrink-0 text-[18px] font-medium text-[#1f2431]">品种</div>
            <div class="relative flex-1">
              <select v-model="form.breed" class="h-10 w-full appearance-none bg-transparent pr-10 text-[18px] text-[#12182a] outline-none">
                <option disabled value="">请选择</option>
                <option v-for="option in breedOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
              </select>
              <van-icon name="arrow-down" class="absolute right-1 top-1/2 -translate-y-1/2 text-[#7c879e]" />
            </div>
          </div>

          <div class="flex min-h-[70px] items-center gap-3">
            <div class="w-[100px] shrink-0 text-[18px] font-medium text-[#1f2431]">生日(月)</div>
            <input
              v-model="form.ageBirthdayText"
              type="text"
              placeholder="例如 2022-05"
              class="h-10 flex-1 bg-transparent text-[18px] text-[#12182a] outline-none placeholder:text-[#c2c8d4]"
            />
          </div>

          <div class="flex min-h-[70px] items-center gap-3">
            <div class="w-[100px] shrink-0 text-[18px] font-medium text-[#1f2431]">体重(kg)</div>
            <input
              v-model="form.weightKg"
              type="number"
              placeholder="例如 4.5"
              class="h-10 flex-1 bg-transparent text-[18px] text-[#12182a] outline-none placeholder:text-[#c2c8d4]"
            />
          </div>
        </div>
      </section>

      <section class="mt-5 rounded-[20px] border border-[#dbe2f4] bg-white p-4">
        <div class="text-[20px] font-bold text-[#12182a]">疫苗情况</div>
        <div class="mt-4 flex flex-wrap gap-3">
          <button
            v-for="tag in vaccineTags"
            :key="tag"
            type="button"
            class="rounded-full px-5 py-2 text-[14px] font-medium transition-all active:scale-95"
            :class="isVaccineSelected(tag)
              ? 'bg-[#bf3a00] text-white'
              : 'bg-[#dfe4f8] text-[#1f2431]'"
            @click="toggleVaccine(tag)"
          >
            {{ tag }}
          </button>
        </div>
      </section>

      <div class="mt-8">
        <button
          type="button"
          class="h-[66px] w-full rounded-[20px] bg-gradient-to-br from-[#b83a00] to-[#ff6b35] text-[18px] font-bold text-white shadow-[0_12px_30px_rgba(255,107,53,0.3)] disabled:opacity-60 active:scale-[0.99]"
          :disabled="saving"
          @click="save"
        >
          {{ saving ? '保存中...' : '保存修改' }}
        </button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { closeToast, showToast } from 'vant';
import { useCatManagement } from '@/composables/useCatManagement';
import { useCatsStore } from '@/stores';
import type { UpdateCatProfileRequest } from '@/types/cat';
import { CAT_BREED_OPTIONS } from '@/constants/catBreeds';

const props = defineProps<{ id: string }>();
const router = useRouter();
const catsStore = useCatsStore();
const { updateCat } = useCatManagement();

const loading = ref(false);
const saving = ref(false);
const error = ref<string | null>(null);

const avatarInputRef = ref<HTMLInputElement | null>(null);
const avatarPreviewUrl = ref<string>('');

const form = ref({
  name: '',
  breed: '',
  ageBirthdayText: '',
  weightKg: ''
});

const vaccineTags = ['三联疫苗', '狂犬疫苗', '体内驱虫', '体外驱虫'] as const;
type VaccineTag = (typeof vaccineTags)[number];
const selectedVaccines = ref<VaccineTag[]>([]);

const breedOptions = CAT_BREED_OPTIONS.map((option) => ({
  label: option.label,
  value: option.label
}));

const cat = computed(() => catsStore.getCatById(props.id));

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

const ageInMonths = computed<number | undefined>(() => {
  const raw = form.value.ageBirthdayText.trim();
  if (!raw) {
    return undefined;
  }
  const parsed = parseBirthdayMonth(raw);
  if (!parsed) {
    return undefined;
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

const hydrate = async () => {
  loading.value = true;
  error.value = null;
  try {
    if (!catsStore.getAllCats.length) {
      await catsStore.fetchAllCats();
    }
    const c = catsStore.getCatById(props.id);
    if (!c) {
      return;
    }
    form.value.name = c.name;
    form.value.breed = c.breed;
    form.value.weightKg = c.weight ? String(c.weight) : '';
    avatarPreviewUrl.value = c.avatarUrl || '';
    selectedVaccines.value = (c.vaccineStatus ? c.vaccineStatus.split('、') : []).filter(Boolean) as VaccineTag[];
  } catch {
    error.value = '档案加载失败，请检查后端服务';
  } finally {
    loading.value = false;
  }
};

const reload = () => hydrate();

const save = async () => {
  if (!form.value.name.trim()) {
    showToast({ type: 'fail', message: '请输入猫咪名字' });
    return;
  }
  if (!form.value.breed) {
    showToast({ type: 'fail', message: '请选择猫咪品种' });
    return;
  }

  const payload: UpdateCatProfileRequest = {
    name: form.value.name.trim(),
    breed: form.value.breed,
    age: ageInMonths.value,
    weight: weightNumber.value,
    vaccineStatus: selectedVaccines.value.join('、') || undefined,
    avatarUrl: avatarPreviewUrl.value || undefined
  };

  saving.value = true;
  showToast({ type: 'loading', message: '正在保存...', duration: 0, forbidClick: true });
  try {
    await updateCat(props.id, payload);
    closeToast();
    showToast({ type: 'success', message: '已保存' });
    router.replace({ name: 'CatArchive', params: { id: props.id } });
  } catch {
    closeToast();
    showToast({ type: 'fail', message: '保存失败，请稍后重试' });
  } finally {
    saving.value = false;
  }
};

onMounted(hydrate);
</script>
