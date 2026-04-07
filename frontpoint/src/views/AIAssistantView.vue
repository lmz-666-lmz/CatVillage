<template>
  <div class="page-container ai-page">
    <header class="topbar">
      <div class="brand">智宠通译</div>
      <van-icon name="setting-o" size="24" color="#5d6b82" />
    </header>

    <section class="hero-card">
      <div class="hero-tag">PRO ASSISTANT</div>
      <h1>猫语实时翻译</h1>
      <p>基于深度学习的音频引擎，为您精准解析猫咪的每一种情绪。</p>
      <div class="hero-actions">
        <van-button round type="primary" class="listen-btn" @click="onListen">开始监听</van-button>
        <div class="sound-bars">
          <span v-for="bar in 6" :key="bar" :style="{ height: `${10 + (bar % 3) * 8}px` }" />
        </div>
      </div>
      <div class="hero-mascot">🐱</div>
    </section>

    <section class="feature-grid">
      <div class="feature-item" @click="router.push({ name: 'Emotions' })">
        <div class="icon blue"><van-icon name="medal-o" /></div>
        <h3>健康体检</h3>
        <p>AI 视觉分析</p>
      </div>
      <div class="feature-item">
        <div class="icon orange"><van-icon name="shop-o" /></div>
        <h3>配餐建议</h3>
        <p>营养平衡助手</p>
      </div>
    </section>

    <section class="shortcut-card">
      <div>
        <h3>行为纠正</h3>
        <p>改善乱抓乱尿</p>
      </div>
      <van-icon name="arrow" size="20" />
    </section>

    <section v-if="!hasCats" class="empty-cat-card">
      <van-icon name="info-o" size="28" color="#ff8a00" />
      <h3>还没有可用的猫咪档案</h3>
      <p>AI 养育助手需要先选择一只猫咪，才能调用后端分析接口。</p>
      <van-button round type="primary" class="empty-action" @click="router.push({ name: 'AddCat' })">
        先去添加猫咪
      </van-button>
    </section>

    <section class="chat-section">
      <div class="section-head">
        <h2>对话助手</h2>
        <span>{{ selectedCatName }}</span>
      </div>

      <div class="chat-list">
        <div v-for="item in messages" :key="item.id" class="chat-item" :class="item.role">
          <div class="avatar">{{ item.role === 'assistant' ? '🤖' : '🧑' }}</div>
          <div class="bubble">{{ item.text }}</div>
        </div>
      </div>
    </section>

    <div class="input-bar">
      <van-icon name="plus" size="22" color="#8b9ab3" />
      <input v-model="question" class="ask-input" placeholder="向 AI 提问关于您的宠物..." @keyup.enter="sendQuestion" />
      <button class="send-btn" type="button" :disabled="!hasCats" @click="sendQuestion">
        <van-icon name="play" color="#fff" size="18" />
      </button>
    </div>

    <van-tabbar route>
      <van-tabbar-item icon="location-o" to="/social">广场</van-tabbar-item>
      <van-tabbar-item icon="setting-o" to="/ai-assistant">AI助理</van-tabbar-item>
      <van-tabbar-item icon="smile-o" to="/emotions">喵喵台</van-tabbar-item>
      <van-tabbar-item icon="chat-o" to="/messages">消息</van-tabbar-item>
      <van-tabbar-item icon="contact-o" to="/cats">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { closeToast, showToast } from 'vant';
import { chatWithAI } from '@/api/apiService';
import { useCatsStore, useCurrentCatStore } from '@/stores';

type ChatRole = 'assistant' | 'user';

const router = useRouter();
const catsStore = useCatsStore();
const currentCatStore = useCurrentCatStore();
const question = ref('');
const messages = ref<Array<{ id: string; role: ChatRole; text: string }>>([
  {
    id: 'init-1',
    role: 'assistant',
    text: '喵！我是您的 AI 养宠专家。您可以上传猫咪照片，或者描述它的行为。'
  },
  {
    id: 'init-2',
    role: 'user',
    text: '我的猫今天一直盯着墙看，它是看到了什么吗？'
  },
  {
    id: 'init-3',
    role: 'assistant',
    text: '这通常与听觉敏感、动态视觉捕捉或狩猎本能有关。你可以先观察它是否伴随甩尾和耳朵转向。'
  }
]);

const selectedCatId = computed(() => currentCatStore.getCurrentCatId || catsStore.getAllCats[0]?.id || '');
const selectedCatName = computed(() => {
  const catId = selectedCatId.value;
  if (!catId) {
    return '未选择猫咪';
  }
  const cat = catsStore.getCatById(catId);
  return cat?.name || '未选择猫咪';
});

const hasCats = computed(() => catsStore.getAllCats.length > 0);

const ensureCatReady = async () => {
  // 始终以服务端列表为准，避免旧缓存导致使用了无效 pet_id
  await catsStore.fetchAllCats();

  const firstCat = catsStore.getAllCats[0];
  if (!currentCatStore.getCurrentCatId && firstCat) {
    currentCatStore.setCurrentCat(firstCat.id);
  }
};

onMounted(async () => {
  try {
    await ensureCatReady();
  } catch (error) {
    showToast({ type: 'fail', message: '加载猫咪档案失败，请先检查登录状态' });
  }
});

const onListen = () => {
  showToast({ message: '已启动实时监听（演示）' });
};

