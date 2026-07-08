<template>
  <div class="admin-page">
    <header class="admin-hero">
      <div class="admin-nav">
        <button class="icon-btn glass" type="button" aria-label="返回" @click="router.back()">
          <van-icon name="arrow-left" size="20" />
        </button>
        <div class="admin-title-block">
          <span class="eyebrow">Cat Village Ops</span>
          <h1>后台管理</h1>
        </div>
        <button class="icon-btn accent" type="button" aria-label="刷新" @click="loadAll">
          <van-icon name="replay" size="18" />
        </button>
      </div>

      <section class="hero-panel">
        <div>
          <span class="hero-kicker">今日运营</span>
          <div class="hero-number">{{ todayTotal }}</div>
          <p>动态、情绪、消息与 AI 咨询的新增活跃</p>
          <div class="hero-metrics">
            <span>今日动态 {{ stats.today_dynamics }}</span>
            <span>活跃用户 {{ stats.active_users }}</span>
            <span>管理员 {{ stats.admins }}</span>
          </div>
        </div>
        <div class="hero-status">
          <span :class="overview?.health.aiConfigured ? 'online' : 'warning'" />
          {{ overview?.health.aiConfigured ? 'AI 已配置' : 'AI 待配置' }}
        </div>
      </section>
    </header>

    <section class="stat-grid">
      <button
        v-for="item in statItems"
        :key="item.label"
        type="button"
        class="stat-card"
        @click="activeTab = item.target"
      >
        <span class="stat-icon"><van-icon :name="item.icon" size="18" /></span>
        <strong>{{ item.value }}</strong>
        <small>{{ item.label }}</small>
      </button>
    </section>

    <nav class="admin-tabs">
      <button
        v-for="tab in tabList"
        :key="tab.key"
        class="admin-tab"
        :class="{ active: activeTab === tab.key }"
        type="button"
        @click="activeTab = tab.key"
      >
        <van-icon :name="tab.icon" size="15" />
        <span>{{ tab.label }}</span>
      </button>
    </nav>

    <section class="admin-content">
      <div v-if="loading" class="state-panel">
        <van-loading size="28" color="#f97316" />
        <span>正在同步后台数据...</span>
      </div>

      <template v-else>
        <section v-if="activeTab === 'overview'" class="overview-layout">
          <div class="section-title">
            <h2>运营概览</h2>
            <span>最近 7 天</span>
          </div>

          <div class="pulse-grid">
            <div class="pulse-card">
              <span>本周动态</span>
              <strong>{{ overview?.week.dynamics || 0 }}</strong>
            </div>
            <div class="pulse-card teal">
              <span>情绪识别</span>
              <strong>{{ overview?.week.emotions || 0 }}</strong>
            </div>
            <div class="pulse-card violet">
              <span>健康记录</span>
              <strong>{{ (overview?.week.feedings || 0) + (overview?.week.weights || 0) }}</strong>
            </div>
          </div>

          <div class="chart-panel">
            <div v-for="day in chartItems" :key="day.date" class="chart-row">
              <span>{{ shortDay(day.date) }}</span>
              <div class="chart-track">
                <i :style="{ width: day.width + '%' }" />
              </div>
              <b>{{ day.total }}</b>
            </div>
          </div>

          <div class="section-title compact">
            <h2>最近活动</h2>
          </div>
          <div class="activity-list">
            <article v-for="item in sortedActivities" :key="`${item.type}-${item.id}`" class="activity-item">
              <span class="activity-icon" :class="item.type">
                <van-icon :name="item.type === 'dynamic' ? 'photo-o' : 'music-o'" size="16" />
              </span>
              <div>
                <strong>{{ item.title }}</strong>
                <p>{{ item.desc || '暂无内容' }}</p>
              </div>
              <time>{{ formatDate(item.time) }}</time>
            </article>
            <div v-if="sortedActivities.length === 0" class="empty-inline">暂无最近活动</div>
          </div>
        </section>

        <section v-if="activeTab === 'users'" class="admin-list">
          <van-search v-model="keyword" placeholder="搜索用户名或昵称" shape="round" @search="loadByTab" @clear="loadByTab" />
          <article v-for="user in users" :key="user.id" class="data-card">
            <div class="card-main">
              <div class="avatar user">{{ firstLetter(user.nickname || user.username) }}</div>
              <div class="card-text">
                <strong>{{ user.nickname || user.username }}</strong>
                <span>@{{ user.username }} · {{ user.isActive ? '账号正常' : '账号禁用' }}</span>
              </div>
              <span class="badge" :class="user.isAdmin ? 'admin' : 'normal'">{{ user.isAdmin ? '管理员' : '用户' }}</span>
            </div>
            <div class="action-row">
              <button type="button" class="text-btn" @click="toggleActive(user)">{{ user.isActive ? '禁用' : '启用' }}</button>
              <button type="button" class="text-btn warn" @click="toggleAdmin(user)">{{ user.isAdmin ? '取消管理' : '设为管理' }}</button>
              <button type="button" class="text-btn" @click="resetPassword(user)">重置密码</button>
              <button type="button" class="text-btn danger" @click="removeUser(user)">删除</button>
            </div>
          </article>
          <EmptyState v-if="users.length === 0" text="暂无用户" />
        </section>

        <section v-if="activeTab === 'pets'" class="admin-list">
          <van-search v-model="petKeyword" placeholder="搜索猫咪、品种或主人" shape="round" @search="loadByTab" @clear="loadByTab" />
          <article v-for="pet in pets" :key="pet.id" class="data-card">
            <div class="card-main">
              <div class="avatar pet"><van-icon name="smile-o" size="18" /></div>
              <div class="card-text">
                <strong>{{ pet.name }} · {{ pet.breed || '未知品种' }}</strong>
                <span>{{ pet.owner }} · {{ formatCatAge(pet.age) }} · {{ pet.weight ? pet.weight + 'kg' : '体重未知' }}</span>
              </div>
              <time>{{ formatDate(pet.createdAt) }}</time>
            </div>
            <div class="action-row">
              <button type="button" class="text-btn danger" @click="removePet(pet)">删除档案</button>
            </div>
          </article>
          <EmptyState v-if="pets.length === 0" text="暂无猫咪档案" />
        </section>

        <section v-if="activeTab === 'content'" class="admin-list">
          <van-search v-model="dynKeyword" placeholder="搜索动态或作者" shape="round" @search="loadByTab" @clear="loadByTab" />
          <article v-for="dynamic in dynamics" :key="dynamic.id" class="data-card clickable" @click="openDynamic(dynamic.id)">
            <p class="dynamic-content">{{ dynamic.content || '无文字内容' }}</p>
            <div class="meta-row">
              <span>{{ dynamic.author }} · {{ dynamic.likeCount }} 赞 · {{ dynamic.commentCount }} 评</span>
              <time>{{ formatDate(dynamic.createdAt) }}</time>
            </div>
            <div v-if="dynamic.isRecommended" class="recommend-badge">
              <van-icon name="fire-o" size="13" />
              村长推荐
            </div>
            <div class="action-row">
              <button type="button" class="text-btn" @click.stop="openDynamic(dynamic.id)">查看详情</button>
              <button type="button" class="text-btn warn" @click.stop="toggleDynamicRecommend(dynamic)">
                {{ dynamic.isRecommended ? '取消推荐' : '设为村长推荐' }}
              </button>
              <button type="button" class="text-btn danger" @click.stop="removeDynamic(dynamic)">删除动态</button>
            </div>
          </article>
          <EmptyState v-if="dynamics.length === 0" text="暂无社区动态" />
        </section>

        <section v-if="activeTab === 'health'" class="admin-list">
          <div class="filter-row">
            <van-search v-model="healthKeyword" placeholder="搜索猫咪、主人或食物" shape="round" @search="loadByTab" @clear="loadByTab" />
            <select v-model="healthKind" class="kind-select" @change="loadByTab">
              <option value="">全部</option>
              <option value="feeding">投喂</option>
              <option value="weight">体重</option>
            </select>
          </div>
          <article v-for="record in healthRecords" :key="`${record.kind}-${record.id}`" class="data-card">
            <div class="card-main">
              <div class="avatar health" :class="record.kind">
                <van-icon :name="record.kind === 'feeding' ? 'shop-o' : 'bar-chart-o'" size="18" />
              </div>
              <div class="card-text">
                <strong>{{ record.petName }} · {{ record.metric }}</strong>
                <span>{{ record.owner || '未知主人' }} · {{ record.note }}</span>
              </div>
              <time>{{ formatDate(record.recordedAt) }}</time>
            </div>
            <div class="action-row">
              <button type="button" class="text-btn danger" @click="removeHealthRecord(record)">删除记录</button>
            </div>
          </article>
          <EmptyState v-if="healthRecords.length === 0" text="暂无健康记录" />
        </section>

        <section v-if="activeTab === 'signals'" class="admin-list">
          <article v-for="record in emotionRecords" :key="record.id" class="data-card">
            <div class="card-main">
              <div class="avatar signal">{{ emotionEmoji(record.label) }}</div>
              <div class="card-text">
                <strong>{{ record.label }} · {{ record.confidence ? Math.round(record.confidence * 100) : '?' }}%</strong>
                <span>{{ record.petName }} · {{ formatDate(record.recordTime) }}</span>
              </div>
              <button type="button" class="round-danger" @click="removeEmotion(record)">
                <van-icon name="delete-o" size="16" />
              </button>
            </div>
          </article>
          <EmptyState v-if="emotionRecords.length === 0" text="暂无情绪识别记录" />
        </section>

        <section v-if="activeTab === 'messages'" class="admin-list">
          <article v-for="message in messages" :key="message.id" class="data-card">
            <div class="card-main">
              <div class="avatar msg">{{ firstLetter(message.senderName) }}</div>
              <div class="card-text">
                <strong>{{ message.senderName }} · {{ typeLabel(message.messageType) }}</strong>
                <span>{{ message.content }}</span>
              </div>
              <button type="button" class="round-danger" @click="removeMessage(message)">
                <van-icon name="delete-o" size="16" />
              </button>
            </div>
            <div class="meta-row single">
              <time>{{ formatDate(message.sentAt) }}</time>
            </div>
          </article>
          <EmptyState v-if="messages.length === 0" text="暂无私信记录" />
        </section>

        <section v-if="activeTab === 'topics'" class="admin-list topic-admin">
          <div class="section-title">
            <h2>热门话题</h2>
            <span>管理展示、推荐与排序</span>
          </div>
          <div class="topic-create-row">
            <input v-model="topicDraft" type="text" placeholder="新增话题，如 猫咪护理" @keyup.enter="createTopic" />
            <button type="button" class="primary-btn compact" @click="createTopic">新增</button>
          </div>
          <article v-for="topic in hotTopics" :key="topic.id || topic.topic" class="data-card topic-card">
            <div class="card-main">
              <div class="avatar topic">#</div>
              <div class="card-text">
                <input v-model="topic.topic" class="topic-name-input" @change="saveTopic(topic)" />
                <span>{{ topic.count || 0 }} 次出现 · 排序 {{ topic.sortOrder || 0 }}</span>
              </div>
            </div>
            <div class="topic-controls">
              <label><input v-model="topic.isVisible" type="checkbox" @change="saveTopic(topic)" /> 展示</label>
              <label><input v-model="topic.isRecommended" type="checkbox" @change="saveTopic(topic)" /> 推荐</label>
              <input v-model.number="topic.sortOrder" type="number" min="1" @change="saveTopic(topic)" />
              <button type="button" class="round-danger" @click="removeTopic(topic)">
                <van-icon name="delete-o" size="15" />
              </button>
            </div>
          </article>
          <button type="button" class="primary-btn" @click="saveTopicSort">
            <van-icon name="passed" size="17" />
            保存排序
          </button>
        </section>

        <section v-if="activeTab === 'system'" class="system-panel">
          <div class="section-title">
            <h2>系统配置</h2>
            <span>{{ config.runtimeOnly ? '运行时生效' : '持久配置' }}</span>
          </div>
          <label class="form-field">
            <span>DeepSeek API Key</span>
            <input v-model="config.aiApiKey" type="password" placeholder="保持掩码不修改，输入新 key 可更新" />
          </label>
          <div class="config-safe-note">
            API Key 仅显示掩码；保留掩码不会覆盖当前密钥。
          </div>
          <label class="form-field">
            <span>AI Base URL</span>
            <input v-model="config.aiBaseUrl" type="text" placeholder="https://api.deepseek.com" />
          </label>
          <label class="form-field">
            <span>AI Model</span>
            <input v-model="config.aiModel" type="text" placeholder="deepseek-chat" />
          </label>
          <div class="config-note">
            当前管理员：{{ config.adminUsername || '未知' }}。配置会立即影响当前后端进程，生产环境重启后仍建议同步 `.env`。
          </div>
          <button type="button" class="primary-btn" :disabled="savingConfig" @click="saveConfig">
            <van-icon name="passed" size="17" />
            {{ savingConfig ? '保存中...' : '保存配置' }}
          </button>
        </section>
      </template>
    </section>

    <van-dialog
      v-model:show="showPasswordDialog"
      title="重置密码"
      show-cancel-button
      confirm-button-text="确认重置"
      :before-close="beforePasswordDialogClose"
    >
      <div class="password-dialog">
        <p>为 {{ passwordTarget?.nickname || passwordTarget?.username || '用户' }} 设置不少于 6 位的新密码。</p>
        <input
          v-model="passwordDraft"
          type="password"
          autocomplete="new-password"
          placeholder="输入新密码"
        />
      </div>
    </van-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { showConfirmDialog, showToast } from 'vant';
