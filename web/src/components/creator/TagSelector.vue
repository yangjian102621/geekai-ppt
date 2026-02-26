<template>
  <div class="tag-selector">
    <!-- 已选标签 -->
    <div class="flex flex-wrap gap-1.5 mb-2">
      <el-tag
        v-for="tag in modelValue"
        :key="tag"
        size="small"
        closable
        @close="removeTag(tag)"
        class="tag-item"
      >
        {{ tag }}
      </el-tag>
    </div>
    <!-- 预设选择 + 自定义输入 -->
    <div class="flex flex-wrap items-center gap-2">
      <el-popover :width="280" trigger="click" placement="bottom-start" title="选择预设">
        <template #reference>
          <el-button size="small" type="primary" class="flex-shrink-0">
            {{ selectPresetLabel }}
          </el-button>
        </template>
        <div class="preset-chips flex flex-wrap gap-1.5">
          <el-tag
            v-for="opt in presets"
            :key="opt"
            size="small"
            :type="modelValue.includes(opt) ? 'success' : 'primary'"
            class="preset-chip cursor-pointer hover:opacity-80"
            @click="togglePreset(opt)"
          >
            {{ opt }}{{ modelValue.includes(opt) ? ' ✓' : '' }}
          </el-tag>
        </div>
      </el-popover>
      <el-input
        v-model="customInput"
        size="small"
        :placeholder="customPlaceholder ?? '输入自定义，回车添加'"
        class="custom-input flex-1 min-w-[120px]"
        @keyup.enter="addCustomTag"
      />
    </div>
  </div>
</template>

<script setup lang="js">
import { ref } from 'vue'

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  presets: { type: Array, default: () => [] },
  selectPresetLabel: { type: String, default: '选择' },
  customPlaceholder: { type: String, default: '输入自定义，回车添加' },
})

const emit = defineEmits(['update:modelValue'])

const customInput = ref('')

function addTag(val) {
  if (!val.trim() || props.modelValue.includes(val)) return
  emit('update:modelValue', [...props.modelValue, val])
}

function togglePreset(val) {
  if (props.modelValue.includes(val)) {
    removeTag(val)
  } else {
    addTag(val)
  }
}

function removeTag(val) {
  emit(
    'update:modelValue',
    props.modelValue.filter((t) => t !== val)
  )
}

function addCustomTag() {
  const v = customInput.value.trim()
  if (!v) return
  addTag(v)
  customInput.value = ''
}
</script>

<style scoped>
.tag-selector {
  @apply rounded-lg border border-[var(--el-border-color)] p-2 bg-[var(--el-fill-color-blank)];
}
.preset-chip {
  transition: opacity 0.15s;
}
</style>
