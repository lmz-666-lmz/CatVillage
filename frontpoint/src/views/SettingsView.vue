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
        v-for="item in visibleSettingItems"
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

    <!-- 保存更改 -->
    <button
      type="button"
      class="mt-5 h-12 w-full rounded-[16px] bg-[linear-gradient(135deg,#e06912,#f97316)] text-[18px] font-extrabold tracking-tight text-white shadow-[0_12px_28px_rgba(249,115,22,0.28)]"
      @click="saveChanges"
    >
      保存更改
    </button>

    <!-- 退出登录 -->
    <button
      type="button"
      class="mt-3 h-11 w-full rounded-[14px] border border-[#e5e7eb] bg-white text-[15px] font-semibold text-[#748094]"
      @click="handleLogout"
    >
      退出登录
    </button>

    <!-- 当前版本 -->
    <button
      type="button"
      class="mt-3 mb-8 w-full text-center text-[13px] font-bold text-[#748094]"
      @click="showVersionDialog = true"
    >
      当前版本 V2.4
    </button>

    <!-- 修改用户名弹窗 -->
    <van-overlay :show="showNicknameSheet" @click="showNicknameSheet = false">
      <div class="nickname-dialog-wrapper" @click.stop>
        <div class="nickname-dialog">
          <h3 class="nickname-dialog-title">修改用户名</h3>
          <p class="nickname-dialog-desc">设置一个让猫友记住的名字吧</p>
          <input
            v-model="nicknameDraft"
            type="text"
            maxlength="24"
            placeholder="请输入新用户名"
            class="nickname-dialog-input"
            @keyup.enter="confirmNickname"
          />
          <div class="nickname-dialog-actions">
            <button type="button" class="nickname-dialog-btn cancel" @click="showNicknameSheet = false">取消</button>
            <button type="button" class="nickname-dialog-btn confirm" @click="confirmNickname">保存</button>
          </div>
        </div>
      </div>
    </van-overlay>

    <!-- 版本介绍弹窗 -->
    <van-overlay :show="showVersionDialog" @click="showVersionDialog = false">
      <div class="nickname-dialog-wrapper" @click.stop>
        <div class="nickname-dialog version-dialog">
          <h3 class="nickname-dialog-title">CatVillage V2.4</h3>
          <div class="version-list">
            <div class="version-item">疫苗登记增强</div>
            <div class="version-item">消息红点与搜索增强</div>
            <div class="version-item">搜索页视觉升级</div>
            <div class="version-item">设置项有效性增强</div>
            <div class="version-item">欢迎页与主导航体验优化</div>
            <div class="version-item">后台管理体验优化</div>
          </div>
          <div class="nickname-dialog-actions">
            <button type="button" class="nickname-dialog-btn confirm" @click="showVersionDialog = false">知道了</button>
          </div>
        </div>
      </div>
    </van-overlay>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { showConfirmDialog, showToast } from 'vant';
import type { UploaderFileListItem } from 'vant';
import { getMe, updateUserProfile } from '@/api/auth';
import { clearAccountRuntimeState, getUserDisplayProfile, patchUserDisplayProfile, setCurrentUserIdentity } from '@/utils/userProfile';
import { useCatsStore, useCurrentCatStore } from '@/stores';

const router = useRouter();
const catsStore = useCatsStore();
const currentCatStore = useCurrentCatStore();

const avatarUrl = ref('');
const nickname = ref('');
const miaoId = ref('');
const nicknameDraft = ref('');
const showNicknameSheet = ref(false);
const showVersionDialog = ref(false);
const isAdmin = ref(false);

interface SettingItem {
  icon: string;
  title: string;
  desc: string;
  routeName: string;
  adminOnly?: boolean;
}

const allSettingItems: SettingItem[] = [
  { icon: 'bell', title: '通知设置', desc: '管理提醒与消息推送', routeName: 'SettingsNotification' },
  { icon: 'lock', title: '隐私设置', desc: '控制资料可见性与互动权限', routeName: 'SettingsPrivacy' },
  { icon: 'manager-o', title: '后台管理', desc: '管理员查看用户、内容与数据', routeName: 'AdminDashboard', adminOnly: true }
];

const visibleSettingItems = computed(() =>
  allSettingItems.filter(item => !item.adminOnly || isAdmin.value)
);

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

const handleLogout = async () => {
  try {
    await showConfirmDialog({ title: '退出登录', message: '确认退出当前账号？' });
  } catch {
    return;
  }
  clearAccountRuntimeState({ includeToken: true });
  catsStore.clearCats();
  currentCatStore.clearCurrentCat();
  showToast({ message: '已退出登录' });
  router.replace({ name: 'Login' });
};

const handleBack = () => {
  router.back();
};

onMounted(() => {
  isAdmin.value = localStorage.getItem('is_admin') === 'true';
  void hydrate();
});
</script>

<style scoped>
/* ========== NICKNAME / VERSION DIALOG ========== */
.nickname-dialog-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 0 24px;
}

.nickname-dialog {
  width: 100%;
  max-width: 340px;
  background: #fff;
  border-radius: 24px;
  padding: 28px 24px 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  animation: dialogIn 0.2s ease-out;
}

@keyframes dialogIn {
  from { opacity: 0; transform: scale(0.92) translateY(12px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}

.nickname-dialog-title {
  margin: 0;
  font-size: 20px;
  font-weight: 900;
  color: #172033;
  text-align: center;
}

.nickname-dialog-desc {
  margin: 6px 0 18px;
  font-size: 13px;
  color: #748094;
  text-align: center;
}

.nickname-dialog-input {
  width: 100%;
  box-sizing: border-box;
  height: 46px;
  border: 1.5px solid #e2e8f0;
  border-radius: 14px;
  background: #f8fafc;
  padding: 0 14px;
  font-size: 15px;
  color: #172033;
  outline: none;
  font-weight: 700;
}

.nickname-dialog-input:focus {
  border-color: #f97316;
  background: #fff;
}

.nickname-dialog-input::placeholder {
  color: #b0b8c4;
}

.nickname-dialog-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 20px;
}

.nickname-dialog-btn {
  height: 44px;
  border: none;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 800;
  cursor: pointer;
  transition: transform 0.12s;
}

.nickname-dialog-btn:active {
  transform: scale(0.96);
}

.nickname-dialog-btn.cancel {
  background: #f1f5f9;
  color: #64748b;
}

.nickname-dialog-btn.confirm {
  background: linear-gradient(135deg, #e06912, #f97316);
  color: #fff;
  box-shadow: 0 8px 20px rgba(249, 115, 22, 0.25);
}

/* ========== VERSION DIALOG ========== */
.version-dialog .nickname-dialog-actions {
  grid-template-columns: 1fr;
}

.version-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 16px 0 4px;
}

.version-item {
  padding: 10px 14px;
  border-radius: 12px;
  background: #f4f7fb;
  color: #172033;
  font-size: 14px;
  font-weight: 700;
}
</style>
