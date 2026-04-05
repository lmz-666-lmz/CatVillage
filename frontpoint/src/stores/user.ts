import { defineStore } from 'pinia';
import type { User } from '@/types';

interface UserState {
  userInfo: User | null;
  token: string | null;
  isAuthenticated: boolean;
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    userInfo: null,
    token: null,
    isAuthenticated: false
  }),

  getters: {
    isLoggedIn: (state) => !!state.token && state.isAuthenticated,
    getUserInfo: (state) => state.userInfo,
    getToken: (state) => state.token
  },

  actions: {
    // 登录
    async login(token: string) {
      this.token = token;
      this.isAuthenticated = true;
      localStorage.setItem('token', token);
    },

    // 登出
    async logout() {
      this.userInfo = null;
      this.token = null;
      this.isAuthenticated = false;
      localStorage.removeItem('token');
    },

    // 设置用户信息
    setUserInfo(userInfo: User) {
      this.userInfo = userInfo;
    },

    // 从本地存储恢复登录状态
    restoreLoginState() {
      const token = localStorage.getItem('token');
      if (token) {
        this.token = token;
        this.isAuthenticated = true;
      }
    }
  }
});