import { defineStore } from 'pinia';
import type { CatProfile } from '@/types';
import type { CreateCatProfileRequest, UpdateCatProfileRequest } from '@/types/cat';
import { getAllPetProfiles, createPetProfile, updatePetProfile, deletePetProfile } from '@/api/petProfile';

interface CatsState {
  cats: CatProfile[];
  loading: boolean;
  error: string | null;
}

export const useCatsStore = defineStore('cats', {
  state: (): CatsState => ({
    cats: [],
    loading: false,
    error: null
  }),

  getters: {
    getAllCats: (state) => state.cats,
    getCatById: (state) => {
      return (id: string) => state.cats.find(cat => cat.id === id);
    },
    getCatsByUserId: (state) => {
      return (userId: string) => state.cats.filter(cat => cat.userId === userId);
    },
    getCatsCount: (state) => state.cats.length,
    isLoading: (state) => state.loading,
    getError: (state) => state.error
  },

  actions: {
    // 从API获取所有猫咪档案
    async fetchAllCats() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await getAllPetProfiles();
        const payload = response.data;
        this.cats = Array.isArray(payload) ? payload : payload.list || [];
        // 同步到本地存储
        this.syncToLocalStorage();
      } catch (error: unknown) {
        const errorMessage = (error instanceof Error) ? error.message : '获取猫咪档案列表失败';
        this.error = errorMessage;
        console.error('获取猫咪档案列表失败:', error);
      } finally {
        this.loading = false;
      }
    },

    // 添加猫咪档案
    async addCat(catData: CreateCatProfileRequest) {
      this.loading = true;
      this.error = null;
      
      try {
        // 调用API创建猫咪档案
        const response = await createPetProfile(catData);
        const newCat = response.data;
        
        // 添加到本地状态
        this.cats.push(newCat);
        // 同步到本地存储
        this.syncToLocalStorage();
        
        return newCat;
      } catch (error: unknown) {
        const errorMessage = (error instanceof Error) ? error.message : '添加猫咪档案失败';
        this.error = errorMessage;
        console.error('添加猫咪档案失败:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // 更新猫咪档案
    async updateCat(catId: string, catData: UpdateCatProfileRequest) {
      this.loading = true;
      this.error = null;
      
      try {
        // 调用API更新猫咪档案
        const response = await updatePetProfile(catId, catData);
        const updatedCat = response.data;
        
        // 更新本地状态
        const index = this.cats.findIndex(cat => cat.id === catId);
        if (index !== -1) {
          this.cats.splice(index, 1, updatedCat);
        }
        
        // 同步到本地存储
        this.syncToLocalStorage();
        
        return updatedCat;
      } catch (error: unknown) {
        const errorMessage = (error instanceof Error) ? error.message : '更新猫咪档案失败';
        this.error = errorMessage;
        console.error('更新猫咪档案失败:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // 删除猫咪档案
    async removeCat(catId: string) {
      this.loading = true;
      this.error = null;
      
      try {
        // 调用API删除猫咪档案
        await deletePetProfile(catId);
        
        // 从本地状态移除
        this.cats = this.cats.filter(cat => cat.id !== catId);
        
        // 同步到本地存储
        this.syncToLocalStorage();
      } catch (error: unknown) {
        const errorMessage = (error instanceof Error) ? error.message : '删除猫咪档案失败';
        this.error = errorMessage;
        console.error('删除猫咪档案失败:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // 根据ID获取单个猫咪档案
    async fetchCatById(catId: string) {
      this.loading = true;
      this.error = null;
      
      try {
        // 先检查本地是否存在
        const localCat = this.cats.find(cat => cat.id === catId);
        if (localCat) {
          this.loading = false;
          return localCat;
        }
        
        // 如果本地不存在，从API获取
        // 注意：这里需要在API中添加获取单个猫咪的函数
        // const response = await getPetProfile(catId);
        // const fetchedCat = response.data;
        
        // 更新本地状态
        // this.cats.push(fetchedCat);
        
        // 同步到本地存储
        // this.syncToLocalStorage();
        
        // 这里返回本地的猫咪，如果没有则返回undefined
        return localCat;
      } catch (error: unknown) {
        const errorMessage = (error instanceof Error) ? error.message : '获取猫咪档案详情失败';
        this.error = errorMessage;
        console.error('获取猫咪档案详情失败:', error);
        throw error;
      } finally {
        this.loading = false;
      }
    },

    // 设置所有猫咪档案
    setCats(cats: CatProfile[]) {
      this.cats = cats;
      // 同步到本地存储
      this.syncToLocalStorage();
    },

    // 清空所有猫咪档案
    clearCats() {
      this.cats = [];
      // 同步到本地存储
      this.syncToLocalStorage();
    },

    // 从本地存储同步数据
    loadFromLocalStorage() {
      const storedCats = localStorage.getItem('cats');
      if (storedCats) {
        try {
          this.cats = JSON.parse(storedCats);
        } catch (error) {
          console.error('解析本地存储的猫咪数据失败:', error);
        }
      }
    },

    // 同步数据到本地存储
    syncToLocalStorage() {
      try {
        localStorage.setItem('cats', JSON.stringify(this.cats));
      } catch (error) {
        console.error('同步猫咪数据到本地存储失败:', error);
      }
    }
  }
});