import {
  deleteAdminDynamic,
  deleteAdminTopic,
  deleteAdminEmotionRecord,
  deleteAdminHealthRecord,
  deleteAdminMessage,
  deleteAdminPet,
  deleteAdminUser,
  getAdminConfig,
  getAdminDynamics,
  getAdminEmotionRecords,
  getAdminHealthRecords,
  getAdminHotTopics,
  createAdminTopic,
  updateAdminTopic,
  sortAdminTopics,
  getAdminMessages,
  getAdminOverview,
  getAdminPets,
  getAdminStats,
  getAdminUsers,
  setAdminUserActive,
  setAdminUserRole,
  setAdminDynamicRecommended,
  updateAdminConfig,
  resetAdminUserPassword,
  type AdminHotTopic,
  type AdminConfig,
  type AdminDynamic,
  type AdminEmotionRecord,
  type AdminHealthRecord,
  type AdminMessage,
  type AdminOverview,
  type AdminPet,
  type AdminStats,
  type AdminUser
} from '@/api/admin';
import { formatCatAge } from '@/utils/age';

type TabKey = 'overview' | 'users' | 'pets' | 'content' | 'health' | 'signals' | 'messages' | 'topics' | 'system';

const EmptyState = defineComponent({
  props: { text: { type: String, required: true } },
  setup(props) {
    return () => h('div', { class: 'empty-state' }, [
      h('span', '暂无数据'),
      h('p', props.text)
    ]);
  }
});

