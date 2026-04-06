<template>
  <div class="login-page">
    <h2 class="title">欢迎回到猫村 🐾</h2>

    <van-form @submit="onSubmit">
      <van-cell-group inset>
        <van-field
          v-model="username"
          name="username"
          label="账号"
          placeholder="请输入账号"
          :rules="[{ required: true, message: '请填写账号' }]"
        />
        <van-field
          v-model="password"
          type="password"
          name="password"
          label="密码"
          placeholder="请输入密码"
          :rules="[{ required: true, message: '请填写密码' }]"
        />
      </van-cell-group>

      <div style="margin: 32px 16px;">
        <van-button round block type="primary" native-type="submit">
          点我登录
        </van-button>
      </div>

      <div class="register-link">
        还没有账号？
        <router-link to="/register">立即注册</router-link>
      </div>
    </van-form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { closeToast, showToast } from 'vant';
import { loginUser } from '@/api/apiService';

const router = useRouter();

// 定义前端输入的变量
const username = ref('');
const password = ref('');

// 点击按钮后触发的真实逻辑！
const onSubmit = async (values: any) => {
  try {
    showToast({ type: 'loading', message: '正在进入猫村...', forbidClick: true });
    const res = await loginUser(values.username, values.password);

    // 拿到你刚才看到的那个长长的 token，存起来
    localStorage.setItem('token', res.access_token);
    // 避免切换账号后沿用旧账号的猫咪缓存，导致 AI 使用错误 pet_id
    localStorage.removeItem('cats');
    localStorage.removeItem('currentCatId');
    closeToast();
    showToast({ type: 'success', message: '登录成功！' });

    // 丝滑跳转到首页
    router.push('/');
    
  } catch (error) {
    closeToast();
    showToast({ type: 'fail', message: '账号或密码错啦' });
  }
};
</script>

<style scoped>
.login-page {
  padding-top: 80px;
}
.title {
  text-align: center;
  color: #333;
  margin-bottom: 40px;
}

.register-link {
  text-align: center;
  margin-top: 8px;
  color: #666;
}

.register-link a {
  color: #ff8a00;
  font-weight: 700;
  text-decoration: none;
}
</style>