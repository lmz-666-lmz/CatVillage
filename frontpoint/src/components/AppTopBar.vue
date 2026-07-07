<template>
  <header class="app-topbar">
    <div class="app-topbar-row">
      <button v-if="back" class="app-topbar-icon" type="button" aria-label="返回" @click="$emit('back')">
        <van-icon name="arrow-left" size="20" />
      </button>
      <div v-else-if="logo" class="app-topbar-logo">
        <img :src="logo" alt="" />
      </div>

      <div class="app-topbar-title">
        <span v-if="kicker" class="app-topbar-kicker">{{ kicker }}</span>
        <h1>{{ title }}</h1>
        <p v-if="subtitle">{{ subtitle }}</p>
      </div>

      <div class="app-topbar-actions">
        <slot name="actions" />
      </div>
    </div>

    <div v-if="$slots.default" class="app-topbar-extra">
      <slot />
    </div>
  </header>
</template>

<script setup lang="ts">
defineProps<{
  title: string;
  subtitle?: string;
  kicker?: string;
  logo?: string;
  back?: boolean;
}>();

defineEmits<{
  back: [];
}>();
</script>

<style scoped>
.app-topbar {
  position: sticky;
  top: 0;
  z-index: 30;
  margin: 0 -16px;
  padding: 12px 16px 12px;
  background:
    linear-gradient(180deg, rgba(255, 248, 243, 0.98) 0%, rgba(255, 248, 243, 0.92) 54%, rgba(245, 247, 251, 0.86) 100%);
  backdrop-filter: blur(18px);
}

.app-topbar-row {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 44px;
}

.app-topbar-icon,
.app-topbar-logo,
:deep(.topbar-action) {
  display: grid;
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  place-items: center;
  border: 1px solid rgba(226, 232, 240, 0.86);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.84);
  color: #172033;
  box-shadow: 0 8px 22px rgba(23, 32, 51, 0.07);
  transition: transform 0.14s ease, background 0.14s ease;
}

.app-topbar-icon:active,
:deep(.topbar-action:active) {
  transform: scale(0.94);
}

.app-topbar-logo img {
  width: 28px;
  height: 28px;
  object-fit: contain;
}

.app-topbar-title {
  min-width: 0;
  flex: 1;
}

.app-topbar-kicker {
  display: block;
  color: #f97316;
  font-size: 10px;
  font-weight: 900;
  letter-spacing: 0.08em;
  line-height: 1;
  text-transform: uppercase;
}

.app-topbar-title h1 {
  margin: 2px 0 0;
  overflow: hidden;
  color: #172033;
  font-size: 24px;
  font-weight: 900;
  letter-spacing: 0;
  line-height: 1.08;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.app-topbar-title p {
  margin: 3px 0 0;
  overflow: hidden;
  color: #748094;
  font-size: 12px;
  font-weight: 700;
  line-height: 1.2;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.app-topbar-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 40px;
  justify-content: flex-end;
}

.app-topbar-extra {
  margin-top: 12px;
}
</style>
