import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';

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
    path: '/home',
    name: 'Home',
    component: () => import('../views/SocialView.vue'),
    meta: { title: '社交广场', requiresAuth: true }
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
    component: () => import('../views/CatsView.vue'),
    meta: { title: '我的猫咪', requiresAuth: true }
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
    meta: { title: 'AI助理', requiresAuth: true }
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
    path: '/settings/account',
    name: 'SettingsAccount',
    component: () => import('../views/SettingsAccountView.vue'),
    meta: { title: '账号与安全', requiresAuth: true, hideTabbar: true }
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
    path: '/settings/history',
    name: 'SettingsHistory',
    component: () => import('../views/SettingsHistoryView.vue'),
    meta: { title: '浏览历史', requiresAuth: true, hideTabbar: true }
  },
  {
    path: '/settings/about',
    name: 'SettingsAbout',
    component: () => import('../views/SettingsAboutView.vue'),
    meta: { title: '关于猫村', requiresAuth: true, hideTabbar: true }
  },
  {
    path: '/settings/policy',
    name: 'SettingsPolicy',
    component: () => import('../views/SettingsPolicyView.vue'),
    meta: { title: '隐私协议与条款', requiresAuth: true, hideTabbar: true }
  },
  {
    path: '/settings/visual-recognition',
    name: 'VisualRecognition',
    component: () => import('../views/VisualRecognitionView.vue'),
    meta: { title: '视觉识别', requiresAuth: true, hideTabbar: true }
  },
  {
    path: '/settings/audio-visual-fusion',
    name: 'AudioVisualFusion',
    component: () => import('../views/AudioVisualFusionView.vue'),
    meta: { title: '视听融合', requiresAuth: true, hideTabbar: true }
  },
  {
    path: '/cats/audio-history',
    name: 'AudioHistory',
    component: () => import('../views/AudioHistoryView.vue'),
    meta: { title: '全部音频记录', requiresAuth: true }
  },
  {
    path: '/feeding',
    name: 'FeedRecord',
    component: () => import('../views/FeedRecordView.vue'),
    meta: { title: '投喂记录', requiresAuth: true }
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
  }
  // 默认放行
  return true;
});

export default router;