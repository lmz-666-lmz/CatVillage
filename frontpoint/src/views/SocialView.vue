<template>
  <div class="page-container social-page">
    <header class="topbar">
      <div class="brand">智宠通译</div>
      <div class="search-box">
        <van-icon name="search" />
        <span>搜索宠物动态</span>
      </div>
      <van-icon name="setting-o" size="24" color="#5b6981" />
    </header>

    <van-tabs v-model:active="activeTab" line-width="34" line-height="3" color="#ff8a00">
      <van-tab title="关注" name="follow" />
      <van-tab title="推荐" name="recommend" />
      <van-tab title="同城" name="city" />
    </van-tabs>

    <section class="feed-list">
      <article class="post-card" v-for="item in feedList" :key="item.id">
        <div class="post-head">
          <div class="author">
            <div class="avatar">🐱</div>
            <div>
              <h3>{{ item.author }}</h3>
              <p>{{ item.time }} · {{ item.city }}</p>
            </div>
          </div>
          <button class="more-btn" type="button">···</button>
        </div>

        <div class="post-images" :class="{ single: item.images.length === 1 }">
          <div class="image-box" v-for="(image, idx) in item.images" :key="idx" :style="{ background: image }" />
        </div>

        <p class="post-text">{{ item.content }}</p>

        <div class="translate-box">
          <div class="play-icon">▶</div>
          <div class="translate-text">AI 翻译：{{ item.translation }}</div>
          <div class="duration">0:04</div>
        </div>

        <div class="post-actions">
          <button type="button" @click="item.likes += 1">❤ {{ item.likes }}</button>
          <button type="button">💬 {{ item.comments }}</button>
          <button type="button">↗ 分享</button>
        </div>
      </article>
    </section>

    <button class="add-post" type="button" @click="router.push({ name: 'CreatePost' })">＋</button>

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
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const activeTab = ref('recommend');

const feedList = ref([
  {
    id: '1',
    author: '芝士奶盖酱',
    time: '15分钟前',
    city: '杭州',
    images: ['linear-gradient(135deg, #8a5b2b 0%, #3b2b1a 100%)'],
    content: '今天的大橘好像有很多话要说，一直对着我喵喵叫。用了智宠通译才知道，原来它是饿了想吃罐罐了！',
    translation: '我想吃鱼肉罐头啦！',
    likes: 1200,
    comments: 84
  },
  {
    id: '2',
    author: '布丁的铲屎官',
    time: '1小时前',
    city: '上海',
    images: ['linear-gradient(135deg, #96653d 0%, #3a291f 100%)', 'linear-gradient(135deg, #7d4f2f 0%, #2f1e17 100%)'],
    content: '今天带布丁去体检，小家伙有点紧张，一直在喵喵抗议。翻译结果是：我想回家躲在被子里。',
    translation: '这里太陌生了，我想回家',
    likes: 328,
    comments: 12
  }
]);
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #f6f7f9;
  padding: 10px 14px 84px;
}

.topbar {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 10px;
  align-items: center;
}

.brand {
  color: #ff7f00;
  font-size: 30px;
  font-weight: 800;
  white-space: nowrap;
}

.search-box {
  height: 38px;
  border-radius: 999px;
  border: 1px solid #e9edf3;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 12px;
  color: #8b9ab3;
  background: #fff;
}

.feed-list {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.post-card {
  background: #fff;
  border-radius: 16px;
  border: 1px solid #eceff4;
  padding: 12px;
}

.post-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.author {
  display: flex;
  gap: 8px;
  align-items: center;
}

.avatar {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: #ffe7c6;
  display: grid;
  place-items: center;
}

.author h3 {
  margin: 0;
  color: #121a2b;
  font-size: 18px;
}

.author p {
  margin: 2px 0 0;
  color: #73829a;
  font-size: 12px;
}

.more-btn {
  border: none;
  background: transparent;
  color: #ff9800;
  font-size: 18px;
}

.post-images {
  margin-top: 10px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.post-images.single {
  grid-template-columns: 1fr;
}

.image-box {
  height: 180px;
  border-radius: 12px;
}

.post-text {
  margin: 10px 0;
  color: #1b2538;
  line-height: 1.7;
}

.translate-box {
  border-radius: 14px;
  border: 1px solid #f2ddbf;
  background: #fffaf2;
  padding: 10px;
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 8px;
}

.play-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #ff9800;
  color: #fff;
  display: grid;
  place-items: center;
}

.translate-text {
  color: #ff8a00;
  font-weight: 700;
}

.duration {
  color: #ffa84a;
}

.post-actions {
  margin-top: 10px;
  display: flex;
  gap: 18px;
}

.post-actions button {
  border: none;
  background: transparent;
  color: #61738e;
  padding: 0;
}

.add-post {
  position: fixed;
  left: 50%;
  transform: translateX(-50%);
  bottom: 68px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: 3px solid #fff;
  background: #ff4b4b;
  color: #fff;
  font-size: 34px;
  line-height: 1;
  box-shadow: 0 8px 16px rgba(255, 75, 75, 0.28);
}

:deep(.van-tabbar-item--active),
:deep(.van-tabs__nav .van-tab--active) {
  color: #ff8a00;
}
</style>
