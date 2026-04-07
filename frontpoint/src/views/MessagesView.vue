<template>
  <div class="page-container messages-page">
    <!-- 会话列表视图 -->
    <template v-if="!activeConversation">
      <header class="topbar">
        <div class="brand">消息</div>
        <van-icon name="plus" size="24" color="#5b6981" @click="showToast({ message: '添加好友功能开发中' })" />
      </header>

      <div class="search-wrap">
        <div class="search-box">
          <van-icon name="search" size="16" color="#8b9ab3" />
          <input v-model="searchKeyword" class="search-input" placeholder="搜索会话" />
        </div>
      </div>

      <div v-if="loading" class="center-tip">
        <van-loading type="spinner" color="#ff8a00" />
      </div>

      <div v-else-if="filteredConversations.length === 0" class="empty-tip">
        <van-icon name="chat-o" size="56" color="#d0d7e3" />
        <p>暂无会话，去广场认识新朋友吧</p>
        <van-button round type="primary" class="go-btn" @click="router.push({ name: 'Social' })">
          去广场逛逛
        </van-button>
      </div>

      <ul v-else class="conv-list">
        <li
          v-for="conv in filteredConversations"
          :key="conv.id"
          class="conv-item"
          @click="openConversation(conv)"
        >
          <div class="conv-avatar">
            <span class="avatar-emoji">🐱</span>
            <span v-if="conv.isOnline" class="online-dot" />
          </div>
          <div class="conv-body">
            <div class="conv-head">
              <span class="conv-name">{{ conv.nickname }}</span>
              <span class="conv-time">{{ formatTime(conv.updatedAt) }}</span>
            </div>
            <div class="conv-preview">
              <span class="conv-last">{{ conv.lastMessage }}</span>
              <span v-if="conv.unreadCount > 0" class="unread-badge">{{ conv.unreadCount }}</span>
            </div>
          </div>
        </li>
      </ul>
    </template>

    <!-- 聊天视图 -->
    <template v-else>
      <van-nav-bar
        :title="activeConversation.nickname"
        left-arrow
        @click-left="closeChat"
      >
        <template #right>
          <van-icon name="ellipsis" size="22" color="#5b6981" />
        </template>
      </van-nav-bar>

      <div class="chat-body" ref="chatBodyRef">
        <div v-if="chatLoading" class="center-tip">
          <van-loading type="spinner" color="#ff8a00" />
        </div>

        <template v-else>
          <div
            v-for="msg in chatMessages"
            :key="msg.id"
            class="msg-row"
            :class="{ mine: msg.senderId !== activeConversation.targetUserId }"
          >
            <!-- 对方消息：显示对方头像在左 -->
            <div v-if="msg.senderId === activeConversation.targetUserId" class="msg-avatar">🐱</div>
            <div class="msg-bubble" :class="{ mine: msg.senderId !== activeConversation.targetUserId }">
              {{ msg.content }}
            </div>
            <!-- 我的消息：显示自己头像在右 -->
            <div v-if="msg.senderId !== activeConversation.targetUserId" class="msg-avatar self">🧑</div>
          </div>
        </template>
      </div>

      <div class="input-bar">
        <van-icon name="smile-o" size="24" color="#8b9ab3" />
        <input
          v-model="newMessage"
          class="msg-input"
          placeholder="说点什么..."
          @keyup.enter="sendMsg"
        />
        <button
          type="button"
          class="send-btn"
          :disabled="!newMessage.trim() || sending"
          @click="sendMsg"
        >
          <van-icon name="play" color="#fff" size="18" />
        </button>
      </div>
    </template>

    <van-tabbar v-if="!activeConversation" route>
      <van-tabbar-item icon="location-o" to="/social">广场</van-tabbar-item>
      <van-tabbar-item icon="setting-o" to="/ai-assistant">AI助理</van-tabbar-item>
      <van-tabbar-item icon="smile-o" to="/emotions">喵喵台</van-tabbar-item>
      <van-tabbar-item icon="chat-o" to="/messages">消息</van-tabbar-item>
      <van-tabbar-item icon="contact-o" to="/cats">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';
