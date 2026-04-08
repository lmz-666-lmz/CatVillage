<template>
  <div class="min-h-[100dvh] bg-[#f6efe8] pb-8">
    <header class="sticky top-0 z-20 flex min-h-[54px] items-center justify-between bg-[#f6efe8]/95 px-4 py-2 backdrop-blur">
      <button type="button" class="grid h-10 w-10 place-items-center text-[#1f1f1f]" @click="router.back()">
        <van-icon name="arrow-left" size="20" />
      </button>
      <div class="text-[18px] font-extrabold text-[#1f1f1f]">猫咪档案</div>
      <button
        type="button"
        class="rounded-full bg-[#ff6b35] px-3 py-1.5 text-[13px] font-semibold text-white disabled:opacity-60"
        :disabled="!canRecordWeight"
        @click="showWeightPopup = true"
      >
        记录体重
      </button>
    </header>

    <section v-if="loading" class="mx-4 mt-6 py-10 text-center">
      <van-loading size="24" />
      <div class="mt-3 text-sm text-[#7a6f68]">正在加载档案...</div>
    </section>

    <section v-else class="mx-4 mt-3 overflow-hidden rounded-[24px] bg-white shadow-sm">
      <div class="relative h-[260px] w-full overflow-hidden bg-[#fde8da]">
        <van-image :src="catAvatar" fit="cover" width="100%" height="100%" />
        <div class="absolute left-4 top-4 rounded-full bg-white/90 px-3 py-1 text-[12px] text-[#5b534f]">喵咪证件照</div>
      </div>

      <div class="p-4">
        <div class="flex items-end justify-between">
          <div>
            <div class="text-[30px] font-black leading-none text-[#1f1f1f]">{{ catInfo.name || '未命名猫咪' }}</div>
            <div class="mt-2 text-[14px] text-[#7a6f68]">{{ catInfo.breed || '未知品种' }}</div>
          </div>
          <div class="rounded-[14px] bg-[#ffe6d5] px-3 py-1.5 text-[13px] font-semibold text-[#b55325]">{{ genderText }}</div>
        </div>

        <div class="mt-4 grid grid-cols-3 gap-2">
          <div class="rounded-[14px] bg-[#f7f8fc] px-3 py-2 text-center">
            <div class="text-[12px] text-[#8c8480]">年龄</div>
            <div class="mt-1 text-[16px] font-bold text-[#2f2f35]">{{ ageText }}</div>
          </div>
          <div class="rounded-[14px] bg-[#f7f8fc] px-3 py-2 text-center">
            <div class="text-[12px] text-[#8c8480]">当前体重</div>
            <div class="mt-1 text-[16px] font-bold text-[#2f2f35]">{{ latestWeightText }}</div>
          </div>
          <div class="rounded-[14px] bg-[#f7f8fc] px-3 py-2 text-center">
            <div class="text-[12px] text-[#8c8480]">绝育状态</div>
            <div class="mt-1 text-[16px] font-bold text-[#2f2f35]">{{ neuteredText }}</div>
          </div>
        </div>

        <div class="mt-4 rounded-[16px] bg-[#fff7f2] p-3">
          <div class="text-[14px] font-bold text-[#3f3632]">健康备注</div>
          <div class="mt-1 text-[13px] leading-relaxed text-[#6f6560]">
            疫苗：{{ catInfo.vaccineStatus || '暂无' }}
            <br>
            病史：{{ catInfo.medicalHistory || '暂无' }}
          </div>
        </div>
      </div>
    </section>

    <section class="mx-4 mt-4 rounded-[20px] bg-white p-4 shadow-sm">
      <div class="flex items-center justify-between">
        <div class="text-[20px] font-black text-[#1f1f1f]">体重记录</div>
        <div class="text-[12px] text-[#8c8480]">最近 {{ weightRecords.length }} 条</div>
      </div>

      <div v-if="weightLoading" class="py-6 text-center">
        <van-loading size="22" />
      </div>

      <div v-else-if="weightRecords.length === 0" class="mt-4 rounded-[14px] bg-[#f7f8fc] p-4 text-center text-[13px] text-[#7e7672]">
        还没有体重记录，先来记录第一条吧。
      </div>

      <div v-else class="mt-3 space-y-2">
        <div v-for="row in weightRecords" :key="row.id" class="flex items-center justify-between rounded-[14px] border border-[#f0ece9] px-3 py-2.5">
          <div>
            <div class="text-[15px] font-bold text-[#2f2f35]">{{ row.weight.toFixed(1) }} kg</div>
            <div class="text-[12px] text-[#8c8480]">{{ formatDateTime(row.recordDate) }}</div>
          </div>
          <van-icon name="chart-trending-o" size="18" color="#ff6b35" />
        </div>
      </div>
    </section>

    <van-popup v-model:show="showWeightPopup" round position="bottom" :style="{ padding: '16px' }">
      <div class="text-[18px] font-extrabold text-[#1f1f1f]">新增体重记录</div>
      <div class="mt-3">
        <van-field v-model="weightInput" type="number" label="体重(kg)" placeholder="例如 4.6" />
      </div>
      <div class="mt-4 grid grid-cols-2 gap-2">
        <van-button block plain type="primary" @click="showWeightPopup = false">取消</van-button>
        <van-button block type="primary" :loading="savingWeight" @click="submitWeight">保存</van-button>
      </div>
    </van-popup>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { showToast } from 'vant';
