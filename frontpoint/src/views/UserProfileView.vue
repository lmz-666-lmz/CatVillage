<template>
  <div class="page-container profile-page">
    <van-nav-bar title="完善个人信息" left-arrow @click-left="router.back()" />

    <van-form @submit="onSubmit">
      <div class="content">
        <div class="avatar-block">
          <van-uploader
            v-model="avatarList"
            :max-count="1"
            :preview-image="false"
            :after-read="onAvatarRead"
            class="avatar-uploader"
          >
            <div class="avatar-ring">
              <van-image v-if="avatarUrl" :src="avatarUrl" fit="cover" class="avatar-image" />
              <div v-else class="avatar-placeholder" />
              <div class="avatar-camera">
                <van-icon name="photograph" />
              </div>
            </div>
          </van-uploader>
          <div class="avatar-text">点击上传头像</div>
        </div>

        <div class="form-block">
          <label class="field-label" for="profile-nickname">昵称</label>
          <van-field
            id="profile-nickname"
            v-model="nickname"
            name="nickname"
            placeholder="请输入您的昵称"
            :rules="[{ required: true, message: '请输入昵称' }]"
          />
        </div>

        <div class="form-block">
          <label class="field-label">性别</label>
          <div class="gender-options">
            <button type="button" class="gender-card" :class="{ active: gender === 'male' }" @click="gender = 'male'">
              <span class="gender-dot male" />
              <span>男</span>
            </button>
            <button
              type="button"
              class="gender-card"
              :class="{ active: gender === 'female' }"
              @click="gender = 'female'"
            >
              <span class="gender-dot female" />
              <span>女</span>
            </button>
          </div>
        </div>

        <div class="form-block">
          <label class="field-label" for="profile-bio">个人简介</label>
          <van-field
            id="profile-bio"
            v-model="bio"
            name="bio"
            type="textarea"
            rows="4"
            autosize
            placeholder="简单介绍一下自己和你的萌宠吧..."
          />
        </div>
      </div>

      <div class="bottom-actions">
        <van-button class="primary-button" round block type="primary" native-type="submit">
          开启猫村之旅
          <van-icon name="arrow" class="arrow-icon" />
        </van-button>
      </div>
    </van-form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { closeToast, showToast } from 'vant';
import type { UploaderFileListItem } from 'vant';

const router = useRouter();

const avatarList = ref<UploaderFileListItem[]>([]);
const avatarUrl = ref('');
const nickname = ref('');
const gender = ref<'male' | 'female'>('female');
const bio = ref('');

const onAvatarRead = (file: UploaderFileListItem | UploaderFileListItem[]) => {
  const fileItem = Array.isArray(file) ? file[0] : file;
  if (!fileItem) {
    return;
  }
  if (typeof fileItem.content === 'string') {
    avatarUrl.value = fileItem.content;
  }
};

const onSubmit = async () => {
  if (!nickname.value) {
    showToast({ type: 'fail', message: '请填写昵称' });
    return;
  }
  showToast({ type: 'loading', message: '正在开启旅程...', forbidClick: true, duration: 0 });
  await new Promise(resolve => setTimeout(resolve, 800));
  closeToast();
  showToast({ type: 'success', message: '个人信息已保存' });
  router.replace({ name: 'Home' });
};
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: radial-gradient(circle at 20% 10%, #fff2df 0, #fff8f1 40%, #fdf7f1 100%);
  color: #1d1f23;
}

.content {
  padding: 10px 20px 20px;
}

.avatar-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 12px 0 22px;
}

.avatar-uploader {
  width: 160px;
  display: flex;
  justify-content: center;
}

.avatar-ring {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  background: #f5e4cd;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  box-shadow: 0 18px 30px rgba(255, 138, 0, 0.18);
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #fbd7a5 0%, #f7e3c8 60%, #f1e7d8 100%);
  filter: blur(0.2px);
}

.avatar-image {
  width: 100%;
  height: 100%;
}

.avatar-camera {
  position: absolute;
  width: 46px;
  height: 46px;
  border-radius: 14px;
  background: #ff8a00;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-size: 20px;
  box-shadow: 0 10px 18px rgba(255, 138, 0, 0.3);
}

.avatar-text {
  margin-top: 12px;
  color: #ff8a00;
  font-weight: 600;
}

.form-block {
  margin-bottom: 18px;
}

.field-label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #3f4349;
}

.gender-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

.gender-card {
  border-radius: 16px;
  padding: 14px 16px;
  border: 2px solid #f1e1d1;
  background: #ffffff;
  color: #2b2f33;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  box-shadow: 0 10px 18px rgba(51, 51, 51, 0.04);
}

.gender-card.active {
  border-color: #ff8a00;
  background: #fff1df;
  color: #ff7a00;
}

.gender-dot {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: inline-block;
}

.gender-dot.male {
  background: #4a90ff;
}

.gender-dot.female {
  background: #ff5fa3;
}

.bottom-actions {
  padding: 8px 20px 28px;
}

.primary-button {
  background: linear-gradient(135deg, #ff9900 0%, #ff7a00 100%);
  border: none;
  height: 54px;
  font-size: 16px;
  font-weight: 600;
  box-shadow: 0 18px 30px rgba(255, 122, 0, 0.3);
}

.arrow-icon {
  margin-left: 8px;
}

:deep(.van-nav-bar) {
  background: transparent;
}

:deep(.van-nav-bar__title) {
  font-weight: 700;
  color: #1b1f24;
}

:deep(.van-field) {
  border-radius: 16px;
  background: #ffffff;
  padding: 12px 10px;
  box-shadow: 0 8px 18px rgba(51, 51, 51, 0.06);
}

:deep(.van-field__control) {
  font-size: 15px;
  color: #1d1f23;
}

:deep(.van-field__control::placeholder) {
  color: #a0a6ad;
}
</style>
