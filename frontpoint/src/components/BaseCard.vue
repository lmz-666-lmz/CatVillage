<template>
  <div class="base-card" :class="{ 'base-card--shadow': shadow }">
    <div v-if="$slots.header || title" class="base-card__header">
      <h3 v-if="title" class="base-card__title">{{ title }}</h3>
      <div v-if="$slots.header" class="base-card__header-content">
        <slot name="header" />
      </div>
    </div>
    
    <div class="base-card__body">
      <slot />
    </div>
    
    <div v-if="$slots.footer" class="base-card__footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title?: string;
  shadow?: 'always' | 'hover' | 'never';
}

withDefaults(defineProps<Props>(), {
  shadow: 'always'
});
</script>

<style scoped>
.base-card {
  background-color: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  overflow: hidden;
}

.base-card--shadow {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.base-card__header {
  padding: 20px;
  border-bottom: 1px solid #ebeef5;
  box-sizing: border-box;
}

.base-card__title {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.base-card__header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.base-card__body {
  padding: 20px;
}

.base-card__footer {
  padding: 16px 20px;
  border-top: 1px solid #ebeef5;
  box-sizing: border-box;
}
</style>