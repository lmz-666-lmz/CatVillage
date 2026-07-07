<template>
  <div class="base-card" :class="{ 'base-card--shadow': shadow !== 'never' }">
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
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(226, 232, 240, 0.92);
  border-radius: 22px;
  overflow: hidden;
}

.base-card--shadow {
  box-shadow: 0 12px 26px rgba(23, 32, 51, 0.06);
}

.base-card__header {
  padding: 16px 20px;
  border-bottom: 1px solid rgba(226, 232, 240, 0.6);
  box-sizing: border-box;
}

.base-card__title {
  margin: 0;
  font-size: 17px;
  font-weight: 900;
  color: #172033;
}

.base-card__header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.base-card__body {
  padding: 16px 20px;
}

.base-card__footer {
  padding: 14px 20px;
  border-top: 1px solid rgba(226, 232, 240, 0.6);
  box-sizing: border-box;
}
</style>
