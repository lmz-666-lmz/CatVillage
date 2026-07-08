<template>
  <div class="ai-page">
    <AppTopBar title="AI 养育助手" subtitle="结合档案、疫苗与喵喵台记录给出建议" kicker="AI 养育">
      <template #actions>
        <button v-if="selectedCat && hasChatHistory" class="topbar-action ai-clear-btn" type="button" @click="handleClearHistory">清空</button>
      </template>
    </AppTopBar>

    <main class="ai-main">
      <!-- Pet Info Card -->
      <section v-if="selectedCat" class="ai-pet-card" :class="{ expanded: petCardExpanded }">
        <button type="button" class="ai-pet-card-btn" @click="petCardExpanded = !petCardExpanded">
          <div class="ai-pet-left">
            <div class="ai-pet-avatar-ring">
              <img :src="petInfo.avatar" width="44" height="44" class="ai-pet-avatar" @error="handleImageError($event, defaultAvatar)" />
            </div>
            <div class="ai-pet-info">
              <div class="ai-pet-name-row">
                <span class="ai-pet-name">{{ petInfo.name }}</span>
                <span class="ai-pet-tag">{{ petInfo.breed }}</span>
              </div>
              <div class="ai-pet-status">{{ petInfo.age }} · {{ petInfo.weight }}</div>
              <div class="ai-pet-mini-chips">
                <span>{{ vaccineBrief }}</span>
                <span>{{ selectedCat.isNeutered ? '已绝育' : '未绝育' }}</span>
              </div>
            </div>
          </div>
          <div class="ai-pet-score" :aria-label="petCardExpanded ? '收起猫咪档案' : '展开猫咪档案'">
            <span class="ai-pet-score-num">{{ petCardExpanded ? '收起' : '展开' }}</span>
            <van-icon :name="petCardExpanded ? 'arrow-up' : 'arrow-down'" size="14" />
          </div>
        </button>
        <div v-if="petCardExpanded" class="ai-pet-detail">
          <div v-for="item in petDetailChips" :key="item.label" class="ai-health-chip" :class="item.tone">
            <span class="ai-health-icon">{{ item.icon }}</span>
            <div>
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
            </div>
          </div>

          <div v-if="vaccineItems.length" class="ai-vaccine-list">
            <span v-for="item in visibleVaccineItems" :key="item">{{ item }}</span>
            <span v-if="hiddenVaccineCount > 0">+{{ hiddenVaccineCount }}</span>
          </div>

          <div class="ai-reference-card">
            <div class="ai-reference-title">
              <span>🎧</span>
              <strong>AI 参考信息</strong>
            </div>
            <p>{{ emotionReferenceText }}</p>
            <small>AI 会结合年龄、体重、疫苗、健康记录和喵喵台情绪给出建议</small>
          </div>
        </div>
        <div v-if="petCardExpanded" class="ai-pet-actions">
          <button type="button" class="ai-pet-action" @click="openCatSwitcher">
            <van-icon name="exchange" size="16" /> 切换猫咪
          </button>
          <button type="button" class="ai-pet-action accent" @click="openCatArchive">
            详细报告 <van-icon name="arrow" size="14" />
          </button>
        </div>
      </section>

      <!-- No cat empty state -->
      <section v-else class="ai-empty">
        <div class="ai-empty-illustration">
          <span class="ai-empty-emoji">🐱</span>
          <div class="ai-empty-paws"><span>🐾</span><span>🐾</span><span>🐾</span></div>
        </div>
        <h2 class="ai-empty-title">还没有猫咪伙伴</h2>
        <p class="ai-empty-desc">先添加一只猫咪，AI 才能结合档案、年龄、疫苗和喵喵台记录给出养育建议。</p>
        <button class="ai-empty-btn" @click="router.push({ name: 'AddCat' })">
          <van-icon name="plus" size="18" /> 添加猫咪伙伴
        </button>
      </section>

      <!-- Chat Area (hidden when no cat) -->
      <section v-if="selectedCat" ref="chatScrollRef" class="ai-chat">
        <template v-for="msg in messages" :key="msg.id">
          <!-- AI message -->
          <div v-if="msg.role !== 'user'" class="ai-msg ai-msg--bot">
            <div class="ai-msg-avatar bot">
              <van-icon name="service" size="20" />
            </div>
            <div class="ai-msg-bubble-wrap">
              <div v-if="msg.type === 'consult_card'" class="ai-bubble ai-bubble--consult">
                <div class="ai-bubble-tag-row">
                  <span class="ai-bubble-tag">养猫问答</span>
                  <span class="ai-bubble-tag-sub">已准备好</span>
                </div>
                <p class="ai-bubble-text">{{ msg.content }}</p>
                <button type="button" class="ai-bubble-cta" @click="focusConsultInput">去下方输入咨询</button>
              </div>
              <div v-else class="ai-bubble ai-bubble--analysis">
                <div class="ai-bubble-tag-row">
                  <span class="ai-bubble-tag analysis">照护建议</span>
                  <span class="ai-bubble-tag-sub">结构化建议</span>
                </div>
                <div class="ai-sections">
                  <div v-for="(section, i) in buildAssistantSections(msg.content)" :key="`${msg.id}-${i}`" class="ai-section">
                    <h4 class="ai-section-title">{{ section.title }}</h4>
                    <p class="ai-section-text" v-html="highlightKeywords(section.content)" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- User message -->
          <div v-else class="ai-msg ai-msg--user">
            <div class="ai-msg-bubble user">{{ msg.content }}</div>
            <div class="ai-msg-avatar user">
              <van-icon name="contact" size="20" />
            </div>
          </div>
        </template>

        <!-- Thinking indicator -->
        <div v-if="sending" class="ai-msg ai-msg--bot">
          <div class="ai-msg-avatar bot">
            <van-icon name="service" size="20" />
          </div>
          <div class="ai-bubble ai-bubble--thinking">正在整理建议...</div>
        </div>
      </section>

    </main>

    <!-- Bottom Input (hidden when no cat) -->
    <div v-if="selectedCat" class="ai-input-bar">
      <section class="ai-chip-row">
        <button v-for="(item, idx) in actionCards" :key="idx" class="ai-chip" type="button" @click="handleActionClick(item)">
          <van-icon :name="item.icon" size="15" />
          {{ item.name }}
        </button>
      </section>
      <div class="ai-input-wrap">
        <van-icon name="volume-o" size="22" class="ai-input-icon" />
        <input ref="consultInputRef" v-model="inputText" type="text" class="ai-input" placeholder="输入养护问题..." @keyup.enter="handleSend" />
        <button class="ai-send-btn" :disabled="sending || !inputText.trim()" @click="handleSend">发送</button>
      </div>
    </div>

    <!-- Cat Switcher Sheet -->
    <van-action-sheet v-model:show="showCatSheet" title="切换猫咪" :round="true">
      <div class="sheet-body">
        <p class="sheet-hint">选择后将同步切换当前咨询的猫咪</p>
        <div class="sheet-list">
          <button v-for="cat in cats" :key="cat.id" type="button" class="sheet-item" :class="{ active: cat.id === selectedCat?.id }" @click="selectCat(cat.id)">
            <span class="sheet-item-name">{{ cat.name }}</span>
            <span class="sheet-item-breed">{{ cat.breed || '未填写品种' }}</span>
            <van-icon v-if="cat.id === selectedCat?.id" name="success" size="18" />
            <span v-else class="sheet-item-radio" />
          </button>
        </div>
      </div>
    </van-action-sheet>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, nextTick, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';
