<template>
  <div class="login">
    <h1>用户登录</h1>
    <form @submit.prevent="handleLogin">
      <div class="input-group">
        <label for="username">用户名:</label>
        <input 
          id="username" 
          v-model="username" 
          type="text" 
          placeholder="请输入用户名"
          required
        />
      </div>
      
      <div class="input-group">
        <label for="password">密码:</label>
        <input 
          id="password" 
          v-model="password" 
          type="password" 
          placeholder="请输入密码"
          required
        />
      </div>
      
      <button type="submit" :disabled="loading">
        {{ loading ? '登录中...' : '登录' }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';

const router = useRouter();
const userStore = useUserStore();

const username = ref('');
const password = ref('');
const loading = ref(false);

const handleLogin = async () => {
  loading.value = true;
  
  try {
    // 这里模拟登录请求，实际开发中需要调用API
    // const response = await loginApi({ username: username.value, password: password.value });
    // 模拟成功登录，设置一个假的token
    await userStore.login('fake-token-' + Date.now());
    await userStore.setUserInfo({
      id: '1',
      username: username.value,
      nickname: username.value,
      avatar: '',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    });
    
    // 登录成功后跳转到首页
    router.push({ name: 'Home' });
  } catch (error) {
    console.error('登录失败:', error);
    alert('登录失败，请检查用户名和密码');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.input-group {
  margin-bottom: 15px;
}

.input-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.input-group input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
}

button {
  width: 100%;
  padding: 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
</style>