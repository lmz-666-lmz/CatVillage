<template>
  <article class="bg-surface-container-lowest dark:bg-inverse-surface rounded-xl overflow-hidden shadow-sm">
    <!-- Header: 用户信息与操作 -->
    <div class="flex items-center justify-between p-3">
      <div class="flex items-center gap-3">
        <div class="relative">
          <img :src="post.author.avatar" :alt="post.author.name" class="w-10 h-10 rounded-full object-cover"/>
          <div class="absolute -bottom-1 -right-1 bg-primary-container text-white rounded-full w-4 h-4 flex items-center justify-center border-2 border-white dark:border-inverse-surface">
            <span class="material-symbols-outlined text-[10px] font-bold">add</span>
          </div>
        </div>
        <div>
          <p class="font-bold text-sm text-on-surface dark:text-inverse-on-surface">{{ post.author.name }}</p>
          <p class="text-[10px] text-on-surface-variant">{{ post.author.metaInfo }}</p>
        </div>
      </div>
      
      <!-- 更多操作下拉菜单 -->
      <div class="relative group">
        <button class="material-symbols-outlined text-on-surface-variant hover:bg-surface-container dark:hover:bg-surface-container-high rounded-full p-1 transition-colors">
          more_horiz
        </button>
        <div class="absolute right-0 top-full mt-2 w-32 bg-surface-container-lowest dark:bg-inverse-surface rounded-xl shadow-[0_8px_30px_rgba(20,27,43,0.1)] border border-outline-variant/20 py-2 hidden group-focus-within:block z-[70]">
          <button class="w-full px-4 py-2 text-left text-sm hover:focus:bg-surface-container transition-colors text-on-surface dark:text-inverse-on-surface">分享</button>
          <button class="w-full px-4 py-2 text-left text-sm hover:focus:bg-surface-container transition-colors text-on-surface dark:text-inverse-on-surface">不感兴趣</button>
          <button class="w-full px-4 py-2 text-left text-sm text-error hover:bg-error-container/20 transition-colors">举报</button>
        </div>
      </div>
    </div>

    <!-- Content: 正文与配图 -->
    <div class="px-3 pb-3">
      <p class="text-sm leading-relaxed mb-3 text-on-surface dark:text-inverse-on-surface">{{ post.content }}</p>
      
      <!-- 图片网格 (自动适配1图或多图) -->
      <div :class="['gap-2', post.images.length > 1 ? 'grid grid-cols-2' : 'flex']">
        <img 
          v-for="(img, index) in post.images" 
          :key="index"
          :src="img" 
          class="object-cover rounded-xl w-full"
          :class="post.images.length === 1 ? 'h-72' : 'h-32'"
          alt="Post Image"
        />
      </div>
    </div>

    <!-- Footer: 交互区与 BGM -->
    <div class="flex items-center justify-between px-4 py-3 bg-surface/30 dark:bg-black/10">
      <div class="flex items-center gap-6">
        <!-- 点赞 -->
        <div class="flex items-center gap-1.5 cursor-pointer group" @click="toggleLike">
          <span 
            class="material-symbols-outlined text-xl transition-colors"
            :class="post.stats.isLiked ? 'text-error' : 'text-on-surface-variant'"
            :style="{ fontVariationSettings: post.stats.isLiked ? `'FILL' 1` : `'FILL' 0` }"
          >favorite</span>
          <span class="text-xs text-on-surface-variant">{{ post.stats.likes }}</span>
        </div>
        <!-- 评论 -->
        <div class="flex items-center gap-1.5 cursor-pointer group">
          <span class="material-symbols-outlined text-xl text-on-surface-variant group-hover:text-primary transition-colors">chat_bubble</span>
          <span class="text-xs text-on-surface-variant">{{ post.stats.comments }}</span>
        </div>
        <!-- 收藏/分享 -->
        <div class="flex items-center gap-1.5 cursor-pointer group" @click="toggleBookmark">
          <span 
            class="material-symbols-outlined text-xl transition-colors"
            :class="post.stats.isBookmarked ? 'text-yellow-500' : 'text-on-surface-variant'"
            :style="{ fontVariationSettings: post.stats.isBookmarked ? `'FILL' 1` : `'FILL' 0` }"
          >bookmark</span>
          <span class="text-xs text-on-surface-variant">分享</span>
        </div>
      </div>
      
      <!-- BGM 标识 -->
      <div v-if="post.bgm" class="flex items-center gap-1 bg-surface-container-low dark:bg-surface-container px-2 py-1 rounded-full">
        <span class="material-symbols-outlined text-xs text-primary-container" style="font-variation-settings: 'FILL' 1;">music_note</span>
        <span class="text-[10px] font-medium max-w-[60px] truncate text-on-surface dark:text-inverse-on-surface">{{ post.bgm }}</span>
      </div>
    </div>
  </article>
</template>

<script setup lang="ts">
import type { PropType } from 'vue';

export interface Post {
  id: string | number;
  author: {
    name: string;
    avatar: string;
    metaInfo: string;
  };
  content: string;
  images: string[];
  stats: {
    likes: string | number;
    comments: string | number;
    isLiked?: boolean;
    isBookmarked?: boolean;
  };
  bgm?: string;
}

const props = defineProps({
  post: {
    type: Object as PropType<Post>,
    required: true
  }
});

const emit = defineEmits(['update:post']);

// 简易交互状态处理，实际开发中由父组件接管或通过Pinia管理
const toggleLike = () => {
  const updatedPost = { ...props.post };
  updatedPost.stats.isLiked = !updatedPost.stats.isLiked;
  emit('update:post', updatedPost);
};

const toggleBookmark = () => {
  const updatedPost = { ...props.post };
  updatedPost.stats.isBookmarked = !updatedPost.stats.isBookmarked;
  emit('update:post', updatedPost);
};
</script>