import AppTopBar from '@/components/AppTopBar.vue';
import { useAIAssistant } from '@/composables/useAIAssistant';
import { useHealthScore } from '@/composables/useHealthScore';
import { useCatsStore, useCurrentCatStore } from '@/stores';
import { DEFAULT_CAT_AVATAR, getSafeImageUrl, handleImageError } from '@/utils/image';
import { formatCatAge } from '@/utils/age';

const router = useRouter();
const catsStore = useCatsStore();
const currentCatStore = useCurrentCatStore();
const { sendMessageToAI, fetchChatHistory, clearCurrentSession, getCurrentChatHistory, isLoading } = useAIAssistant();
const { healthInfo, fetchHealthData, calculateScore } = useHealthScore();

interface ChatItem { id: string; role: 'user' | 'assistant'; content: string; type?: 'default' | 'consult_card'; }

const inputText = ref('');
const consultInputRef = ref<HTMLInputElement | null>(null);
const chatScrollRef = ref<HTMLElement | null>(null);
const showCatSheet = ref(false);
const petCardExpanded = ref(false);
const lastEmotionRefCount = ref(0);
const sending = computed(() => isLoading.value);
const defaultAvatar = DEFAULT_CAT_AVATAR;
const messages = ref<ChatItem[]>([]);
const welcomeMessage: ChatItem[] = [{ id: 'welcome-1', role: 'assistant', content: '你好，我会结合猫咪档案给你一些日常养护建议。有什么想问的吗？' }];

const selectedCat = computed(() => {
  const currentId = currentCatStore.getCurrentCatId;
  const current = currentId ? catsStore.getCatById(currentId) : null;
  return current || catsStore.getAllCats[0] || null;
});
const petInfo = computed(() => ({
  avatar: getSafeImageUrl(selectedCat.value?.avatarUrl, defaultAvatar),
  name: selectedCat.value?.name || '未选择猫咪',
  breed: selectedCat.value?.breed || '猫咪',
  age: formatCatAge(selectedCat.value?.age),
  weight: selectedCat.value?.weight ? `${selectedCat.value.weight}kg` : '体重未知',
  status: healthInfo.value.status,
  score: healthInfo.value.score
}));
const cats = computed(() => catsStore.getAllCats);
const hasChatHistory = computed(() => selectedCat.value && messages.value.some((item) => item.id !== 'welcome-1'));
const vaccineBrief = computed(() => {
  return vaccineItems.value.length ? '已登记疫苗' : '暂无疫苗';
});
const vaccineItems = computed(() => {
  const raw = String(selectedCat.value?.vaccineStatus || '').trim();
  if (!raw) return [];
  const items = raw
    .split(/[、,，;；\n\r]+/)
    .map((item) => item.trim())
    .filter(Boolean);
  return Array.from(new Set(items));
});
const vaccineDetail = computed(() => {
  return vaccineItems.value.length ? `已登记 ${vaccineItems.value.length} 项` : '暂无疫苗';
});
const visibleVaccineItems = computed(() => vaccineItems.value.slice(0, 3));
const hiddenVaccineCount = computed(() => Math.max(0, vaccineItems.value.length - visibleVaccineItems.value.length));
const emotionReferenceText = computed(() =>
  lastEmotionRefCount.value > 0
    ? `已参考最近 ${lastEmotionRefCount.value} 条喵喵台记录`
    : '还没有喵喵台记录，上传一次猫叫后 AI 建议会更准确'
);
const petDetailChips = computed(() => [
  { icon: '💚', label: '健康状态', value: petInfo.value.status, tone: 'mint' },
  { icon: '⭐', label: '健康分', value: `${petInfo.value.score}`, tone: 'warm' },
  { icon: '🛡', label: '疫苗状态', value: vaccineDetail.value, tone: 'blue' },
  { icon: '🐾', label: '绝育状态', value: selectedCat.value?.isNeutered ? '已绝育' : '未绝育', tone: 'soft' }
]);

