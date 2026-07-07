<template>
  <div
    class="min-h-[100dvh] bg-[#fff7f0] pb-8"
    @touchstart.passive="onTouchStart"
    @touchend="onTouchEnd"
  >
    <header class="sticky top-0 z-20 bg-[#f5f7fb]/95 px-4 py-2 backdrop-blur">
      <div class="flex min-h-[46px] items-center justify-between">
        <button type="button" class="grid h-10 w-10 place-items-center text-[#172033]" @click="router.back()">
          <van-icon name="arrow-left" size="20" />
        </button>
        <div class="flex items-center gap-2">
          <div class="text-2xl font-black text-[#172033] tracking-tight whitespace-nowrap">猫咪档案</div>
          <div v-if="isShared" class="rounded-full bg-[#ffe6d5] px-3 py-1 text-[12px] font-bold text-[#f97316]">仅预览</div>
        </div>
        <div class="h-10 w-10"></div>
      </div>

      <div v-if="!isShared" class="mt-2 flex gap-2 overflow-x-auto pb-1">
        <button
          type="button"
          class="whitespace-nowrap rounded-full border border-[#d7def7] bg-white px-4 py-2 text-[14px] font-semibold text-[#172033] disabled:opacity-60"
          :disabled="isShared"
          @click="openCatSwitch"
        >
          切换猫
        </button>
        <button
          type="button"
          class="whitespace-nowrap rounded-full border border-[#d7def7] bg-white px-4 py-2 text-[14px] font-semibold text-[#172033] disabled:opacity-60"
          :disabled="!catId"
          @click="goEdit"
        >
          编辑
        </button>
        <button
          type="button"
          class="whitespace-nowrap rounded-full border border-[#ffd8c2] bg-[#fff4ee] px-4 py-2 text-[14px] font-semibold text-[#f97316] disabled:opacity-60"
          :disabled="!catId"
          @click="goFeeding"
        >
          投喂
        </button>
        <button
          type="button"
          class="whitespace-nowrap rounded-full bg-[#f97316] px-4 py-2 text-[14px] font-semibold text-white disabled:opacity-60"
          :disabled="!canRecordWeight"
          @click="showWeightPopup = true"
        >
          记录体重
        </button>
      </div>
    </header>

    <section v-if="loading" class="mx-4 mt-6 py-10 text-center">
      <van-loading size="24" />
      <div class="mt-3 text-sm text-[#748094]">正在加载档案...</div>
    </section>

    <section v-else class="mx-4 mt-3 overflow-hidden rounded-[22px] border border-[rgba(226,232,240,0.92)] bg-[rgba(255,255,255,0.92)] shadow-[0_12px_26px_rgba(23,32,51,0.06)]">
      <div class="relative h-[200px] w-full overflow-hidden bg-[#e8ecff]">
        <van-image :src="catAvatar" fit="cover" width="100%" height="100%" />
        <div class="absolute left-4 top-4 rounded-full bg-white/90 px-3 py-1 text-[12px] text-[#748094]">喵咪证件照</div>
      </div>

      <div class="p-4">
        <div class="flex items-end justify-between">
          <div>
            <div class="text-[30px] font-black leading-none text-[#172033]">{{ catInfo.name || '喵咪档案' }}</div>
            <div class="mt-2 text-[14px] text-[#748094]">{{ breedText }}</div>
          </div>
          <div v-if="genderText" class="rounded-[14px] bg-[#ffe6d5] px-3 py-1.5 text-[13px] font-semibold text-[#f97316]">{{ genderText }}</div>
        </div>

        <div class="mt-4 grid grid-cols-3 gap-2">
          <div class="rounded-[14px] bg-[#f3f6ff] px-3 py-2 text-center">
            <div class="text-[12px] text-[#748094]">年龄</div>
            <div class="mt-1 text-[16px] font-bold text-[#172033]">{{ ageText }}</div>
          </div>
          <div v-if="latestWeightText" class="rounded-[14px] bg-[#f3f6ff] px-3 py-2 text-center">
            <div class="text-[12px] text-[#748094]">当前体重</div>
            <div class="mt-1 text-[16px] font-bold text-[#172033]">{{ latestWeightText }}</div>
          </div>
          <div v-if="neuteredText" class="rounded-[14px] bg-[#f3f6ff] px-3 py-2 text-center">
            <div class="text-[12px] text-[#748094]">绝育状态</div>
            <div class="mt-1 text-[16px] font-bold text-[#172033]">{{ neuteredText }}</div>
          </div>
        </div>

        <div v-if="vaccineStatusText || catInfo.medicalHistory" class="mt-4 rounded-[16px] bg-[#fff6ef] p-3">
          <div class="text-[14px] font-bold text-[#172033]">健康备注</div>
          <div class="mt-1 text-[13px] leading-relaxed text-[#748094]">
            <template v-if="vaccineStatusText">疫苗：{{ vaccineStatusText }}</template>
            <br v-if="vaccineStatusText && catInfo.medicalHistory">
            <template v-if="catInfo.medicalHistory">病史：{{ catInfo.medicalHistory }}</template>
          </div>
        </div>
        <div v-else-if="isShared" class="mt-4 rounded-[16px] bg-[#fff6ef] p-3 text-[13px] leading-relaxed text-[#748094]">
          主人还没有补充更多健康备注。
        </div>
      </div>
    </section>

    <section v-if="!isShared || emotionRecords.length > 0" class="mx-4 mt-4 rounded-[22px] border border-[rgba(226,232,240,0.92)] bg-[rgba(255,255,255,0.92)] p-4 shadow-[0_12px_26px_rgba(23,32,51,0.06)]">
      <div class="flex items-center justify-between">
        <div class="text-[20px] font-black text-[#172033]">情绪记录</div>
        <div class="text-[12px] text-[#748094]">最近 {{ emotionRecords.length }} 条</div>
      </div>

      <div v-if="emotionLoading" class="py-6 text-center">
        <van-loading size="22" />
      </div>

      <div v-else-if="!isShared && emotionRecords.length === 0" class="mt-4 rounded-[14px] bg-[#f3f6ff] p-4 text-center text-[13px] text-[#748094]">
        还没有情绪记录，去喵喵台记录一下吧。
      </div>

      <div v-else class="mt-3 space-y-2">
        <div v-for="item in emotionRecords" :key="item.id" class="flex items-center justify-between rounded-[14px] border border-[#f0ece9] px-3 py-2.5">
          <div class="flex-1">
            <div class="text-[15px] font-bold text-[#172033]">{{ item.emotionTag }}</div>
            <div class="text-[12px] text-[#748094]">{{ formatDateTime(item.createdAt) }}</div>
            <div v-if="item.emotionDescription" class="mt-1 text-[12px] text-[#748094]">{{ item.emotionDescription }}</div>
          </div>
          <div class="ml-2 text-right">
            <div class="text-[12px] text-[#f97316] font-semibold">{{ (item.confidence * 100).toFixed(0) }}%</div>
          </div>
        </div>
      </div>
    </section>

    <section v-if="weeklyReport && weeklyReport.summary" class="mx-4 mt-4 rounded-[22px] border border-[rgba(226,232,240,0.92)] bg-[rgba(255,255,255,0.92)] p-4 shadow-[0_12px_26px_rgba(23,32,51,0.06)]">
      <div class="flex items-center justify-between">
        <div class="text-[20px] font-black text-[#172033]">照护建议</div>
        <div class="text-[12px] text-[#748094]">基于最近数据</div>
      </div>

      <div class="mt-3 rounded-[16px] border border-[#e8e4df] bg-[#fffdf9] p-3">
        <div class="text-[14px] leading-relaxed text-[#172033]">
          {{ weeklyReport.summary }}
        </div>
      </div>
    </section>

    <section v-if="!isShared && !emotionLoading && !emotionRecords.length" class="mx-4 mt-4 rounded-[22px] border border-[rgba(226,232,240,0.92)] bg-[rgba(255,255,255,0.92)] p-4 shadow-[0_12px_26px_rgba(23,32,51,0.06)]">
      <div class="text-[14px] font-bold text-[#748094] text-center">体重记录与健康时间线需要先记录情绪数据</div>
    </section>

    <template v-if="emotionRecords.length > 0 || weightRecords.length > 0">
      <section class="mx-4 mt-4 rounded-[22px] border border-[rgba(226,232,240,0.92)] bg-[rgba(255,255,255,0.92)] p-4 shadow-[0_12px_26px_rgba(23,32,51,0.06)]">
        <div class="flex items-center justify-between">
          <div class="text-[20px] font-black text-[#172033]">体重记录</div>
          <div class="text-[12px] text-[#748094]">最近 {{ weightRecords.length }} 条</div>
        </div>

        <div v-if="weightLoading" class="py-6 text-center">
          <van-loading size="22" />
        </div>

        <div v-else-if="weightRecords.length === 0" class="mt-4 rounded-[14px] bg-[#f3f6ff] p-4 text-center text-[13px] text-[#748094]">
          还没有体重记录，先来记录第一条吧。
        </div>

        <div v-else class="mt-3 space-y-2">
          <div v-for="row in weightRecords" :key="row.id" class="flex items-center justify-between rounded-[14px] border border-[#f0ece9] px-3 py-2.5">
            <div>
              <div class="text-[15px] font-bold text-[#172033]">{{ row.weight.toFixed(1) }} kg</div>
              <div class="text-[12px] text-[#748094]">{{ formatDateTime(row.recordDate) }}</div>
            </div>
            <van-icon name="chart-trending-o" size="18" color="#f97316" />
          </div>
        </div>
      </section>

      <section class="mx-4 mt-4 rounded-[22px] border border-[rgba(226,232,240,0.92)] bg-[rgba(255,255,255,0.92)] p-4 shadow-[0_12px_26px_rgba(23,32,51,0.06)]">
        <div class="flex items-center justify-between">
          <div class="text-[20px] font-black text-[#172033]">时间线视图</div>
          <div class="text-[12px] text-[#748094]">完整健康档案</div>
        </div>

        <div class="mt-3 rounded-[16px] border border-[#e4e8f7] bg-[#f7f9ff] p-3">
          <div class="flex items-center justify-between">
            <div class="text-[14px] font-bold text-[#2f3d66]">体重趋势</div>
            <div class="text-[12px]" :class="trendSummary.delta >= 0 ? 'text-[#c2410c]' : 'text-[#2563eb]'">
              {{ trendSummary.delta >= 0 ? '+' : '' }}{{ trendSummary.delta.toFixed(1) }}kg
            </div>
          </div>

          <div class="mt-2 rounded-xl bg-white px-3 py-3">
            <div v-if="weightRecords.length <= 1" class="text-[13px] text-[#748094]">
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
              <div class="mt-1 flex items-center justify-between text-[12px] text-[#748094]">
                <span>{{ trendSummary.startDate }}</span>
                <span>{{ trendSummary.endDate }}</span>
              </div>
              <div class="mt-2 text-[13px] text-[#748094]">
                {{ trendSummary.description }}
              </div>
            </div>
          </div>
        </div>

        <div class="mt-4 rounded-[16px] border border-[#f0ece9] bg-[#fffdfb] p-3">
          <div class="mb-2 text-[14px] font-bold text-[#172033]">关键健康事件</div>

          <div class="space-y-3">
            <div
              v-for="event in timelineEvents"
              :key="event.id"
              class="relative rounded-xl border border-[#efe8e2] bg-white px-3 py-3"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="min-w-0">
                  <div class="text-[14px] font-bold text-[#172033]">{{ event.title }}</div>
                  <div class="mt-1 text-[13px] leading-relaxed text-[#748094]">{{ event.detail }}</div>
                </div>
                <span
                  class="rounded-full px-2 py-0.5 text-[11px] font-semibold"
                  :class="event.level === 'alert' ? 'bg-[#ffe4dc] text-[#b42318]' : 'bg-[#eef2ff] text-[#3451a3]'"
                >
                  {{ event.level === 'alert' ? '重点' : '记录' }}
                </span>
              </div>
              <div class="mt-2 text-[11px] text-[#748094]">{{ event.time }}</div>
            </div>
          </div>
        </div>
      </section>
    </template>

    <van-popup v-model:show="showWeightPopup" round position="bottom" :style="{ padding: '0', background: 'transparent' }">
      <div class="weight-popup">
        <div class="weight-popup-bar"></div>
        <div class="weight-popup-title">新增体重记录</div>
        <p class="weight-popup-hint">记录当前体重，追踪健康变化趋势</p>

        <div class="weight-popup-input-row">
          <input
            v-model="weightInput"
            type="number"
            step="0.1"
            min="0"
            class="weight-popup-input"
            placeholder="4.6"
          />
          <span class="weight-popup-unit">kg</span>
        </div>

        <div class="weight-popup-presets">
          <button
            v-for="w in [3.0, 4.0, 4.5, 5.0, 6.0]"
            :key="w"
            type="button"
            class="weight-preset-chip"
            :class="{ active: weightInput === String(w) }"
            @click="weightInput = String(w)"
          >
            {{ w }} kg
          </button>
        </div>

        <div class="weight-popup-actions">
          <button type="button" class="weight-popup-cancel" @click="showWeightPopup = false">取消</button>
          <button type="button" class="weight-popup-save" :disabled="savingWeight" @click="submitWeight">
            {{ savingWeight ? '保存中...' : '保存记录' }}
          </button>
        </div>
      </div>
    </van-popup>

    <van-action-sheet v-model:show="showCatSheet" title="切换猫咪">
      <div class="p-4">
        <div class="mb-3 text-xs text-[#748094]">选择后将切换到对应健康档案</div>
        <div class="space-y-2">
          <button
            v-for="cat in cats"
            :key="cat.id"
            type="button"
            class="flex w-full items-center justify-between rounded-xl px-3 py-3"
            :class="cat.id === catId ? 'bg-orange-50 text-orange-600' : 'bg-[#f5f7ff] text-[#172033]'"
            @click="switchCat(cat.id)"
          >
            <span class="text-sm font-semibold">{{ cat.name }} · {{ cat.breed || '未填写品种' }}</span>
            <van-icon v-if="cat.id === catId" name="success" />
            <van-icon v-else name="arrow" color="#748094" />
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
import { DEFAULT_CAT_AVATAR, getSafeCatAvatarUrl } from '@/utils/image';
import { formatCatAge } from '@/utils/age';
import { buildVaccineStatus, normalizeVaccineList } from '@/utils/vaccines';

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

