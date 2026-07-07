<template>
  <div class="app-stage min-h-[100dvh] bg-background text-on-background antialiased">
    <div class="app-shell mx-auto w-full min-h-[100dvh] flex flex-col">
      <main class="flex-1 app-main" :class="{ 'pb-safe-tabbar': showTabbar && !isAiAssistant, 'ai-route-main': isAiAssistant }">
        <router-view />
      </main>

      <footer v-if="!isAiAssistant" class="app-footer" :class="{ 'with-tabbar': showTabbar }">
        <p class="footer-copy">© 2026 YSU.L.M.Z 版权所有</p>
        <p class="footer-contact">联系邮箱：8224439@qq.com</p>
      </footer>

      <van-tabbar v-if="showTabbar" route safe-area-inset-bottom active-color="#f97316" inactive-color="#748094">
        <van-tabbar-item icon="smile-o" to="/social">广场</van-tabbar-item>
        <van-tabbar-item icon="chat-o" to="/ai-assistant">养护</van-tabbar-item>
        <van-tabbar-item icon="apps-o" to="/emotions">喵喵台</van-tabbar-item>
        <van-tabbar-item icon="comment-o" to="/messages">消息</van-tabbar-item>
        <van-tabbar-item icon="user-o" to="/profile">我的</van-tabbar-item>
      </van-tabbar>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();

// 判断逻辑：如果是登录页，就不显示底部导航栏
const showTabbar = computed(() => {
  const routeName = route?.name ? String(route.name) : '';
  const hiddenRoutes = new Set(['Login', 'Register']);
  if (hiddenRoutes.has(routeName)) {
    return false;
  }
  return !route.meta?.hideTabbar;
});

const isAiAssistant = computed(() => route.name === 'AIAssistant');
</script>

<style scoped>
.app-stage {
  padding: 0;
  --app-mobile-width: 430px;
  --app-tabbar-height: 50px;
}

.app-shell {
  max-width: var(--app-mobile-width);
  background: #f5f7fb;
}

.app-main {
  padding-bottom: 0;
  min-width: 0;
  overflow-x: hidden;
}

.app-main.pb-safe-tabbar {
  padding-bottom: calc(var(--app-tabbar-height) + env(safe-area-inset-bottom, 0px) + 8px);
}

.app-main.ai-route-main {
  display: flex;
  min-height: 0;
  overflow: hidden;
}

/* ── Global Copyright Footer ── */
.app-footer {
  text-align: center;
  padding: 12px 16px 16px;
  flex-shrink: 0;
}

.app-footer.with-tabbar {
  padding-bottom: 8px;
}

.footer-copy {
  margin: 0;
  font-size: 11px;
  font-weight: 600;
  color: #b0a89e;
  letter-spacing: 0.3px;
}

.footer-contact {
  margin: 2px 0 0;
  font-size: 10px;
  font-weight: 500;
  color: #c4bcb2;
}

@media (min-width: 768px) {
  .app-stage {
    display: grid;
    place-items: center;
    min-height: 100dvh;
    padding: 12px;
    background:
      radial-gradient(circle at 18% 0%, rgba(255, 218, 185, 0.54), transparent 34%),
      radial-gradient(circle at 80% 8%, rgba(20, 184, 166, 0.14), transparent 28%),
      linear-gradient(135deg, #f7f3ee 0%, #eef3f7 48%, #e9eef5 100%);
  }

  .app-shell {
    width: min(430px, 100%);
    min-height: calc(100dvh - 24px);
    max-height: calc(100dvh - 24px);
    border-radius: 30px;
    overflow: auto;
    background: #f5f7fb;
    border: 1px solid rgba(255, 255, 255, 0.78);
    box-shadow: 0 22px 60px rgba(23, 32, 51, 0.18);
  }
}
</style>

<!-- 全局样式：手机壳约束 — 统一 van-tabbar / van-popup / van-action-sheet / fixed 元素 -->
<style>
:root {
  --app-mobile-width: 430px;
  --app-tabbar-height: 50px;
  --app-popup-radius: 20px;
}

/* ── Vant Tabbar ── */
.van-tabbar {
  z-index: 90 !important;
  width: 100% !important;
  max-width: var(--app-mobile-width) !important;
  left: 50% !important;
  right: auto !important;
  transform: translateX(-50%);
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-bottom: 0;
  border-radius: 22px 22px 0 0;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(18px);
  overflow: hidden;
  box-shadow: 0 -12px 32px rgba(23, 32, 51, 0.1);
  padding-bottom: env(safe-area-inset-bottom, 0px);
}

.van-tabbar-item {
  font-weight: 800;
}

/* ── Vant Popup (bottom) ──
   使用 margin-left 居中，不碰 transform，保留 Vant 滑入动画 */
@media (min-width: 431px) {
  .van-popup--bottom {
    left: 50% !important;
    right: auto !important;
    width: var(--app-mobile-width) !important;
    margin-left: calc(var(--app-mobile-width) / -2) !important;
    border-radius: var(--app-popup-radius) var(--app-popup-radius) 0 0;
    overflow: hidden;
  }
}

/* ── Vant ActionSheet ──
   同样用 margin-left 居中 */
@media (min-width: 431px) {
  .van-action-sheet {
    left: 50% !important;
    right: auto !important;
    width: var(--app-mobile-width) !important;
    margin-left: calc(var(--app-mobile-width) / -2) !important;
    border-radius: var(--app-popup-radius) var(--app-popup-radius) 0 0;
    overflow: hidden;
  }
}

/* ── Vant van-popup round（CatArchiveView 体重弹窗等）── */
@media (min-width: 431px) {
  .van-popup--bottom.van-popup--round {
    left: 50% !important;
    right: auto !important;
    width: var(--app-mobile-width) !important;
    margin-left: calc(var(--app-mobile-width) / -2) !important;
  }
}

/* ── Overlay 遮罩保持全屏（不改动）── */

/* ── 移动端：恢复默认铺满 ── */
@media (max-width: 430px) {
  .van-tabbar {
    max-width: 100% !important;
    border-radius: 0;
  }
  .van-popup--bottom,
  .van-popup--bottom.van-popup--round,
  .van-action-sheet {
    left: 0 !important;
    margin-left: 0 !important;
    width: 100% !important;
  }
}

/* ── 全局 fixed-bottom 工具类 ── */
.fixed-bottom-safe {
  max-width: var(--app-mobile-width);
  left: 50% !important;
  right: auto !important;
  margin-left: calc(var(--app-mobile-width) / -2);
}
@media (max-width: 430px) {
  .fixed-bottom-safe {
    left: 0 !important;
    margin-left: 0 !important;
    max-width: 100% !important;
  }
}
</style>
