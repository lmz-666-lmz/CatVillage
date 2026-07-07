<template>
  <div class="feed-page">
    <!-- Header -->
    <header class="feed-header">
      <button type="button" class="feed-back" @click="router.push({ name: 'UserProfile' })">
        <van-icon name="arrow-left" size="20" />
      </button>
      <div>
        <h1 class="feed-title">投喂记录</h1>
        <p class="feed-sub">记录每日饮食，科学养护猫咪健康</p>
      </div>
    </header>

    <!-- Cat Selector -->
    <section class="cat-selector-card">
      <div class="cat-selector-header">
        <h2 class="card-section-title">当前猫咪</h2>
        <button type="button" class="switch-cat-btn" @click="showCatSheet = true">切换</button>
      </div>

      <div class="cat-cards-row">
        <button
          v-for="cat in cats"
          :key="cat.id"
          type="button"
          class="cat-mini-card"
          :class="{ active: cat.id === selectedCatId }"
          @click="selectCat(cat.id)"
        >
          <van-image :src="cat.avatarUrl || fallbackAvatar" width="56" height="56" fit="cover" round />
          <div class="cat-mini-info">
            <div class="cat-mini-name">{{ cat.name }}</div>
            <div class="cat-mini-breed">{{ cat.breed || '未知品种' }} · {{ catAge(cat.age) }}</div>
          </div>
        </button>
      </div>
    </section>

    <!-- Feeding Input -->
    <section class="form-card">
      <div class="form-field">
        <label class="form-label">猫粮品牌 / 口味</label>
        <input
          v-model="foodType"
          type="text"
          class="form-input"
          placeholder="例如：Orijen 鸡肉味"
        />
      </div>

      <div class="form-field">
        <label class="form-label">投喂量</label>
        <div class="weight-grid">
          <button
            v-for="weight in quickWeights"
            :key="weight"
            type="button"
            class="weight-chip"
            :class="{ active: selectedWeight === weight }"
            @click="pickWeight(weight)"
          >
            {{ weight === 0 ? '自定义' : `${weight}g` }}
          </button>
        </div>
        <input
          v-if="selectedWeight === 0"
          v-model="customWeight"
          type="number"
          class="form-input mt-3"
          placeholder="请输入投喂克数"
        />
      </div>
    </section>

    <!-- Weight + Recommendation -->
    <section class="form-card">
      <div class="form-field">
        <label class="form-label">今日体重 (kg)</label>
        <div class="weight-input-row">
          <input
            v-model="currentWeightInput"
            type="number"
            step="0.1"
            min="0"
            class="weight-big-input"
            placeholder="4.5"
          />
          <span class="weight-unit">kg</span>
        </div>
      </div>

      <div class="weight-tip">
        <van-icon name="info-o" />
        定期记录体重有助于监测猫咪健康状况
      </div>

      <!-- Recommendation -->
      <div class="recommend-box">
        <div class="recommend-header">
          <span class="recommend-title">按体重推荐投喂区间</span>
          <span class="recommend-badge" :class="`badge-${feedingHint.level}`">
            {{ feedingHint.label }}
          </span>
        </div>

        <div v-if="recommendedRange" class="recommend-body">
          当前体重 <strong>{{ currentWeightText }}kg</strong>，建议每日总投喂
          <strong class="text-orange">{{ recommendedRange.min }}g - {{ recommendedRange.max }}g</strong>
        </div>
        <div v-else class="recommend-body">
          暂无体重数据，记录体重后可自动生成推荐区间
        </div>

        <div class="recommend-stats">
          <div>
            <div class="stats-label">今日累计</div>
            <div class="stats-value">{{ todayTotalFeed }}g</div>
          </div>
          <div class="stats-hint">{{ feedingHint.tip }}</div>
        </div>

        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: `${feedingProgress}%` }"></div>
        </div>
      </div>
    </section>

    <!-- Save Button -->
    <button
      type="button"
      class="save-btn"
      :disabled="submitting"
      @click="submitRecord"
    >
      {{ submitting ? '保存中...' : '保存投喂记录' }}
    </button>

    <!-- Daily Stats -->
    <section class="data-card">
      <div class="data-card-header">
        <h2 class="card-section-title">每日投喂统计</h2>
        <span class="data-card-badge">最近 7 天</span>
      </div>

      <div v-if="dailyFeedStats.length === 0" class="empty-text">暂无统计数据</div>

      <div v-else class="data-list">
        <div v-for="row in dailyFeedStats" :key="row.dateKey" class="data-row">
          <div>
            <div class="data-row-title">{{ row.dateLabel }}</div>
            <div class="data-row-sub">{{ row.count }} 次投喂</div>
          </div>
          <div class="data-row-right">
            <div class="data-row-value">{{ row.totalWeight.toFixed(0) }}g</div>
            <div class="data-row-sub">最近：{{ row.lastTime }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Recent Records -->
    <section class="data-card">
      <div class="data-card-header">
        <h2 class="card-section-title">最近投喂记录</h2>
        <span class="data-card-badge">{{ feedRecords.length }} 条</span>
      </div>

      <div v-if="loadingRecords" class="loading-state">
        <van-loading size="22" color="#ff6b35" />
      </div>
      <div v-else-if="feedRecords.length === 0" class="empty-text">还没有投喂记录</div>
      <div v-else class="data-list">
        <div v-for="row in feedRecords" :key="row.id" class="data-row">
          <div class="min-w-0">
            <div class="data-row-title truncate">{{ row.foodType }}</div>
            <div class="data-row-sub">{{ formatTime(row.feedingTime) }}</div>
          </div>
          <div class="data-row-value">{{ Number(row.foodWeight).toFixed(0) }}g</div>
        </div>
      </div>
    </section>

    <!-- Cat Switcher Sheet -->
    <van-action-sheet v-model:show="showCatSheet" title="切换猫咪">
      <div class="sheet-body">
        <button
          v-for="cat in cats"
          :key="cat.id"
          type="button"
          class="sheet-item"
          :class="{ active: cat.id === selectedCatId }"
          @click="selectCat(cat.id); showCatSheet = false"
        >
          <span class="sheet-item-name">{{ cat.name }} · {{ cat.breed || '未填写品种' }}</span>
          <van-icon v-if="cat.id === selectedCatId" name="success" size="18" color="#ff6b35" />
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
  if (currentWeightKg.value === null) return '暂无';
  return currentWeightKg.value.toFixed(1);
});

