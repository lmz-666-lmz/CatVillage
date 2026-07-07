<template>
  <div :class="['flex items-start gap-3', isUser ? 'justify-end flex-row-reverse' : '']">
    
    <!-- Avatar -->
    <div 
      :class="[
        'w-8 h-8 flex items-center justify-center flex-shrink-0 rounded-full',
        isUser ? 'bg-surface-variant' : 'bg-primary-container'
      ]"
    >
      <span 
        class="material-symbols-outlined text-sm" 
        :class="isUser ? 'text-on-surface-variant' : 'text-white'"
        :style="!isUser ? { fontVariationSettings: `'FILL' 1` } : {}"
      >
        {{ isUser ? 'person' : 'smart_toy' }}
      </span>
    </div>

    <!-- Bubble -->
    <div 
      class="p-4 max-w-[80%] text-sm leading-relaxed"
      :class="[
        isUser ? 'bg-primary-container text-white' : 'bg-surface-container-low dark:bg-inverse-surface text-on-surface dark:text-inverse-on-surface'
      ]"
      :style="{ 
        borderRadius: isUser ? '16px 16px 4px 16px' : '4px 16px 16px 16px' 
      }"
      v-html="formattedContent"
    >
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  content: string;
  isUser: boolean;
}>();

/** 转义 HTML 特殊字符，防止 AI 输出中的 XSS 注入 */
const escapeHtml = (text: string): string => {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
};

const formattedContent = computed(() => {
  return escapeHtml(props.content);
});
</script>