const actionCards = ref([
  { name: '养猫问答', icon: 'shop-o', iconClass: 'orange' },
  { name: '异常预警', icon: 'warning', iconClass: 'rose' },
  { name: '专业医生', icon: 'plus', iconClass: 'blue' },
  { name: '健康报告', icon: 'notes-o', iconClass: 'red' },
]);

const scrollChatToBottom = async () => {
  await nextTick();
  const el = chatScrollRef.value;
  if (el) {
    el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' });
  }
};

const handleActionClick = (item: any) => {
  if (item.name === '异常预警') void runWarningCheck();
  else if (item.name === '健康报告') void runHealthReport();
  else if (item.name === '专业医生') router.push({ name: 'ProfessionalDoctors' });
  else if (item.name === '养猫问答') { pushConsultCard(); focusConsultInput(); }
  else showToast('该功能正在开发中');
};

const buildWarningPrompt = () => {
  const cat = selectedCat.value;
  const emotionHint = lastEmotionRefCount.value > 0
    ? `最近喵喵台记录：已参考 ${lastEmotionRefCount.value} 条。`
    : '最近喵喵台记录：目前缺少喵喵台记录，建议上传一次猫叫后再综合判断。';
  return [
    '请基于以下猫咪资料做一次异常预警，回答务必简短、说重点。',
    '请按这四段输出：当前状态判断、需要注意的2-4个点、建议立即做什么、是否建议就医。',
    `猫名：${cat?.name || '未填写'}`,
    `品种：${cat?.breed || '未填写'}`,
    `年龄：${formatCatAge(cat?.age) || '未知'}`,
    `体重：${cat?.weight ? `${cat.weight}kg` : '未知'}`,
    `性别：${(cat as any)?.gender || (cat as any)?.sex || '未知'}`,
    `绝育：${cat?.isNeutered ? '已绝育' : '未绝育'}`,
    `疫苗：${vaccineItems.value.length ? vaccineItems.value.join('、') : '暂无疫苗登记'}`,
    `健康状态：${petInfo.value.status}，健康分：${petInfo.value.score}`,
    emotionHint
  ].join('\n');
};

const runWarningCheck = async () => {
  const catId = selectedCat.value?.id;
  if (!catId) { showToast('请先添加猫咪后再使用'); return; }
  messages.value.push({ id: `u-warning-${Date.now()}`, role: 'user', content: '请帮我做一次异常预警' });
  void scrollChatToBottom();
  try {
    const result = await sendMessageToAI({ catId, message: buildWarningPrompt() });
    messages.value.push({ id: result.id || `a-warning-${Date.now()}`, role: 'assistant', content: result.message });
    if (typeof result.emotionRecordsCount === 'number') lastEmotionRefCount.value = result.emotionRecordsCount;
  } catch (err: any) {
    const msg = String(err?.message || '');
    const friendly = /key|configured|503|AI assistant/i.test(msg) ? '异常预警服务暂未配置，当前功能待完善。' : '异常预警生成失败，请稍后重试。';
    messages.value.push({ id: `a-warning-fail-${Date.now()}`, role: 'assistant', content: friendly });
    showToast(friendly);
  } finally {
    void scrollChatToBottom();
  }
};

const buildHealthReportPrompt = () => {
  const cat = selectedCat.value;
  const emotionHint = lastEmotionRefCount.value > 0
    ? `最近喵喵台记录：已参考 ${lastEmotionRefCount.value} 条。`
    : '最近喵喵台记录：暂无可参考记录。';
  return [
    '请基于以下猫咪资料生成一份简洁健康报告，语气温和，重点清晰。',
    '请按这四段输出：健康概览、档案重点、养护建议、下次关注。',
    `猫名：${cat?.name || '未填写'}`,
    `品种：${cat?.breed || '未填写'}`,
    `年龄：${formatCatAge(cat?.age) || '未知'}`,
    `体重：${cat?.weight ? `${cat.weight}kg` : '未知'}`,
    `性别：${(cat as any)?.gender || (cat as any)?.sex || '未知'}`,
    `绝育：${cat?.isNeutered ? '已绝育' : '未绝育'}`,
    `疫苗：${vaccineItems.value.length ? vaccineItems.value.join('、') : '暂无疫苗登记'}`,
    `健康状态：${petInfo.value.status}，健康分：${petInfo.value.score}`,
    emotionHint
  ].join('\n');
};