const todayTotalFeed = computed(() => {
  const today = new Date();
  const y = today.getFullYear();
  const m = today.getMonth();
  const d = today.getDate();
  return feedRecords.value.reduce((sum, row) => {
    const time = new Date(row.feedingTime);
    if (Number.isNaN(time.getTime())) return sum;
    if (time.getFullYear() === y && time.getMonth() === m && time.getDate() === d)
      return sum + Number(row.foodWeight || 0);
    return sum;
  }, 0);
});

const recommendedRange = computed(() => {
  if (currentWeightKg.value === null) return null;
  const min = Math.round(currentWeightKg.value * 45);
  const max = Math.round(currentWeightKg.value * 55);
  return { min, max };
});

const feedingHint = computed(() => {
  if (!recommendedRange.value) return { level: 'unknown' as const, label: '待评估', tip: '先记录体重' };
  if (todayTotalFeed.value < recommendedRange.value.min)
    return { level: 'low' as const, label: '偏低', tip: `还差 ${Math.max(recommendedRange.value.min - todayTotalFeed.value, 0).toFixed(0)}g` };
  if (todayTotalFeed.value > recommendedRange.value.max)
    return { level: 'high' as const, label: '偏高', tip: `超出 ${Math.max(todayTotalFeed.value - recommendedRange.value.max, 0).toFixed(0)}g` };
  return { level: 'ok' as const, label: '达标', tip: '维持当前节奏' };
});

const feedingProgress = computed(() => {
  if (!recommendedRange.value || recommendedRange.value.max <= 0) return 0;
  const raw = (todayTotalFeed.value / recommendedRange.value.max) * 100;
  return Math.max(0, Math.min(100, raw));
});

