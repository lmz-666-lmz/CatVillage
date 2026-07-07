<template>
  <div class="welcome-page">
    <div class="paw-field" aria-hidden="true">
      <span>•</span><span>•</span><span>•</span>
    </div>

    <section class="welcome-hero">
      <div class="logo-wrap">
        <img src="/logo.png" alt="CatVillage" />
      </div>
      <p class="kicker">CatVillage</p>
      <h1>欢迎来到猫村</h1>
      <p class="subtitle">猫咪社交、喵喵情绪识别、AI 养育助手和健康档案，一起照顾每一只小伙伴。</p>
    </section>

    <section class="feature-row" aria-label="核心能力">
      <div class="feature-pill"><van-icon name="friends-o" size="17" />猫咪社交</div>
      <div class="feature-pill"><van-icon name="volume-o" size="17" />情绪识别</div>
      <div class="feature-pill"><van-icon name="service-o" size="17" />AI养育</div>
      <div class="feature-pill"><van-icon name="records" size="17" />健康档案</div>
    </section>

    <section class="cat-card" aria-hidden="true">
      <div class="cat-face">
        <i></i><i></i>
        <b></b>
      </div>
      <div>
        <strong>今天也要好好养猫</strong>
        <span>记录、分享、分析和陪伴都在一个村子里。</span>
      </div>
    </section>

    <div class="welcome-actions">
      <button type="button" class="primary-btn" @click="goLogin">登录</button>
      <button type="button" class="secondary-btn" @click="goRegister">注册新账号</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();

const rememberSeen = () => {
  localStorage.setItem('welcomeSeen', '1');
};

const goLogin = () => {
  rememberSeen();
  router.push({ name: 'Login' });
};

const goRegister = () => {
  rememberSeen();
  router.push({ name: 'Register' });
};
</script>

<style scoped>
.welcome-page {
  position: relative;
  min-height: 100dvh;
  overflow: hidden;
  padding: clamp(22px, 5vh, 42px) 22px calc(18px + env(safe-area-inset-bottom, 0px));
  background:
    radial-gradient(circle at 16% 8%, rgba(249, 115, 22, 0.18), transparent 28%),
    radial-gradient(circle at 86% 32%, rgba(20, 184, 166, 0.14), transparent 26%),
    linear-gradient(165deg, #f6f8fb 0%, #fff4ec 50%, #eef6f5 100%);
  color: #172033;
}

.paw-field {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.paw-field span {
  position: absolute;
  width: 16px;
  height: 16px;
  border-radius: 999px;
  background: rgba(249, 115, 22, 0.22);
  box-shadow: 12px 10px 0 rgba(249, 115, 22, 0.12), -8px 12px 0 rgba(249, 115, 22, 0.1);
  animation: pawFloat 5s ease-in-out infinite;
}

.paw-field span:nth-child(1) { left: 20px; top: 110px; }
.paw-field span:nth-child(2) { right: 34px; top: 250px; animation-delay: .8s; }
.paw-field span:nth-child(3) { left: 64px; bottom: 142px; animation-delay: 1.4s; }

.welcome-hero {
  position: relative;
  z-index: 1;
  text-align: center;
}

.logo-wrap {
  display: grid;
  width: clamp(70px, 18vw, 88px);
  height: clamp(70px, 18vw, 88px);
  place-items: center;
  margin: 0 auto 12px;
  overflow: hidden;
  border: 4px solid rgba(255,255,255,0.9);
  border-radius: 26px;
  background: #fff;
  box-shadow: 0 16px 34px rgba(249, 115, 22, 0.18);
  animation: logoBreath 3.4s ease-in-out infinite;
}

.logo-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.kicker {
  margin: 0;
  color: #f97316;
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0;
}

h1 {
  margin: 4px 0 0;
  color: #172033;
  font-size: clamp(30px, 8vw, 38px);
  font-weight: 1000;
  letter-spacing: 0;
}

.subtitle {
  max-width: 330px;
  margin: 10px auto 0;
  color: #5f6c80;
  font-size: 15px;
  font-weight: 700;
  line-height: 1.55;
}

.feature-row {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 9px;
  margin-top: clamp(18px, 4vh, 28px);
}

.feature-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  min-height: 40px;
  border: 1px solid rgba(226, 232, 240, 0.92);
  border-radius: 16px;
  background: rgba(255,255,255,0.84);
  color: #172033;
  font-size: 13px;
  font-weight: 900;
  box-shadow: 0 10px 22px rgba(23, 32, 51, 0.05);
}

.cat-card {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: clamp(16px, 4vh, 28px);
  border: 1px solid rgba(226, 232, 240, 0.92);
  border-radius: 22px;
  background: rgba(255,255,255,0.86);
  padding: 13px;
  box-shadow: 0 14px 30px rgba(23, 32, 51, 0.07);
}

.cat-face {
  position: relative;
  width: 58px;
  height: 58px;
  flex-shrink: 0;
  border-radius: 22px 22px 18px 18px;
  background: linear-gradient(135deg, #f97316, #fb923c);
}

.cat-face::before,
.cat-face::after {
  content: '';
  position: absolute;
  top: -8px;
  width: 24px;
  height: 24px;
  background: #f97316;
  transform: rotate(45deg);
}

.cat-face::before { left: 5px; }
.cat-face::after { right: 5px; }

.cat-face i {
  position: absolute;
  top: 24px;
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: #fff;
}

.cat-face i:first-child { left: 18px; }
.cat-face i:nth-child(2) { right: 18px; }
.cat-face b {
  position: absolute;
  left: 50%;
  bottom: 15px;
  width: 16px;
  height: 8px;
  border-bottom: 3px solid #fff;
  border-radius: 999px;
  transform: translateX(-50%);
}

.cat-card strong,
.cat-card span {
  display: block;
}

.cat-card strong {
  font-size: 15px;
  font-weight: 1000;
}

.cat-card span {
  margin-top: 3px;
  color: #748094;
  font-size: 12px;
  font-weight: 700;
  line-height: 1.45;
}

.welcome-actions {
  position: relative;
  z-index: 1;
  display: grid;
  gap: 10px;
  margin-top: clamp(18px, 4vh, 28px);
}

.primary-btn,
.secondary-btn {
  height: 50px;
  border: 0;
  border-radius: 18px;
  font-size: 16px;
  font-weight: 1000;
  transition: transform .14s ease;
}

.primary-btn {
  background: linear-gradient(135deg, #e06912, #f97316);
  color: #fff;
  box-shadow: 0 14px 26px rgba(249, 115, 22, 0.26);
}

.secondary-btn {
  border: 1px solid rgba(226, 232, 240, 0.92);
  background: rgba(255,255,255,0.78);
  color: #172033;
}

.primary-btn:active,
.secondary-btn:active {
  transform: scale(.98);
}

@keyframes logoBreath {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-4px) scale(1.025); }
}

@keyframes pawFloat {
  0%, 100% { transform: translateY(0); opacity: .78; }
  50% { transform: translateY(-9px); opacity: 1; }
}

@media (max-height: 680px) {
  .welcome-page { padding-top: 20px; }
  .subtitle { font-size: 14px; line-height: 1.45; }
  .cat-card { padding: 11px; }
  .feature-pill { min-height: 38px; }
  .primary-btn, .secondary-btn { height: 48px; }
}

@media (prefers-reduced-motion: reduce) {
  .logo-wrap,
  .paw-field span,
  .primary-btn,
  .secondary-btn {
    animation: none !important;
    transition: none !important;
  }
}
</style>
