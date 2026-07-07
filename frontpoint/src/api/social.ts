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
import { getOptionalImageUrl, getSafeAvatarUrl } from '@/utils/image';

// 转换后端 snake_case → 前端 camelCase
type BackendDynamic = Record<string, unknown>;
type BackendComment = Record<string, unknown>;
type BackendFollower = Record<string, unknown>;

const pickAuthorAvatar = (item: Record<string, unknown>) => {
  const author = (item.author || item.user) as Record<string, unknown> | undefined;
  return (
    item.authorAvatar ||
    item.author_avatar ||
    item.avatarUrl ||
    item.avatar_url ||
    author?.avatarUrl ||
    author?.avatar_url ||
    author?.avatar ||
    item.avatar
  ) as string | undefined;
};

const mapDynamic = (d: BackendDynamic) => ({
  ...d,
  id: d.id as string,
  userId: d.user_id ?? d.userId,
  catId: d.cat_id ?? d.catId,
  username: d.username ?? (d.author as Record<string, unknown> | undefined)?.nickname ?? (d.user as Record<string, unknown> | undefined)?.nickname,
  catName: d.cat_name ?? d.catName,
  avatar: getSafeAvatarUrl(pickAuthorAvatar(d), String(d.user_id ?? d.userId ?? d.username ?? '')),
  content: d.content,
  images: Array.isArray(d.images) ? d.images.map((url) => getOptionalImageUrl(String(url))).filter(Boolean) : [],
  likeCount: d.like_count ?? d.likeCount ?? 0,
  commentCount: d.comment_count ?? d.commentCount ?? 0,
  favoriteCount: d.favorite_count ?? d.favoriteCount ?? 0,
  createdAt: d.created_at ?? d.createdAt ?? '',
  isRecommended: d.is_recommended ?? d.isRecommended ?? false,
  recommendedAt: d.recommended_at ?? d.recommendedAt ?? '',
  isLiked: d.is_liked ?? d.isLiked ?? false,
  isFavorited: d.is_favorited ?? d.isFavorited ?? false,
  isFollowing: d.is_following ?? d.isFollowing ?? false,
  isOwner: d.is_owner ?? d.isOwner ?? false,
  comments: Array.isArray(d.comments) ? d.comments.map(mapComment) : undefined,
  recentLikers: Array.isArray(d.recent_likers ?? d.recentLikers)
    ? ((d.recent_likers ?? d.recentLikers) as any[]).map((l: any) => ({
        userId: l.user_id ?? l.userId,
        username: l.username,
        avatar: getSafeAvatarUrl(l.avatar, String(l.user_id ?? l.userId ?? '')),
      }))
    : undefined,
  latestComment: (() => {
      const raw: any = d.latest_comment ?? d.latestComment;
      if (!raw) return undefined;
      return {
        userId: raw.user_id ?? raw.userId,
        username: raw.username,
        avatar: getSafeAvatarUrl(raw.avatar, String(raw.user_id ?? raw.userId ?? '')),
        content: raw.content,
        createdAt: raw.created_at ?? raw.createdAt ?? '',
      };
    })(),
}) as unknown;

const mapComment = (c: BackendComment) => ({
  ...c,
  id: c.id as string,
  userId: c.user_id ?? c.userId,
  username: c.username ?? (c.author as Record<string, unknown> | undefined)?.nickname ?? (c.user as Record<string, unknown> | undefined)?.nickname,
  avatar: getSafeAvatarUrl(pickAuthorAvatar(c), String(c.user_id ?? c.userId ?? c.username ?? '')),
  dynamicId: c.dynamic_id ?? c.dynamicId,
  content: c.content,
  createdAt: c.created_at ?? c.createdAt ?? '',
  likeCount: c.like_count ?? c.likeCount ?? 0,
  isLiked: c.is_liked ?? c.isLiked ?? false,
  isOwner: c.is_owner ?? c.isOwner ?? false,
}) as unknown;

const mapFollower = (f: BackendFollower) => ({
  ...f,
  id: f.id as string,
  userId: f.user_id ?? f.userId,
  username: f.username,
  nickname: f.nickname ?? '',
  avatar: getSafeAvatarUrl(pickAuthorAvatar(f), String(f.user_id ?? f.userId ?? f.username ?? '')),
  lastOnlineAt: f.last_online_at ?? f.lastOnlineAt ?? '',
  isOnline: f.is_online ?? f.isOnline ?? false,
  isFollowing: f.is_following ?? f.isFollowing ?? false,
}) as unknown;

const mapLike = (data: Record<string, unknown>) => ({
  isLiked: Boolean(data.is_liked ?? data.isLiked ?? false),
  likeCount: Number(data.like_count ?? data.likeCount ?? 0)
});

const mapFavorite = (data: Record<string, unknown>) => ({
  isFavorited: Boolean(data.is_favorited ?? data.isFavorited ?? false),
  favoriteCount: Number(data.favorite_count ?? data.favoriteCount ?? 0)
});

