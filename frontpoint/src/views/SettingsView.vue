<template>
  <div class="min-h-[100dvh] bg-[#f3f4fb] px-5 pt-5 pb-24">
    <header class="flex items-center gap-3">
      <button type="button" class="grid h-10 w-10 place-items-center text-[#b33500]" @click="handleBack">
        <van-icon name="arrow-left" size="24" />
      </button>
      <h1 class="text-[22px] font-black tracking-tight text-[#12182a]">个人设置</h1>
    </header>

    <section class="mt-7 rounded-[18px] bg-white p-4 shadow-[0_4px_14px_rgba(20,27,43,0.05)]">
      <div class="flex items-center gap-3">
        <van-uploader
          :max-count="1"
          :preview-image="false"
          :after-read="onAvatarRead"
          class="inline-flex"
        >
          <div class="relative h-20 w-20">
            <div class="h-full w-full overflow-hidden rounded-full border-4 border-white shadow-[0_6px_16px_rgba(20,27,43,0.08)]">
              <van-image :src="avatarUrl" fit="cover" width="80" height="80" />
            </div>
            <div class="absolute -bottom-1 -right-1 grid h-8 w-8 place-items-center rounded-full border-2 border-white bg-[#b33500] text-white">
              <van-icon name="photograph" size="14" />
            </div>
          </div>
        </van-uploader>

        <div class="min-w-0 flex-1">
          <button type="button" class="w-full truncate text-left text-[19px] font-extrabold text-[#12182a]" @click="showNicknameSheet = true">
            {{ nickname }}
          </button>
          <p class="mt-1 text-[13px] text-[#7a7483]">喵村号：{{ miaoId }}</p>
          <p class="mt-1 text-[12px] text-[#a39eac]">点击头像或昵称可修改资料</p>
        </div>
      </div>
    </section>

    <section class="mt-5 rounded-[18px] bg-white p-2 shadow-[0_4px_14px_rgba(20,27,43,0.05)]">
      <button
        v-for="item in settingItems"
        :key="item.title"
        type="button"
        class="flex w-full items-center justify-between rounded-[12px] px-3 py-3 text-left"
        @click="router.push({ name: item.routeName })"
      >
        <div class="flex items-center gap-3">
          <div class="grid h-9 w-9 place-items-center rounded-xl bg-[#f2f5ff] text-[#5f6b86]">
            <van-icon :name="item.icon" size="18" />
          </div>
          <div>
            <div class="text-[15px] font-bold text-[#12182a]">{{ item.title }}</div>
            <div class="text-[12px] text-[#8f94a3]">{{ item.desc }}</div>
          </div>
        </div>
        <van-icon name="arrow" color="#9ca3b4" />
      </button>
    </section>

    <section class="mt-5 text-center">
      <button
        type="button"
        class="h-10 rounded-full border border-[#e2e5ef] bg-white px-5 text-[14px] font-semibold text-[#5f677d]"
        @click="router.push({ name: 'SettingsPolicy' })"
      >
        隐私协议与条款
      </button>
    </section>

    <button
      type="button"
      class="fixed bottom-7 left-1/2 h-12 w-[calc(100%-40px)] max-w-[420px] -translate-x-1/2 rounded-[14px] bg-[#b33500] text-[18px] font-bold tracking-tight text-white shadow-[0_12px_24px_rgba(179,53,0,0.22)]"
      @click="saveChanges"
    >
      保存更改
    </button>

    <van-action-sheet v-model:show="showNicknameSheet" title="修改用户名">
      <div class="p-4">
        <van-field v-model="nicknameDraft" label="用户名" maxlength="24" placeholder="请输入新用户名" />
        <div class="mt-4 grid grid-cols-2 gap-2">
          <van-button block plain type="primary" @click="showNicknameSheet = false">取消</van-button>
          <van-button block type="primary" @click="confirmNickname">确认</van-button>
        </div>
      </div>
    </van-action-sheet>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';
import type { UploaderFileListItem } from 'vant';
import { updateUserProfile } from '@/api/auth';
import { getUserDisplayProfile, patchUserDisplayProfile } from '@/utils/userProfile';

const router = useRouter();

const avatarUrl = ref('');
const nickname = ref('');
const miaoId = ref('');
const nicknameDraft = ref('');
const showNicknameSheet = ref(false);

const settingItems = [
  { icon: 'shield-o', title: '账号与安全', desc: '查看喵村号与账号信息', routeName: 'SettingsAccount' },
  { icon: 'bell', title: '通知设置', desc: '管理提醒与消息推送', routeName: 'SettingsNotification' },
  { icon: 'lock', title: '隐私设置', desc: '控制资料可见性与互动权限', routeName: 'SettingsPrivacy' },
  { icon: 'clock-o', title: '浏览历史', desc: '查看最近访问记录', routeName: 'SettingsHistory' },
  { icon: 'info-o', title: '关于猫村', desc: '版本信息与帮助入口', routeName: 'SettingsAbout' }
] as const;

const syncNicknameToServer = async (nicknameValue: string) => {
  const token = localStorage.getItem('token');
  if (!token) {
    return;
  }
  try {
    await updateUserProfile(nicknameValue);
  } catch {
    showToast({ type: 'fail', message: '昵称仅本地更新，云端同步失败' });
  }
};

const hydrate = () => {
  const profile = getUserDisplayProfile();
  avatarUrl.value = profile.avatarUrl;
  nickname.value = profile.nickname;
  miaoId.value = profile.miaoId;
  nicknameDraft.value = profile.nickname;
};

const onAvatarRead = (file: UploaderFileListItem | UploaderFileListItem[]) => {
  const fileItem = Array.isArray(file) ? file[0] : file;
  if (!fileItem) {
    return;
  }
  if (typeof fileItem.content === 'string') {
    const next = patchUserDisplayProfile({ nickname: nickname.value, avatarUrl: fileItem.content });
    avatarUrl.value = next.avatarUrl;
    nickname.value = next.nickname;
    miaoId.value = next.miaoId;
    nicknameDraft.value = next.nickname;
    showToast({ type: 'success', message: '头像已更新' });
  }
};

const confirmNickname = async () => {
  const value = nicknameDraft.value.trim();
  if (!value) {
    showToast({ type: 'fail', message: '用户名不能为空' });
    return;
  }

  // Confirming nickname should immediately persist, so profile page updates right away.
  const next = patchUserDisplayProfile({ nickname: value, avatarUrl: avatarUrl.value });
  avatarUrl.value = next.avatarUrl;
  nickname.value = next.nickname;
  miaoId.value = next.miaoId;
  nicknameDraft.value = next.nickname;
  await syncNicknameToServer(next.nickname);
  showNicknameSheet.value = false;
  showToast({ type: 'success', message: '用户名已更新' });
};

const saveChanges = async () => {
  const value = (nicknameDraft.value || nickname.value).trim();
  if (!value) {
    showToast({ type: 'fail', message: '用户名不能为空' });
    return;
  }
  nickname.value = value;
  nicknameDraft.value = value;
  const next = patchUserDisplayProfile({ nickname: value, avatarUrl: avatarUrl.value });
  await syncNicknameToServer(next.nickname);
  showToast({ type: 'success', message: '已保存' });
  router.back();
};

const handleBack = () => {
  router.back();
};

onMounted(() => {
  hydrate();
});
</script>
