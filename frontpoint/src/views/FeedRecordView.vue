<template>
  <div class="min-h-[100dvh] bg-[#f3f4fa] px-4 pt-3 pb-8">
    <header class="flex min-h-[54px] items-center justify-between">
      <button type="button" class="grid h-10 w-10 place-items-center text-[#594139]" @click="router.back()">
        <van-icon name="arrow-left" size="22" />
      </button>
      <h1 class="text-[30px] font-black text-[#ff6b35]">Feed Pet</h1>
      <div class="w-10"></div>
    </header>

    <section class="mt-4 rounded-[20px] bg-white px-4 py-4 shadow-sm">
      <div class="mb-2 flex items-center justify-between">
        <h2 class="text-[26px] font-black text-[#12182a]">Current Pet</h2>
        <button type="button" class="text-[20px] font-bold text-[#c34f23]" @click="showCatSheet = true">Switch Pet</button>
      </div>

      <div class="flex gap-3 overflow-x-auto pb-2">
        <button
          v-for="cat in cats"
          :key="cat.id"
          type="button"
          class="min-w-[220px] rounded-[16px] border-2 px-3 py-3 text-left transition"
          :class="cat.id === selectedCatId ? 'border-[#f39a79] bg-[#fff8f4]' : 'border-transparent bg-[#f1f3fb]'"
          @click="selectCat(cat.id)"
        >
          <div class="flex items-center gap-3">
            <van-image :src="cat.avatarUrl || fallbackAvatar" width="64" height="64" fit="cover" round />
            <div class="min-w-0">
              <div class="truncate text-[26px] font-black text-[#1d2438]">{{ cat.name }}</div>
              <div class="truncate text-[18px] text-[#807d89]">{{ cat.breed || '未知品种' }} • {{ catAge(cat.age) }}</div>
            </div>
          </div>
        </button>
      </div>
    </section>

    <section class="mt-4 rounded-[20px] bg-[#eceffa] p-4">
      <div class="text-[24px] font-black text-[#1f2943]">猫粮品牌/口味</div>
      <input
        v-model="foodType"
        type="text"
        class="mt-3 h-12 w-full rounded-[14px] border border-transparent bg-white px-4 text-[18px] text-[#27324d] outline-none placeholder:text-[#a4acbe]"
        placeholder="e.g. Orijen Original / Chicken"
      />

      <div class="mt-4 text-[24px] font-black text-[#1f2943]">投喂量(g)</div>
      <div class="mt-3 grid grid-cols-4 gap-2">
        <button
          v-for="weight in quickWeights"
          :key="weight"
          type="button"
          class="h-11 rounded-[12px] text-[20px] font-bold"
          :class="selectedWeight === weight ? 'bg-[#ff6b35] text-white shadow-[0_8px_16px_rgba(255,107,53,0.3)]' : 'bg-white text-[#6f7381]'"
          @click="pickWeight(weight)"
        >
          {{ weight === 0 ? 'Other' : `${weight}g` }}
        </button>
      </div>

      <input
        v-if="selectedWeight === 0"
        v-model="customWeight"
        type="number"
        class="mt-3 h-11 w-full rounded-[12px] border border-transparent bg-white px-4 text-[18px] text-[#27324d] outline-none placeholder:text-[#a4acbe]"
        placeholder="请输入投喂克数"
      />
    </section>

    <section class="mt-4 rounded-[20px] bg-[#eceffa] p-4">
      <div class="text-[24px] font-black text-[#1f2943]">今日体重(kg)</div>
      <div class="mt-3 flex items-center justify-between rounded-[14px] bg-white px-4 py-3">
        <input
          v-model="currentWeightInput"
          type="number"
          step="0.1"
          min="0"
          class="h-10 flex-1 bg-transparent text-[32px] font-black text-[#4a556f] outline-none placeholder:text-[#b2b9c7]"
          placeholder="例如 4.5"
        />
        <div class="text-[30px] font-black text-[#5a4b45]">kg</div>
      </div>

      <div class="mt-4 rounded-[14px] bg-[#fff2f1] px-3 py-3 text-[15px] leading-relaxed text-[#8f6770]">
        <van-icon name="warning-o" />
        定期记录体重有助于监测猫咪健康状况，预防肥胖引起的疾病。
      </div>

      <div class="mt-4 rounded-[14px] border border-[#dfe6fb] bg-white px-3 py-3">
        <div class="flex items-center justify-between gap-2">
          <div class="text-[17px] font-black text-[#27324d]">按体重推荐区间</div>
          <span
            class="rounded-full px-2.5 py-1 text-[13px] font-bold"
            :class="feedingHint.level === 'ok' ? 'bg-[#e8f8ef] text-[#0f8a44]' : feedingHint.level === 'low' ? 'bg-[#eaf2ff] text-[#2f5fbf]' : feedingHint.level === 'high' ? 'bg-[#ffe8e4] text-[#c13b1f]' : 'bg-[#eef2f8] text-[#66718a]'"
          >
            {{ feedingHint.label }}
          </span>
        </div>

        <div v-if="recommendedRange" class="mt-2 text-[15px] text-[#4a556f]">
          当前体重 {{ currentWeightText }}kg，建议每日总投喂
          <span class="font-black text-[#ff6b35]">{{ recommendedRange.min }}g - {{ recommendedRange.max }}g</span>
        </div>
        <div v-else class="mt-2 text-[15px] text-[#7f899e]">暂无体重数据，记录体重后可自动生成推荐区间。</div>

        <div class="mt-3 flex items-end justify-between">
          <div>
            <div class="text-[13px] text-[#7f899e]">今日累计</div>
            <div class="text-[30px] font-black text-[#1f2943]">{{ todayTotalFeed }}g</div>
          </div>
          <div class="text-[13px] text-[#8f99af]">{{ feedingHint.tip }}</div>
        </div>

        <div class="mt-2 h-2.5 overflow-hidden rounded-full bg-[#eef2fb]">
          <div class="h-full rounded-full bg-gradient-to-r from-[#ffad66] to-[#ff6b35]" :style="{ width: `${feedingProgress}%` }"></div>
        </div>
      </div>
    </section>

    <button
      type="button"
      class="mt-6 h-14 w-full rounded-[16px] bg-gradient-to-r from-[#cc3f00] to-[#ff6b35] text-[34px] font-black text-white shadow-[0_14px_24px_rgba(204,63,0,0.28)] disabled:opacity-60"
      :disabled="submitting"
      @click="submitRecord"
    >
      保存记录
    </button>

    <section class="mt-5 rounded-[20px] bg-white p-4 shadow-sm">
      <div class="flex items-center justify-between">
        <div class="text-[22px] font-black text-[#12182a]">按天统计总投喂量</div>
        <div class="text-[16px] text-[#8c90a1]">最近 7 天</div>
      </div>

      <div v-if="dailyFeedStats.length === 0" class="py-6 text-center text-[16px] text-[#8c90a1]">暂无统计数据</div>

      <div v-else class="mt-3 space-y-2">
        <div
          v-for="row in dailyFeedStats"
          :key="row.dateKey"
          class="flex items-center justify-between rounded-[12px] border border-[#eceff8] px-3 py-2"
        >
          <div>
            <div class="text-[17px] font-bold text-[#27324d]">{{ row.dateLabel }}</div>
            <div class="text-[13px] text-[#8b90a2]">{{ row.count }} 次投喂</div>
          </div>
          <div class="text-right">
            <div class="text-[22px] font-black text-[#ff6b35]">{{ row.totalWeight.toFixed(0) }}g</div>
            <div class="text-[12px] text-[#8b90a2]">最近：{{ row.lastTime }}</div>
          </div>
        </div>
      </div>
    </section>

    <section class="mt-5 rounded-[20px] bg-white p-4 shadow-sm">
      <div class="flex items-center justify-between">
        <div class="text-[22px] font-black text-[#12182a]">最近投喂记录</div>
        <div class="text-[16px] text-[#8c90a1]">{{ feedRecords.length }} 条</div>
      </div>
      <div v-if="loadingRecords" class="py-6 text-center">
        <van-loading size="22" />
      </div>
      <div v-else-if="feedRecords.length === 0" class="py-6 text-center text-[16px] text-[#8c90a1]">还没有投喂记录</div>
      <div v-else class="mt-3 space-y-2">
        <div
          v-for="row in feedRecords"
          :key="row.id"
          class="flex items-center justify-between rounded-[12px] border border-[#eceff8] px-3 py-2"
        >
          <div class="min-w-0">
            <div class="truncate text-[18px] font-bold text-[#27324d]">{{ row.foodType }}</div>
            <div class="text-[14px] text-[#8b90a2]">{{ formatTime(row.feedingTime) }}</div>
          </div>
          <div class="text-[22px] font-black text-[#ff6b35]">{{ Number(row.foodWeight).toFixed(0) }}g</div>
        </div>
      </div>
    </section>

    <van-action-sheet v-model:show="showCatSheet" title="切换猫咪">
      <div class="p-4 space-y-2">
        <button
          v-for="cat in cats"
          :key="cat.id"
          type="button"
          class="flex w-full items-center justify-between rounded-xl px-3 py-3"
          :class="cat.id === selectedCatId ? 'bg-orange-50 text-orange-600' : 'bg-[#f5f7ff] text-[#1f2937]'"
          @click="selectCat(cat.id); showCatSheet = false"
        >
          <span class="text-sm font-semibold">{{ cat.name }} · {{ cat.breed || '未填写品种' }}</span>
          <van-icon v-if="cat.id === selectedCatId" name="success" />
          <van-icon v-else name="arrow" color="#8c95a8" />
        </button>
      </div>
    </van-action-sheet>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { showToast } from 'vant';
