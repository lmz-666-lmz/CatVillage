<template>
  <div class="min-h-[100dvh] bg-[#f5f7fb] px-5 pt-4 pb-8">
    <header class="flex items-center gap-3">
      <button type="button" class="grid h-10 w-10 place-items-center text-[#f97316]" @click="handleBack">
        <van-icon name="arrow-left" size="24" />
      </button>
      <h1 class="text-2xl font-black text-[#172033] tracking-tight">个人设置</h1>
    </header>

    <section class="mt-7 rounded-[22px] bg-[rgba(255,255,255,0.92)] border border-[rgba(226,232,240,0.92)] p-4 shadow-[0_12px_26px_rgba(23,32,51,0.06)]">
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
            <div class="absolute -bottom-1 -right-1 grid h-8 w-8 place-items-center rounded-full border-2 border-white bg-[#f97316] text-white">
              <van-icon name="photograph" size="14" />
            </div>
          </div>
        </van-uploader>

        <div class="min-w-0 flex-1">
          <button type="button" class="w-full truncate text-left text-[19px] font-extrabold text-[#172033]" @click="showNicknameSheet = true">
            {{ nickname }}
          </button>
          <p class="mt-1 text-[13px] text-[#748094]">喵村号：{{ miaoId }}</p>
          <p class="mt-1 text-[12px] text-[#748094]">点击头像或昵称可修改资料</p>
        </div>
      </div>
    </section>

    <section class="mt-5 rounded-[22px] bg-[rgba(255,255,255,0.92)] border border-[rgba(226,232,240,0.92)] p-2 shadow-[0_12px_26px_rgba(23,32,51,0.06)]">
      <button
        v-for="item in settingItems"
        :key="item.title"
        type="button"
        class="flex w-full items-center justify-between rounded-[12px] px-3 py-3 text-left"
        @click="router.push({ name: item.routeName })"
      >
        <div class="flex items-center gap-3">
          <div class="grid h-9 w-9 place-items-center rounded-xl bg-[#f2f5ff] text-[#748094]">
            <van-icon :name="item.icon" size="18" />
          </div>
          <div>
            <div class="text-[15px] font-bold text-[#172033]">{{ item.title }}</div>
            <div class="text-[12px] text-[#748094]">{{ item.desc }}</div>
          </div>
        </div>
        <van-icon name="arrow" color="#748094" />
      </button>
    </section>

    <button
      type="button"
      class="fixed bottom-7 left-1/2 h-12 w-[calc(100%-40px)] max-w-[430px] -translate-x-1/2 rounded-[16px] bg-[linear-gradient(135deg,#e06912,#f97316)] text-[18px] font-extrabold tracking-tight text-white shadow-[0_12px_28px_rgba(249,115,22,0.28)]"
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
import { getMe, updateUserProfile } from '@/api/auth';
import { getUserDisplayProfile, patchUserDisplayProfile, setCurrentUserIdentity } from '@/utils/userProfile';

const router = useRouter();

const avatarUrl = ref('');
const nickname = ref('');
const miaoId = ref('');
const nicknameDraft = ref('');
const showNicknameSheet = ref(false);

const settingItems = [
  { icon: 'bell', title: '通知设置', desc: '管理提醒与消息推送', routeName: 'SettingsNotification' },
  { icon: 'lock', title: '隐私设置', desc: '控制资料可见性与互动权限', routeName: 'SettingsPrivacy' },
  { icon: 'manager-o', title: '后台管理', desc: '管理员查看用户、内容与数据', routeName: 'AdminDashboard' }
] as const;

const syncProfileToServer = async (profile: { nickname?: string; avatarUrl?: string }) => {
  const token = localStorage.getItem('token');
  if (!token) {
    return false;
  }
  try {
    const res = await updateUserProfile(profile);
    if (res.data?.id) {
      const next = setCurrentUserIdentity(res.data);
      avatarUrl.value = next.avatarUrl;
      nickname.value = next.nickname;
      miaoId.value = next.miaoId;
      nicknameDraft.value = next.nickname;
    }
    return true;
  } catch {
    showToast({ type: 'fail', message: '资料同步失败，请稍后重试' });
    return false;
  }
};

const hydrate = async () => {
  try {
    const res = await getMe();
    if (res.data?.id) {
      setCurrentUserIdentity(res.data);
    }
  } catch {
    // 进入设置页仍允许读取当前账号本地缓存。
  }
  const profile = getUserDisplayProfile();
  avatarUrl.value = profile.avatarUrl;
  nickname.value = profile.nickname;
  miaoId.value = profile.miaoId;
  nicknameDraft.value = profile.nickname;
};

const onAvatarRead = async (file: UploaderFileListItem | UploaderFileListItem[]) => {
  const fileItem = Array.isArray(file) ? file[0] : file;
  if (!fileItem) {
    return;
  }
  if (typeof fileItem.content === 'string') {
    showToast({ type: 'loading', message: '头像上传中...', forbidClick: true, duration: 0 });
    const ok = await syncProfileToServer({ nickname: nickname.value, avatarUrl: fileItem.content });
    if (ok) {
      showToast({ type: 'success', message: '头像已更新' });
    }
  }
};

const confirmNickname = async () => {
  const value = nicknameDraft.value.trim();
  if (!value) {
    showToast({ type: 'fail', message: '用户名不能为空' });
    return;
  }

  // Confirming nickname should immediately persist, so profile page updates right away.
  const ok = await syncProfileToServer({ nickname: value, avatarUrl: avatarUrl.value });
  if (ok) {
    const next = patchUserDisplayProfile({ nickname: value, avatarUrl: avatarUrl.value });
    avatarUrl.value = next.avatarUrl;
    nickname.value = next.nickname;
    miaoId.value = next.miaoId;
    nicknameDraft.value = next.nickname;
    showNicknameSheet.value = false;
    showToast({ type: 'success', message: '用户名已更新' });
  }
};

const saveChanges = async () => {
  const value = (nicknameDraft.value || nickname.value).trim();
  if (!value) {
    showToast({ type: 'fail', message: '用户名不能为空' });
    return;
  }
  nickname.value = value;
  nicknameDraft.value = value;
  const ok = await syncProfileToServer({ nickname: value, avatarUrl: avatarUrl.value });
  if (ok) {
    patchUserDisplayProfile({ nickname: value, avatarUrl: avatarUrl.value });
    showToast({ type: 'success', message: '已保存' });
    router.back();
  }
};

const handleBack = () => {
  router.back();
};

onMounted(() => {
  void hydrate();
});
</script>
