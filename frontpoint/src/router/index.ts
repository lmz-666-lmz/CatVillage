import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';

// 定义路由数组
const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomeView.vue'),
    meta: { title: '首页', requiresAuth: true }
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
    path: '/social',
    name: 'Social',
    component: () => import('../views/SocialView.vue'),
    meta: { title: '社交广场', requiresAuth: true }
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
    path: '/profile',
    name: 'UserProfile',
    component: () => import('../views/UserProfileView.vue'),
    meta: { title: '个人资料', requiresAuth: true }
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