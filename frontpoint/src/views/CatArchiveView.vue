<template>
  <div
    class="min-h-[100dvh] bg-[#f4f6ff] pb-8"
    @touchstart.passive="onTouchStart"
    @touchend="onTouchEnd"
  >
    <header class="sticky top-0 z-20 bg-[#f4f6ff]/95 px-4 py-2 backdrop-blur">
      <div class="flex min-h-[46px] items-center justify-between">
        <button type="button" class="grid h-10 w-10 place-items-center text-[#1f1f1f]" @click="router.back()">
          <van-icon name="arrow-left" size="20" />
        </button>
        <div class="flex items-center gap-2">
          <div class="text-[22px] font-extrabold tracking-tight text-[#1f1f1f] whitespace-nowrap">猫咪档案</div>
          <div v-if="isShared" class="rounded-full bg-[#ffe6d5] px-3 py-1 text-[12px] font-bold text-[#c95828]">仅预览</div>
        </div>
        <div class="h-10 w-10"></div>
      </div>

      <div v-if="!isShared" class="mt-2 flex gap-2 overflow-x-auto pb-1">
        <button
          type="button"
          class="whitespace-nowrap rounded-full border border-[#d7def7] bg-white px-4 py-2 text-[14px] font-semibold text-[#43517a] disabled:opacity-60"
          :disabled="isShared"
          @click="openCatSwitch"
        >
          切换猫
        </button>
        <button
          type="button"
          class="whitespace-nowrap rounded-full border border-[#d7def7] bg-white px-4 py-2 text-[14px] font-semibold text-[#43517a] disabled:opacity-60"
          :disabled="!catId"
          @click="goEdit"
        >
          编辑
        </button>
        <button
          type="button"
          class="whitespace-nowrap rounded-full border border-[#ffd8c2] bg-[#fff4ee] px-4 py-2 text-[14px] font-semibold text-[#c95828] disabled:opacity-60"
          :disabled="!catId"
          @click="goFeeding"
        >
          投喂
        </button>
        <button
          type="button"
          class="whitespace-nowrap rounded-full bg-[#ff6b35] px-4 py-2 text-[14px] font-semibold text-white disabled:opacity-60"
          :disabled="!canRecordWeight"
          @click="showWeightPopup = true"
        >
          记录体重
        </button>
      </div>
    </header>

    <section v-if="loading" class="mx-4 mt-6 py-10 text-center">
      <van-loading size="24" />
      <div class="mt-3 text-sm text-[#7a6f68]">正在加载档案...</div>
    </section>

    <section v-else class="mx-4 mt-3 overflow-hidden rounded-[24px] bg-white shadow-sm">
      <div class="relative h-[200px] w-full overflow-hidden bg-[#e8ecff]">
        <van-image :src="catAvatar" fit="cover" width="100%" height="100%" />
        <div class="absolute left-4 top-4 rounded-full bg-white/90 px-3 py-1 text-[12px] text-[#5b5f6e]">喵咪证件照</div>
      </div>

      <div class="p-4">
        <div class="flex items-end justify-between">
          <div>
            <div class="text-[30px] font-black leading-none text-[#1f1f1f]">{{ catInfo.name || '未命名猫咪' }}</div>
            <div class="mt-2 text-[14px] text-[#6d7382]">{{ catInfo.breed || '未知品种' }}</div>
          </div>
          <div class="rounded-[14px] bg-[#ffe6d5] px-3 py-1.5 text-[13px] font-semibold text-[#b55325]">{{ genderText }}</div>
        </div>

        <div class="mt-4 grid grid-cols-3 gap-2">
          <div class="rounded-[14px] bg-[#f3f6ff] px-3 py-2 text-center">
            <div class="text-[12px] text-[#71798f]">年龄</div>
            <div class="mt-1 text-[16px] font-bold text-[#2f2f35]">{{ ageText }}</div>
          </div>
          <div class="rounded-[14px] bg-[#f3f6ff] px-3 py-2 text-center">
            <div class="text-[12px] text-[#71798f]">当前体重</div>
            <div class="mt-1 text-[16px] font-bold text-[#2f2f35]">{{ latestWeightText }}</div>
          </div>
          <div class="rounded-[14px] bg-[#f3f6ff] px-3 py-2 text-center">
            <div class="text-[12px] text-[#71798f]">绝育状态</div>
            <div class="mt-1 text-[16px] font-bold text-[#2f2f35]">{{ neuteredText }}</div>
          </div>
        </div>

        <div class="mt-4 rounded-[16px] bg-[#fff6ef] p-3">
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
        <div class="text-[20px] font-black text-[#1f1f1f]">情绪记录</div>
        <div class="text-[12px] text-[#8c8480]">最近 {{ emotionRecords.length }} 条</div>
      </div>

      <div v-if="emotionLoading" class="py-6 text-center">
        <van-loading size="22" />
      </div>

      <div v-else-if="emotionRecords.length === 0" class="mt-4 rounded-[14px] bg-[#f3f6ff] p-4 text-center text-[13px] text-[#7e7672]">
        还没有情绪记录，去喵喵台记录一下吧。
      </div>

      <div v-else class="mt-3 space-y-2">
        <div v-for="item in emotionRecords" :key="item.id" class="flex items-center justify-between rounded-[14px] border border-[#f0ece9] px-3 py-2.5">
          <div class="flex-1">
            <div class="text-[15px] font-bold text-[#2f2f35]">{{ item.emotionTag }}</div>
            <div class="text-[12px] text-[#8c8480]">{{ formatDateTime(item.createdAt) }}</div>
            <div v-if="item.emotionDescription" class="mt-1 text-[12px] text-[#6f6560]">{{ item.emotionDescription }}</div>
          </div>
          <div class="ml-2 text-right">
            <div class="text-[12px] text-[#ff6b35] font-semibold">{{ (item.confidence * 100).toFixed(0) }}%</div>
          </div>
        </div>
      </div>
    </section>

    <section v-if="weeklyReport && weeklyReport.summary" class="mx-4 mt-4 rounded-[20px] bg-white p-4 shadow-sm">
      <div class="flex items-center justify-between">
        <div class="text-[20px] font-black text-[#1f1f1f]">AI 建议</div>
        <div class="text-[12px] text-[#7b8295]">基于最近数据</div>
      </div>

      <div class="mt-3 rounded-[16px] border border-[#e8e4df] bg-[#fffdf9] p-3">
        <div class="text-[14px] leading-relaxed text-[#4a4642]">
          {{ weeklyReport.summary }}
        </div>
      </div>
    </section>

    <section v-if="!isShared && !emotionLoading && !emotionRecords.length" class="mx-4 mt-4 rounded-[20px] bg-white p-4 shadow-sm">
      <div class="text-[14px] font-bold text-[#7e7672] text-center">体重记录与健康时间线需要先记录情绪数据</div>
    </section>

    <template v-if="emotionRecords.length > 0 || weightRecords.length > 0">
      <section class="mx-4 mt-4 rounded-[20px] bg-white p-4 shadow-sm">
        <div class="flex items-center justify-between">
          <div class="text-[20px] font-black text-[#1f1f1f]">体重记录</div>
          <div class="text-[12px] text-[#8c8480]">最近 {{ weightRecords.length }} 条</div>
        </div>

        <div v-if="weightLoading" class="py-6 text-center">
          <van-loading size="22" />
        </div>

        <div v-else-if="weightRecords.length === 0" class="mt-4 rounded-[14px] bg-[#f3f6ff] p-4 text-center text-[13px] text-[#7e7672]">
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

      <section class="mx-4 mt-4 rounded-[20px] bg-white p-4 shadow-sm">
        <div class="flex items-center justify-between">
          <div class="text-[20px] font-black text-[#1f1f1f]">时间线视图</div>
          <div class="text-[12px] text-[#7b8295]">完整健康档案</div>
        </div>

        <div class="mt-3 rounded-[16px] border border-[#e4e8f7] bg-[#f7f9ff] p-3">
          <div class="flex items-center justify-between">
            <div class="text-[14px] font-bold text-[#2f3d66]">体重趋势</div>
            <div class="text-[12px]" :class="trendSummary.delta >= 0 ? 'text-[#c2410c]' : 'text-[#2563eb]'">
              {{ trendSummary.delta >= 0 ? '+' : '' }}{{ trendSummary.delta.toFixed(1) }}kg
            </div>
          </div>

          <div class="mt-2 rounded-xl bg-white px-3 py-3">
            <div v-if="weightRecords.length <= 1" class="text-[13px] text-[#7d8498]">
              体重记录不足 2 条，继续记录后可查看趋势变化。
            </div>

            <div v-else>
              <svg viewBox="0 0 100 42" preserveAspectRatio="none" class="h-24 w-full">
                <polyline
                  :points="weightTrendAreaPoints"
                  fill="rgba(59, 130, 246, 0.12)"
                  stroke="none"
                />
                <polyline
                  :points="weightTrendPoints"
                  fill="none"
                  stroke="#3b82f6"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />
              </svg>
              <div class="mt-1 flex items-center justify-between text-[12px] text-[#7d8498]">
                <span>{{ trendSummary.startDate }}</span>
                <span>{{ trendSummary.endDate }}</span>
              </div>
              <div class="mt-2 text-[13px] text-[#4a556f]">
                {{ trendSummary.description }}
              </div>
            </div>
          </div>
        </div>

        <div class="mt-4 rounded-[16px] border border-[#f0ece9] bg-[#fffdfb] p-3">
          <div class="mb-2 text-[14px] font-bold text-[#3f3632]">关键健康事件</div>

          <div class="space-y-3">
            <div
              v-for="event in timelineEvents"
              :key="event.id"
              class="relative rounded-xl border border-[#efe8e2] bg-white px-3 py-3"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <div class="text-[14px] font-bold text-[#2f2f35]">{{ event.title }}</div>
                  <div class="mt-1 text-[13px] leading-relaxed text-[#6f6560]">{{ event.detail }}</div>
                </div>
                <span
                  class="rounded-full px-2 py-0.5 text-[11px] font-semibold"
                  :class="event.level === 'alert' ? 'bg-[#ffe4dc] text-[#b42318]' : 'bg-[#eef2ff] text-[#3451a3]'"
                >
                  {{ event.level === 'alert' ? '重点' : '记录' }}
                </span>
              </div>
              <div class="mt-2 text-[11px] text-[#9a948f]">{{ event.time }}</div>
            </div>
          </div>
        </div>
      </section>
    </template>

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

    <van-action-sheet v-model:show="showCatSheet" title="切换猫咪">
      <div class="p-4">
        <div class="mb-3 text-xs text-[#7f889d]">选择后将切换到对应健康档案</div>
        <div class="space-y-2">
          <button
            v-for="cat in cats"
            :key="cat.id"
            type="button"
            class="flex w-full items-center justify-between rounded-xl px-3 py-3"
            :class="cat.id === catId ? 'bg-orange-50 text-orange-600' : 'bg-[#f5f7ff] text-[#1f2937]'"
            @click="switchCat(cat.id)"
          >
            <span class="text-sm font-semibold">{{ cat.name }} · {{ cat.breed || '未填写品种' }}</span>
            <van-icon v-if="cat.id === catId" name="success" />
            <van-icon v-else name="arrow" color="#8c95a8" />
          </button>
        </div>
      </div>
    </van-action-sheet>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { showToast } from 'vant';
