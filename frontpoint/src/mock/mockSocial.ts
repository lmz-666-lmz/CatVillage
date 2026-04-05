import type { DynamicResponse, CommentResponse } from '@/types/social';
import type { User } from '@/types';

// 模拟用户数据
export const mockUsers: User[] = [
  {
    id: 'user-1',
    username: '猫咪爱好者',
    nickname: '猫友A',
    avatar: 'https://placekitten.com/100/100',
    email: 'catlover@example.com',
    createdAt: '2022-01-15',
    updatedAt: '2023-05-20'
  },
  {
    id: 'user-2',
    username: '铲屎官小张',
    nickname: '小张',
    avatar: 'https://placekitten.com/100/101',
    email: 'zhang@example.com',
    createdAt: '2022-03-22',
    updatedAt: '2023-05-18'
  },
  {
    id: 'user-3',
    username: '喵星人守护者',
    nickname: '喵守护',
    avatar: 'https://placekitten.com/100/102',
    email: 'guardian@example.com',
    createdAt: '2021-11-30',
    updatedAt: '2023-04-15'
  }
];

// 模拟动态数据
export const mockDynamics: DynamicResponse[] = [
  {
    id: 'dynamic-1',
    userId: 'user-1',
    catId: 'cat-1',
    username: '猫咪爱好者',
    catName: '奶茶',
    avatar: 'https://placekitten.com/100/100',
    content: '今天带奶茶去体检了，各项指标都很健康！',
    images: ['https://placekitten.com/400/300'],
    likeCount: 24,
    commentCount: 5,
    createdAt: new Date(Date.now() - 86400000).toISOString(), // 1天前
    isLiked: false,
    isOwner: true
  },
  {
    id: 'dynamic-2',
    userId: 'user-2',
    catId: 'cat-2',
    username: '铲屎官小张',
    catName: '布丁',
    avatar: 'https://placekitten.com/100/101',
    content: '布丁今天又调皮了，把花瓶打翻了 😹',
    images: ['https://placekitten.com/400/301', 'https://placekitten.com/400/302'],
    likeCount: 42,
    commentCount: 12,
    createdAt: new Date(Date.now() - 3600000).toISOString(), // 1小时前
    isLiked: true,
    isOwner: true
  },
  {
    id: 'dynamic-3',
    userId: 'user-3',
    catId: undefined, // 允许为 undefined，表示不关联特定猫咪
    username: '喵星人守护者',
    catName: undefined, // 允许为 undefined，表示不关联特定猫咪
    avatar: 'https://placekitten.com/100/102',
    content: '分享一个猫咪营养搭配的小知识',
    images: [],
    likeCount: 86,
    commentCount: 21,
    createdAt: new Date(Date.now() - 172800000).toISOString(), // 2天前
    isLiked: false,
    isOwner: false
  }
];

// 模拟评论数据
export const mockComments: CommentResponse[] = [
  {
    id: 'comment-1',
    userId: 'user-2',
    username: '铲屎官小张',
    avatar: 'https://placekitten.com/100/101',
    dynamicId: 'dynamic-1',
    content: '恭喜奶茶健康！',
    createdAt: new Date(Date.now() - 7200000).toISOString(), // 2小时前
    isOwner: true
  },
  {
    id: 'comment-2',
    userId: 'user-3',
    username: '喵星人守护者',
    avatar: 'https://placekitten.com/100/102',
    dynamicId: 'dynamic-1',
    content: '定期体检很重要呢',
    createdAt: new Date(Date.now() - 3600000).toISOString(), // 1小时前
    isOwner: false
  },
  {
    id: 'comment-3',
    userId: 'user-1',
    username: '猫咪爱好者',
    avatar: 'https://placekitten.com/100/100',
    dynamicId: 'dynamic-2',
    content: '布丁真是太调皮啦',
    createdAt: new Date(Date.now() - 1800000).toISOString(), // 半小时前
    isOwner: true
  }
];

// 模拟获取社交动态
export const getMockSocialFeeds = (params: { page: number; pageSize: number; catId?: string }): Promise<{ data: { list: DynamicResponse[]; total: number } }> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      let filteredDynamics = [...mockDynamics];
      
      // 如果指定了catId，则过滤出该猫咪相关的帖子
      if (params.catId) {
        filteredDynamics = filteredDynamics.filter(d => d.catId === params.catId);
      }
      
      const start = (params.page - 1) * params.pageSize;
      const end = start + params.pageSize;
      const paginatedList = filteredDynamics.slice(start, end);
      
      resolve({ 
        data: { 
          list: paginatedList, 
          total: filteredDynamics.length 
        } 
      });
    }, 500);
  });
};

// 模拟获取用户信息
export const getMockUserProfile = (userId: string): Promise<{ data: User }> => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const user = mockUsers.find(u => u.id === userId);
      if (user) {
        resolve({ data: user });
      } else {
        reject(new Error('用户不存在'));
      }
    }, 300);
  });
};

// 模拟获取帖子评论
export const getMockComments = (dynamicId: string): Promise<{ data: CommentResponse[] }> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const comments = mockComments.filter(c => c.dynamicId === dynamicId);
      resolve({ data: comments });
    }, 300);
  });
};

// 模拟点赞
export const mockLikeDynamic = (dynamicId: string): Promise<{ data: { isLiked: boolean; likeCount: number } }> => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const dynamic = mockDynamics.find(d => d.id === dynamicId);
      if (dynamic) {
        dynamic.isLiked = !dynamic.isLiked;
        dynamic.likeCount += dynamic.isLiked ? 1 : -1;
        resolve({ 
          data: { 
            isLiked: dynamic.isLiked,
            likeCount: dynamic.likeCount
          } 
        });
      } else {
        reject(new Error('动态不存在'));
      }
    }, 300);
  });
};

// 模拟发布评论
export const mockAddComment = (dynamicId: string, content: string): Promise<{ data: CommentResponse }> => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const dynamic = mockDynamics.find(d => d.id === dynamicId);
      if (!dynamic) {
        reject(new Error('动态不存在'));
        return;
      }

      const newComment: CommentResponse = {
        id: `comment-${mockComments.length + 1}`,
        dynamicId,
        userId: 'user-1', // 使用当前用户作为评论作者
        username: '猫咪爱好者',
        avatar: 'https://placekitten.com/100/100',
        content,
        createdAt: new Date().toISOString(),
        isOwner: true
      };

      mockComments.push(newComment);
      dynamic.commentCount++;

      resolve({ data: newComment });
    }, 300);
  });
};