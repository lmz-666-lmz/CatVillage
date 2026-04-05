<template>
  <div class="base-input-container">
    <label v-if="label" :for="generatedId" class="input-label">{{ label }}</label>
    <div class="input-wrapper" :class="{ 'input-wrapper--focused': isFocused, 'input-wrapper--error': !!errorMessage }">
      <span v-if="prefixIcon" class="input-prefix">
        <component :is="prefixIcon" />
      </span>
      <input
        :id="generatedId"
        v-bind="$attrs"
        :value="modelValue"
        :type="type"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        @focus="handleFocus"
        @blur="handleBlur"
        @input="handleInput"
        class="base-input"
      />
      <span v-if="suffixIcon" class="input-suffix">
        <component :is="suffixIcon" />
      </span>
      <span v-if="clearable && modelValue && !disabled && !readonly" class="input-suffix input-clear" @click="clearInput">
        ×
      </span>
    </div>
    <div v-if="!!errorMessage" class="input-error-message">{{ errorMessage }}</div>
    <div v-else-if="helpText" class="input-help-text">{{ helpText }}</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import type { VNode } from 'vue';

interface Props {
  id?: string;
  modelValue: string | number;
  type?: string;
  placeholder?: string;
  label?: string;
  disabled?: boolean;
  readonly?: boolean;
  clearable?: boolean;
  prefixIcon?: VNode;
  suffixIcon?: VNode;
  errorMessage?: string;
  helpText?: string;
}

interface Emits {
  (event: 'update:modelValue', value: string): void;
  (event: 'focus', evt: FocusEvent): void;
  (event: 'blur', evt: FocusEvent): void;
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  disabled: false,
  readonly: false,
  clearable: false
});

const emit = defineEmits<Emits>();
const isFocused = ref(false);

const generatedId = computed(() => props.id || `base-input-${Math.random().toString(36).substring(2, 9)}`);

const handleFocus = (event: FocusEvent) => {
  isFocused.value = true;
  emit('focus', event);
};

const handleBlur = (event: FocusEvent) => {
  isFocused.value = false;
  emit('blur', event);
};

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement;
  emit('update:modelValue', target.value);
};

const clearInput = () => {
  emit('update:modelValue', '');
};
</script>

<style scoped>
.base-input-container {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.input-label {
  margin-bottom: 6px;
  font-size: 14px;
  color: #606266;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background-color: #fff;
  transition: border-color 0.3s, box-shadow 0.3s;
}

.input-wrapper--focused {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

.input-wrapper--error {
  border-color: #f56c6c;
}

.base-input {
  flex: 1;
  height: 40px;
  padding: 0 12px;
  border: none;
  outline: none;
  background-color: transparent;
  font-size: 14px;
  color: #303133;
}

.base-input::placeholder {
  color: #c0c4cc;
}

.base-input:disabled {
  color: #c0c4cc;
  cursor: not-allowed;
}

.input-prefix,
.input-suffix {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 100%;
  color: #c0c4cc;
}

.input-prefix {
  padding-left: 10px;
}

.input-suffix {
  padding-right: 10px;
}

.input-clear {
  cursor: pointer;
  font-size: 18px;
  color: #909399;
}

.input-clear:hover {
  color: #606266;
}

.input-error-message {
  margin-top: 4px;
  font-size: 12px;
  color: #f56c6c;
}

.input-help-text {
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}
</style>