import { getConversationList, getConversationMessages, sendMessage } from '@/api/apiService';
import type { ConversationResponse, MessageResponse } from '@/types/message';

const router = useRouter();

// 会话列表状态
const loading = ref(false);
const conversations = ref<ConversationResponse[]>([]);
const searchKeyword = ref('');

// 聊天状态
const activeConversation = ref<ConversationResponse | null>(null);
const chatMessages = ref<MessageResponse[]>([]);
const chatLoading = ref(false);
const newMessage = ref('');
const sending = ref(false);
const chatBodyRef = ref<HTMLElement | null>(null);

const filteredConversations = computed(() => {
  if (!searchKeyword.value.trim()) return conversations.value;
  const kw = searchKeyword.value.trim().toLowerCase();
  return conversations.value.filter(c => c.nickname.toLowerCase().includes(kw));
});

const formatTime = (iso: string): string => {
  if (!iso) return '';
  const date = new Date(iso);
  const now = Date.now();
  const diffMs = now - date.getTime();
  const diffMin = Math.floor(diffMs / 60000);
  if (diffMin < 1) return '刚刚';
  if (diffMin < 60) return `${diffMin}分钟前`;
  const diffHour = Math.floor(diffMin / 60);
  if (diffHour < 24) return `${diffHour}小时前`;
  const diffDay = Math.floor(diffHour / 24);
  if (diffDay < 7) return `${diffDay}天前`;
  return `${date.getMonth() + 1}/${date.getDate()}`;
};

const loadConversations = async () => {
  loading.value = true;
  try {
    const res = await getConversationList({ page: 1, pageSize: 20 });
    conversations.value = res.data.list || [];
  } catch {
    showToast({ type: 'fail', message: '加载会话失败，请稍后重试' });
  } finally {
    loading.value = false;
  }
};

const openConversation = async (conv: ConversationResponse) => {
  activeConversation.value = conv;
  chatMessages.value = [];
  chatLoading.value = true;
  // 清零未读数（前端乐观更新）
  conv.unreadCount = 0;
  try {
    const res = await getConversationMessages(conv.targetUserId, { page: 1, pageSize: 30 });
    // 接口返回倒序（最新在前），展示时翻转为正序
    chatMessages.value = [...(res.data.list || [])].reverse();
  } catch {
    showToast({ type: 'fail', message: '加载消息失败' });
  } finally {
    chatLoading.value = false;
    await nextTick();
    scrollToBottom();
  }
};

const closeChat = () => {
  activeConversation.value = null;
  chatMessages.value = [];
  newMessage.value = '';
};

const sendMsg = async () => {
  const text = newMessage.value.trim();
  if (!text || !activeConversation.value) return;

  sending.value = true;
  const optimistic: MessageResponse = {
    id: `tmp-${Date.now()}`,
    senderId: 'optimistic',
    receiverId: activeConversation.value.targetUserId,
    content: text,
    messageType: 'text',
    sentAt: new Date().toISOString(),
    status: 'sent',
  };
  chatMessages.value.push(optimistic);
  newMessage.value = '';
  await nextTick();
  scrollToBottom();

  try {
    const res = await sendMessage({
      receiverId: activeConversation.value.targetUserId,
      content: text,
      messageType: 'text',
    });
    // 替换乐观消息为服务端真实消息
    const idx = chatMessages.value.findIndex(m => m.id === optimistic.id);
    if (idx !== -1) {
      chatMessages.value[idx] = res.data;
    }
    // 更新会话预览
    activeConversation.value.lastMessage = text;
    activeConversation.value.updatedAt = new Date().toISOString();
  } catch {
    showToast({ type: 'fail', message: '发送失败，请重试' });
    // 回滚乐观消息
    chatMessages.value = chatMessages.value.filter(m => m.id !== optimistic.id);
    newMessage.value = text;
  } finally {
    sending.value = false;
  }
};

