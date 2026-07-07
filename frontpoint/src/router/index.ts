import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';
import { showToast } from 'vant';

// 定义路由数组
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/welcome'
  },
  {
    path: '/welcome',
    name: 'Welcome',
    component: () => import('../views/WelcomeView.vue'),
    meta: { title: '欢迎', hideTabbar: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/RegisterView.vue'),
    meta: { title: '注册' }
  },
  {
    path: '/cats',
    name: 'Cats',
    redirect: { name: 'Emotions' },
    meta: { title: '喵喵台', requiresAuth: true }
  },
  {
    path: '/cats/history/:recordId',
    name: 'MeowRecordDetail',
    component: () => import('../views/MeowRecordDetailView.vue'),
    meta: { title: '喵喵台记录详情', requiresAuth: true, hideTabbar: true },
    props: true
  },
  {
    path: '/cats/add',
    name: 'AddCat',
    component: () => import('../views/AddCatView.vue'),
    meta: { title: '添加猫咪', requiresAuth: true, hideTabbar: true }
  },
  {
    path: '/cats/:id/edit',
    name: 'EditCat',
    component: () => import('../views/EditCatView.vue'),
    meta: { title: '编辑猫咪', requiresAuth: true },
    props: true
  },
  {
    path: '/cats/:id/archive',
    name: 'CatArchive',
    component: () => import('../views/CatArchiveView.vue'),
    meta: { title: '猫咪档案', requiresAuth: true, hideTabbar: true },
    props: true
  },
  {
    path: '/social',
    name: 'Social',
    component: () => import('../views/SocialView.vue'),
    meta: { title: '社交广场', requiresAuth: true }
  },
  {
    path: '/social/search',
    name: 'SocialSearch',
    component: () => import('../views/SocialSearchView.vue'),
    meta: { title: '广场搜索', requiresAuth: true, hideTabbar: true }
  },
  {
    path: '/social/:id',
    name: 'SocialDetail',
    component: () => import('../views/SocialDetailView.vue'),
    meta: { title: '动态详情', requiresAuth: true, hideTabbar: true },
    props: true
  },
  {
    path: '/social/create',
    name: 'CreatePost',
    component: () => import('../views/CreatePostView.vue'),
    meta: { title: '发布动态', requiresAuth: true }
  },
  {
    path: '/messages',
    name: 'Messages',
    component: () => import('../views/MessagesView.vue'),
    meta: { title: '消息中心', requiresAuth: true }
  },
  {
    path: '/messages/add-friend',
    name: 'AddFriend',
    component: () => import('../views/AddFriendView.vue'),
    meta: { title: '添加好友', requiresAuth: true }
  },
  {
    path: '/messages/chat/:targetUserId',
    name: 'ChatDetail',
    component: () => import('../views/ChatDetailView.vue'),
    meta: { title: '私信聊天', requiresAuth: true, hideTabbar: true },
    props: true
  },
  {
    path: '/emotions',
    name: 'Emotions',
    component: () => import('../views/EmotionsView.vue'),
    meta: { title: '情绪识别', requiresAuth: true }
  },
  {
    path: '/ai-assistant',
    name: 'AIAssistant',
    component: () => import('../views/AIAssistantView.vue'),
    meta: { title: '养护助理', requiresAuth: true }
  },
  {
    path: '/doctors',
    name: 'ProfessionalDoctors',
    component: () => import('../views/ProfessionalDoctorsView.vue'),
    meta: { title: '专业医生', requiresAuth: true, hideTabbar: true }
  },
  {
    path: '/profile',
    name: 'UserProfile',
    component: () => import('../views/UserProfileView.vue'),
    meta: { title: '个人资料', requiresAuth: true }
  },
  {
    path: '/profile/favorites',
    name: 'MyFavorites',
    component: () => import('../views/MyFavoritesView.vue'),
    meta: { title: '我的收藏', requiresAuth: true, hideTabbar: true }
  },
  {
    path: '/my-pets',
    name: 'MyPets',
    component: () => import('../views/MyPetsView.vue'),
    meta: { title: '我的萌宠', requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/SettingsView.vue'),
    meta: { title: '系统设置', requiresAuth: true, hideTabbar: true }
  },
  {
    path: '/settings/notification',
    name: 'SettingsNotification',
    component: () => import('../views/SettingsNotificationView.vue'),
    meta: { title: '通知设置', requiresAuth: true, hideTabbar: true }
  },
  {
    path: '/settings/privacy',
    name: 'SettingsPrivacy',
    component: () => import('../views/SettingsPrivacyView.vue'),
    meta: { title: '隐私设置', requiresAuth: true, hideTabbar: true }
  },
  {
    path: '/cats/audio-history',
    name: 'AudioHistory',
    component: () => import('../views/AudioHistoryView.vue'),
    meta: { title: '全部音频记录', requiresAuth: true, hideTabbar: true }
  },
  {
    path: '/feeding',
    name: 'FeedRecord',
    component: () => import('../views/FeedRecordView.vue'),
    meta: { title: '投喂记录', requiresAuth: true, hideTabbar: true }
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: () => import('../views/AdminDashboardView.vue'),
    meta: { title: '后台管理', requiresAuth: true, hideTabbar: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFoundView.vue'),
    meta: { title: '页面未找到' }
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

// 路由守卫：已修正为 Vue Router 4 推荐写法
router.beforeEach((to, _from) => {
  // 设置页面标题
  document.title = (to.meta.title as string) || '猫咪社交与健康管理APP';

  const requiresAuth = to.meta.requiresAuth;
  if (requiresAuth) {
    const token = localStorage.getItem('token');
    if (!token) {
      // 未登录且访问受限页面，跳转到登录页
      return { name: 'Login' };
    }

    // 管理员页面前端预检（后端所有 admin API 均有 require_admin 强制校验，不可绕过）
    if (to.path === '/admin') {
      const isAdmin = localStorage.getItem('is_admin') === 'true';
      if (!isAdmin) {
        showToast({ type: 'fail', message: '需要管理员权限' });
        return { name: 'Social' };
      }
    }
  }
  // 默认放行
  return true;
});

export default router;