import { createFeedingRecord, createWeightRecord, getFeedingRecords, getWeightRecords, type FeedingRecord } from '@/api/health';
import { useCatsStore, useCurrentCatStore } from '@/stores';

const route = useRoute();
const router = useRouter();
const catsStore = useCatsStore();
const currentCatStore = useCurrentCatStore();

const fallbackAvatar = 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg';
const showCatSheet = ref(false);

const foodType = ref('');
const selectedWeight = ref(45);
const customWeight = ref('');
const quickWeights = [20, 45, 60, 0];
const submitting = ref(false);
const loadingRecords = ref(false);
const feedRecords = ref<FeedingRecord[]>([]);
const currentWeightKg = ref<number | null>(null);
const currentWeightInput = ref('');

const currentWeightText = computed(() => {
  if (currentWeightKg.value === null) {
    return '暂无';
  }
  return currentWeightKg.value.toFixed(1);
});

const todayTotalFeed = computed(() => {
  const today = new Date();
  const y = today.getFullYear();
  const m = today.getMonth();
  const d = today.getDate();

  return feedRecords.value.reduce((sum, row) => {
    const time = new Date(row.feedingTime);
    if (Number.isNaN(time.getTime())) {
      return sum;
    }
    if (time.getFullYear() === y && time.getMonth() === m && time.getDate() === d) {
      return sum + Number(row.foodWeight || 0);
    }
    return sum;
  }, 0);
});