const router = useRouter();
const activeTab = ref<TabKey>('overview');
const loading = ref(false);
const savingConfig = ref(false);
const keyword = ref('');
const petKeyword = ref('');
const dynKeyword = ref('');
const healthKeyword = ref('');
const healthKind = ref<'' | 'weight' | 'feeding'>('');

const stats = ref<AdminStats>({
  users: 0,
  pets: 0,
  dynamics: 0,
  emotion_records: 0,
  today_users: 0,
  today_dynamics: 0,
  messages: 0,
  health_records: 0,
  ai_chats: 0,
  active_users: 0,
  disabled_users: 0,
  admins: 0
});
const overview = ref<AdminOverview | null>(null);
const users = ref<AdminUser[]>([]);
const pets = ref<AdminPet[]>([]);
const dynamics = ref<AdminDynamic[]>([]);
const emotionRecords = ref<AdminEmotionRecord[]>([]);
const messages = ref<AdminMessage[]>([]);
const healthRecords = ref<AdminHealthRecord[]>([]);
const hotTopics = ref<AdminHotTopic[]>([]);
const topicDraft = ref('');
const config = ref<AdminConfig>({ aiApiKey: '', aiBaseUrl: '', aiModel: 'deepseek-chat', adminUsername: '', runtimeOnly: true });
const showPasswordDialog = ref(false);
const passwordTarget = ref<AdminUser | null>(null);
const passwordDraft = ref('');

