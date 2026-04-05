<template>
  <div class="cats">
    <h1>我的猫咪</h1>
    <div class="cat-list">
      <div v-for="cat in cats" :key="cat.id" class="cat-card">
        <h3>{{ cat.name }}</h3>
        <p>品种: {{ cat.breed }}</p>
        <p>年龄: {{ cat.age }}个月</p>
        <p>性别: {{ cat.gender === 0 ? '母' : '公' }}</p>
        <button @click="selectCat(cat.id)">选择这只猫</button>
        <button @click="editCat(cat.id)">编辑</button>
      </div>
    </div>
    <button @click="addNewCat">添加新猫咪</button>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useCatsStore, useCurrentCatStore } from '@/stores';

const router = useRouter();
const catsStore = useCatsStore();
const currentCatStore = useCurrentCatStore();

// 加载猫咪列表
onMounted(async () => {
  // 在实际开发中，这里会调用API获取猫咪列表
  // catsStore.setCats(await fetchCatsFromAPI());
});

// 获取猫咪列表
const cats = catsStore.getAllCats;

// 选择猫咪
const selectCat = (catId: string) => {
  currentCatStore.setCurrentCat(catId);
  // 在实际开发中，这里可能会导航到猫咪详情页
};

// 编辑猫咪
const editCat = (catId: string) => {
  router.push({ name: 'EditCat', params: { id: catId } });
};

// 添加新猫咪
const addNewCat = () => {
  router.push({ name: 'AddCat' });
};
</script>

<style scoped>
.cats {
  padding: 20px;
}

.cat-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.cat-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  text-align: left;
}

.cat-card h3 {
  margin-top: 0;
}

button {
  margin-right: 10px;
  margin-bottom: 5px;
  padding: 5px 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>