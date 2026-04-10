<template>
  <div class="relative w-full max-w-[430px] mx-auto min-h-screen bg-surface flex flex-col text-on-surface pb-20">
    
    <!-- TopAppBar -->
    <header class="sticky top-0 w-full flex justify-between items-center px-4 py-3 bg-white/70 dark:bg-black/70 backdrop-blur-md z-50">
      <div class="flex items-center gap-2">
        <span class="text-xl font-bold text-[#FF6B35]">我的</span>
      </div>
      <div class="flex items-center">
        <!-- 去往设置页 -->
        <button class="hover:opacity-80 transition-opacity p-2 active:scale-95">
          <van-icon name="setting-o" class="text-on-surface-variant text-2xl" />
        </button>
      </div>
    </header>

    <main class="flex-1 overflow-y-auto" style="-ms-overflow-style: none; scrollbar-width: none;">
      
      <!-- 1. Profile Section (头像与数据统计) -->
      <section class="px-6 py-8 flex flex-col items-center">
        <div class="relative mb-4">
          <div class="w-24 h-24 rounded-full border-4 border-white dark:border-inverse-surface shadow-xl overflow-hidden">
            <img :src="userInfo.avatar" alt="User Avatar" class="w-full h-full object-cover"/>
          </div>
          <!-- 右下角修饰猫爪 -->
          <div class="absolute bottom-0 right-0 bg-primary-container p-1 rounded-full border-2 border-white dark:border-inverse-surface">
            <!-- 修复的小猫爪 -->
            <svg class="w-4 h-4 text-white" viewBox="0 0 24 24" fill="currentColor">
              <path d="M8.5 7.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zm7 0a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zM4 11.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zm16 0a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zM12 11c-2.3 0-5.1.7-6.5 2.8C4 16.1 5.4 20 12 20s8-3.9 6.5-6.2C17.1 11.7 14.3 11 12 11z"/>
            </svg>
          </div>
        </div>
        <h1 class="text-2xl font-bold text-on-surface mb-1">{{ userInfo.name }}</h1>
        <p class="text-on-surface-variant text-sm mb-6">{{ userInfo.bio }}</p>
        
        <!-- Stats Panel -->
        <div class="flex w-full justify-around bg-surface-container-lowest dark:bg-inverse-surface rounded-xl p-4 shadow-sm max-w-sm">
          <div class="text-center cursor-pointer active:scale-95 transition-transform">
            <div class="text-lg font-bold text-on-surface">{{ userInfo.stats.following }}</div>
            <div class="text-xs text-on-surface-variant">关注</div>
          </div>
          <div class="w-px h-8 bg-surface-container my-auto"></div>
          <div class="text-center cursor-pointer active:scale-95 transition-transform">
            <div class="text-lg font-bold text-on-surface">{{ userInfo.stats.followers }}</div>
            <div class="text-xs text-on-surface-variant">粉丝</div>
          </div>
          <div class="w-px h-8 bg-surface-container my-auto"></div>
          <div class="text-center cursor-pointer active:scale-95 transition-transform">
            <div class="text-lg font-bold text-on-surface">{{ userInfo.stats.likes }}</div>
            <div class="text-xs text-on-surface-variant">获赞</div>
          </div>
        </div>
      </section>

      <!-- 2. Bento Grid Entry Points (便当盒导航网格) -->
      <section class="px-6 space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <!-- 左侧大方块：我的萌宠 -->
          <div class="bg-primary-fixed dark:bg-primary-fixed-dim text-on-primary-fixed-variant p-5 rounded-xl flex flex-col justify-between aspect-square active:scale-[0.98] transition-transform cursor-pointer" @click="navigateTo('MyPets')">
            <svg class="text-white w-9 h-9 opacity-90" viewBox="0 0 24 24" fill="currentColor"><path d="M8.5 7.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zm7 0a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zM4 11.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zm16 0a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zM12 11c-2.3 0-5.1.7-6.5 2.8C4 16.1 5.4 20 12 20s8-3.9 6.5-6.2C17.1 11.7 14.3 11 12 11z"/></svg>
            <div>
              <div class="text-lg font-bold">我的萌宠</div>
              <div class="text-xs opacity-70">{{ userInfo.petsCount }}只毛孩子已上线</div>
            </div>
          </div>
          
          <!-- 右侧堆叠长条卡片 -->
          <div class="grid grid-rows-2 gap-4">
            <!-- 我的收藏 -->
            <div class="bg-surface-container-lowest dark:bg-inverse-surface p-4 rounded-xl flex items-center justify-between active:scale-[0.98] transition-transform cursor-pointer border border-[#FF6B35]/10">
              <div class="flex items-center gap-3">
                <div class="flex items-center justify-center bg-[#FFF3E0] w-8 h-8 rounded-full">
                  <van-icon name="star" class="text-[#F97316] text-lg" />
                </div>
                <span class="font-bold text-sm">我的收藏</span>
              </div>
              <van-icon name="arrow" class="text-sm opacity-50 text-on-surface-variant" />
            </div>
            <!-- 村内笔记 -->
            <div class="bg-surface-container-lowest dark:bg-inverse-surface p-4 rounded-xl flex items-center justify-between active:scale-[0.98] transition-transform cursor-pointer border border-[#3B82F6]/10">
              <div class="flex items-center gap-3">
                <div class="flex items-center justify-center bg-[#EFF6FF] w-8 h-8 rounded-full">
                  <van-icon name="notes-o" class="text-[#3B82F6] text-lg" />
                </div>
                <span class="font-bold text-sm">村内笔记</span>
              </div>
              <van-icon name="arrow" class="text-sm opacity-50 text-on-surface-variant" />
            </div>
          </div>
        </div>

        <!-- 3. List Menus (功能列表) -->
        <div class="bg-surface-container-low dark:bg-surface-container rounded-xl p-2">
          <div class="bg-surface-container-lowest dark:bg-inverse-surface rounded-lg">
            <div 
              v-for="(menu, index) in menuItems" 
              :key="index"
              class="flex items-center justify-between p-4 cursor-pointer active:bg-surface-container dark:active:bg-surface-container-high transition-colors"
              :class="{ 'border-b border-surface-container/20 dark:border-outline-variant/10': index !== menuItems.length - 1 }"
              @click="handleMenuClick(menu.title)"
            >
              <div class="flex items-center gap-4">
                <div :class="`w-10 h-10 rounded-lg flex items-center justify-center ${menu.iconBgClass}`">
                  <van-icon :name="menu.icon" size="20" :class="menu.iconTextClass" />
                </div>
                <div>
                  <div class="font-bold text-sm text-on-surface dark:text-inverse-on-surface">{{ menu.title }}</div>
                  <div class="text-[10px] text-on-surface-variant">{{ menu.subtitle }}</div>
                </div>
              </div>
              <van-icon name="arrow" class="text-on-surface-variant/40" />
            </div>
          </div>
        </div>

        <!-- 4. Decorative Card (VIP 横幅) -->
        <div class="relative overflow-hidden rounded-xl h-24 bg-primary p-4 flex items-center justify-between group cursor-pointer active:scale-[0.98] transition-transform mb-6">
          <div class="relative z-10">
            <h3 class="text-white font-bold text-lg">喵村VIP</h3>
            <p class="text-white/80 text-xs">解锁专属挂件与勋章</p>
          </div>
          <!-- 背景悬浮猫爪水印，自带 hover 扩大动效 -->
          <div class="absolute -right-4 -bottom-4 opacity-10 group-hover:scale-110 transition-transform duration-500">
            <svg class="w-32 h-32 text-white" viewBox="0 0 24 24" fill="currentColor">
              <path d="M8.5 7.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zm7 0a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zM4 11.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zm16 0a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zM12 11c-2.3 0-5.1.7-6.5 2.8C4 16.1 5.4 20 12 20s8-3.9 6.5-6.2C17.1 11.7 14.3 11 12 11z"/>
            </svg>
          </div>
          <button class="bg-white text-primary px-4 py-1.5 rounded-full text-xs font-bold relative z-10 shadow-sm active:scale-95 transition-transform">
            立即开启
          </button>
        </div>

      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();

