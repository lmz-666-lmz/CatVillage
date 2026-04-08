// 社交功能相关类型定义

// 发布动态请求
export interface PublishDynamicRequest {
  catId: string;
  content: string;
  images?: File[]; // 图片文件数组（multipart/form-data）
}

// 动态响应
export interface DynamicResponse {
  id: string;
  userId: string;
  catId?: string;
  username: string;
  catName?: string;
  avatar: string;
  content: string;
  images?: string[];
  likeCount: number;
  commentCount: number;
  favoriteCount?: number;
  createdAt: string;
  isLiked?: boolean;
  isFavorited?: boolean;
  isFollowing?: boolean;
  isOwner: boolean; // 是否是自己的动态
  comments?: CommentResponse[];
}

// 动态列表请求参数
export interface DynamicsListRequest {
  catId?: string; // 可选，指定猫咪的动态
  userId?: string; // 可选，指定用户的动态
  page: number;
  pageSize: number;
}

// 动态列表响应
export interface DynamicsListResponse {
  list: DynamicResponse[];
  total: number;
  page: number;
  pageSize: number;
}

// 评论请求
export interface CommentRequest {
  dynamicId: string;
  content: string;
}

// 评论响应
export interface CommentResponse {
  id: string;
  userId: string;
  username: string;
  avatar: string;
  dynamicId: string;
  content: string;
  createdAt: string;
  likeCount?: number;
  isLiked?: boolean;
  isOwner: boolean; // 是否是自己的评论
}

// 点赞请求
export interface LikeRequest {
  dynamicId: string;
}

// 点赞响应
export interface LikeResponse {
  isLiked: boolean;
  likeCount: number;
}

export interface FavoriteResponse {
  isFavorited: boolean;
  favoriteCount: number;
}

export interface FollowResponse {
  isFollowing: boolean;
  followerCount: number;
}

// 我的动态列表请求参数
export interface MyDynamicsListRequest {
  catId?: string;
  page: number;
  pageSize: number;
}

// 我的动态列表响应
export interface MyDynamicsListResponse {
  list: DynamicResponse[];
  total: number;
  page: number;
  pageSize: number;
}

export interface HotTopicItem {
  topic: string;
  count: number;
}

export interface HotTopicsResponse {
  list: HotTopicItem[];
}

// Backward-compatible aliases for older API/composable names.
export type SocialDynamic = DynamicResponse;
export type SocialDynamicListResponse = DynamicsListResponse;
export type SocialDynamicResponse = DynamicResponse;
export type DynamicDetailResponse = DynamicResponse;
export type LikeDynamicResponse = LikeResponse;