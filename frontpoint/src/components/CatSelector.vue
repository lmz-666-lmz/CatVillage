<template>
  <div class="cat-selector">
    <div class="selector-header">
      <h3>选择猫咪</h3>
      <BaseButton @click="toggleDropdown" variant="outline" size="small">
        {{ isOpen ? '收起' : '展开' }}
        <span :class="['arrow', { 'arrow-down': !isOpen, 'arrow-up': isOpen }]">▼</span>
      </BaseButton>
    </div>

    <div v-show="isOpen" class="selector-content">
      <div 
        v-for="cat in cats" 
        :key="cat.id"
        :class="['cat-item', { 'cat-item--selected': cat.id === currentCatId }]"
        @click="selectCat(cat.id)"
      >
        <img :src="cat.avatarUrl || defaultAvatar" :alt="cat.name" class="cat-avatar" />
        <div class="cat-info">
          <h4>{{ cat.name }}</h4>
          <p>{{ cat.breed }} • {{ cat.age }}个月大</p>
        </div>
      </div>
      
      <div v-if="cats.length === 0" class="no-cats">
        <p>暂无猫咪档案，请先添加</p>
      </div>
    </div>

    <div v-if="currentCatId" class="current-selection">
      <p>当前选中: <strong>{{ currentCatName }}</strong></p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import BaseButton from './BaseButton.vue';
import { useCatsStore, useCurrentCatStore } from '@/stores';

const catsStore = useCatsStore();
const currentCatStore = useCurrentCatStore();

const isOpen = ref(false);
const defaultAvatar = '/src/assets/default-cat-avatar.png'; // 默认猫咪头像

// 切换下拉显示
const toggleDropdown = () => {
  isOpen.value = !isOpen.value;
};

// 选择猫咪
const selectCat = (catId: string) => {
  currentCatStore.setCurrentCat(catId);
  isOpen.value = false; // 选择后自动收起
};

// 获取当前选中的猫咪名称
const currentCatName = computed(() => {
  if (!currentCatStore.getCurrentCatId) return '';
  const cat = catsStore.getCatById(currentCatStore.getCurrentCatId);
  return cat ? cat.name : '';
});

// 获取猫咪列表
const cats = computed(() => catsStore.getAllCats);

// 获取当前选中的猫咪ID
const currentCatId = computed(() => currentCatStore.getCurrentCatId);

// 初始化时获取猫咪列表
onMounted(() => {
  // 在实际应用中，这里应该从API获取猫咪列表
  // catsStore.setCats(await fetchCatsFromAPI());
});
</script>

<style scoped>
.cat-selector {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 16px;
  margin-bottom: 20px;
}

.selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.selector-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.arrow {
  display: inline-block;
  transition: transform 0.3s;
  font-size: 12px;
  margin-left: 4px;
}

.arrow-up {
  transform: rotate(180deg);
}

.selector-content {
  max-height: 300px;
  overflow-y: auto;
}

.cat-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-bottom: 8px;
}

.cat-item:hover {
  background-color: #f5f7fa;
}

.cat-item--selected {
  background-color: #ecf5ff;
  border-left: 4px solid #409eff;
}

.cat-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 12px;
  background-color: #f0f2f5;
}

.cat-info {
  flex: 1;
}

.cat-info h4 {
  margin: 0 0 4px 0;
  font-size: 16px;
  color: #303133;
}

.cat-info p {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.no-cats {
  text-align: center;
  padding: 20px;
  color: #909399;
}

.current-selection {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}
</style>