const runHealthReport = async () => {
  const catId = selectedCat.value?.id;
  if (!catId) { showToast('请先添加猫咪后再使用'); return; }
  messages.value.push({ id: `u-report-${Date.now()}`, role: 'user', content: '请生成一份健康报告' });
  void scrollChatToBottom();
  try {
    const result = await sendMessageToAI({ catId, message: buildHealthReportPrompt() });
    messages.value.push({ id: result.id || `a-report-${Date.now()}`, role: 'assistant', content: result.message });
    if (typeof result.emotionRecordsCount === 'number') lastEmotionRefCount.value = result.emotionRecordsCount;
  } catch (err: any) {
    const msg = String(err?.message || '');
    const friendly = /key|configured|503|AI assistant/i.test(msg) ? '健康报告服务暂未配置，当前功能待完善。' : '健康报告生成失败，请稍后重试。';
    messages.value.push({ id: `a-report-fail-${Date.now()}`, role: 'assistant', content: friendly });
    showToast(friendly);
  } finally {
    void scrollChatToBottom();
  }
};
const pushConsultCard = () => {
  messages.value.push({ id: `consult-${Date.now()}`, role: 'assistant', type: 'consult_card', content: '你可以直接输入：例如"2岁猫咪一周喂几次罐头？""最近掉毛多该怎么护理？""主食和零食比例怎么配？"' });
  void scrollChatToBottom();
};
const openCatArchive = () => { if (!selectedCat.value) { showToast('请先添加猫咪后再使用'); return; } router.push({ name: 'CatArchive', params: { id: selectedCat.value.id } }); };
const openCatSwitcher = () => { if (cats.value.length === 0) { showToast('请先添加猫咪后再使用'); return; } showCatSheet.value = true; };
const selectCat = (catId: string) => { currentCatStore.setCurrentCat(catId); showCatSheet.value = false; };
const focusConsultInput = async () => { await scrollChatToBottom(); consultInputRef.value?.focus(); };

const handleSend = async () => {
  const message = inputText.value.trim();
  if (!message) return;
  const catId = selectedCat.value?.id;
  if (!catId) { showToast('请先添加猫咪后再使用'); return; }
  messages.value.push({ id: `u-${Date.now()}`, role: 'user', content: message }); inputText.value = '';
  void scrollChatToBottom();
  try {
    const result = await sendMessageToAI({ catId, message });
    messages.value.push({ id: result.id || `a-${Date.now()}`, role: 'assistant', content: result.message });
    if (typeof result.emotionRecordsCount === 'number') lastEmotionRefCount.value = result.emotionRecordsCount;
    void scrollChatToBottom();
  } catch (err: any) {
    const msg = String(err?.message || '');
    const friendly = /key|configured|503|AI assistant/i.test(msg) ? '养护问答服务暂未配置，当前功能待完善。' : '网络有点忙，请稍后重试。';
    messages.value.push({ id: `a-fail-${Date.now()}`, role: 'assistant', content: friendly }); showToast(friendly);
    void scrollChatToBottom();
  }
};
const handleClearHistory = async () => {
  const catId = selectedCat.value?.id;
  if (!catId) { showToast('暂无可清空的历史'); return; }
  try {
    await clearCurrentSession(catId);
    inputText.value = '';
    lastEmotionRefCount.value = 0;
    messages.value = welcomeMessage.map(item => ({ ...item }));
    await fetchChatHistory({ catId, page: 1, pageSize: 1 });
    await nextTick();
    const el = chatScrollRef.value;
    if (el) el.scrollTo({ top: 0, behavior: 'auto' });
    showToast('历史已清空');
  } catch {
    showToast('清空失败，请稍后再试');
  }
};
const loadHistory = async () => {
  const catId = selectedCat.value?.id;
  if (!catId) { messages.value = welcomeMessage.map(item => ({ ...item })); return; }
  try {
    await fetchChatHistory({ catId, page: 1, pageSize: 20 });
    const history = [...getCurrentChatHistory.value].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()).map(i => ({ id: i.id, role: i.role, content: i.message }));
    messages.value = history.length > 0 ? history : welcomeMessage.map(item => ({ ...item }));
  } catch { messages.value = welcomeMessage.map(item => ({ ...item })); }
  await scrollChatToBottom();
};

const refreshHealthScore = async () => {
  const cat = selectedCat.value;
  if (!cat?.id) {
    healthInfo.value = { score: 0, status: '无数据' };
    return;
  }
  const data = await fetchHealthData(cat.id);
  if (data) {
    healthInfo.value = calculateScore(cat, data.warningCounts, data.hasWeightRecords, data.hasFeedingRecords);
  } else {
    // API 请求失败时，仅用档案数据计算
    healthInfo.value = calculateScore(cat, { high: 0, medium: 0, low: 0 }, false, false);
  }
};

