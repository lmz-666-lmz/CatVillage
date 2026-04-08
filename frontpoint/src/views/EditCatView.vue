<template>
  <div class="px-6 pt-6 pb-6">
    <van-nav-bar title="编辑猫咪" left-arrow @click-left="router.back()" />

    <div v-if="loading" class="py-10 text-center">
      <van-loading size="24" />
      <div class="mt-3 text-sm text-on-surface-variant">正在加载档案...</div>
    </div>

    <div v-else-if="error" class="mt-6 rounded-2xl border border-surface-container-high bg-surface-container-lowest p-6 text-center">
      <div class="text-3xl">⚠️</div>
      <div class="mt-3 text-base font-semibold text-on-background">档案加载失败</div>
      <div class="mt-1 text-sm text-on-surface-variant">{{ error }}</div>
      <van-button class="mt-5" block type="primary" @click="reload">重试</van-button>
    </div>

    <div v-else-if="!cat" class="mt-6 rounded-2xl border border-surface-container-high bg-surface-container-lowest p-6 text-center">
      <div class="text-3xl">😿</div>
      <div class="mt-3 text-base font-semibold text-on-background">未找到猫咪档案</div>
      <div class="mt-1 text-sm text-on-surface-variant">可能已被删除或本地缓存过期</div>
      <van-button class="mt-5" block type="primary" @click="router.replace({ name: 'Cats' })">返回列表</van-button>
    </div>

    <template v-else>
      <section class="mt-4 rounded-2xl border border-surface-container-high bg-surface-container-lowest p-4">
        <div class="flex items-center gap-4">
          <input ref="avatarInputRef" type="file" accept="image/*" class="hidden" @change="onAvatarChange" />
          <button
            type="button"
            class="h-16 w-16 overflow-hidden rounded-2xl border border-surface-container-high bg-surface-container-high grid place-items-center"
            @click="openAvatarPicker"
          >
            <img v-if="avatarPreviewUrl" :src="avatarPreviewUrl" class="h-full w-full object-cover" alt="猫咪头像" />
            <van-icon v-else name="photo-o" size="24" class="text-on-surface-variant" />
          </button>
          <div class="min-w-0 flex-1">
            <div class="text-sm font-semibold text-on-background">头像</div>
            <div class="mt-1 text-xs text-on-surface-variant">点击左侧图片上传</div>
          </div>
        </div>
      </section>

      <section class="mt-4">
        <van-cell-group inset>
          <van-field v-model="form.name" name="name" label="名字" placeholder="请输入猫咪名字" />

          <van-field name="breed" label="品种">
            <template #input>
              <select
                v-model="form.breed"
                class="h-8 w-full bg-transparent text-sm text-on-background outline-none"
              >
                <option disabled value="">请选择</option>
                <option v-for="option in breedOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
              </select>
            </template>
          </van-field>

          <van-field
            v-model="form.ageBirthdayText"
            name="ageBirthdayText"
            label="生日(月)"
            placeholder="例如 2022-05"
          />

          <van-field v-model="form.weightKg" name="weightKg" label="体重(kg)" placeholder="例如 4.5" type="number" />
        </van-cell-group>
      </section>

      <section class="mt-4 rounded-2xl border border-surface-container-high bg-surface-container-lowest p-4">
        <div class="text-sm font-semibold text-on-background">疫苗情况</div>
        <div class="mt-3 flex flex-wrap gap-2">
          <button
            v-for="tag in vaccineTags"
            :key="tag"
            type="button"
            class="px-4 py-2 rounded-full text-xs font-semibold transition-all active:scale-95"
            :class="isVaccineSelected(tag)
              ? 'bg-primary text-on-primary'
              : 'bg-surface-container-high text-on-surface-variant'"
            @click="toggleVaccine(tag)"
          >
            {{ tag }}
          </button>
        </div>
      </section>

      <div class="mt-6">
        <button
          type="button"
          class="h-12 w-full rounded-xl bg-primary text-on-primary font-semibold shadow-cta disabled:opacity-60 active:scale-[0.99]"
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
    router.replace({ name: 'Cats' });
  } catch {
    closeToast();
    showToast({ type: 'fail', message: '保存失败，请稍后重试' });
  } finally {
    saving.value = false;
  }
};

onMounted(hydrate);
</script>
