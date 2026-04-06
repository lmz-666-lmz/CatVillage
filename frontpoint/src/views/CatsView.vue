<template>
  <div class="page-container profile-page">
    <header class="profile-head">
      <h1>我的</h1>
      <van-icon name="setting-o" size="24" color="#495e7d" />
    </header>

    <section class="user-panel">
      <div class="avatar-wrap">
        <div class="avatar">👩</div>
        <button type="button" class="edit-btn" @click="router.push({ name: 'UserProfile' })">✎</button>
      </div>
      <h2>阿墨与他的猫</h2>
      <p>ID: 88293011</p>
      <small>“希望能听懂每一个喵呜声”</small>
    </section>

    <section class="stats-card">
      <div><strong>1.5k</strong><span>获赞</span></div>
      <div><strong>342</strong><span>关注</span></div>
      <div><strong>2.8k</strong><span>粉丝</span></div>
    </section>

    <section class="pet-section">
      <div class="pet-section-head">
        <h3>我的萌宠</h3>
        <van-button round size="small" type="primary" plain @click="router.push({ name: 'AddCat' })">
          继续添加
        </van-button>
      </div>
      <div v-if="cats.length === 0" class="add-pet-card">
        <div class="plus-circle">＋</div>
        <h4>添加萌宠档案</h4>
        <p>开启AI翻译、健康管理、成长记录等专属功能</p>
        <van-button round type="primary" @click="router.push({ name: 'AddCat' })">立即开启</van-button>
      </div>

      <div v-else class="pet-list">
        <div class="pet-item" v-for="cat in cats" :key="cat.id" @click="router.push(`/cats/${cat.id}/edit`)">
          <van-image :src="cat.avatarUrl || defaultAvatar" fit="cover" width="56" height="56" round />
          <div>
            <h4>{{ cat.name }}</h4>
            <p>{{ cat.breed || '中华田园猫' }} · {{ Math.floor(cat.age / 12) }}岁{{ cat.age % 12 }}个月</p>
          </div>
        </div>
      </div>
    </section>

    <section class="post-section">
      <div class="post-tabs">
        <button type="button" class="active">我的发布</button>
        <button type="button">赞过内容</button>
      </div>
      <div class="post-grid">
        <div class="post-card" v-for="post in postList" :key="post.id">
          <div class="cover" :style="{ background: post.bg }" />
          <p>{{ post.text }}</p>
          <span>🧡 {{ post.likes }}</span>
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
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { closeToast, showToast } from 'vant';
import { getAllPetProfiles } from '@/api/apiService';
import type { CatProfileResponse } from '@/types/cat';

const router = useRouter();
const defaultAvatar = 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg';
const cats = ref<CatProfileResponse[]>([]);

const postList = ref([
  {
    id: '1',
    bg: 'linear-gradient(135deg, #4a5d6c 0%, #b2b8bf 100%)',
    text: '今天翻译了一下午餐的叫声，原来它是想吃罐罐了...',
    likes: 128
  },
  {
    id: '2',
    bg: 'linear-gradient(135deg, #d7d9dc 0%, #f2f3f6 100%)',
    text: '芝麻的新衣服，帅气逼人！',
    likes: 89
  },
  {
    id: '3',
    bg: 'linear-gradient(135deg, #3f4f32 0%, #97aa6f 100%)',
    text: '周末去野餐啦，两只都玩疯了。',
    likes: 243
  },
  {
    id: '4',
    bg: 'linear-gradient(135deg, #80542f 0%, #e6b98d 100%)',
    text: '捕捉到一个呆滞表情包。',
    likes: 56
  }
]);