onMounted(async () => {
  currentCatStore.loadCurrentCat(); await catsStore.fetchAllCats(true);
  if (!currentCatStore.getCurrentCatId && catsStore.getAllCats[0]?.id) currentCatStore.setCurrentCat(catsStore.getAllCats[0].id);
  await loadHistory();
  await refreshHealthScore();
});
watch(() => selectedCat.value?.id, async (n, o) => {
  if (n && n !== o) {
    await loadHistory();
    await refreshHealthScore();
  }
});

const normalizeAssistantText = (c: string) => c.replace(/[\*#>`~\[\]\(\)_|]/g, ' ').replace(/(^|\n)\s*[-+•]\s*/g, '$1').replace(/\s{2,}/g, ' ').replace(/\n{3,}/g, '\n\n').trim();
const escapeHtml = (r: string) => r.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
const highlightKeywords = (t: string) => escapeHtml(t).replace(/(建议|风险|警惕|立即|尽快|就医|观察|下一步|异常|重点)/g, '<span class="ai-kw">$1</span>');
const buildAssistantSections = (content: string) => {
  const lines = normalizeAssistantText(content).split('\n').map(l => l.trim()).filter(Boolean);
  const reg = /^(建议|风险|下一步|处理方式|观察重点|结论|提示|就医建议|异常预警)[：:]\s*(.*)$/;
  const sections: { title: string; content: string }[] = []; let cur: { title: string; content: string } | null = null;
  lines.forEach(line => {
    const m = line.match(reg);
    if (m) { if (cur) sections.push(cur); cur = { title: m[1] || 'AI 分析', content: m[2] || '请结合猫咪实际状态继续观察。' }; return; }
    if (!cur) { cur = { title: sections.length === 0 ? '核心判断' : `补充说明 ${sections.length}`, content: line }; return; }
    cur.content = `${cur.content}\n${line}`;
  });
  if (cur) sections.push(cur);
  return sections.length ? sections : [{ title: '建议回复', content: content || '暂时没有可展示的内容。' }];
};
</script>

<style scoped>
/* ========== PAGE ========== */
.ai-page {
  height: calc(100dvh - var(--app-tabbar-height, 50px));
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--cv-page-gradient);
}
.ai-main {
  display: flex;
  min-height: 0;
  flex: 1;
  flex-direction: column;
  overflow: hidden;
  padding: 6px 16px 10px;
}

:deep(.app-topbar) {
  padding-top: 10px;
  padding-bottom: 9px;
}

:deep(.app-topbar-row) {
  min-height: 40px;
}

:deep(.app-topbar-kicker) {
  width: fit-content;
  border-radius: 999px;
  background: rgba(249, 115, 22, 0.09);
  color: var(--cv-accent);
  padding: 3px 8px;
  font-size: 10px;
  letter-spacing: 0;
  line-height: 1;
  text-transform: none;
}

:deep(.app-topbar-title h1) {
  margin-top: 4px;
  color: var(--cv-ink);
  font-size: 23px;
  line-height: 1.05;
}

:deep(.app-topbar-title p) {
  max-width: 250px;
  color: var(--cv-muted);
  font-size: 12px;
  line-height: 1.25;
}

:deep(.topbar-action.ai-clear-btn) {
  width: auto;
  min-width: 50px;
  height: 36px;
  border-radius: 12px;
  padding: 0 12px;
  color: var(--cv-ink);
  font-size: 12px;
  font-weight: 900;
  box-shadow: 0 6px 16px rgba(23, 32, 51, 0.06);
}

/* ========== HEADER ========== */
.ai-header { display: flex; align-items: center; justify-content: space-between; padding: 10px 12px; flex-shrink: 0; }
.ai-header-btn { width: 38px; height: 38px; border-radius: 14px; border: none; background: rgba(255,255,255,0.7); backdrop-filter: blur(8px); display: grid; place-items: center; color: #5d4037; cursor: pointer; box-shadow: 0 1px 4px rgba(0,0,0,0.04); }
.ai-header-btn:active { transform: scale(.9); }
.ai-header-center { display: flex; align-items: center; gap: 8px; }
.ai-header-icon { font-size: 22px; }
.ai-header-title { font-size: 18px; font-weight: 800; color: var(--cv-ink); margin: 0; }
.ai-header-clear { font-size: 13px; font-weight: 700; color: var(--cv-accent); background: none; border: none; cursor: pointer; padding: 6px 12px; border-radius: 999px; transition: background .12s; }
.ai-header-clear:active { background: rgba(249,115,22,0.08); }

/* ========== PET CARD ========== */
.ai-pet-card {
  position: relative;
  overflow: hidden;
  margin-bottom: 10px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.96);
  padding: 12px;
  box-shadow: 0 14px 30px rgba(23, 32, 51, 0.07);
}
.ai-pet-card::before {
  content: '';
  position: absolute;
  top: -28px;
  right: -22px;
  width: 92px;
  height: 92px;
  border-radius: 999px;
  background: radial-gradient(circle, rgba(249, 115, 22, 0.14), transparent 66%);
  pointer-events: none;
}
.ai-pet-card::after {
  content: '••';
  position: absolute;
  right: 18px;
  bottom: 12px;
  color: rgba(249, 115, 22, 0.16);
  font-size: 20px;
  font-weight: 900;
  letter-spacing: 4px;
  pointer-events: none;
}
.ai-pet-card-btn {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  border: none;
  background: none;
  cursor: pointer;
  padding: 0;
  text-align: left;
}
.ai-pet-left { display: flex; min-width: 0; align-items: center; gap: 11px; }
.ai-pet-avatar-ring {
  position: relative;
  flex-shrink: 0;
  border-radius: 20px;
  padding: 3px;
  background: linear-gradient(135deg, #fff7ed, #ecfdf5);
}
.ai-pet-avatar { width: 50px; height: 50px; border-radius: 18px; object-fit: cover; border: 3px solid #fff; }
.ai-pet-dot { position: absolute; bottom: 2px; right: 2px; width: 12px; height: 12px; border-radius: 50%; background: #22c55e; border: 2px solid #fff; animation: pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.5;transform:scale(1.3)} }
.ai-pet-info { display: flex; min-width: 0; flex: 1; flex-direction: column; gap: 3px; }
.ai-pet-name-row { display: flex; align-items: center; gap: 8px; }
.ai-pet-name { overflow: hidden; color: var(--cv-ink); font-size: 20px; font-weight: 1000; line-height: 1.12; text-overflow: ellipsis; white-space: nowrap; }
.ai-pet-tag { flex-shrink: 0; font-size: 11px; font-weight: 900; color: var(--cv-accent); background: rgba(249,115,22,0.08); padding: 3px 8px; border-radius: 999px; }
.ai-pet-status { overflow: hidden; font-size: 12px; color: #64748b; font-weight: 700; text-overflow: ellipsis; white-space: nowrap; }
.ai-pet-mini-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-top: 2px;
}
.ai-pet-mini-chips span {
  border-radius: 999px;
  background: #f8fafc;
  color: #64748b;
  padding: 3px 7px;
  font-size: 10px;
  font-weight: 900;
  line-height: 1;
}
.ai-pet-score { display: inline-flex; flex-shrink: 0; align-items: center; gap: 4px; border: 1px solid rgba(249,115,22,0.16); background: #fff7ed; border-radius: 999px; padding: 8px 10px; color: var(--cv-accent); }
.ai-pet-score-num { font-size: 12px; font-weight: 900; color: var(--cv-accent); line-height: 1; }
.ai-pet-score-label { font-size: 10px; font-weight: 700; color: var(--cv-accent); margin-top: 2px; }
.ai-pet-detail {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin-top: 12px;
  border-top: 1px solid #f3f4f6;
  padding-top: 11px;
}
.ai-health-chip {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 8px;
  border: 1px solid #edf2f7;
  border-radius: 15px;
  background: #f8fafc;
  padding: 9px;
}
.ai-health-chip.mint { background: #ecfdf5; border-color: #d7f7e8; }
.ai-health-chip.warm { background: #fff7ed; border-color: #ffead5; }
.ai-health-chip.blue { background: #eff6ff; border-color: #dbeafe; }
.ai-health-chip.soft { background: #f7f5ff; border-color: #ece7ff; }
.ai-health-icon {
  display: grid;
  width: 26px;
  height: 26px;
  flex-shrink: 0;
  place-items: center;
  border-radius: 11px;
  background: rgba(255, 255, 255, 0.75);
  font-size: 14px;
}
.ai-health-chip span:not(.ai-health-icon) {
  display: block;
  color: #748094;
  font-size: 10px;
  font-weight: 900;
  line-height: 1.2;
}
.ai-health-chip strong {
  display: block;
  margin-top: 2px;
  overflow: hidden;
  color: var(--cv-ink);
  font-size: 12px;
  font-weight: 1000;
  line-height: 1.25;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.ai-health-chip > div {
  min-width: 0;
}
.ai-vaccine-list {
  grid-column: 1 / -1;
  display: flex;
  min-width: 0;
  flex-wrap: wrap;
  gap: 6px;
  overflow: hidden;
}
.ai-vaccine-list span {
  max-width: 104px;
  overflow: hidden;
  border: 1px solid #dbeafe;
  border-radius: 999px;
  background: rgba(239, 246, 255, 0.9);
  color: #2563eb;
  padding: 4px 8px;
  font-size: 11px;
  font-weight: 900;
  line-height: 1.2;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.ai-reference-card {
  grid-column: 1 / -1;
  border: 1px solid #ffe4d4;
  border-radius: 16px;
  background: linear-gradient(135deg, #fffaf7, #f7fffb);
  padding: 10px 11px;
}
.ai-reference-title {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--cv-ink);
  font-size: 12px;
}
.ai-reference-title strong {
  font-weight: 1000;
}
.ai-reference-card p {
  margin: 6px 0 0;
  color: #0f766e;
  font-size: 12px;
  font-weight: 900;
  line-height: 1.45;
}
.ai-reference-card small {
  display: block;
  margin-top: 4px;
  color: #748094;
  font-size: 11px;
  font-weight: 700;
  line-height: 1.45;
}
.ai-pet-actions {
  position: relative;
  z-index: 1;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #f3f4f6;
}
.ai-pet-action {
  display: inline-flex;
  min-width: 0;
  flex: 1 1 128px;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-height: 38px;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  background: rgba(255,255,255,0.86);
  color: var(--cv-ink);
  cursor: pointer;
  padding: 0 12px;
  font-size: 13px;
  font-weight: 900;
  transition: transform .12s, border-color .12s, color .12s;
}
.ai-pet-action.accent {
  border-color: rgba(249,115,22,0.22);
  background: #fff7ed;
  color: var(--cv-accent);
}
.ai-pet-action:active {
  transform: scale(.98);
}

/* ========== AI EMPTY ========== */
.ai-empty { margin-bottom: 14px; text-align: center; padding: 36px 24px; background: linear-gradient(135deg, #fff8f4 0%, #fff 40%, #fef5ff 100%); border-radius: 24px; border: 2px dashed #ffe0cc; }
.ai-empty-illustration { display: inline-block; margin-bottom: 12px; }
.ai-empty-emoji { font-size: 60px; display: block; filter: drop-shadow(0 4px 8px rgba(255,107,53,0.15)); animation: catFloat 3s ease-in-out infinite; }
.ai-empty-paws { display: flex; justify-content: center; gap: 8px; margin-top: -8px; }
.ai-empty-paws span { font-size: 16px; animation: pawBounce 1.5s ease-in-out infinite; }
.ai-empty-paws span:nth-child(2) { animation-delay: .2s; }
.ai-empty-paws span:nth-child(3) { animation-delay: .4s; }
@keyframes catFloat { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-8px)} }
@keyframes pawBounce { 0%,100%{transform:scale(1);opacity:.5} 50%{transform:scale(1.2);opacity:1} }
.ai-empty-title { font-size: 18px; font-weight: 800; color: var(--cv-ink); margin: 0 0 6px; }
.ai-empty-desc { font-size: 14px; color: var(--cv-muted); margin: 0 0 20px; line-height: 1.6; }
.ai-empty-btn { display: inline-flex; align-items: center; gap: 6px; padding: 12px 32px; border-radius: 999px; background: linear-gradient(135deg, var(--cv-accent), #14b8a6); color: #fff; font-size: 16px; font-weight: 700; border: none; cursor: pointer; box-shadow: 0 8px 24px rgba(249,115,22,0.3); transition: transform .15s; }
.ai-empty-btn:active { transform: scale(.96); }

/* ========== CHAT ========== */
.ai-chat {
  display: flex;
  min-height: 0;
  flex: 1;
  flex-direction: column;
  gap: 12px;
  overflow-x: hidden;
  overflow-y: auto;
  margin: 0 -4px;
  padding: 4px 4px 14px;
  -webkit-overflow-scrolling: touch;
}
.ai-msg { display: flex; gap: 8px; align-items: flex-end; }
.ai-msg--bot { justify-content: flex-start; }
.ai-msg--user { justify-content: flex-end; }
.ai-msg-avatar { width: 34px; height: 34px; border-radius: 50%; display: grid; place-items: center; flex-shrink: 0; }
.ai-msg-avatar.bot { background: var(--cv-ink); color: #fff; }
.ai-msg-avatar.user { background: #e5e7eb; color: var(--cv-muted); }
.ai-msg-bubble-wrap { max-width: 85%; }
.ai-bubble { padding: 12px 14px; border-radius: 18px; }
.ai-bubble--thinking { width: 148px; min-height: 44px; display: flex; align-items: center; background: #f0f3ff; color: #6b7280; font-size: 14px; border-bottom-left-radius: 4px; }
.ai-bubble--consult { background: linear-gradient(135deg, #fff5ef, #fffaf7); border: 1.5px solid #ffd9c8; border-bottom-left-radius: 4px; }
.ai-bubble--analysis { background: #eef2ff; border: 1px solid #dde5ff; border-bottom-left-radius: 4px; }
.ai-bubble-tag-row { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.ai-bubble-tag { font-size: 11px; font-weight: 700; color: #fff; background: var(--cv-ink); padding: 2px 8px; border-radius: 999px; }
.ai-bubble-tag.analysis { background: #dce5ff; color: #3550a1; }
.ai-bubble-tag-sub { font-size: 11px; color: #8e5f4f; }
.ai-bubble-text { font-size: 14px; color: var(--cv-ink); line-height: 1.7; margin: 0; white-space: pre-line; }
.ai-bubble-cta { margin-top: 8px; padding: 6px 16px; border-radius: 999px; background: var(--cv-ink); color: #fff; font-size: 12px; font-weight: 700; border: none; cursor: pointer; }
.ai-sections { display: flex; flex-direction: column; gap: 8px; }
.ai-section { background: rgba(255,255,255,0.85); border: 1px solid #d7e1ff; border-radius: 12px; padding: 10px 12px; }
.ai-section-title { font-size: 12px; font-weight: 700; color: var(--cv-ink); margin: 0 0 4px; }
.ai-section-text { font-size: 14px; color: var(--cv-ink); line-height: 1.7; margin: 0; }
.ai-bubble.user { background: linear-gradient(135deg, var(--cv-accent), #14b8a6); color: #fff; font-size: 14px; max-width: 80%; border-bottom-right-radius: 4px; border-top-right-radius: 4px; }

/* ========== INPUT BAR ========== */
.ai-input-bar {
  flex-shrink: 0;
  width: 100%;
  box-sizing: border-box;
  padding: 6px 12px calc(6px + env(safe-area-inset-bottom, 0px));
  z-index: 60;
  background: var(--cv-page-bg, #f5f7fb);
}
.ai-chip-row { display: flex; gap: 8px; overflow-x: auto; padding: 0 0 8px; scrollbar-width: none; }
.ai-chip-row::-webkit-scrollbar { display: none; }
.ai-chip { display: inline-flex; flex: 0 0 auto; align-items: center; gap: 5px; height: 34px; border: 1px solid #e5e7eb; border-radius: 999px; background: rgba(255,255,255,0.94); color: var(--cv-ink); padding: 0 12px; font-size: 13px; font-weight: 900; box-shadow: 0 4px 14px rgba(15,23,42,0.06); }
.ai-chip:active { transform: scale(.97); }
.ai-input-wrap { display: flex; align-items: center; gap: 8px; background: #fff; border-radius: 28px; padding: 6px 6px 6px 16px; box-shadow: 0 -2px 16px rgba(0,0,0,0.06); }
.ai-input-icon { color: var(--cv-muted); flex-shrink: 0; }
.ai-input { flex: 1; border: none; outline: none; font-size: 14px; color: var(--cv-ink); background: transparent; padding: 6px 0; }
.ai-input::placeholder { color: var(--cv-muted); }
.ai-send-btn { padding: 8px 20px; border-radius: 999px; border: none; background: var(--cv-ink); color: #fff; font-size: 14px; font-weight: 700; cursor: pointer; flex-shrink: 0; box-shadow: 0 4px 12px rgba(249,115,22,0.25); transition: all .12s; }
.ai-send-btn:active { transform: scale(.95); }
.ai-send-btn:disabled { opacity: .4; cursor: not-allowed; transform: none; }

/* ========== SHEET ========== */
.sheet-body { padding: 8px 16px 20px; }
.sheet-hint { font-size: 12px; color: var(--cv-muted); margin: 0 0 10px; }
.sheet-list { display: flex; flex-direction: column; gap: 8px; }
.sheet-item { display: flex; align-items: center; gap: 12px; padding: 14px 16px; border-radius: 16px; border: 2px solid transparent; background: #f5f7fb; cursor: pointer; width: 100%; text-align: left; transition: all .15s; }
.sheet-item:active { transform: scale(.98); }
.sheet-item.active { background: rgba(249,115,22,0.08); border-color: var(--cv-accent); }
.sheet-item-name { font-size: 15px; font-weight: 700; color: var(--cv-ink); }
.sheet-item.active .sheet-item-name { color: var(--cv-accent); }
.sheet-item-breed { font-size: 13px; color: var(--cv-muted); margin-left: auto; }
.sheet-item-radio { width: 18px; height: 18px; border-radius: 50%; border: 2px solid #d1d5db; flex-shrink: 0; }

/* ========== AI KEYWORD ========== */
:deep(.ai-kw) { color: #b42318; font-weight: 700; background: #ffe4dc; border-radius: 6px; padding: 0 4px; }

/* ========== SECOND BLOCK MERGE ========== */
.ai-header {
  display: none;
}

/* Action button uses AppTopBar default .topbar-action style — consistent with MessagesView */

.ai-section,
.ai-empty {
  border: 1px solid var(--cv-card-border);
  background: var(--cv-card-bg);
  box-shadow: var(--cv-card-shadow);
}

.ai-pet-card {
  border: 1px solid var(--cv-card-border);
}

.ai-pet-avatar {
  border-color: #fff;
  border-radius: 18px;
}

.ai-pet-avatar-ring {
  border-radius: 18px;
}

.ai-pet-score,
.ai-pet-tag {
  background: rgba(249,115,22,0.08);
  color: var(--cv-accent);
}

.ai-msg-avatar.bot {
  background: var(--cv-ink);
}

.ai-bubble--consult,
.ai-bubble--analysis,
.ai-bubble--thinking {
  border: 1px solid #e2e8f0;
  background: rgba(255, 255, 255, 0.94);
  box-shadow: 0 10px 24px rgba(23, 32, 51, 0.05);
}

.ai-bubble-tag,
.ai-bubble-cta,
.ai-send-btn,
.ai-empty-btn {
  background: var(--cv-ink);
  box-shadow: none;
}

.ai-bubble-tag.analysis {
  background: #ecfdf5;
  color: #0f766e;
}

.ai-bubble-text,
.ai-section-text {
  color: #40506a;
}

.ai-input-wrap {
  border: 1px solid var(--cv-card-border);
  box-shadow: 0 -12px 28px rgba(23, 32, 51, 0.08);
}

@media (max-width: 380px) {
  :deep(.app-topbar-title h1) {
    font-size: 21px;
  }

  :deep(.app-topbar-title p) {
    max-width: 220px;
  }

  .ai-pet-name {
    font-size: 18px;
  }

  .ai-pet-avatar {
    width: 46px;
    height: 46px;
  }

  .ai-health-chip {
    padding: 8px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .ai-empty-emoji,
  .ai-empty-paws span,
  .ai-pet-dot,
  .ai-pet-action,
  .ai-chip,
  .ai-send-btn,
  :deep(.topbar-action) {
    animation: none !important;
    transition: none !important;
  }
}
</style>