import { getPetProfile } from '@/api/petProfile';
import { createWeightRecord, getWeightRecords, type WeightRecord } from '@/api/health';
import { getEmotionRecords, getWeeklyReport } from '@/api/emotion';
import type { CatProfileResponse } from '@/types/cat';
import type { EmotionRecordResponse, WeeklyReportResponse } from '@/types/emotion';
import { useCatsStore, useCurrentCatStore } from '@/stores';

type TimelineEvent = {
  id: string;
  title: string;
  detail: string;
  time: string;
  level: 'normal' | 'alert';
  sortAt: number;
};

const props = defineProps<{ id?: string }>();
const route = useRoute();
const router = useRouter();
const catId = computed(() => props.id || String(route.params.id || ''));
const catsStore = useCatsStore();
const currentCatStore = useCurrentCatStore();
const showCatSheet = ref(false);

const fallbackAvatar = 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg';

const catInfo = ref<Partial<CatProfileResponse>>({});
const weightRecords = ref<WeightRecord[]>([]);
const emotionRecords = ref<EmotionRecordResponse[]>([]);
const weeklyReport = ref<Partial<WeeklyReportResponse> | null>(null);
const loading = ref(false);
const emotionLoading = ref(false);
const weightLoading = ref(false);
const showWeightPopup = ref(false);
const weightInput = ref('');
const savingWeight = ref(false);
const cats = computed(() => catsStore.getAllCats);
const touchStartX = ref(0);
const touchStartY = ref(0);

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