onMounted(async () => {
  try {
    showToast({ type: 'loading', message: '正在同步萌宠档案...', duration: 0 });
    const res = await getAllPetProfiles();
    cats.value = res.data.list || [];
    closeToast();
  } catch (error) {
    closeToast();
    const requestError = error as { status?: number; message?: string };
    if (requestError.status === 401) {
      showToast({ type: 'fail', message: '登录已失效，请重新登录' });
      router.replace({ name: 'Login' });
      return;
    }
    if (requestError.status === 500) {
      showToast({ type: 'fail', message: '服务器开小差了，请稍后再试' });
      return;
    }
    showToast({ type: 'fail', message: requestError.message || '获取猫咪档案失败' });
  }
});
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #f7f7f8;
  padding: 12px 14px 84px;
}

.profile-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.profile-head h1 {
  margin: 0;
  font-size: 44px;
  color: #101725;
}

.user-panel {
  margin-top: 8px;
  text-align: center;
}

.avatar-wrap {
  margin: 0 auto;
  width: 114px;
  height: 114px;
  position: relative;
}

.avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: #f6d9af;
  border: 4px solid #fff;
  display: grid;
  place-items: center;
  font-size: 56px;
}

.edit-btn {
  position: absolute;
  right: -2px;
  bottom: 4px;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: 2px solid #fff;
  background: #ff9500;
  color: #fff;
}

.user-panel h2 {
  margin: 10px 0 4px;
  color: #0f1729;
}

.user-panel p {
  margin: 0;
  color: #576a86;
}

.user-panel small {
  display: block;
  margin-top: 6px;
  color: #667892;
}

.stats-card {
  margin-top: 14px;
  border-radius: 20px;
  background: #fff;
  border: 1px solid #e8edf4;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  padding: 16px 0;
}

.stats-card div {
  text-align: center;
}

.stats-card strong {
  display: block;
  color: #111827;
  font-size: 30px;
}

.stats-card span {
  color: #607189;
}

.pet-section {
  margin-top: 16px;
}

.pet-section-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.pet-section h3 {
  margin: 0;
  color: #101827;
  font-size: 32px;
}

.add-pet-card {
  background: #fff;
  border: 2px dashed #f3c98e;
  border-radius: 20px;
  padding: 18px;
  text-align: center;
}

.plus-circle {
  width: 66px;
  height: 66px;
  border-radius: 50%;
  background: #f8ead7;
  margin: 0 auto;
  display: grid;
  place-items: center;
  color: #ff8a00;
  font-size: 42px;
}

.add-pet-card h4 {
  margin: 12px 0 6px;
  color: #141b2a;
  font-size: 30px;
}

.add-pet-card p {
  margin: 0 0 10px;
  color: #607189;
  line-height: 1.6;
}

:deep(.add-pet-card .van-button) {
  background: #ff9800;
  border: none;
  width: 132px;
}

.pet-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.pet-item {
  background: #fff;
  border-radius: 16px;
  border: 1px solid #e8edf4;
  padding: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.pet-item h4 {
  margin: 0;
  color: #0f1729;
}

.pet-item p {
  margin: 2px 0 0;
  color: #667892;
  font-size: 12px;
}

.post-section {
  margin-top: 16px;
  background: #fff;
  border-radius: 20px;
  border: 1px solid #edf0f5;
  overflow: hidden;
}

.post-tabs {
  display: flex;
  border-bottom: 1px solid #edf0f5;
}

.post-tabs button {
  flex: 1;
  border: none;
  background: transparent;
  padding: 12px 0;
  color: #8b99b1;
}

.post-tabs button.active {
  color: #ff8a00;
  font-weight: 700;
  border-bottom: 3px solid #ff8a00;
}

.post-grid {
  padding: 10px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.post-card {
  border-radius: 14px;
  background: #f8f9fb;
  overflow: hidden;
}

.cover {
  height: 136px;
}

.post-card p {
  margin: 8px 8px 6px;
  color: #1f2b3d;
  min-height: 40px;
}

.post-card span {
  display: block;
  margin: 0 8px 8px;
  color: #ff8a00;
}

:deep(.van-tabbar-item--active) {
  color: #ff8a00;
}
</style>