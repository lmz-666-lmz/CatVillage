<template>
  <div class="page-container add-cat-page">
    <van-nav-bar title="宠物设置" left-arrow @click-left="router.back()" />

    <van-form @submit="onSubmit">
      <div class="content">
        <div class="avatar-block">
          <h2 class="page-title">上传猫咪头像</h2>
          <p class="subtitle">为您的爱宠设置一个漂亮的头像</p>

          <van-uploader
            v-model="avatarFileList"
            :max-count="1"
            :preview-image="false"
            :after-read="onAvatarRead"
          >
            <div class="avatar-ring">
              <van-image v-if="avatarUrl" :src="avatarUrl" fit="cover" class="avatar-image" />
              <div v-else class="avatar-placeholder">🐱</div>
              <div class="camera-icon"><van-icon name="photograph" /></div>
            </div>
          </van-uploader>
          <p class="avatar-tip">点击更换头像（支持圆框裁剪）</p>
        </div>

        <section class="card-section">
          <h3 class="section-title">基础信息</h3>
          <div class="field-wrap">
            <label class="field-label" for="cat-name">猫咪昵称</label>
            <van-field
              id="cat-name"
              v-model="catName"
              name="catName"
              placeholder="输入您的猫咪名字"
              :rules="[{ required: true, message: '请输入猫咪昵称' }]"
            />
          </div>

          <div class="field-wrap">
            <label class="field-label">性别选择</label>
            <div class="gender-options">
              <button type="button" class="gender-btn" :class="{ active: gender === 1 }" @click="gender = 1">
                <span class="male-dot">♂</span>
                <span>弟弟</span>
              </button>
              <button type="button" class="gender-btn" :class="{ active: gender === 0 }" @click="gender = 0">
                <span class="female-dot">♀</span>
                <span>妹妹</span>
              </button>
            </div>
          </div>

          <div class="sterilize-row">
            <span>是否绝育</span>
            <van-switch v-model="isNeutered" />
          </div>
        </section>

        <section class="card-section">
          <h3 class="section-title">详细资料</h3>
          <div class="grid-two">
            <div class="field-wrap">
              <label class="field-label">品种</label>
              <van-dropdown-menu class="dropdown-menu">
                <van-dropdown-item v-model="breed" :options="breedOptions" />
              </van-dropdown-menu>
            </div>

            <div class="field-wrap">
              <label class="field-label">出生日期</label>
              <van-field readonly clickable :value="birthday" placeholder="请选择" @click="showDatePicker = true" />
            </div>
          </div>
        </section>

        <section class="card-section">
          <h3 class="section-title">健康状况</h3>
          <div class="health-tags">
            <button
              v-for="tag in healthTagOptions"
              :key="tag"
              type="button"
              class="health-tag"
              :class="{ active: healthTags.includes(tag) }"
              @click="toggleHealthTag(tag)"
            >
              {{ tag }}
            </button>
          </div>
        </section>
      </div>

      <div class="bottom-actions">
        <van-button class="submit-btn" round block type="primary" native-type="submit">完成</van-button>
      </div>
    </van-form>

    <van-popup v-model:show="showDatePicker" position="bottom" round>
      <van-date-picker
        v-model="currentDate"
        title="选择出生日期"
        :min-date="minDate"
        :max-date="maxDate"
        @confirm="onConfirmDate"
        @cancel="showDatePicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import { closeToast, showToast } from 'vant';
import type { UploaderFileListItem } from 'vant';
import { createPetProfile } from '@/api/apiService';

const router = useRouter();

const catName = ref('');
const gender = ref<0 | 1>(1);
const isNeutered = ref(false);
const avatarUrl = ref('');
const avatarFileList = ref<UploaderFileListItem[]>([]);

const breedOptions = [
  { text: '英国短毛猫', value: '英国短毛猫' },
  { text: '暹罗猫', value: '暹罗猫' },
  { text: '布偶猫', value: '布偶猫' },
  { text: '缅因猫', value: '缅因猫' },
  { text: '中华田园猫', value: '中华田园猫' }
];
const breed = ref('英国短毛猫');

const minDate = new Date(2010, 0, 1);
const maxDate = new Date();
const showDatePicker = ref(false);
const currentDate = ref([String(maxDate.getFullYear()), String(maxDate.getMonth() + 1).padStart(2, '0'), String(maxDate.getDate()).padStart(2, '0')]);
const birthday = ref('2022-05-12');

const healthTagOptions = ['肠胃脆弱', '曾患猫藓', '无病史', '已打疫苗', '挑食'];
const healthTags = ref<string[]>(['肠胃脆弱']);

const ageInMonths = computed(() => {
  const [year, month] = birthday.value.split('-').map(Number);
  if (!year || !month) {
    return 1;
  }
  const now = new Date();
  return Math.max(1, (now.getFullYear() - year) * 12 + (now.getMonth() + 1 - month));
});