const recommendedRange = computed(() => {
  if (currentWeightKg.value === null) {
    return null;
  }
  const min = Math.round(currentWeightKg.value * 45);
  const max = Math.round(currentWeightKg.value * 55);
  return { min, max };
});

const feedingHint = computed(() => {
  if (!recommendedRange.value) {
    return {
      level: 'unknown' as const,
      label: '待评估',
      tip: '先记录体重'
    };
  }

  if (todayTotalFeed.value < recommendedRange.value.min) {
    return {
      level: 'low' as const,
      label: '偏低',
      tip: `还差 ${Math.max(recommendedRange.value.min - todayTotalFeed.value, 0).toFixed(0)}g`
    };
  }

  if (todayTotalFeed.value > recommendedRange.value.max) {
    return {
      level: 'high' as const,
      label: '偏高',
      tip: `超出 ${Math.max(todayTotalFeed.value - recommendedRange.value.max, 0).toFixed(0)}g`
    };
  }

  return {
    level: 'ok' as const,
    label: '达标',
    tip: '维持当前节奏'
  };
});

const feedingProgress = computed(() => {
  if (!recommendedRange.value || recommendedRange.value.max <= 0) {
    return 0;
  }
  const raw = (todayTotalFeed.value / recommendedRange.value.max) * 100;
  return Math.max(0, Math.min(100, raw));
});

type DailyFeedStat = {
  dateKey: string;
  dateLabel: string;
  totalWeight: number;
  count: number;
  lastTime: string;
};

const dailyFeedStats = computed<DailyFeedStat[]>(() => {
  const grouped = new Map<string, DailyFeedStat>();

  feedRecords.value.forEach((row) => {
    const time = new Date(row.feedingTime);
    if (Number.isNaN(time.getTime())) {
      return;
    }
    const key = `${time.getFullYear()}-${String(time.getMonth() + 1).padStart(2, '0')}-${String(time.getDate()).padStart(2, '0')}`;
    const existed = grouped.get(key);
    if (!existed) {
      grouped.set(key, {
        dateKey: key,
        dateLabel: formatDateLabel(time),
        totalWeight: Number(row.foodWeight || 0),
        count: 1,
        lastTime: formatClock(time)
      });
      return;
    }

    existed.totalWeight += Number(row.foodWeight || 0);
    existed.count += 1;
    if (formatClock(time) > existed.lastTime) {
      existed.lastTime = formatClock(time);
    }
  });

  return Array.from(grouped.values())
    .sort((a, b) => (a.dateKey > b.dateKey ? -1 : 1))
    .slice(0, 7);
});

const selectedCatId = computed(() => {
  const routeCatId = typeof route.query.catId === 'string' ? route.query.catId : '';
  return routeCatId || currentCatStore.getCurrentCatId || catsStore.getAllCats[0]?.id || '';
});