type DailyFeedStat = { dateKey: string; dateLabel: string; totalWeight: number; count: number; lastTime: string };
const dailyFeedStats = computed<DailyFeedStat[]>(() => {
  const grouped = new Map<string, DailyFeedStat>();
  feedRecords.value.forEach((row) => {
    const time = new Date(row.feedingTime);
    if (Number.isNaN(time.getTime())) return;
    const key = `${time.getFullYear()}-${String(time.getMonth() + 1).padStart(2, '0')}-${String(time.getDate()).padStart(2, '0')}`;
    const existed = grouped.get(key);
    if (!existed) {
      grouped.set(key, { dateKey: key, dateLabel: formatDateLabel(time), totalWeight: Number(row.foodWeight || 0), count: 1, lastTime: formatClock(time) });
      return;
    }
    existed.totalWeight += Number(row.foodWeight || 0);
    existed.count += 1;
    if (formatClock(time) > existed.lastTime) existed.lastTime = formatClock(time);
  });
  return Array.from(grouped.values()).sort((a, b) => (a.dateKey > b.dateKey ? -1 : 1)).slice(0, 7);
});

const selectedCatId = computed(() => {
  const routeCatId = typeof route.query.catId === 'string' ? route.query.catId : '';
  return routeCatId || currentCatStore.getCurrentCatId || catsStore.getAllCats[0]?.id || '';
});
const cats = computed(() => catsStore.getAllCats);

const catAge = (age?: number) => {
  if (!age || age <= 0) return '未知年龄';
  if (age < 12) return `${age} 个月`;
  return `${Math.floor(age / 12)} 岁`;
};

const pickWeight = (value: number) => {
  selectedWeight.value = value;
  if (value !== 0) customWeight.value = '';
};

const selectCat = (catId: string) => {
  currentCatStore.setCurrentCat(catId);
  router.replace({ name: 'FeedRecord', query: { catId } });
};

const getSelectedWeight = () => {
  if (selectedWeight.value !== 0) return selectedWeight.value;
  const custom = Number(customWeight.value);
  return Number.isFinite(custom) && custom > 0 ? custom : 0;
};

const loadCurrentWeight = async () => {
  if (!selectedCatId.value) { currentWeightKg.value = null; currentWeightInput.value = ''; return; }
  try {
    const res = await getWeightRecords({ petId: selectedCatId.value, page: 1, pageSize: 1 });
    const row = res.data.list[0];
    currentWeightKg.value = row ? Number(row.weight) : null;
    currentWeightInput.value = row ? Number(row.weight).toFixed(1) : '';
  } catch { currentWeightKg.value = null; currentWeightInput.value = ''; }
};

const loadFeedingRecords = async () => {
  if (!selectedCatId.value) { feedRecords.value = []; return; }
  loadingRecords.value = true;
  try {
    const res = await getFeedingRecords({ petId: selectedCatId.value, page: 1, pageSize: 20 });
    feedRecords.value = res.data.list || [];
  } catch { feedRecords.value = []; }
  finally { loadingRecords.value = false; }
};

const submitRecord = async () => {
  const catId = selectedCatId.value;
  if (!catId) { showToast({ type: 'fail', message: '请先添加并选择猫咪' }); return; }
  if (!foodType.value.trim()) { showToast({ type: 'fail', message: '请输入猫粮品牌或口味' }); return; }
  const weight = getSelectedWeight();
  if (weight <= 0) { showToast({ type: 'fail', message: '请输入正确投喂量' }); return; }
  const editedWeight = Number(currentWeightInput.value);
  const hasEditedWeight = Number.isFinite(editedWeight) && editedWeight > 0;

  submitting.value = true;
  try {
    const res = await createFeedingRecord({ petId: catId, foodType: foodType.value.trim(), foodWeight: weight });
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
  } catch { showToast({ type: 'fail', message: '保存失败，请稍后再试' }); }
  finally { submitting.value = false; }
};

const formatTime = (value: string) => {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  const y = date.getFullYear(); const m = String(date.getMonth() + 1).padStart(2, '0');
  const d = String(date.getDate()).padStart(2, '0');
  const hh = String(date.getHours()).padStart(2, '0'); const mm = String(date.getMinutes()).padStart(2, '0');
  return `${y}-${m}-${d} ${hh}:${mm}`;
};