import { getPetProfile } from '@/api/petProfile';
import { createWeightRecord, getWeightRecords, type WeightRecord } from '@/api/health';
import type { CatProfileResponse } from '@/types/cat';

const props = defineProps<{ id: string }>();
const route = useRoute();
const router = useRouter();

const fallbackAvatar = 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg';

const catInfo = ref<Partial<CatProfileResponse>>({});
const weightRecords = ref<WeightRecord[]>([]);
const loading = ref(false);
const weightLoading = ref(false);
const showWeightPopup = ref(false);
const weightInput = ref('');
const savingWeight = ref(false);

const sharedPayload = computed(() => {
  const raw = route.query.shared;
  if (!raw || typeof raw !== 'string') {
    return null;
  }
  try {
    return JSON.parse(raw) as { id?: string; name?: string; breed?: string; ageText?: string; weight?: number; avatarUrl?: string };
  } catch {
    return null;
  }
});

const isShared = computed(() => route.query.mode === 'shared' || Boolean(sharedPayload.value));

const canRecordWeight = computed(() => !isShared.value && Boolean(props.id));
const catAvatar = computed(() => catInfo.value.avatarUrl || sharedPayload.value?.avatarUrl || fallbackAvatar);
const genderText = computed(() => (catInfo.value.gender === 1 ? '男孩子' : catInfo.value.gender === 0 ? '女孩子' : '未知'));
const ageText = computed(() => {
  if (sharedPayload.value?.ageText) {
    return sharedPayload.value.ageText;
  }
  const age = catInfo.value.age;
  if (!age || age <= 0) {
    return '未知';
  }
  if (age < 12) {
    return `${age}个月`;
  }
  const year = Math.floor(age / 12);
  const month = age % 12;
  return month ? `${year}岁${month}个月` : `${year}岁`;
});

const latestWeightText = computed(() => {
  const latest = weightRecords.value[0];
  if (latest) {
    return `${latest.weight.toFixed(1)}kg`;
  }
  if (typeof sharedPayload.value?.weight === 'number') {
    return `${sharedPayload.value.weight.toFixed(1)}kg`;
  }
  if (typeof catInfo.value.weight === 'number') {
    return `${catInfo.value.weight.toFixed(1)}kg`;
  }
  return '暂无';
});

const neuteredText = computed(() => {
  if (catInfo.value.isNeutered === true) {
    return '已绝育';
  }
  if (catInfo.value.isNeutered === false) {
    return '未绝育';
  }
  return '未知';
});

const formatDateTime = (value: string) => {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  const hh = String(date.getHours()).padStart(2, '0');
  const mm = String(date.getMinutes()).padStart(2, '0');
  return `${y}-${m}-${d} ${hh}:${mm}`;
};

const loadProfile = async () => {
  loading.value = true;
  try {
    if (isShared.value && sharedPayload.value) {
      catInfo.value = {
        id: sharedPayload.value.id,
        name: sharedPayload.value.name || '喵咪档案',
        breed: sharedPayload.value.breed || '未知品种',
        avatarUrl: sharedPayload.value.avatarUrl,
        gender: undefined,
        weight: sharedPayload.value.weight
      };
      return;
    }

    const res = await getPetProfile(props.id);
    catInfo.value = res.data;
  } catch {
    showToast({ type: 'fail', message: '档案加载失败' });
  } finally {
    loading.value = false;
  }
};

const loadWeight = async () => {
  if (!canRecordWeight.value) {
    return;
  }
  weightLoading.value = true;
  try {
    const res = await getWeightRecords({ petId: props.id, page: 1, pageSize: 20 });
    weightRecords.value = res.data.list;
  } catch {
    weightRecords.value = [];
  } finally {
    weightLoading.value = false;
  }
};

const submitWeight = async () => {
  const value = Number(weightInput.value);
  if (!Number.isFinite(value) || value <= 0) {
    showToast({ type: 'fail', message: '请输入正确体重' });
    return;
  }
  if (!props.id) {
    return;
  }

  savingWeight.value = true;
  try {
    const res = await createWeightRecord({ petId: props.id, weight: value });
    weightRecords.value = [res.data, ...weightRecords.value];
    catInfo.value = { ...catInfo.value, weight: value };
    weightInput.value = '';
    showWeightPopup.value = false;
    showToast({ type: 'success', message: '体重记录已保存' });
  } catch {
    showToast({ type: 'fail', message: '保存失败，请稍后重试' });
  } finally {
    savingWeight.value = false;
  }
};

onMounted(async () => {
  await loadProfile();
  await loadWeight();
});
</script>
