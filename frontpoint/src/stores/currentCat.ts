import { defineStore } from 'pinia';
import { ref, watch, computed } from 'vue';
import { useCatsStore } from './index';
import { getCurrentUserId } from '@/utils/userProfile';

interface CurrentCatState {
  currentCatId: string | null;
}

const getCurrentPetStorageKey = () => {
  const userId = getCurrentUserId();
  return userId ? `current_pet_id:${userId}` : '';
};

const readCurrentCatId = () => {
  const storageKey = getCurrentPetStorageKey();
  return storageKey ? localStorage.getItem(storageKey) : null;
};

export const useCurrentCatStore = defineStore('currentCat', {
  state: (): CurrentCatState => ({
    currentCatId: readCurrentCatId()
  }),

  getters: {
    getCurrentCatId: (state) => state.currentCatId,
    hasSelectedCat: (state) => !!state.currentCatId
  },

  actions: {
    // 设置当前猫咪
    setCurrentCat(catId: string) {
      if (!catId || catId === 'undefined') {
        this.clearCurrentCat();
        return;
      }
      this.currentCatId = catId;
      
      const storageKey = getCurrentPetStorageKey();
      if (storageKey) {
        localStorage.setItem(storageKey, catId);
      }
      localStorage.removeItem('currentCatId');
      localStorage.removeItem('current_pet_id');
      this.onCatChanged(catId);
    },

    // 清除当前猫咪选择
    clearCurrentCat() {
      this.currentCatId = null;
      
      const storageKey = getCurrentPetStorageKey();
      if (storageKey) {
        localStorage.removeItem(storageKey);
      }
      localStorage.removeItem('currentCatId');
      localStorage.removeItem('current_pet_id');
    },

    loadCurrentCat() {
      this.currentCatId = readCurrentCatId();
      localStorage.removeItem('currentCatId');
      localStorage.removeItem('current_pet_id');
    },
    
    onCatChanged(catId: string) {
      void catId;
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
    void newCatId;
  });

  return {
    currentCatId,
    setCurrentCat: currentCatStore.setCurrentCat,
    clearCurrentCat: currentCatStore.clearCurrentCat,
    currentCat: computed(() => catsStore.getCatById(currentCatStore.getCurrentCatId || ''))
  };
};
