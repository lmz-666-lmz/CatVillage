<template>
  <div class="page-container register-page">
    <van-nav-bar title="加入猫村" left-arrow @click-left="router.back()" />

    <div class="content">
      <div class="login-link">
        已有账号？
        <router-link to="/login">去登录</router-link>
      </div>

      <div class="hero">
        <div class="hero-icon">🐾</div>
      </div>

      <van-form @submit="onSubmit">
        <div class="form-block">
          <label class="field-label" for="register-phone">手机号</label>
          <van-field
            id="register-phone"
            v-model="phone"
            name="phone"
            type="tel"
            placeholder="请输入手机号"
            :rules="[{ required: true, message: '请输入手机号' }, { validator: validatePhone, message: '手机号格式不正确' }]"
          >
            <template #left-icon>
              <van-icon name="phone-o" />
            </template>
          </van-field>
        </div>

        <div class="form-block">
          <label class="field-label" for="register-code">验证码</label>
          <van-field
            id="register-code"
            v-model="code"
            name="code"
            placeholder="输入验证码"
            :rules="[{ required: true, message: '请输入验证码' }]"
          >
            <template #left-icon>
              <van-icon name="shield-o" />
            </template>
            <template #button>
              <van-button
                class="code-button"
                size="small"
                round
                :disabled="codeCooldown > 0 || !phone"
                type="primary"
                @click="onSendCode"
              >
                {{ codeCooldown > 0 ? `${codeCooldown}s后重试` : '获取验证码' }}
              </van-button>
            </template>
          </van-field>
        </div>

        <div class="form-block">
          <label class="field-label" for="register-password">设置密码</label>
          <van-field
            id="register-password"
            v-model="password"
            name="password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="6-16位字母、数字组合"
            :rules="[{ required: true, message: '请输入密码' }, { validator: validatePassword, message: '密码需为6-16位字母或数字组合' }]"
            @click-right-icon="togglePassword"
          >
            <template #left-icon>
              <van-icon name="lock" />
            </template>
            <template #right-icon>
              <van-icon :name="showPassword ? 'eye-o' : 'closed-eye'" />
            </template>
          </van-field>
        </div>

        <div class="agreement">
          <van-checkbox v-model="agree" icon-size="18px">
            <span>阅读并同意</span>
            <span class="link" @click.stop="onViewTerms">《猫村用户服务协议》</span>
            <span>与</span>
            <span class="link" @click.stop="onViewPrivacy">《隐私政策》</span>
          </van-checkbox>
        </div>

        <div class="submit-wrap">
          <van-button class="primary-button" round block type="primary" native-type="submit">
            立即注册
            <van-icon name="arrow" class="arrow-icon" />
          </van-button>
        </div>
      </van-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onUnmounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { closeToast, showToast } from 'vant';
import { registerUser } from '@/api/apiService';

const router = useRouter();

const phone = ref('');
const code = ref('');
const password = ref('');
const agree = ref(false);
const showPassword = ref(false);
const codeCooldown = ref(0);
let cooldownTimer: number | null = null;

const validatePhone = (value: string) => /^1\d{10}$/.test(value);
const validatePassword = (value: string) => /^[A-Za-z\d]{6,16}$/.test(value);

const togglePassword = () => {
  showPassword.value = !showPassword.value;
};

const startCooldown = () => {
  codeCooldown.value = 60;
  cooldownTimer = window.setInterval(() => {
    if (codeCooldown.value <= 1) {
      codeCooldown.value = 0;
      if (cooldownTimer !== null) {
        window.clearInterval(cooldownTimer);
        cooldownTimer = null;
      }
      return;
    }
    codeCooldown.value -= 1;
  }, 1000);
};

const onSendCode = () => {
  if (!validatePhone(phone.value)) {
    showToast({ type: 'fail', message: '请输入正确的手机号' });
    return;
  }
  if (codeCooldown.value > 0) {
    return;
  }
  showToast({ type: 'success', message: '验证码已发送' });
  startCooldown();
};

const onViewTerms = () => {
  showToast({ message: '服务协议稍后上线', duration: 1500 });
};

const onViewPrivacy = () => {
  showToast({ message: '隐私政策稍后上线', duration: 1500 });
};

const onSubmit = async () => {
  if (!agree.value) {
    showToast({ type: 'fail', message: '请先阅读并同意协议' });
    return;
  }

  showToast({ type: 'loading', message: '正在注册...', forbidClick: true, duration: 0 });
  try {
    await registerUser(phone.value, password.value);
    closeToast();
    showToast({ type: 'success', message: '注册成功，欢迎加入猫村' });
    router.replace({ name: 'Login' });
  } catch (error) {
    closeToast();
    showToast({ type: 'fail', message: '注册失败，请稍后重试' });
  }
};

onUnmounted(() => {
  if (cooldownTimer !== null) {
    window.clearInterval(cooldownTimer);
  }
});
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: radial-gradient(circle at 20% 10%, #fff2df 0, #fff8f1 40%, #fdf7f1 100%);
  color: #1d1f23;
}

.content {
  padding: 6px 20px 32px;
}

.login-link {
  text-align: center;
  padding: 8px 0 0;
  color: #666;
}

.login-link a {
  color: #ff8a00;
  font-weight: 700;
  text-decoration: none;
}

.hero {
  display: flex;
  justify-content: center;
  margin: 18px 0 22px;
}

.hero-icon {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: #ffe6c9;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: #ff8a00;
  box-shadow: 0 16px 28px rgba(255, 138, 0, 0.18);
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

.agreement {
  margin: 6px 4px 0;
  font-size: 12px;
  color: #6b7076;
}

.agreement .link {
  color: #ff8a00;
  font-weight: 600;
  margin: 0 4px;
}

.submit-wrap {
  margin-top: 28px;
}

.primary-button {
  background: linear-gradient(135deg, #ff9900 0%, #ff7a00 100%);
  border: none;
  height: 52px;
  font-size: 16px;
  font-weight: 600;
  box-shadow: 0 18px 30px rgba(255, 122, 0, 0.3);
}

.arrow-icon {
  margin-left: 8px;
}

.code-button {
  background: #ffe9d1;
  color: #ff8a00;
  border: none;
  font-weight: 600;
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

:deep(.van-field__left-icon) {
  color: #a0a6ad;
}

:deep(.van-field__control) {
  font-size: 15px;
  color: #1d1f23;
}

:deep(.van-checkbox__label) {
  line-height: 1.6;
}
</style>