const cats = computed(() => catsStore.getAllCats);

const catAge = (age?: number) => {
  if (!age || age <= 0) return '未知年龄';
  if (age < 12) return `${age} months`;
  const years = Math.floor(age / 12);
  return `${years} years`;
};

const pickWeight = (value: number) => {
  selectedWeight.value = value;
  if (value !== 0) {
    customWeight.value = '';
  }
};

const selectCat = (catId: string) => {
  currentCatStore.setCurrentCat(catId);
  router.replace({ name: 'FeedRecord', query: { catId } });
};

const getSelectedWeight = () => {
  if (selectedWeight.value !== 0) {
    return selectedWeight.value;
  }
  const custom = Number(customWeight.value);
  if (!Number.isFinite(custom) || custom <= 0) {
    return 0;
  }
  return custom;
};

const loadCurrentWeight = async () => {
  if (!selectedCatId.value) {
    currentWeightKg.value = null;
    currentWeightInput.value = '';
    return;
  }

  try {
    const res = await getWeightRecords({ petId: selectedCatId.value, page: 1, pageSize: 1 });
    const row = res.data.list[0];
    currentWeightKg.value = row ? Number(row.weight) : null;
    currentWeightInput.value = row ? Number(row.weight).toFixed(1) : '';
  } catch {
    currentWeightKg.value = null;
    currentWeightInput.value = '';
  }
};

const loadFeedingRecords = async () => {
  if (!selectedCatId.value) {
    feedRecords.value = [];
    return;
  }

  loadingRecords.value = true;
  try {
    const res = await getFeedingRecords({ petId: selectedCatId.value, page: 1, pageSize: 20 });
    feedRecords.value = res.data.list || [];
  } catch {
    feedRecords.value = [];
  } finally {
    loadingRecords.value = false;
  }
};

const submitRecord = async () => {
  const catId = selectedCatId.value;
  if (!catId) {
    showToast({ type: 'fail', message: '请先添加并选择猫咪' });
    return;
  }
  if (!foodType.value.trim()) {
    showToast({ type: 'fail', message: '请输入猫粮品牌或口味' });
    return;
  }

  const weight = getSelectedWeight();
  if (weight <= 0) {
    showToast({ type: 'fail', message: '请输入正确投喂量' });
    return;
  }

  const editedWeight = Number(currentWeightInput.value);
  const hasEditedWeight = Number.isFinite(editedWeight) && editedWeight > 0;

  submitting.value = true;
  try {
    const res = await createFeedingRecord({
      petId: catId,
      foodType: foodType.value.trim(),
      foodWeight: weight
    });

    feedRecords.value = [res.data, ...feedRecords.value];

    let syncedWeight = false;
    if (hasEditedWeight && (currentWeightKg.value === null || Math.abs(editedWeight - currentWeightKg.value) >= 0.05)) {
      await createWeightRecord({ petId: catId, weight: editedWeight });
      currentWeightKg.value = editedWeight;
      currentWeightInput.value = editedWeight.toFixed(1);
      syncedWeight = true;
    }

    showToast({ type: 'success', message: syncedWeight ? '投喂和体重已同步保存' : '投喂记录已保存' });
    foodType.value = '';
    selectedWeight.value = 45;
    customWeight.value = '';
  } catch {
    showToast({ type: 'fail', message: '保存失败，请稍后再试' });
  } finally {
    submitting.value = false;
  }
};

const formatTime = (value: string) => {
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

const formatClock = (value: Date) => {
  return `${String(value.getHours()).padStart(2, '0')}:${String(value.getMinutes()).padStart(2, '0')}`;
};

const formatDateLabel = (value: Date) => {
  const today = new Date();
  if (
    value.getFullYear() === today.getFullYear() &&
    value.getMonth() === today.getMonth() &&
    value.getDate() === today.getDate()
  ) {
    return '今天';
  }

  const yesterday = new Date();
  yesterday.setDate(today.getDate() - 1);
  if (
    value.getFullYear() === yesterday.getFullYear() &&
    value.getMonth() === yesterday.getMonth() &&
    value.getDate() === yesterday.getDate()
  ) {
    return '昨天';
  }

  return `${value.getMonth() + 1}月${value.getDate()}日`;
};

onMounted(async () => {
  await catsStore.fetchAllCats();
  await loadCurrentWeight();
  await loadFeedingRecords();
});

watch(
  () => selectedCatId.value,
  async (newId, oldId) => {
    if (!newId || newId === oldId) {
      return;
    }
    await loadCurrentWeight();
    await loadFeedingRecords();
  }
);
</script>