const tabList: Array<{ key: TabKey; label: string; icon: string }> = [
  { key: 'overview', label: '概览', icon: 'bar-chart-o' },
  { key: 'users', label: '用户', icon: 'contact' },
  { key: 'pets', label: '猫咪', icon: 'smile-o' },
  { key: 'content', label: '内容', icon: 'photo-o' },
  { key: 'health', label: '健康', icon: 'bar-chart-o' },
  { key: 'signals', label: '情绪', icon: 'music-o' },
  { key: 'messages', label: '消息', icon: 'chat-o' },
  { key: 'topics', label: '话题', icon: 'fire-o' },
  { key: 'system', label: '配置', icon: 'setting-o' }
];

const statItems = computed(() => [
  { label: '用户', value: stats.value.users, icon: 'friends-o', target: 'users' as TabKey },
  { label: '猫咪', value: stats.value.pets, icon: 'smile-o', target: 'pets' as TabKey },
  { label: '内容', value: stats.value.dynamics, icon: 'photo-o', target: 'content' as TabKey },
  { label: '识别', value: stats.value.emotion_records, icon: 'music-o', target: 'signals' as TabKey },
  { label: '热点话题', value: hotTopics.value.length || 3, icon: 'fire-o', target: 'topics' as TabKey },
  { label: '今日动态', value: stats.value.today_dynamics, icon: 'fire-o', target: 'content' as TabKey },
  { label: '健康', value: stats.value.health_records, icon: 'bar-chart-o', target: 'health' as TabKey },
  { label: '消息', value: stats.value.messages, icon: 'chat-o', target: 'messages' as TabKey },
  { label: '配置', value: 1, icon: 'setting-o', target: 'system' as TabKey }
]);

const todayTotal = computed(() => {
  const today = overview.value?.today;
  if (!today) return 0;
  return today.dynamics + today.emotions + today.messages + today.aiChats;
});

const chartItems = computed(() => {
  const daily = overview.value?.daily || [];
  const items = daily.map((item) => ({
    date: item.date,
    total: item.dynamics + item.emotions + item.messages
  }));
  const max = Math.max(1, ...items.map((item) => item.total));
  return items.map((item) => ({ ...item, width: Math.max(8, Math.round((item.total / max) * 100)) }));
});

const sortedActivities = computed(() => {
  return [...(overview.value?.recentActivities || [])]
    .sort((a, b) => new Date(b.time).getTime() - new Date(a.time).getTime())
    .slice(0, 8);
});

const withLoading = async (fn: () => Promise<void>) => {
  loading.value = true;
  try {
    await fn();
  } catch (error: any) {
    showToast({ type: 'fail', message: error?.message || '加载失败' });
  } finally {
    loading.value = false;
  }
};

const loadStats = async () => {
  const response = await getAdminStats();
  stats.value = response.data;
};
const loadOverview = async () => {
  const response = await getAdminOverview();
  overview.value = response.data;
};
const loadUsers = async () => {
  const response = await getAdminUsers({ page: 1, pageSize: 50, keyword: keyword.value || undefined });
  users.value = response.data.list;
};
const loadPets = async () => {
  const response = await getAdminPets({ page: 1, pageSize: 50, keyword: petKeyword.value || undefined });
  pets.value = response.data.list;
};
const loadDynamics = async () => {
  const response = await getAdminDynamics({ page: 1, pageSize: 50, keyword: dynKeyword.value || undefined });
  dynamics.value = response.data.list;
};
const loadEmotions = async () => {
  const response = await getAdminEmotionRecords({ page: 1, pageSize: 50 });
  emotionRecords.value = response.data.list;
};
const loadMessages = async () => {
  const response = await getAdminMessages({ page: 1, pageSize: 50 });
  messages.value = response.data.list;
};
const loadTopics = async () => {
  const response = await getAdminHotTopics();
  hotTopics.value = response.data.list;
};
const loadHealth = async () => {
  const response = await getAdminHealthRecords({
    page: 1,
    pageSize: 50,
    keyword: healthKeyword.value || undefined,
    kind: healthKind.value || undefined
  });
  healthRecords.value = response.data.list;
};
const loadConfig = async () => {
  const response = await getAdminConfig();
  config.value = response.data;
};