const canRecordWeight = computed(() => !isShared.value && Boolean(catId.value));
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

const sortedWeightAsc = computed(() => {
  return [...weightRecords.value].sort((a, b) => new Date(a.recordDate).getTime() - new Date(b.recordDate).getTime());
});

const weightTrendPoints = computed(() => {
  const records = sortedWeightAsc.value;
  if (records.length <= 1) {
    return '0,28 100,28';
  }

  const weights = records.map((item) => item.weight);
  const min = Math.min(...weights);
  const max = Math.max(...weights);
  const range = Math.max(max - min, 0.01);

  return records
    .map((item, index) => {
      const x = (index / (records.length - 1)) * 100;
      const y = 36 - ((item.weight - min) / range) * 28;
      return `${x.toFixed(2)},${y.toFixed(2)}`;
    })
    .join(' ');
});

const weightTrendAreaPoints = computed(() => {
  const line = weightTrendPoints.value;
  const records = sortedWeightAsc.value;
  if (records.length <= 1) {
    return '0,36 100,36 100,42 0,42';
  }
  return `${line} 100,42 0,42`;
});

const trendSummary = computed(() => {
  const records = sortedWeightAsc.value;
  if (records.length <= 1) {
    return {
      delta: 0,
      description: '体重记录还不够，建议每周固定时间记录，方便观察趋势。',
      startDate: '--',
      endDate: '--'
    };
  }

  const first = records[0];
  const last = records[records.length - 1];
  if (!first || !last) {
    return {
      delta: 0,
      description: '体重记录还不够，建议每周固定时间记录，方便观察趋势。',
      startDate: '--',
      endDate: '--'
    };
  }
  const delta = last.weight - first.weight;
  const direction = delta > 0 ? '上升' : delta < 0 ? '下降' : '平稳';

  return {
    delta,
    description: `近期体重整体${direction}，建议结合饮食与运动状态持续观察。`,
    startDate: formatDateTime(first.recordDate).slice(0, 10),
    endDate: formatDateTime(last.recordDate).slice(0, 10)
  };
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

const timelineEvents = computed<TimelineEvent[]>(() => {
  const events: TimelineEvent[] = [];

  const createdAt = catInfo.value.createdAt;
  if (createdAt) {
    events.push({
      id: 'created',
      title: '档案创建',
      detail: '猫咪档案已建立，可持续记录健康数据。',
      time: formatDateTime(createdAt),
      level: 'normal',
      sortAt: new Date(createdAt).getTime()
    });
  }

  if (catInfo.value.vaccineStatus) {
    events.push({
      id: 'vaccine',
      title: '疫苗状态更新',
      detail: `当前疫苗状态：${catInfo.value.vaccineStatus}`,
      time: formatDateTime(catInfo.value.updatedAt || createdAt || new Date().toISOString()),
      level: 'normal',
      sortAt: new Date(catInfo.value.updatedAt || createdAt || new Date().toISOString()).getTime()
    });
  }

  if (catInfo.value.isNeutered === true) {
    events.push({
      id: 'neutered',
      title: '绝育状态记录',
      detail: '已绝育，建议关注术后体重变化。',
      time: formatDateTime(catInfo.value.updatedAt || createdAt || new Date().toISOString()),
      level: 'normal',
      sortAt: new Date(catInfo.value.updatedAt || createdAt || new Date().toISOString()).getTime()
    });
  }

  if (catInfo.value.medicalHistory) {
    events.push({
      id: 'history',
      title: '病史关注项',
      detail: catInfo.value.medicalHistory,
      time: formatDateTime(catInfo.value.updatedAt || createdAt || new Date().toISOString()),
      level: 'alert',
      sortAt: new Date(catInfo.value.updatedAt || createdAt || new Date().toISOString()).getTime()
    });
  }

  if (weightRecords.value.length > 0) {
    const latest = weightRecords.value[0];
    if (latest) {
      events.push({
        id: 'latest-weight',
        title: '最新体重记录',
        detail: `记录体重 ${latest.weight.toFixed(1)}kg。`,
        time: formatDateTime(latest.recordDate),
        level: 'normal',
        sortAt: new Date(latest.recordDate).getTime()
      });
    }
  }

  if (sortedWeightAsc.value.length > 1) {
    const delta = trendSummary.value.delta;
    const lastTrendRow = sortedWeightAsc.value[sortedWeightAsc.value.length - 1];
    if (!lastTrendRow) {
      return events.sort((a, b) => b.sortAt - a.sortAt);
    }
    events.push({
      id: 'trend',
      title: '体重趋势提醒',
      detail: `体重变化 ${delta >= 0 ? '+' : ''}${delta.toFixed(1)}kg，建议定期复查。`,
      time: formatDateTime(lastTrendRow.recordDate),
      level: Math.abs(delta) >= 0.6 ? 'alert' : 'normal',
      sortAt: new Date(lastTrendRow.recordDate).getTime()
    });
  }

  return events.sort((a, b) => b.sortAt - a.sortAt);
});

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

    if (!catId.value) {
      throw new Error('缺少猫咪ID');
    }
    const res = await getPetProfile(catId.value);
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
    const res = await getWeightRecords({ petId: catId.value, page: 1, pageSize: 20 });
    weightRecords.value = res.data.list;
  } catch {
    weightRecords.value = [];
  } finally {
    weightLoading.value = false;
  }
};

