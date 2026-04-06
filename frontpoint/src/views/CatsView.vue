<template>
  <div class="cats-page">
    <van-nav-bar title="我的猫咪" fixed placeholder safe-area-inset-top />

    <div class="cat-list" v-if="cats.length > 0">
      <van-card
        v-for="cat in cats"
        :key="cat.id"
        :desc="cat.breed || '神秘的中华田园猫'"
        :title="cat.name"
        :thumb="cat.avatar_url || defaultAvatar"
        @click="goToDetail(cat.id)"
      >
        <template #tags>
          <van-tag plain type="primary" style="margin-right: 4px;">
            {{ cat.gender === 'male' ? '弟弟 ♂' : '妹妹 ♀' }}
          </van-tag>
          <van-tag plain type="success">{{ cat.age_years }}岁{{ cat.age_months }}个月</van-tag>
        </template>
        <template #footer>
          <van-button size="mini" icon="notes-o">健康档案</van-button>
          <van-button size="mini" type="primary" icon="edit">编辑档案</van-button>
        </template>
      </van-card>
    </div>

    <van-empty v-else description="还没有添加猫咪哦，快去接主子回家吧！" />

    <div class="add-btn-wrapper">
      <van-button round type="primary" icon="plus" class="add-btn" @click="goAddCat">
        添加猫咪
      </van-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { showToast } from 'vant';
import { getAllPetProfiles } from '@/api/apiService'; // 正确姿势 🆕
import type { PetProfile } from '@/types/cat';


const router = useRouter();
const cats = ref<PetProfile[]>([]);
// 如果后端没传头像，用这个可爱的默认图
const defaultAvatar = 'https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg'; 

// 页面一打开，就自动去后端拿数据！
onMounted(async () => {
  try {
    showToast({ type: 'loading', message: '正在呼唤主子...', duration: 0 });
    // 💥 看到没？这就是你之前搭好的基建！一行代码就能拿到数据！
  const res = await getAllPetProfiles(); // 正确姿势 🆕
    cats.value = res.data || [];
    showToast.clear();
  } catch (error) {
    showToast.clear();
    showToast({ type: 'fail', message: '获取列表失败，请检查网络' });
  }
});

const goToDetail = (id: string) => {
  console.log('准备查看猫咪详情:', id);
  // router.push(`/cats/${id}`); // 等你写了详情页，把这行注释解开
};

const goAddCat = () => {
  router.push('/cats/add');
};
</script>

<style scoped>
.cats-page {
  min-height: 100vh;
  background-color: #f7f8fa;
  padding-bottom: 80px; /* 给悬浮按钮留位置 */
}

.cat-list {
  padding: 12px;
}

/* 覆盖 Vant 卡片的默认样式，让它变成现代 APP 的圆角阴影卡片 */
:deep(.van-card) {
  border-radius: 12px;
  background-color: #ffffff;
  margin-bottom: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}

.add-btn-wrapper {
  position: fixed;
  bottom: 70px; /* 悬浮在 Tabbar 上方 */
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  pointer-events: none; /* 让包装盒不遮挡下面的点击 */
}

.add-btn {
  pointer-events: auto;
  box-shadow: 0 4px 12px rgba(25, 137, 250, 0.4);
  width: 160px;
}
</style>