const loadByTab = async () => {
  await withLoading(async () => {
    await loadStats();
    if (activeTab.value === 'overview') await loadOverview();
    if (activeTab.value === 'users') await loadUsers();
    if (activeTab.value === 'pets') await loadPets();
    if (activeTab.value === 'content') await loadDynamics();
    if (activeTab.value === 'health') await loadHealth();
    if (activeTab.value === 'signals') await loadEmotions();
    if (activeTab.value === 'messages') await loadMessages();
    if (activeTab.value === 'topics') await loadTopics();
    if (activeTab.value === 'system') await loadConfig();
  });
};

const loadAll = async () => {
  await withLoading(async () => {
    await Promise.all([loadStats(), loadOverview(), loadUsers(), loadPets(), loadDynamics(), loadEmotions(), loadMessages(), loadHealth(), loadTopics(), loadConfig()]);
  });
};

const toggleActive = async (user: AdminUser) => {
  await withLoading(async () => {
    await setAdminUserActive(user.id, !user.isActive);
    await Promise.all([loadUsers(), loadStats(), loadOverview()]);
  });
};
const toggleAdmin = async (user: AdminUser) => {
  await withLoading(async () => {
    await setAdminUserRole(user.id, !user.isAdmin);
    await Promise.all([loadUsers(), loadStats(), loadOverview()]);
  });
};
const resetPassword = (user: AdminUser) => {
  passwordTarget.value = user;
  passwordDraft.value = '';
  showPasswordDialog.value = true;
};
const beforePasswordDialogClose = async (action: string) => {
  if (action !== 'confirm') return true;
  if (!passwordTarget.value) return true;
  const password = passwordDraft.value.trim();
  if (password.length < 6) {
    showToast({ type: 'fail', message: '密码至少 6 位' });
    return false;
  }
  try {
    await resetAdminUserPassword(passwordTarget.value.id, password);
    showToast({ type: 'success', message: '密码已重置' });
    passwordTarget.value = null;
    passwordDraft.value = '';
    return true;
  } catch (error: any) {
    showToast({ type: 'fail', message: error?.message || '重置失败' });
    return false;
  }
};
const removeUser = async (user: AdminUser) => {
  try {
    await showConfirmDialog({ title: '删除用户', message: `确认删除 ${user.nickname || user.username}？此操作不可撤销。` });
  } catch {
    return;
  }
  await withLoading(async () => {
    await deleteAdminUser(user.id);
    await Promise.all([loadUsers(), loadStats(), loadOverview()]);
  });
};
const removePet = async (pet: AdminPet) => {
  try {
    await showConfirmDialog({ title: '删除猫咪档案', message: `确认删除 ${pet.name}（主人：${pet.owner}）？` });
  } catch {
    return;
  }
  await withLoading(async () => {
    await deleteAdminPet(pet.id);
    await Promise.all([loadPets(), loadStats(), loadOverview()]);
  });
};
const removeDynamic = async (dynamic: AdminDynamic) => {
  try {
    await showConfirmDialog({ title: '删除动态', message: `确认删除该动态？\n\n${dynamic.content.slice(0, 80)}` });
  } catch {
    return;
  }
  await withLoading(async () => {
    await deleteAdminDynamic(dynamic.id);
    await Promise.all([loadDynamics(), loadStats(), loadOverview()]);
  });
};
const toggleDynamicRecommend = async (dynamic: AdminDynamic) => {
  await withLoading(async () => {
    await setAdminDynamicRecommended(dynamic.id, !dynamic.isRecommended);
    await Promise.all([loadDynamics(), loadStats(), loadOverview()]);
  });
};
const removeEmotion = async (record: AdminEmotionRecord) => {
  try {
    await showConfirmDialog({ title: '删除情绪记录', message: `确认删除 ${record.petName} 的 ${record.label} 记录？` });
  } catch {
    return;
  }
  await withLoading(async () => {
    await deleteAdminEmotionRecord(record.id);
    await Promise.all([loadEmotions(), loadStats(), loadOverview()]);
  });
};
const removeMessage = async (message: AdminMessage) => {
  try {
    await showConfirmDialog({ title: '删除消息', message: `确认删除这条消息？\n\n${message.content.slice(0, 80)}` });
  } catch {
    return;
  }
  await withLoading(async () => {
    await deleteAdminMessage(message.id);
    await Promise.all([loadMessages(), loadStats(), loadOverview()]);
  });
};
const removeHealthRecord = async (record: AdminHealthRecord) => {
  try {
    await showConfirmDialog({ title: '删除健康记录', message: `确认删除 ${record.petName} 的${record.kind === 'feeding' ? '投喂' : '体重'}记录？` });
  } catch {
    return;
  }
  await withLoading(async () => {
    await deleteAdminHealthRecord(record.kind, record.id);
    await Promise.all([loadHealth(), loadStats(), loadOverview()]);
  });
};

const saveConfig = async () => {
  savingConfig.value = true;
  try {
    await updateAdminConfig({
      aiApiKey: config.value.aiApiKey,
      aiBaseUrl: config.value.aiBaseUrl,
      aiModel: config.value.aiModel
    });
    showToast({ type: 'success', message: '配置已更新' });
    await loadConfig();
    await loadOverview();
  } catch (error: any) {
    showToast({ type: 'fail', message: error?.message || '保存失败' });
  } finally {
    savingConfig.value = false;
  }
};