const onAvatarRead = (file: UploaderFileListItem | UploaderFileListItem[]) => {
  const fileItem = Array.isArray(file) ? file[0] : file;
  if (!fileItem) {
    return;
  }
  if (typeof fileItem.content === 'string') {
    avatarUrl.value = fileItem.content;
  }
};

const onConfirmDate = ({ selectedValues }: { selectedValues: string[] }) => {
  birthday.value = `${selectedValues[0]}-${selectedValues[1]}-${selectedValues[2]}`;
  currentDate.value = selectedValues;
  showDatePicker.value = false;
};

const toggleHealthTag = (tag: string) => {
  if (healthTags.value.includes(tag)) {
    healthTags.value = healthTags.value.filter(item => item !== tag);
  } else {
    healthTags.value = [...healthTags.value, tag];
  }
};

const onSubmit = async () => {
  showToast({ type: 'loading', message: '正在创建档案...', forbidClick: true, duration: 0 });
  try {
    await createPetProfile({
      name: catName.value,
      breed: breed.value,
      age: ageInMonths.value,
      gender: gender.value,
      isNeutered: isNeutered.value,
      medicalHistory: healthTags.value.join('、'),
      avatarUrl: avatarUrl.value
    });
    closeToast();
    showToast({ type: 'success', message: '猫咪档案创建成功' });
    router.replace({ name: 'Cats' });
  } catch (error) {
    closeToast();
    showToast({ type: 'fail', message: '创建失败，请稍后再试' });
  }
};
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: #f7f7f8;
}

.content {
  padding: 8px 16px 24px;
}

.avatar-block {
  text-align: center;
  margin-bottom: 20px;
}

.page-title {
  margin: 2px 0 6px;
  font-size: 36px;
  line-height: 1.2;
  font-weight: 800;
  color: #121826;
}

.subtitle {
  margin: 0 0 16px;
  font-size: 15px;
  color: #5a6d86;
}

.avatar-ring {
  width: 180px;
  height: 180px;
  margin: 0 auto;
  border-radius: 50%;
  overflow: hidden;
  position: relative;
  border: 4px solid #9a5f1b;
  box-shadow: 0 14px 24px rgba(154, 95, 27, 0.18);
}

.avatar-image,
.avatar-placeholder {
  width: 100%;
  height: 100%;
}

.avatar-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 68px;
  background: linear-gradient(135deg, #ffcb8f 0%, #ffb86b 100%);
}

.camera-icon {
  position: absolute;
  right: 0;
  bottom: 4px;
  width: 44px;
  height: 44px;
  border-radius: 14px;
  background: #ff8a00;
  color: #fff;
  font-size: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-tip {
  margin-top: 12px;
  color: #ff8a00;
  font-weight: 600;
}

.card-section {
  margin-bottom: 16px;
}

.section-title {
  font-size: 34px;
  margin: 0 0 12px;
  font-weight: 800;
  color: #121826;
  position: relative;
  padding-left: 12px;
}

.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 5px;
  bottom: 5px;
  width: 4px;
  border-radius: 2px;
  background: #ff8a00;
}

.field-wrap {
  margin-bottom: 12px;
}

.field-label {
  display: block;
  margin-bottom: 8px;
  color: #2b2f33;
  font-size: 14px;
}

.gender-options {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.gender-btn {
  height: 64px;
  border-radius: 22px;
  border: 1px solid #eedcc7;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 28px;
  color: #151c2b;
}

.gender-btn.active {
  border-color: #ff9b29;
  background: #fff6eb;
}

.male-dot {
  color: #4f8df7;
}

.female-dot {
  color: #e85ea3;
}

.sterilize-row {
  border-radius: 22px;
  background: #fff;
  border: 1px solid #f0e2cf;
  height: 64px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.grid-two {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.dropdown-menu {
  border-radius: 18px;
  overflow: hidden;
}

.health-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.health-tag {
  border: 1px solid #d8e0ec;
  background: #eaf0f8;
  color: #374151;
  border-radius: 999px;
  padding: 8px 16px;
  font-size: 14px;
}

.health-tag.active {
  border-color: #ff9b29;
  color: #ff8a00;
  background: #fff6eb;
}

.bottom-actions {
  padding: 8px 16px 26px;
}

.submit-btn {
  height: 56px;
  border: none;
  background: linear-gradient(135deg, #ff9900 0%, #ff7a00 100%);
  font-size: 30px;
  font-weight: 700;
  box-shadow: 0 16px 28px rgba(255, 122, 0, 0.3);
}

:deep(.van-nav-bar__title) {
  font-size: 36px;
  font-weight: 800;
  color: #111827;
}

:deep(.van-field) {
  border-radius: 22px;
  border: 1px solid #f0dcc0;
  background: #fff;
}
</style>
