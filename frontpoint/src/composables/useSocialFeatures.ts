/* eslint-disable @typescript-eslint/no-explicit-any */

import { ref, computed } from 'vue';
import type { 
  SocialDynamic, 
  PublishDynamicRequest, 
  CommentRequest,
  CommentResponse
} from '@/types/social';
import { 
  publishDynamic, 
  getDynamicsList, 
  getFollowingDynamicsList,
  getDynamicDetail, 
  updateDynamic,
  likeDynamic, 
  unlikeDynamic, 
  toggleFavoriteDynamic,
  toggleFollowUser,
  toggleCommentLike,
  postComment, 
  deleteComment,
  deleteDynamic,
  getMyDynamicsList 
} from '@/api/social';

/**
 * 社交功能 Composable
 * 提供动态发布、获取、点赞、评论等操作方法
 */
export function useSocialFeatures() {
  const loading = ref(false);
  const error = ref<string | null>(null);
  const dynamics = ref<SocialDynamic[]>([]);

  /**
   * 发布动态
   */
  const publishNewDynamic = async (data: PublishDynamicRequest) => {
    loading.value = true;
    error.value = null;

    try {
      const formData = new FormData();
      formData.append('catId', data.catId);
      formData.append('content', data.content);
      (data.images || []).forEach((image) => formData.append('images', image));
      const response = await publishDynamic(formData);
      // TODO: 根据实际API响应结构调整
      return response.data;
    } catch (err: any) {
      error.value = err.message || '发布动态失败';
      console.error('发布动态失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 获取广场动态列表
   */
  const fetchDynamicsList = async (params: { page: number; pageSize: number; catId?: string; scope?: 'all' | 'following' }) => {
    loading.value = true;
    error.value = null;

    try {
      const response = params.scope === 'following'
        ? await getFollowingDynamicsList(params)
        : await getDynamicsList(params);
      dynamics.value = response.data.list || [];
      return response.data;
    } catch (err: any) {
      error.value = err.message || '获取动态列表失败';
      console.error('获取动态列表失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const fetchFollowingDynamicsList = async (params: { page: number; pageSize: number; catId?: string }) => {
    return fetchDynamicsList({ ...params, scope: 'following' });
  };

  /**
   * 获取我的动态列表
   */
  const fetchMyDynamicsList = async (params: { page: number; pageSize: number; catId?: string }) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await getMyDynamicsList(params);
      dynamics.value = response.data.list || [];
      return response.data;
    } catch (err: any) {
      error.value = err.message || '获取我的动态列表失败';
      console.error('获取我的动态列表失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 获取动态详情
   */
  const fetchDynamicDetail = async (dynamicId: string) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await getDynamicDetail(dynamicId);
      return response.data;
    } catch (err: any) {
      error.value = err.message || '获取动态详情失败';
      console.error('获取动态详情失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const editDynamic = async (dynamicId: string, content: string) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await updateDynamic(dynamicId, { content });
      const dynamicIndex = dynamics.value.findIndex(d => d.id === dynamicId);
      if (dynamicIndex !== -1) {
        dynamics.value[dynamicIndex] = response.data as SocialDynamic;
      }
      return response.data as SocialDynamic;
    } catch (err: any) {
      error.value = err.message || '编辑动态失败';
      console.error('编辑动态失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 点赞动态
   */
  const likeADynamic = async (dynamicId: string) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await likeDynamic(dynamicId);
      // 以后端返回真实值为准，不做本地 +1（避免重复叠加）
      const serverLikeCount = (response.data as any)?.like_count ?? (response.data as any)?.likeCount;
      const dynamicIndex = dynamics.value.findIndex(d => d.id === dynamicId);
      if (dynamicIndex !== -1) {
        dynamics.value[dynamicIndex]!.isLiked = true;
        if (typeof serverLikeCount === 'number') {
          dynamics.value[dynamicIndex]!.likeCount = serverLikeCount;
        }
      }
      return response.data;
    } catch (err: any) {
      error.value = err.message || '点赞动态失败';
      console.error('点赞动态失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 取消点赞
   */
  const unlikeADynamic = async (dynamicId: string) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await unlikeDynamic(dynamicId);
      // 以后端返回真实值为准，不做本地 -1
      const serverLikeCount = (response.data as any)?.like_count ?? (response.data as any)?.likeCount;
      const dynamicIndex = dynamics.value.findIndex(d => d.id === dynamicId);
      if (dynamicIndex !== -1) {
        dynamics.value[dynamicIndex]!.isLiked = false;
        if (typeof serverLikeCount === 'number') {
          dynamics.value[dynamicIndex]!.likeCount = serverLikeCount;
        }
      }
      return response.data;
    } catch (err: any) {
      error.value = err.message || '取消点赞失败';
      console.error('取消点赞失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const toggleFavoriteADynamic = async (dynamicId: string) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await toggleFavoriteDynamic(dynamicId);
      const dynamicIndex = dynamics.value.findIndex(d => d.id === dynamicId);
      if (dynamicIndex !== -1) {
        const currentDynamic = dynamics.value[dynamicIndex]!;
        currentDynamic.isFavorited = response.data.isFavorited;
        currentDynamic.favoriteCount = response.data.favoriteCount;
      }
      return response.data;
    } catch (err: any) {
      error.value = err.message || '收藏动态失败';
      console.error('收藏动态失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const toggleFollowAUser = async (userId: string) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await toggleFollowUser(userId);
      dynamics.value.forEach((dynamic) => {
        if (dynamic.userId === userId) {
          dynamic.isFollowing = response.data.isFollowing;
        }
      });
      return response.data;
    } catch (err: any) {
      error.value = err.message || '关注用户失败';
      console.error('关注用户失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 发表评论
   */
  const postNewComment = async (dynamicId: string, commentData: CommentRequest) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await postComment(dynamicId, commentData);
      return response.data;
    } catch (err: any) {
      error.value = err.message || '发表评论失败';
      console.error('发表评论失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const toggleCommentLikeById = async (commentId: string) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await toggleCommentLike(commentId);
      return response.data;
    } catch (err: any) {
      error.value = err.message || '评论点赞失败';
      console.error('评论点赞失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 删除评论
   */
  const removeComment = async (commentId: string) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await deleteComment(commentId);
      return response.data;
    } catch (err: any) {
      error.value = err.message || '删除评论失败';
      console.error('删除评论失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const removeDynamic = async (dynamicId: string) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await deleteDynamic(dynamicId);
      dynamics.value = dynamics.value.filter((item) => item.id !== dynamicId);
      return response.data;
    } catch (err: any) {
      error.value = err.message || '删除动态失败';
      console.error('删除动态失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 获取当前动态列表
   */
  const getCurrentDynamics = computed(() => dynamics.value);

  /**
   * 是否正在加载
   */
  const isLoading = computed(() => loading.value);

  /**
   * 获取错误信息
   */
  const getError = computed(() => error.value);

  return {
    // Methods
    publishNewDynamic,
    fetchDynamicsList,
    fetchFollowingDynamicsList,
    fetchMyDynamicsList,
    fetchDynamicDetail,
    editDynamic,
    likeADynamic,
    unlikeADynamic,
    toggleFavoriteADynamic,
    toggleFollowAUser,
    postNewComment,
    toggleCommentLikeById,
    removeComment,
    removeDynamic,

    // Getters
    getCurrentDynamics,
    isLoading,
    getError
  };
}