const createTopic = async () => {
  const topic = topicDraft.value.trim().replace(/^#/, '');
  if (!topic) {
    showToast({ type: 'fail', message: '请输入话题名' });
    return;
  }
  await withLoading(async () => {
    await createAdminTopic({ topic, sortOrder: hotTopics.value.length + 1, isRecommended: true, isVisible: true });
    topicDraft.value = '';
    await loadTopics();
    showToast({ type: 'success', message: '话题已新增' });
  });
};

const saveTopic = async (topic: AdminHotTopic) => {
  if (!topic.id) return;
  const name = topic.topic.trim().replace(/^#/, '');
  if (!name) {
    showToast({ type: 'fail', message: '话题名不能为空' });
    await loadTopics();
    return;
  }
  await withLoading(async () => {
    await updateAdminTopic(topic.id as string, {
      topic: name,
      sortOrder: Number(topic.sortOrder || 0),
      isRecommended: !!topic.isRecommended,
      isVisible: !!topic.isVisible
    });
    await loadTopics();
  });
};

const removeTopic = async (topic: AdminHotTopic) => {
  if (!topic.id) return;
  try {
    await showConfirmDialog({ title: '删除话题', message: `确认删除 #${topic.topic}？` });
  } catch {
    return;
  }
  await withLoading(async () => {
    await deleteAdminTopic(topic.id as string);
    await loadTopics();
    showToast({ type: 'success', message: '话题已删除' });
  });
};

const saveTopicSort = async () => {
  const items = hotTopics.value
    .filter((item) => item.id)
    .map((item, index) => ({ id: item.id as string, sortOrder: Number(item.sortOrder || index + 1) }));
  await withLoading(async () => {
    await sortAdminTopics(items);
    await loadTopics();
    showToast({ type: 'success', message: '排序已保存' });
  });
};

const openDynamic = (id: string) => router.push({ name: 'SocialDetail', params: { id } });
const firstLetter = (value: string) => (value || '?').trim().slice(0, 1).toUpperCase();
const shortDay = (value: string) => {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '';
  return `${date.getMonth() + 1}/${date.getDate()}`;
};
const formatDate = (value: string) => {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '';
  return `${date.getMonth() + 1}/${date.getDate()} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
};
const emotionEmoji = (label: string) => {
  if (/开心|愉快|兴奋|满足/i.test(label)) return '悦';
  if (/焦虑|紧张|警惕|害怕/i.test(label)) return '警';
  if (/生气|愤怒|暴躁/i.test(label)) return '怒';
  if (/悲伤|难过/i.test(label)) return '忧';
  return '稳';
};
const typeLabel = (type: string) => type === 'quick_meow' ? '喵喵卡' : type === 'image' ? '图片' : type === 'audio' ? '语音' : '文本';

watch(activeTab, () => {
  void loadByTab();
});

onMounted(() => {
  void loadAll();
});
</script>

<style scoped>
.admin-page {
  min-height: 100dvh;
  padding: 0 14px 36px;
  background:
    radial-gradient(circle at 18% 0%, rgba(255, 214, 179, 0.62), transparent 34%),
    linear-gradient(180deg, #fff8f3 0%, #f5f7fb 32%, #eef3f7 100%);
  color: #172033;
}

.admin-hero {
  margin: 0 -14px;
  padding: 12px 14px 16px;
}

.admin-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.icon-btn {
  display: grid;
  width: 40px;
  height: 40px;
  place-items: center;
  border: 0;
  border-radius: 14px;
  color: #172033;
  cursor: pointer;
  transition: transform 0.14s ease;
}

.icon-btn:active,
.stat-card:active,
.admin-tab:active,
.text-btn:active,
.primary-btn:active {
  transform: scale(0.96);
}

.glass {
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 8px 24px rgba(21, 31, 48, 0.08);
}

.accent {
  background: #172033;
  color: #fff;
  box-shadow: 0 10px 24px rgba(23, 32, 51, 0.16);
}

.admin-title-block {
  min-width: 0;
  flex: 1;
}

.eyebrow,
.hero-kicker {
  display: block;
  color: #f97316;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.admin-title-block h1 {
  margin: 2px 0 0;
  font-size: 24px;
  line-height: 1.1;
  font-weight: 900;
  letter-spacing: 0;
}

.hero-panel {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 14px;
  margin-top: 14px;
  padding: 18px;
  border: 1px solid rgba(255, 255, 255, 0.7);
  border-radius: 24px;
  background: linear-gradient(135deg, rgba(23, 32, 51, 0.95), rgba(38, 57, 77, 0.92));
  color: #fff;
  box-shadow: 0 18px 42px rgba(23, 32, 51, 0.18);
}

.hero-number {
  margin-top: 4px;
  font-size: 42px;
  line-height: 1;
  font-weight: 900;
}

.hero-panel p {
  margin: 8px 0 0;
  color: rgba(255, 255, 255, 0.68);
  font-size: 12px;
}

.hero-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}

.hero-metrics span,
.config-safe-note {
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  color: rgba(255, 255, 255, 0.86);
  padding: 5px 8px;
  font-size: 11px;
  font-weight: 900;
}

.hero-status {
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  gap: 6px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  padding: 8px 10px;
  font-size: 12px;
  font-weight: 800;
}

.hero-status span,
.hero-status .warning {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #34d399;
}

.hero-status .warning {
  background: #fbbf24;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 9px;
  margin-top: -2px;
}

.stat-card {
  display: flex;
  min-width: 0;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
  border: 1px solid rgba(226, 232, 240, 0.92);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.92);
  padding: 12px;
  text-align: left;
  box-shadow: 0 12px 26px rgba(23, 32, 51, 0.06);
}

.stat-icon {
  display: grid;
  width: 30px;
  height: 30px;
  place-items: center;
  border-radius: 11px;
  background: #fff3ea;
  color: #f97316;
}

.stat-card strong {
  font-size: 20px;
  line-height: 1;
  font-weight: 900;
  color: #172033;
}

.stat-card small {
  color: #748094;
  font-size: 12px;
  font-weight: 700;
}

.admin-tabs {
  display: flex;
  gap: 8px;
  margin: 14px -14px 0;
  overflow-x: auto;
  padding: 0 14px 2px;
  scrollbar-width: none;
}

.admin-tabs::-webkit-scrollbar {
  display: none;
}

.admin-tab {
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  gap: 5px;
  border: 1px solid #dde5ee;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.78);
  padding: 9px 12px;
  color: #748094;
  font-size: 12px;
  font-weight: 800;
}

.admin-tab.active {
  border-color: #172033;
  background: #172033;
  color: #fff;
  box-shadow: 0 10px 22px rgba(23, 32, 51, 0.16);
}

.admin-content {
  margin-top: 14px;
}

.state-panel,
.empty-state {
  display: grid;
  min-height: 180px;
  place-items: center;
  border: 1px dashed #ccd6e2;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.62);
  color: #748094;
  font-size: 13px;
}

.empty-state {
  gap: 4px;
}

.empty-state span {
  font-weight: 900;
  color: #172033;
}

.empty-state p {
  margin: 0;
}

.overview-layout,
.admin-list,
.system-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.section-title {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin: 2px 2px 0;
}

.section-title h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 900;
}

.section-title span {
  color: #748094;
  font-size: 12px;
  font-weight: 800;
}

.section-title.compact {
  margin-top: 6px;
}

.pulse-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}

.pulse-card {
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.92);
  padding: 13px;
  box-shadow: 0 12px 26px rgba(23, 32, 51, 0.06);
}

.pulse-card span {
  color: #748094;
  font-size: 11px;
  font-weight: 800;
}

.pulse-card strong {
  display: block;
  margin-top: 6px;
  color: #f97316;
  font-size: 24px;
  line-height: 1;
  font-weight: 900;
}

.pulse-card.teal strong {
  color: #0f766e;
}

.pulse-card.violet strong {
  color: #6d5bd0;
}

.chart-panel,
.activity-list,
.system-panel {
  border: 1px solid rgba(226, 232, 240, 0.92);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.92);
  padding: 12px;
  box-shadow: 0 12px 26px rgba(23, 32, 51, 0.06);
}

.chart-row {
  display: grid;
  grid-template-columns: 42px 1fr 28px;
  align-items: center;
  gap: 8px;
  padding: 7px 0;
  color: #748094;
  font-size: 12px;
  font-weight: 800;
}

.chart-track {
  height: 8px;
  overflow: hidden;
  border-radius: 999px;
  background: #edf2f7;
}

.chart-track i {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #f97316, #14b8a6);
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.activity-item {
  display: grid;
  grid-template-columns: 36px 1fr auto;
  align-items: center;
  gap: 10px;
  border-radius: 15px;
  background: #f7fafc;
  padding: 10px;
}

.activity-icon,
.avatar {
  display: grid;
  place-items: center;
  border-radius: 14px;
  font-weight: 900;
}

.activity-icon {
  width: 36px;
  height: 36px;
  background: #fff3ea;
  color: #f97316;
}

.activity-icon.emotion {
  background: #eef2ff;
  color: #5b5bd6;
}

.activity-item strong,
.card-text strong {
  display: block;
  color: #172033;
  font-size: 14px;
  font-weight: 900;
}

.activity-item p,
.card-text span {
  display: block;
  margin: 2px 0 0;
  overflow: hidden;
  color: #748094;
  font-size: 12px;
  line-height: 1.35;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.activity-item time,
.card-main time,
.meta-row time {
  color: #748094;
  font-size: 11px;
  font-weight: 800;
}

.empty-inline {
  padding: 16px 0;
  text-align: center;
  color: #748094;
  font-size: 12px;
}

.filter-row {
  display: grid;
  grid-template-columns: 1fr 86px;
  gap: 8px;
}

.kind-select {
  height: 44px;
  border: 1px solid #dbe4ee;
  border-radius: 999px;
  background: #fff;
  color: #172033;
  padding: 0 10px;
  font-size: 13px;
  font-weight: 800;
  outline: none;
}

.data-card {
  border: 1px solid rgba(226, 232, 240, 0.92);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.92);
  padding: 13px;
  box-shadow: 0 12px 26px rgba(23, 32, 51, 0.06);
}

.data-card.clickable {
  cursor: pointer;
}

.card-main {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.avatar {
  width: 42px;
  height: 42px;
  flex-shrink: 0;
  color: #fff;
}

.avatar.user {
  background: linear-gradient(135deg, #f97316, #fb7185);
}

.avatar.pet {
  background: linear-gradient(135deg, #14b8a6, #0f766e);
}

.avatar.health {
  background: linear-gradient(135deg, #38bdf8, #2563eb);
}

.avatar.health.feeding {
  background: linear-gradient(135deg, #e06912, #f97316);
}

.avatar.signal {
  background: linear-gradient(135deg, #6d5bd0, #9f7aea);
}

.avatar.msg {
  background: linear-gradient(135deg, #172033, #40506a);
}

.card-text {
  min-width: 0;
  flex: 1;
}

.badge {
  flex-shrink: 0;
  border-radius: 999px;
  padding: 5px 8px;
  font-size: 11px;
  font-weight: 900;
}

.badge.admin {
  background: #eef2ff;
  color: #4f46e5;
}

.badge.normal {
  background: #ecfdf5;
  color: #047857;
}

.action-row {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 11px;
  border-top: 1px solid #edf2f7;
  padding-top: 10px;
}

.text-btn,
.round-danger,
.primary-btn {
  border: 0;
  cursor: pointer;
  font-weight: 900;
  transition: transform 0.14s ease, opacity 0.14s ease;
}

.text-btn {
  flex: 0 1 auto;
  border-radius: 12px;
  background: #eef3f8;
  color: #172033;
  padding: 8px 11px;
  font-size: 12px;
}

.text-btn.warn {
  background: #fff7ed;
  color: #f97316;
}

.text-btn.danger {
  background: #fef2f2;
  color: #b91c1c;
}

.round-danger {
  display: grid;
  width: 34px;
  height: 34px;
  flex-shrink: 0;
  place-items: center;
  border-radius: 12px;
  background: #fef2f2;
  color: #b91c1c;
}

.dynamic-content {
  display: -webkit-box;
  margin: 0;
  overflow: hidden;
  color: #172033;
  font-size: 14px;
  line-height: 1.62;
  white-space: pre-wrap;
  word-break: break-word;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 4;
}

.meta-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-top: 8px;
  color: #748094;
  font-size: 12px;
  font-weight: 700;
}

.recommend-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  width: fit-content;
  margin-top: 10px;
  padding: 4px 10px;
  border-radius: 999px;
  background: #fff7ed;
  color: #ea580c;
  font-size: 12px;
  font-weight: 900;
}

.meta-row span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.meta-row.single {
  justify-content: flex-end;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.form-field span {
  color: #172033;
  font-size: 13px;
  font-weight: 900;
}

.form-field input {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid #dbe4ee;
  border-radius: 15px;
  background: #f8fafc;
  color: #172033;
  outline: none;
  padding: 12px;
  font-size: 14px;
}

.form-field input:focus {
  border-color: #f97316;
  background: #fff;
}

.config-note {
  border-radius: 15px;
  background: #f7fafc;
  color: #748094;
  padding: 12px;
  font-size: 12px;
  line-height: 1.6;
}

.config-safe-note {
  border-radius: 14px;
  background: #ecfdf5;
  color: #047857;
  line-height: 1.5;
}

@media (max-width: 380px) {
  .stat-card {
    padding: 10px;
  }

  .card-main {
    align-items: flex-start;
  }

  .action-row {
    justify-content: flex-start;
  }

  .text-btn {
    flex: 1 1 calc(50% - 8px);
  }
}

.topic-admin .topic-card {
  display: grid;
  gap: 12px;
  background: linear-gradient(135deg, #fff 0%, #fff8f2 100%);
}

.topic-create-row {
  display: flex;
  gap: 8px;
}

.topic-create-row input,
.topic-name-input,
.topic-controls input[type="number"] {
  min-width: 0;
  border: 1px solid #dbe4ee;
  border-radius: 12px;
  background: #fff;
  color: #172033;
  outline: none;
  padding: 10px 12px;
  font-size: 14px;
  font-weight: 800;
}

.topic-create-row input {
  flex: 1;
}

.primary-btn.compact {
  flex-shrink: 0;
  padding: 10px 14px;
  box-shadow: 0 8px 18px rgba(249, 115, 22, 0.2);
}

.topic-name-input {
  width: 100%;
  padding: 8px 10px;
}

.topic-controls {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.topic-controls label {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.75);
  color: #748094;
  padding: 7px 10px;
  font-size: 12px;
  font-weight: 900;
}

.topic-controls input[type="number"] {
  width: 76px;
  padding: 7px 9px;
}

.avatar.topic {
  background: linear-gradient(135deg, #f97316, #14b8a6);
  font-size: 22px;
}

.password-dialog {
  padding: 2px 18px 18px;
}

.password-dialog p {
  margin: 0 0 12px;
  color: #748094;
  font-size: 13px;
  line-height: 1.55;
}

.password-dialog input {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid #dbe4ee;
  border-radius: 14px;
  background: #f8fafc;
  color: #172033;
  outline: none;
  padding: 12px;
  font-size: 14px;
}

.password-dialog input:focus {
  border-color: #f97316;
  background: #fff;
}

.primary-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  border-radius: 16px;
  background: linear-gradient(135deg, #e06912, #f97316);
  color: #fff;
  padding: 13px 16px;
  font-size: 15px;
  font-weight: 800;
  box-shadow: 0 12px 28px rgba(249, 115, 22, 0.28);
}

.primary-btn:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

:deep(.van-search) {
  padding: 0;
  background: transparent;
}

:deep(.van-search__content) {
  border: 1px solid #dbe4ee;
  background: rgba(255, 255, 255, 0.82);
}
</style>
