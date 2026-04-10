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

const formattedContent = computed(() => {
  return props.content;
});
</script>
