<template>
  <div class="px-6 pt-6 pb-6">
    <header class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold tracking-tight text-on-background">我的</h1>
        <p class="mt-1 text-sm text-on-surface-variant">账号信息与基础设置</p>
      </div>
      <van-icon name="setting-o" size="20" class="text-on-surface-variant" />
    </header>

    <van-form class="mt-6" @submit="onSubmit">
      <section class="rounded-2xl border border-surface-container-high bg-surface-container-lowest p-4">
        <div class="flex items-center gap-4">
          <van-uploader
            v-model="avatarList"
            :max-count="1"
            :preview-image="false"
            :after-read="onAvatarRead"
          >
            <div class="h-16 w-16 overflow-hidden rounded-2xl border border-surface-container-high bg-surface-container-high grid place-items-center">
              <van-image v-if="avatarUrl" :src="avatarUrl" fit="cover" width="64" height="64" />
              <span v-else class="text-2xl">👩</span>
            </div>
          </van-uploader>

          <div class="min-w-0 flex-1">
            <div class="text-sm text-on-surface-variant">点击头像可更换</div>
            <div class="mt-1 text-base font-semibold text-on-background truncate">{{ nickname || '未设置昵称' }}</div>
          </div>
        </div>
      </section>

      <section class="mt-4">
        <van-cell-group inset>
          <van-field
            v-model="nickname"
            name="nickname"
            label="昵称"
            placeholder="请输入昵称"
            :rules="[{ required: true, message: '请输入昵称' }]"
          />

          <van-field
            v-model="gender"
            name="gender"
            label="性别"
            readonly
            is-link
            placeholder="请选择"
            @click="showGenderPicker = true"
          />

          <van-field
            v-model="bio"
            name="bio"
            label="简介"
            type="textarea"
            rows="3"
            autosize
            placeholder="简单介绍一下你和你的萌宠..."
          />
        </van-cell-group>
      </section>

      <div class="mt-5 space-y-3">
        <button
          type="submit"
          class="h-12 w-full rounded-xl bg-primary text-on-primary font-semibold shadow-cta active:scale-[0.99]"
        >
          保存
        </button>

        <button
          type="button"
          class="h-12 w-full rounded-xl border border-outline-variant bg-surface-container-lowest text-on-background font-semibold active:scale-[0.99]"
          @click="logout"
        >
          退出登录
        </button>
      </div>
    </van-form>

    <van-action-sheet v-model:show="showGenderPicker" title="选择性别">
      <div class="p-4 space-y-2">
        <van-button block type="primary" @click="setGender('女')">女</van-button>
        <van-button block type="primary" plain @click="setGender('男')">男</van-button>
      </div>
    </van-action-sheet>
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
const gender = ref<'男' | '女'>('女');
const bio = ref('');
const showGenderPicker = ref(false);

const onAvatarRead = (file: UploaderFileListItem | UploaderFileListItem[]) => {
  const fileItem = Array.isArray(file) ? file[0] : file;
  if (!fileItem) {
    return;
  }
  if (typeof fileItem.content === 'string') {
    avatarUrl.value = fileItem.content;
  }
};

const setGender = (value: '男' | '女') => {
  gender.value = value;
  showGenderPicker.value = false;
};

const onSubmit = async () => {
  if (!nickname.value.trim()) {
    showToast({ type: 'fail', message: '请填写昵称' });
    return;
  }

  showToast({ type: 'loading', message: '正在保存...', forbidClick: true, duration: 0 });
  await new Promise((resolve) => setTimeout(resolve, 500));
  closeToast();
  showToast({ type: 'success', message: '已保存' });
};

const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('cats');
  localStorage.removeItem('currentCatId');
  showToast({ message: '已退出登录' });
  router.replace({ name: 'Login' });
};
</script>
