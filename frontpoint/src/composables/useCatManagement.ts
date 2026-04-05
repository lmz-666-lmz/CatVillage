/* eslint-disable @typescript-eslint/no-explicit-any */

import { ref, computed } from 'vue';
import { useCatsStore } from '@/stores';
import type { CreateCatProfileRequest, UpdateCatProfileRequest } from '@/types/cat';

/**
 * 猫咪档案管理 Composable
 * 提供猫咪档案的增删改查等操作方法
 */
export function useCatManagement() {
  const catsStore = useCatsStore();
  const loading = ref(false);
  const error = ref<string | null>(null);

  /**
   * 创建新猫咪档案
   */
  const createCat = async (catData: CreateCatProfileRequest) => {
    loading.value = true;
    error.value = null;

    try {
      const result = await catsStore.addCat(catData);
      return result;
    } catch (err: any) {
      error.value = err.message || '创建猫咪档案失败';
      console.error('创建猫咪档案失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 更新猫咪档案
   */
  const updateCat = async (catId: string, catData: UpdateCatProfileRequest) => {
    loading.value = true;
    error.value = null;

    try {
      const result = await catsStore.updateCat(catId, catData);
      return result;
    } catch (err: any) {
      error.value = err.message || '更新猫咪档案失败';
      console.error('更新猫咪档案失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 删除猫咪档案
   */
  const deleteCat = async (catId: string) => {
    loading.value = true;
    error.value = null;

    try {
      await catsStore.removeCat(catId);
    } catch (err: any) {
      error.value = err.message || '删除猫咪档案失败';
      console.error('删除猫咪档案失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 获取所有猫咪档案
   */
  const getAllCats = computed(() => catsStore.getAllCats);

  /**
   * 根据ID获取猫咪档案
   */
  const getCatById = (id: string) => {
    return catsStore.getCatById(id);
  };

  /**
   * 根据用户ID获取猫咪档案
   */
  const getCatsByUserId = (userId: string) => {
    return catsStore.getCatsByUserId(userId);
  };

  /**
   * 获取猫咪数量
   */
  const getCatsCount = computed(() => catsStore.getCatsCount);

  /**
   * 是否正在加载
   */
  const isLoading = computed(() => catsStore.isLoading || loading.value);

  /**
   * 获取错误信息
   */
  const getError = computed(() => error.value || catsStore.getError);

  return {
    // Methods
    createCat,
    updateCat,
    deleteCat,
    
    // Getters
    getAllCats,
    getCatById,
    getCatsByUserId,
    getCatsCount,
    isLoading,
    getError
  };
}