const navigateTo = (routeName: string) => {
  router.push({ name: routeName });
};

const handleMenuClick = (title: string) => {
  if (title === '健康档案') {
    router.push({ name: 'CatArchive' });
  } else if (title === '喵村市集') {
    // TODO: 实现喵村市集
  } else if (title === '领养信息') {
    // TODO: 实现领养信息
  }
};

const menuItems = ref([
  {
    icon: 'cart-o',
    title: '喵村市集',
    subtitle: '领券买罐罐更划算',
    iconBgClass: 'bg-[#FFF3E0] dark:bg-orange-900/30',
    iconTextClass: 'text-[#F97316]' // 高对比橙色
  },
  {
    icon: 'notes-o',
    title: '健康档案',
    subtitle: '记录疫苗与体检',
    iconBgClass: 'bg-[#EFF6FF] dark:bg-blue-900/30',
    iconTextClass: 'text-[#3B82F6]' // 高对比蓝色
  },
  {
    icon: 'friends-o',
    title: '领养信息',
    subtitle: '寻找温暖的家',
    iconBgClass: 'bg-[#F3E8FF] dark:bg-purple-900/30',
    iconTextClass: 'text-[#8B5CF6]' // 高对比紫色
  }
]);

const userInfo = ref({
  name: '橘猫村长',
  avatar: 'https://lh3.googleusercontent.com/aida-public/AB6AXuCAuOPBDDXlqyjPXspBSIzUZ9QdJldSFhFDwTVv-ZKBzGgZ-Zn302KSb5bZNvxYcmIaGxpwl3nbZ1PUMW6Oy5XLJpcWQK9KM4srdITVAbTMxsOu9VWyoeKiEZkqSz_Wx_964TDvY234eA0ZVMGRNaHU3yJVCUe_IyhXF619g6b6a_SZrdqeGnGGMvnx1k4ARyvvyGCM-lXq-n62ZL14mE67HzeL8vRtyoEKF_zOvObfSfloobq9Ebi1HIF33sQlZy9gVAJQK7aDSQ',
  bio: '村里的一只普通巡逻官 🐾',
  petsCount: 3,
  stats: {
    following: '1.2k',
    followers: '5.8k',
    likes: '12.4k'
  }
});
</script>

<style scoped>
main::-webkit-scrollbar {
  display: none;
}
</style>