const loadEmotions = async () => {
  if (!catId.value || isShared.value) {
    return;
  }
  emotionLoading.value = true;
  try {
    const [recordsRes, reportRes] = await Promise.all([
      getEmotionRecords({ page: 1, pageSize: 5, catId: catId.value }),
      getWeeklyReport({ catId: catId.value })
    ]);
    emotionRecords.value = recordsRes.data.list;
    weeklyReport.value = reportRes.data;
  } catch {
    emotionRecords.value = [];
    weeklyReport.value = null;
  } finally {
    emotionLoading.value = false;
  }
};

const submitWeight = async () => {
  const value = Number(weightInput.value);
  if (!Number.isFinite(value) || value <= 0) {
    showToast({ type: 'fail', message: '请输入正确体重' });
    return;
  }
  if (!catId.value) {
    return;
  }

  savingWeight.value = true;
  try {
    const res = await createWeightRecord({ petId: catId.value, weight: value });
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

const goEdit = () => {
  if (!catId.value || isShared.value) {
    return;
  }
  router.push({ name: 'EditCat', params: { id: catId.value } });
};

const goFeeding = () => {
  if (!catId.value) {
    return;
  }
  router.push({ name: 'FeedRecord', query: { catId: catId.value } });
};

const openCatSwitch = async () => {
  await catsStore.fetchAllCats();
  showCatSheet.value = true;
};

const switchCat = (id: string) => {
  currentCatStore.setCurrentCat(id);
  showCatSheet.value = false;
  router.replace({ name: 'CatArchive', params: { id } });
};

const onTouchStart = (event: TouchEvent) => {
  if (isShared.value) {
    return;
  }
  const touch = event.touches[0];
  if (!touch) return;
  touchStartX.value = touch.clientX;
  touchStartY.value = touch.clientY;
};

const onTouchEnd = (event: TouchEvent) => {
  if (isShared.value || showCatSheet.value || showWeightPopup.value) {
    return;
  }

  const touch = event.changedTouches[0];
  if (!touch) return;

  const deltaX = touch.clientX - touchStartX.value;
  const deltaY = touch.clientY - touchStartY.value;

  // 仅处理明显的水平滑动，避免与上下滚动冲突
  if (Math.abs(deltaX) < 60 || Math.abs(deltaX) <= Math.abs(deltaY)) {
    return;
  }

  const list = cats.value;
  if (!list.length || !catId.value) {
    return;
  }

  const currentIndex = list.findIndex((item) => item.id === catId.value);
  if (currentIndex < 0) {
    return;
  }

  // 需求：左滑上一只，右滑下一只
  const targetIndex = deltaX < 0 ? currentIndex - 1 : currentIndex + 1;

  if (targetIndex < 0 || targetIndex >= list.length) {
    showToast({ message: '已经是边界成员了' });
    return;
  }

  const target = list[targetIndex];
  if (!target) {
    return;
  }

  switchCat(target.id);
};

onMounted(async () => {
  await catsStore.fetchAllCats();
  await loadProfile();
  await loadWeight();
  await loadEmotions();
});

watch(
  () => catId.value,
  async (newId, oldId) => {
    if (!newId || newId === oldId) {
      return;
    }
    await loadProfile();
    await loadWeight();
    await loadEmotions();
  }
);
</script>