const scrollToBottom = () => {
  if (chatBodyRef.value) {
    chatBodyRef.value.scrollTop = chatBodyRef.value.scrollHeight;
  }
};

onMounted(loadConversations);
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #f6f7f9;
}

/* ── 会话列表 ─────────────────────────── */
.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px 6px;
}

.brand {
  color: #ff7f00;
  font-size: 30px;
  font-weight: 800;
}

.search-wrap {
  padding: 6px 16px 10px;
}

.search-box {
  height: 40px;
  border-radius: 999px;
  background: #fff;
  border: 1px solid #e9edf3;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 14px;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 14px;
  color: #243145;
  background: transparent;
}

.center-tip {
  display: flex;
  justify-content: center;
  padding: 60px 0;
}

.empty-tip {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 24px 0;
  gap: 10px;
  color: #8b9ab3;
  text-align: center;
}

.go-btn {
  margin-top: 6px;
  background: linear-gradient(135deg, #ff9900 0%, #ff7a00 100%);
  border: none;
}

.conv-list {
  list-style: none;
  margin: 0;
  padding: 0 0 84px;
}

.conv-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #fff;
  border-bottom: 1px solid #f2f4f7;
}

.conv-avatar {
  position: relative;
  flex-shrink: 0;
}

.avatar-emoji {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  background: #ffe7c6;
  display: grid;
  place-items: center;
  font-size: 26px;
}

.online-dot {
  position: absolute;
  right: -2px;
  bottom: -2px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #52c41a;
  border: 2px solid #fff;
}

.conv-body {
  flex: 1;
  min-width: 0;
}

.conv-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.conv-name {
  font-size: 15px;
  font-weight: 600;
  color: #121a2b;
}

.conv-time {
  font-size: 12px;
  color: #8b9ab3;
}

.conv-preview {
  margin-top: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.conv-last {
  font-size: 13px;
  color: #73829a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}

.unread-badge {
  flex-shrink: 0;
  min-width: 18px;
  height: 18px;
  border-radius: 999px;
  background: #ff4b4b;
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  display: grid;
  place-items: center;
  padding: 0 4px;
}

/* ── 聊天窗口 ─────────────────────────── */
.chat-body {
  overflow-y: auto;
  padding: 12px 16px 80px;
  height: calc(100vh - 46px);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.msg-row {
  display: flex;
  align-items: flex-end;
  gap: 8px;
}

.msg-row.mine {
  justify-content: flex-end;
}

.msg-avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: #ffe7c6;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  font-size: 18px;
}

.msg-avatar.self {
  background: #e2f3ff;
}

.msg-bubble {
  max-width: 72%;
  background: #fff;
  border: 1px solid #eceff4;
  border-radius: 16px 16px 16px 4px;
  padding: 10px 14px;
  line-height: 1.6;
  color: #232d3f;
  word-break: break-word;
}

.msg-bubble.mine {
  background: #fff8ee;
  border-color: #f2e2cd;
  border-radius: 16px 16px 4px 16px;
}

.input-bar {
  position: fixed;
  left: 14px;
  right: 14px;
  bottom: 12px;
  background: #fff;
  border-radius: 18px;
  border: 1px solid #ecf0f5;
  height: 56px;
  padding: 0 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 8px 16px rgba(19, 36, 64, 0.08);
}

.msg-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 15px;
  color: #243145;
  background: transparent;
}

.send-btn {
  width: 38px;
  height: 38px;
  border: none;
  border-radius: 12px;
  background: #ff9800;
  cursor: pointer;
  display: grid;
  place-items: center;
}

.send-btn:disabled {
  background: #d9dee8;
  cursor: not-allowed;
}

:deep(.van-tabbar-item--active) {
  color: #ff8a00;
}

:deep(.van-nav-bar__title) {
  font-weight: 700;
  color: #121a2b;
}
</style>