const mapFollow = (data: Record<string, unknown>) => ({
  isFollowing: Boolean(data.is_following ?? data.isFollowing ?? false),
  followerCount: Number(data.follower_count ?? data.followerCount ?? 0)
});

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
  return request<any>({
    url: '/social/dynamics/list',
    method: 'get',
    params
  }).then((res) => {
    const data = res.data || res;
    const list = Array.isArray(data.list) ? data.list.map(mapDynamic) : [];
    return { ...res, data: { ...data, list } } as any;
  });
}

export function searchDynamics(params: { q: string; page: number; pageSize: number }) {
  return request<any>({
    url: '/social/dynamics/search',
    method: 'get',
    params
  }).then((res) => {
    const data = res.data || res;
    const list = Array.isArray(data.list) ? data.list.map(mapDynamic) : [];
    return { ...res, data: { ...data, list } } as { data: SocialDynamicListResponse };
  });
}

// 获取关注流动态列表
export function getFollowingDynamicsList(params: { page: number; pageSize: number; catId?: string }) {
  return request<any>({
    url: '/social/dynamics/list',
    method: 'get',
    params: { ...params, scope: 'following' }
  }).then((res) => {
    const data = res.data || res;
    const list = Array.isArray(data.list) ? data.list.map(mapDynamic) : [];
    return { ...res, data: { ...data, list } } as any;
  });
}

// 获取动态详情
export function getDynamicDetail(dynamicId: string) {
  return request<any>({
    url: `/social/dynamics/${dynamicId}`,
    method: 'get'
  }).then((res) => {
    const data = res.data || res;
    return { ...res, data: mapDynamic(data) } as any;
  });
}

// 编辑动态文字内容
export function updateDynamic(dynamicId: string, data: { content: string }) {
  return request<any>({
    url: `/social/dynamics/${dynamicId}`,
    method: 'put',
    data
  }).then((res) => {
    const mapped = mapDynamic(res.data as unknown as BackendDynamic);
    return { ...res, data: mapped } as any;
  });
}

// 点赞动态
export function likeDynamic(dynamicId: string) {
  return request<LikeDynamicResponse>({
    url: `/social/dynamics/${dynamicId}/like`,
    method: 'post'
  }).then((res) => ({ ...res, data: mapLike(res.data as unknown as Record<string, unknown>) }));
}

// 取消点赞
export function unlikeDynamic(dynamicId: string) {
  return request<LikeDynamicResponse>({
    url: `/social/dynamics/${dynamicId}/like`,
    method: 'delete'
  }).then((res) => ({ ...res, data: mapLike(res.data as unknown as Record<string, unknown>) }));
}

// 收藏动态
export function toggleFavoriteDynamic(dynamicId: string) {
  return request<FavoriteResponse>({
    url: `/social/dynamics/${dynamicId}/favorite`,
    method: 'post'
  }).then((res) => ({ ...res, data: mapFavorite(res.data as unknown as Record<string, unknown>) }));
}

// 关注/取消关注用户
export function toggleFollowUser(userId: string) {
  return request<FollowResponse>({
    url: `/social/users/${userId}/follow`,
    method: 'post'
  }).then((res) => ({ ...res, data: mapFollow(res.data as unknown as Record<string, unknown>) }));
}

// 评论点赞/取消点赞
export function toggleCommentLike(commentId: string) {
  return request<LikeDynamicResponse>({
    url: `/social/comments/${commentId}/like`,
    method: 'post'
  }).then((res) => ({ ...res, data: mapLike(res.data as unknown as Record<string, unknown>) }));
}

// 发表评论
export function postComment(dynamicId: string, data: CommentRequest) {
  return request<CommentResponse>({
    url: `/social/dynamics/${dynamicId}/comments`,
    method: 'post',
    data
  }).then((res) => ({ ...res, data: mapComment(res.data as unknown as BackendComment) as CommentResponse }));
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
  return request<any>({
    url: '/social/dynamics/my/list',
    method: 'get',
    params
  }).then((res) => {
    const data = res.data || res;
    const list = Array.isArray(data.list) ? data.list.map(mapDynamic) : [];
    return { ...res, data: { ...data, list } } as any;
  });
}

// 获取热门话题
export function getHotTopics(params?: { limit?: number; sampleSize?: number }) {
  return request<any>({
    url: '/social/topics/hot',
    method: 'get',
    params
  }).then((res) => {
    const data = res.data || res;
    const list = Array.isArray(data.list)
      ? data.list.map((item: any) => ({
          topic: String(item.topic || ''),
          count: Number(item.count || 0),
          isDefault: Boolean(item.is_default ?? item.isDefault ?? false)
        })).filter((item: any) => item.topic)
      : [];
    return { ...res, data: { ...data, list } } as { data: HotTopicsResponse };
  });
}

// 获取关注者列表/粉丝列表
export function getFollowersList(params: { page: number; pageSize: number }) {
  return request<any>({
    url: '/social/users/followers/list',
    method: 'get',
    params
  }).then((res) => {
    const data = res.data || res;
    const list = Array.isArray(data.list) ? data.list.map(mapFollower) : [];
    return { ...res, data: { ...data, list } } as any;
  });
}

// 获取动态点赞用户列表
export function getDynamicLikers(dynamicId: string, params: { page: number; pageSize: number }) {
  return request<any>({
    url: `/social/dynamics/${dynamicId}/likers`,
    method: 'get',
    params
  });
}
