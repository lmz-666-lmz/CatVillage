import { defineStore } from 'pinia';
import { ref, watch, computed } from 'vue';
import { useCatsStore } from './index';

interface CurrentCatState {
  currentCatId: string | null;
}

export const useCurrentCatStore = defineStore('currentCat', {
  state: (): CurrentCatState => ({
    currentCatId: localStorage.getItem('currentCatId') || null
  }),

  getters: {
    getCurrentCatId: (state) => state.currentCatId,
    hasSelectedCat: (state) => !!state.currentCatId
  },

  actions: {
    // 设置当前猫咪
    setCurrentCat(catId: string) {
      this.currentCatId = catId;
      
      // 保存到本地存储
      localStorage.setItem('currentCatId', catId);
      
      // 当猫咪切换时，可以在这里触发其他模块的更新逻辑
      console.log(`当前选中猫咪已切换至: ${catId}`);
      
      // 可以在这里通知其他模块更新数据
      this.onCatChanged(catId);
    },

    // 清除当前猫咪选择
    clearCurrentCat() {
      this.currentCatId = null;
      
      // 从本地存储中清除
      localStorage.removeItem('currentCatId');
    },
    
    // 猫咪切换后的处理逻辑
    onCatChanged(catId: string) {
      // 这里可以触发其他模块的数据更新
      // 例如：更新社交动态、消息、情绪记录等
      console.log(`猫咪切换后处理逻辑执行，新猫咪ID: ${catId}`);
      
      // 示例：触发相关模块数据刷新
      // refreshSocialDataForCat(catId);
      // refreshMessageDataForCat(catId);
      // refreshEmotionDataForCat(catId);
      // refreshAIAssistantDataForCat(catId);
    }
  }
});

// 创建一个响应式引用，用于监听猫咪切换事件
export const currentCatWatcher = () => {
  const currentCatStore = useCurrentCatStore();
  const catsStore = useCatsStore();
  const currentCatId = ref(currentCatStore.getCurrentCatId);

  // 监听猫咪切换
  watch(() => currentCatStore.getCurrentCatId, (newCatId) => {
    currentCatId.value = newCatId;
    console.log(`监测到猫咪切换: ${newCatId}`);
    
    // 在这里可以执行其他模块的数据更新逻辑
    if (newCatId) {
      // 更新与当前猫咪相关的数据
      // 示例：获取与新猫咪相关的社交动态、消息等
      console.log(`正在为猫咪 ${newCatId} 更新相关数据`);
    }
  });

  return {
    currentCatId,
    setCurrentCat: currentCatStore.setCurrentCat,
    clearCurrentCat: currentCatStore.clearCurrentCat,
    currentCat: computed(() => catsStore.getCatById(currentCatStore.getCurrentCatId || ''))
  };
};