const formatClock = (value: Date) => `${String(value.getHours()).padStart(2, '0')}:${String(value.getMinutes()).padStart(2, '0')}`;

const formatDateLabel = (value: Date) => {
  const today = new Date();
  if (value.getFullYear() === today.getFullYear() && value.getMonth() === today.getMonth() && value.getDate() === today.getDate()) return '今天';
  const yesterday = new Date(); yesterday.setDate(today.getDate() - 1);
  if (value.getFullYear() === yesterday.getFullYear() && value.getMonth() === yesterday.getMonth() && value.getDate() === yesterday.getDate()) return '昨天';
  return `${value.getMonth() + 1}月${value.getDate()}日`;
};

onMounted(async () => { await catsStore.fetchAllCats(); await loadCurrentWeight(); await loadFeedingRecords(); });
watch(() => selectedCatId.value, async (n, o) => { if (!n || n === o) return; await loadCurrentWeight(); await loadFeedingRecords(); });
</script>

<style scoped>
.feed-page { min-height: 100dvh; padding: 0 16px 24px; background: #fff7f0; }

/* Header */
.feed-header { display: flex; align-items: flex-start; gap: 12px; padding: 14px 0 8px; }
.feed-back { width: 38px; height: 38px; flex-shrink: 0; border: none; border-radius: 14px; background: #fff; display: grid; place-items: center; color: #ff6b35; cursor: pointer; box-shadow: 0 2px 8px rgba(16,32,51,0.06); }
.feed-back:active { transform: scale(.93); }
.feed-title { margin: 0; font-size: 22px; font-weight: 900; color: #102033; }
.feed-sub { margin: 2px 0 0; font-size: 12px; font-weight: 600; color: #7a8494; }

/* Cat Selector */
.cat-selector-card { margin-top: 12px; border-radius: 22px; background: #fff; padding: 16px 18px; box-shadow: 0 2px 12px rgba(16,32,51,0.04); }
.cat-selector-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.switch-cat-btn { border: none; background: none; font-size: 13px; font-weight: 700; color: #ff6b35; cursor: pointer; }
.cat-cards-row { display: flex; gap: 10px; overflow-x: auto; padding-bottom: 4px; }
.cat-mini-card { display: flex; align-items: center; gap: 10px; min-width: 210px; border: 2px solid transparent; border-radius: 16px; background: #fdfaf6; padding: 10px 12px; cursor: pointer; transition: border-color .14s; }
.cat-mini-card.active { border-color: #ff6b35; background: #fff8f3; }
.cat-mini-name { font-size: 15px; font-weight: 800; color: #102033; }
.cat-mini-breed { font-size: 12px; color: #7a8494; }
.cat-mini-info { min-width: 0; }

/* Form Card */
.form-card { margin-top: 14px; border-radius: 22px; background: #fff; padding: 18px; box-shadow: 0 2px 12px rgba(16,32,51,0.04); }
.form-field + .form-field { margin-top: 18px; }
.form-label { display: block; margin-bottom: 8px; font-size: 15px; font-weight: 700; color: #102033; }
.form-input { width: 100%; height: 46px; box-sizing: border-box; border: 1.5px solid #e8e4df; border-radius: 14px; background: #fdfaf6; padding: 0 14px; font-size: 15px; color: #102033; outline: none; transition: border-color .14s; }
.form-input:focus { border-color: #ff6b35; background: #fffaf5; }
.form-input::placeholder { color: #b0b8c4; }

/* Weight Grid */
.weight-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
.weight-chip { height: 42px; border: 2px solid #e8e4df; border-radius: 13px; background: #fdfaf6; font-size: 14px; font-weight: 700; color: #7a8494; cursor: pointer; transition: all .14s; }
.weight-chip.active { border-color: #ff6b35; background: #fff1e8; color: #ff6b35; }
.weight-chip:active { transform: scale(.96); }

/* Weight Input Row */
.weight-input-row { display: flex; align-items: center; gap: 10px; border: 1.5px solid #e8e4df; border-radius: 14px; background: #fdfaf6; padding: 8px 14px; transition: border-color .14s; }
.weight-input-row:focus-within { border-color: #ff6b35; background: #fffaf5; }
.weight-big-input { flex: 1; min-width: 0; border: none; background: transparent; font-size: 28px; font-weight: 800; color: #102033; outline: none; }
.weight-big-input::placeholder { color: #c0b8ac; }
.weight-unit { font-size: 18px; font-weight: 700; color: #7a8494; }

/* Weight Tip */
.weight-tip { margin-top: 10px; display: flex; align-items: center; gap: 6px; border-radius: 12px; background: #fff8f3; padding: 10px 12px; font-size: 12px; font-weight: 500; color: #b85a30; }

/* Recommend Box */
.recommend-box { margin-top: 14px; border-radius: 16px; background: #fdfaf6; padding: 14px 16px; }
.recommend-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.recommend-title { font-size: 14px; font-weight: 700; color: #102033; }
.recommend-badge { border-radius: 999px; padding: 3px 10px; font-size: 11px; font-weight: 700; }
.badge-ok { background: #ecfdf5; color: #0f8a44; }
.badge-low { background: #eff6ff; color: #2563eb; }
.badge-high { background: #ffe8e4; color: #c13b1f; }
.badge-unknown { background: #f1f3f6; color: #7a8494; }
.recommend-body { font-size: 13px; color: #7a8494; line-height: 1.6; }
.recommend-body strong { color: #102033; }
.text-orange { color: #ff6b35 !important; }
.recommend-stats { display: flex; align-items: flex-end; justify-content: space-between; margin-top: 12px; }
.stats-label { font-size: 11px; color: #7a8494; }
.stats-value { font-size: 26px; font-weight: 900; color: #102033; }
.stats-hint { font-size: 12px; color: #7a8494; }
.progress-bar { margin-top: 8px; height: 6px; border-radius: 3px; background: #ede8e0; overflow: hidden; }
.progress-fill { height: 100%; border-radius: 3px; background: linear-gradient(90deg, #ff8a4c, #ff6b35); transition: width .3s ease; }

/* Save Button */
.save-btn { display: block; width: 100%; height: 52px; margin-top: 20px; border: none; border-radius: 16px; background: linear-gradient(135deg, #ff8a4c, #ff6b35); font-size: 16px; font-weight: 800; color: #fff; cursor: pointer; box-shadow: 0 8px 22px rgba(255,107,53,0.24); transition: opacity .14s, transform .14s; }
.save-btn:active { transform: scale(.97); }
.save-btn:disabled { opacity: .5; transform: none; }

/* Data Card */
.data-card { margin-top: 14px; border-radius: 22px; background: #fff; padding: 18px; box-shadow: 0 2px 12px rgba(16,32,51,0.04); }
.data-card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.card-section-title { margin: 0; font-size: 17px; font-weight: 800; color: #102033; }
.data-card-badge { font-size: 11px; font-weight: 600; color: #7a8494; background: #f1f3f6; padding: 3px 10px; border-radius: 999px; }
.empty-text { padding: 32px 0; text-align: center; font-size: 14px; color: #7a8494; }
.loading-state { padding: 32px 0; text-align: center; }

/* Data List */
.data-list { display: flex; flex-direction: column; gap: 8px; }
.data-row { display: flex; align-items: center; justify-content: space-between; border-radius: 14px; background: #fdfaf6; padding: 12px 14px; }
.data-row-title { font-size: 15px; font-weight: 700; color: #102033; }
.data-row-sub { font-size: 12px; color: #7a8494; margin-top: 2px; }
.data-row-right { text-align: right; }
.data-row-value { font-size: 20px; font-weight: 800; color: #ff6b35; }

/* Sheet */
.sheet-body { padding: 8px 16px 20px; display: flex; flex-direction: column; gap: 8px; }
.sheet-item { display: flex; align-items: center; justify-content: space-between; padding: 14px 16px; border-radius: 14px; border: none; background: #f5f7fb; cursor: pointer; width: 100%; text-align: left; font-size: 14px; font-weight: 600; color: #102033; }
.sheet-item.active { background: #fff1e8; color: #ff6b35; }
.sheet-item-name { flex: 1; }
</style>