const fallbackAvatar = DEFAULT_CAT_AVATAR;

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
    return JSON.parse(raw) as {
      id?: string;
      name?: string;
      breed?: string;
      ageText?: string;
      weight?: number;
      avatarUrl?: string;
      gender?: number;
      genderText?: string;
      vaccineStatus?: string;
      medicalHistory?: string;
      neutered?: boolean;
      recentWeightText?: string;
      recentMood?: string;
      recentNote?: string;
      createdAt?: string;
      updatedAt?: string;
    };
  } catch {
    return null;
  }
});

const isShared = computed(() => route.query.mode === 'shared' || Boolean(sharedPayload.value));

const canRecordWeight = computed(() => !isShared.value && Boolean(catId.value));
const catAvatar = computed(() => getSafeCatAvatarUrl(catInfo.value.avatarUrl || sharedPayload.value?.avatarUrl));
const breedText = computed(() => catInfo.value.breed || sharedPayload.value?.breed || '猫咪档案');
const genderText = computed(() => {
  if (sharedPayload.value?.genderText) return sharedPayload.value.genderText;
  if (catInfo.value.gender === 1) return '男孩子';
  if (catInfo.value.gender === 0) return '女孩子';
  return '';
});
const ageText = computed(() => {
  if (sharedPayload.value?.ageText) {
    return sharedPayload.value.ageText;
  }
  return formatCatAge(catInfo.value.age);
});

