import request from '@/utils/request';
import type { 
  SocialDynamicListResponse,
  SocialDynamicResponse,
  LikeDynamicResponse,
  FavoriteResponse,
  FollowResponse,
  CommentRequest,
  CommentResponse,
  HotTopicsResponse,
  FollowersListResponse
} from '@/types/social';

// 发布动态
export function publishDynamic(data: FormData) {
  return request({
    url: '/social/dynamics',
    method: 'post',
    headers: { 'Content-Type': 'multipart/form-data' },
    data
  });
}

// 获取广场动态列表
export function getDynamicsList(params: { page: number; pageSize: number; catId?: string }) {
  return request<SocialDynamicListResponse>({
    url: '/social/dynamics/list',
    method: 'get',
    params
  });
}

// 获取关注流动态列表
export function getFollowingDynamicsList(params: { page: number; pageSize: number; catId?: string }) {
  return request<SocialDynamicListResponse>({
    url: '/social/dynamics/list',
    method: 'get',
    params: {
      ...params,
      scope: 'following'
    }
  });
}

// 获取动态详情
export function getDynamicDetail(dynamicId: string) {
  return request<SocialDynamicResponse>({
    url: `/social/dynamics/${dynamicId}`,
    method: 'get'
  });
}

// 点赞动态
export function likeDynamic(dynamicId: string) {
  return request<LikeDynamicResponse>({
    url: `/social/dynamics/${dynamicId}/like`,
    method: 'post'
  });
}

// 取消点赞
export function unlikeDynamic(dynamicId: string) {
  return request({
    url: `/social/dynamics/${dynamicId}/like`,
    method: 'delete'
  });
}

// 收藏动态
export function toggleFavoriteDynamic(dynamicId: string) {
  return request<FavoriteResponse>({
    url: `/social/dynamics/${dynamicId}/favorite`,
    method: 'post'
  });
}

// 关注/取消关注用户
export function toggleFollowUser(userId: string) {
  return request<FollowResponse>({
    url: `/social/users/${userId}/follow`,
    method: 'post'
  });
}

// 评论点赞/取消点赞
export function toggleCommentLike(commentId: string) {
  return request<LikeDynamicResponse>({
    url: `/social/comments/${commentId}/like`,
    method: 'post'
  });
}

// 发表评论
export function postComment(dynamicId: string, data: CommentRequest) {
  return request<CommentResponse>({
    url: `/social/dynamics/${dynamicId}/comments`,
    method: 'post',
    data
  });
}

// 删除评论
export function deleteComment(commentId: string) {
  return request({
    url: `/social/comments/${commentId}`,
    method: 'delete'
  });
}

// 删除动态
export function deleteDynamic(dynamicId: string) {
  return request({
    url: `/social/dynamics/${dynamicId}`,
    method: 'delete'
  });
}

// 获取我的动态列表
export function getMyDynamicsList(params: { page: number; pageSize: number; catId?: string }) {
  return request<SocialDynamicListResponse>({
    url: '/social/dynamics/my/list',
    method: 'get',
    params
  });
}

// 获取热门话题
export function getHotTopics(params?: { limit?: number; sampleSize?: number }) {
  return request<HotTopicsResponse>({
    url: '/social/topics/hot',
    method: 'get',
    params
  });
}

// 获取关注者列表/粉丝列表
export function getFollowersList(params: { page: number; pageSize: number }) {
  return request<FollowersListResponse>({
    url: '/social/users/followers/list',
    method: 'get',
    params
  });
}