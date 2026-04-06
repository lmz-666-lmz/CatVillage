<template>
  <div class="page-container emotions-page">
    <header class="topbar">
      <div class="left-avatar">🐱</div>
      <div class="brand">智宠通译</div>
      <van-icon name="setting-o" size="24" color="#5b6981" />
    </header>

    <section class="listen-panel">
      <h1>喵喵台</h1>
      <p>正在等待猫咪的声音...</p>
      <div class="rings">
        <div class="ring outer" />
        <div class="ring inner" />
        <button type="button" class="listen-core" @click="onTapListen">
          <van-icon name="volume-o" size="24" />
          <span>TAP TO LISTEN</span>
        </button>
      </div>
      <div class="voice-bars">
        <span v-for="index in 7" :key="index" :style="{ height: `${8 + (index % 4) * 8}px` }" />
      </div>
    </section>

    <section class="state-card card">
      <div class="card-head">
        <span class="badge">CURRENT STATE</span>
        <span class="emoji">😸</span>
      </div>
      <h2>心情指数：愉快</h2>
      <p>你的猫咪目前处于非常放松的状态，尾巴轻微摆动。它可能在表达对环境的满意和对您的信任。</p>
      <div class="mood-progress"><span /></div>
      <div class="mood-labels">
        <span>焦虑</span>
        <span>平静</span>
        <span>兴奋</span>
      </div>
    </section>

    <section class="analysis-card">
      <div class="analysis-icon">✨</div>
      <p>AI 深度分析</p>
      <h3>它可能想吃罐头了</h3>
    </section>

    <section class="card chart-card">
      <h3>今日频率</h3>
      <div class="bars">
        <span v-for="(height, idx) in chartData" :key="idx" :style="{ height: `${height}px` }" :class="{ active: idx === 3 }" />
      </div>
      <p class="caption">近6小时活跃度</p>
    </section>

    <section class="card history-card">
      <div class="history-head">
        <h3>历史足迹</h3>
        <button type="button" @click="showToast({ message: '历史列表开发中' })">查看全部</button>
      </div>
      <div class="history-item" v-for="item in histories" :key="item.id">
        <div class="history-icon" :class="item.type">{{ item.type === 'soft' ? '🔊' : '⚠️' }}</div>
        <div>
          <h4>{{ item.title }}</h4>
          <p>{{ item.time }} · 翻译：{{ item.desc }}</p>
        </div>
      </div>
    </section>

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
import { showToast } from 'vant';

const chartData = [30, 50, 78, 40, 86, 22];

const histories = [
  { id: '1', type: 'soft', title: '"喵呜？" (短促)', time: '10:45 AM', desc: '好奇/询问' },
  { id: '2', type: 'warn', title: '"嘶一一" (低沉)', time: '08:12 AM', desc: '警惕/不适' }
];

const onTapListen = () => {
  showToast({ message: '正在监听中（演示）' });
};
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #f6f7f9;
  padding: 8px 16px 84px;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 4px 0 12px;
}

.left-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #ffe8c6;
  display: grid;
  place-items: center;
}

.brand {
  color: #ff7d00;
  font-size: 30px;
  font-weight: 800;
}

.listen-panel {
  text-align: center;
}

.listen-panel h1 {
  margin: 8px 0 6px;
  color: #131a28;
  font-size: 40px;
}

.listen-panel p {
  margin: 0;
  color: #697a95;
}

.rings {
  position: relative;
  margin: 12px auto 0;
  width: 320px;
  height: 320px;
}

.ring {
  border-radius: 50%;
  position: absolute;
  border: 1px solid #f3ddc2;
}

.ring.outer {
  inset: 0;
}

.ring.inner {
  inset: 36px;
}

.listen-core {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 170px;
  height: 170px;
  border: none;
  border-radius: 50%;
  color: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-weight: 700;
  background: linear-gradient(140deg, #ffa300 0%, #ff8900 100%);
  box-shadow: 0 16px 28px rgba(255, 137, 0, 0.28);
}

.voice-bars {
  margin-top: -22px;
  display: flex;
  justify-content: center;
  align-items: flex-end;
  gap: 4px;
}

.voice-bars span {
  width: 4px;
  border-radius: 3px;
  background: #ffae3d;
}

.card {
  margin-top: 14px;
  border-radius: 16px;
  background: #fff;
  border: 1px solid #edf0f5;
  padding: 14px;
}

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.badge {
  border-radius: 999px;
  background: #ffedd8;
  color: #ff8a00;
  font-size: 11px;
  padding: 4px 8px;
  font-weight: 700;
}

.emoji {
  font-size: 20px;
}

.state-card h2 {
  margin: 10px 0;
  color: #121a2b;
}

.state-card p {
  margin: 0;
  color: #5f6f87;
  line-height: 1.6;
}

.mood-progress {
  margin-top: 14px;
  height: 8px;
  border-radius: 999px;
  background: #e8edf4;
}

.mood-progress span {
  display: block;
  width: 84%;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #ff9300 0%, #ff7a00 100%);
}

.mood-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 6px;
  color: #70829e;
  font-size: 12px;
}

.analysis-card {
  margin-top: 14px;
  border-radius: 16px;
  padding: 16px;
  text-align: center;
  background: linear-gradient(135deg, #ff9b00 0%, #ff8600 100%);
  color: #fff;
}

.analysis-card p {
  margin: 2px 0 8px;
  opacity: 0.9;
}

.analysis-card h3 {
  margin: 0;
  font-size: 28px;
}

.analysis-icon {
  font-size: 26px;
}

.chart-card h3,
.history-card h3 {
  margin: 0;
  color: #121a2b;
}

.bars {
  margin: 12px 0 4px;
  height: 96px;
  display: flex;
  align-items: flex-end;
  gap: 8px;
}

.bars span {
  flex: 1;
  border-radius: 2px;
  background: #f2dfc1;
}

.bars span.active {
  background: #ff9800;
}

.caption {
  margin: 0;
  text-align: center;
  color: #7a8ba4;
  font-size: 12px;
}

.history-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-head button {
  border: none;
  background: transparent;
  color: #ff8a00;
  font-weight: 700;
}

.history-item {
  margin-top: 12px;
  display: flex;
  gap: 10px;
  align-items: center;
}

.history-icon {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: grid;
  place-items: center;
}

.history-icon.soft {
  background: #e8f5ff;
}

.history-icon.warn {
  background: #fff0f0;
}

.history-item h4 {
  margin: 0;
  color: #121a2b;
}

.history-item p {
  margin: 2px 0 0;
  color: #6e7f98;
  font-size: 12px;
}

:deep(.van-tabbar-item--active) {
  color: #ff8a00;
}
</style>