const latestWeightText = computed(() => {
  if (sharedPayload.value?.recentWeightText) {
    return sharedPayload.value.recentWeightText;
  }
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
  return '';
});

const vaccineStatusText = computed(() =>
  buildVaccineStatus(normalizeVaccineList(catInfo.value.vaccineStatus || sharedPayload.value?.vaccineStatus)) || ''
);

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
  if (sharedPayload.value?.neutered === true) {
    return '已绝育';
  }
  if (sharedPayload.value?.neutered === false) {
    return '未绝育';
  }
  return '';
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

  if (vaccineStatusText.value) {
    events.push({
      id: 'vaccine',
      title: '疫苗状态更新',
      detail: `当前疫苗状态：${vaccineStatusText.value}`,
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
        breed: sharedPayload.value.breed || '猫咪',
        avatarUrl: getSafeCatAvatarUrl(sharedPayload.value.avatarUrl),
        gender: sharedPayload.value.gender,
        weight: sharedPayload.value.weight,
        isNeutered: sharedPayload.value.neutered,
        vaccineStatus: buildVaccineStatus(normalizeVaccineList(sharedPayload.value.vaccineStatus)),
        medicalHistory: sharedPayload.value.medicalHistory,
        createdAt: sharedPayload.value.createdAt,
        updatedAt: sharedPayload.value.updatedAt
      };
      if (sharedPayload.value.recentMood || sharedPayload.value.recentNote) {
        emotionRecords.value = [{
          id: 'shared-recent-mood',
          catId: sharedPayload.value.id || '',
          userId: '',
          audioUrl: '',
          emotionTag: sharedPayload.value.recentMood || '最近情绪',
          confidence: 0,
          emotionDescription: sharedPayload.value.recentNote || '',
          createdAt: sharedPayload.value.updatedAt || new Date().toISOString()
        }];
      }
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
    if (!newId || newId === oldId) return;
    await loadProfile();
    await loadWeight();
    await loadEmotions();
  }
);
</script>