const sendQuestion = async () => {
  const text = question.value.trim();
  if (!text) {
    return;
  }

  if (!hasCats.value) {
    showToast({ type: 'fail', message: '请先添加猫咪档案后再使用 AI 助理' });
    return;
  }

  const catId = selectedCatId.value;
  if (!catId) {
    showToast({ type: 'fail', message: '请先在“我的”页添加并选择一只猫咪' });
    return;
  }

  messages.value.push({ id: `user-${Date.now()}`, role: 'user', text });
  question.value = '';
  showToast({ type: 'loading', message: 'AI 正在思考...', duration: 0 });

  try {
    const res = await chatWithAI({ catId, message: text });
    closeToast();
    messages.value.push({ id: res.data.id, role: 'assistant', text: res.data.message });
  } catch (error) {
    closeToast();
    const requestError = error as { status?: number; message?: string };
    if (requestError.status === 404 && requestError.message?.includes('Cat profile not found')) {
      showToast({ type: 'fail', message: '当前猫咪档案无效，请重新选择或新建' });
      await ensureCatReady();
      return;
    }
    if (requestError.status === 500 && requestError.message?.includes('AI API key is not configured')) {
      showToast({ type: 'fail', message: '后端 AI 密钥未配置，请检查 backend/.env' });
      return;
    }
    messages.value.push({
      id: `fallback-${Date.now()}`,
      role: 'assistant',
      text: '我建议先排查环境噪声、食物与玩具刺激，再观察 1-2 天行为变化。'
    });
    showToast({ type: 'fail', message: requestError.message || '接口暂不可用，已使用本地建议' });
  }
};
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8f9fb 0%, #f4f6fa 100%);
  padding: 12px 16px 126px;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 4px 12px;
}

.brand {
  color: #ff7e00;
  font-size: 30px;
  font-weight: 800;
}

.hero-card {
  background: linear-gradient(135deg, #fffcf7 0%, #f2efe9 100%);
  border-radius: 18px;
  padding: 16px;
  position: relative;
  overflow: hidden;
  border: 1px solid #f0e8dd;
}

.hero-tag {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  background: #fde8c7;
  color: #f38700;
  font-weight: 700;
  font-size: 12px;
}

.hero-card h1 {
  margin: 10px 0 8px;
  font-size: 38px;
  line-height: 1.1;
  color: #121826;
}

.hero-card p {
  margin: 0;
  max-width: 72%;
  color: #5a6d86;
  line-height: 1.6;
}

.hero-actions {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 14px;
}

.listen-btn {
  background: linear-gradient(135deg, #ff9c00 0%, #ff7b00 100%);
  border: none;
  width: 136px;
  font-weight: 700;
  box-shadow: 0 12px 20px rgba(255, 125, 0, 0.28);
}

.sound-bars {
  display: flex;
  align-items: flex-end;
  gap: 4px;
}

.sound-bars span {
  width: 4px;
  border-radius: 4px;
  background: #ffb13a;
}

.hero-mascot {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 124px;
  height: 124px;
  display: grid;
  place-items: center;
  background: #3d3b4a;
  color: #fff;
  font-size: 56px;
}

.feature-grid {
  margin-top: 14px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.feature-item {
  background: #fff;
  border-radius: 16px;
  padding: 16px;
  border: 1px solid #edf0f4;
}

.feature-item h3 {
  margin: 14px 0 6px;
  color: #141b2a;
}

.feature-item p {
  margin: 0;
  color: #73829a;
}

.icon {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  font-size: 22px;
}

.icon.blue {
  background: #e2f3ff;
  color: #0c7cb6;
}

.icon.orange {
  background: #fff3df;
  color: #ff9600;
}

.shortcut-card {
  margin-top: 14px;
  background: linear-gradient(110deg, #122245 0%, #0f1c3d 80%);
  border-radius: 16px;
  padding: 16px;
  color: #dbe8ff;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.shortcut-card h3 {
  margin: 0 0 4px;
  color: #ffa429;
}

.shortcut-card p {
  margin: 0;
}

.empty-cat-card {
  margin-top: 14px;
  border-radius: 16px;
  background: #fff7ed;
  border: 1px solid #ffe2bc;
  padding: 16px;
  text-align: center;
}

.empty-cat-card h3 {
  margin: 10px 0 6px;
  color: #172033;
}

.empty-cat-card p {
  margin: 0;
  color: #61738e;
  line-height: 1.6;
}

.empty-action {
  margin-top: 12px;
  background: linear-gradient(135deg, #ff9c00 0%, #ff7b00 100%);
  border: none;
}

.chat-section {
  margin-top: 18px;
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-head h2 {
  margin: 0;
  font-size: 32px;
  color: #101827;
}

.section-head span {
  color: #6f8098;
  background: #f2f4f7;
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 12px;
}

.chat-list {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.chat-item {
  display: flex;
  gap: 10px;
}

.chat-item.user {
  justify-content: flex-end;
}

.avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #fff1df;
  display: grid;
  place-items: center;
}

.bubble {
  max-width: 82%;
  background: #fff;
  border: 1px solid #eceff4;
  border-radius: 14px;
  padding: 10px 12px;
  line-height: 1.6;
  color: #232d3f;
}

.chat-item.user .bubble {
  background: #fff8ee;
  border-color: #f2e2cd;
}

.input-bar {
  position: fixed;
  left: 14px;
  right: 14px;
  bottom: 58px;
  background: #fff;
  border-radius: 18px;
  border: 1px solid #ecf0f5;
  height: 56px;
  padding: 0 10px;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 10px 18px rgba(19, 36, 64, 0.1);
}

.ask-input {
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
}

.send-btn:disabled {
  background: #d9dee8;
}

:deep(.van-tabbar-item--active) {
  color: #ff8a00;
}
</style>