<style scoped>
/* Warm theme overrides for CatArchive */
.cat-archive { --cv-page-bg: #fff7f0; }

/* Header */
header { background: rgba(255, 247, 240, 0.95) !important; }

/* Cards — warm background & shadow */
.bg-\[rgba\(255\,255\,255\,0\.92\)\] { background: #fff !important; }
.border-\[rgba\(226\,232\,240\,0\.92\)\] { border-color: #ede8e0 !important; }
.shadow-\[0_12px_26px_rgba\(23\,32\,51\,0\.06\)\] { box-shadow: 0 2px 14px rgba(16, 32, 51, 0.04) !important; }

/* Stats grid — warm light bg instead of cold blue */
.bg-\[\#f3f6ff\] { background: #fdfaf6 !important; }
.bg-\[\#f7f9ff\] { background: #fdfaf6 !important; }

/* Health note — warm cream */
.bg-\[\#fff6ef\] { background: #fff8f3 !important; }

/* Timeline cards */
.bg-\[\#fffdfb\] { background: #fffdf9 !important; }
.bg-\[\#fffdf9\] { background: #fffdf9 !important; }
.border-\[\#e4e8f7\] { border-color: #ede8e0 !important; }
.border-\[\#f0ece9\] { border-color: #ede8e0 !important; }
.border-\[\#efe8e2\] { border-color: #ede8e0 !important; }

/* Cards rounded unified */
.rounded-\[22px\] { border-radius: 22px; }

/* Header chip buttons */
.border-\[\#d7def7\] { border-color: #e8e4df !important; }
.bg-white { background: #fff; }

/* Emotion record border */
.border-\[\#f0ece9\] { border-color: #ede8e0 !important; }

/* Feeding button accent */
.bg-\[\#fff4ee\] { background: #fff1e8 !important; }
.border-\[\#ffd8c2\] { border-color: #ffd8c2 !important; }

/* Recommendation card */
.border-\[\#e8e4df\] { border-color: #ede8e0 !important; }

/* Weight trend area fill */
[fill="rgba(59, 130, 246, 0.12)"] { fill: rgba(255, 107, 53, 0.1) !important; }
[stroke="#3b82f6"] { stroke: #ff6b35 !important; }

/* ===== Weight Record Popup ===== */
.weight-popup {
  background: #fff;
  border-radius: 24px 24px 0 0;
  padding: 0 20px 28px;
}

.weight-popup-bar {
  width: 36px;
  height: 4px;
  border-radius: 2px;
  background: #ddd9d4;
  margin: 10px auto 16px;
}

.weight-popup-title {
  font-size: 20px;
  font-weight: 900;
  color: #102033;
  margin-bottom: 4px;
}

.weight-popup-hint {
  font-size: 13px;
  color: #7a8494;
  margin: 0 0 20px;
}

.weight-popup-input-row {
  display: flex;
  align-items: center;
  gap: 8px;
  border: 2px solid #e8e4df;
  border-radius: 18px;
  background: #fdfaf6;
  padding: 14px 18px;
  transition: border-color .15s;
}

.weight-popup-input-row:focus-within {
  border-color: #ff6b35;
  background: #fffaf5;
}

.weight-popup-input {
  flex: 1;
  min-width: 0;
  border: none;
  background: transparent;
  font-size: 36px;
  font-weight: 900;
  color: #102033;
  outline: none;
}

.weight-popup-input::placeholder {
  color: #d0c8bc;
}

.weight-popup-unit {
  font-size: 20px;
  font-weight: 700;
  color: #7a8494;
}

.weight-popup-presets {
  display: flex;
  gap: 8px;
  margin-top: 14px;
  flex-wrap: wrap;
}

.weight-preset-chip {
  height: 34px;
  border: 1.5px solid #e8e4df;
  border-radius: 999px;
  background: #fdfaf6;
  padding: 0 14px;
  font-size: 13px;
  font-weight: 600;
  color: #7a8494;
  cursor: pointer;
  transition: all .14s;
}

.weight-preset-chip.active {
  border-color: #ff6b35;
  background: #fff1e8;
  color: #ff6b35;
}

.weight-preset-chip:active {
  transform: scale(.95);
}

.weight-popup-actions {
  display: grid;
  grid-template-columns: 1fr 1.6fr;
  gap: 10px;
  margin-top: 22px;
}

.weight-popup-cancel {
  height: 48px;
  border: 1.5px solid #e8e4df;
  border-radius: 14px;
  background: #fff;
  font-size: 15px;
  font-weight: 700;
  color: #7a8494;
  cursor: pointer;
  transition: background .14s;
}

.weight-popup-cancel:active {
  background: #f5f5f3;
}

.weight-popup-save {
  height: 48px;
  border: none;
  border-radius: 14px;
  background: linear-gradient(135deg, #ff8a4c, #ff6b35);
  font-size: 15px;
  font-weight: 700;
  color: #fff;
  cursor: pointer;
  box-shadow: 0 6px 18px rgba(255, 107, 53, 0.22);
  transition: opacity .14s, transform .14s;
}

.weight-popup-save:active {
  transform: scale(.96);
}

.weight-popup-save:disabled {
  opacity: .5;
  transform: none;
}
</style>
