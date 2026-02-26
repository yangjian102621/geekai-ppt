<template>
  <el-dialog
    :model-value="visible"
    :width="width"
    :close-on-click-modal="false"
    :destroy-on-close="true"
    :show-close="false"
    :class="['app-dialog']"
    body-class="p-0"
    @close="handleCancel"
  >
    <!-- 自定义关闭按钮 -->
    <div class="app-dialog__close" @click="handleCancel">
      <i class="iconfont icon-error-line"></i>
    </div>

    <!-- 自定义头部插槽 -->
    <template #header>
      <h3
        class="text-xl text-gray-800 font-medium border-b border-gray-200 pb-4"
      >
        {{ title }}
      </h3>
    </template>

    <div class="app-dialog__body">
      <slot></slot>
    </div>

    <template #footer v-if="!hideFooter">
      <div class="border-t border-gray-200 pt-4 flex justify-end gap-3">
        <button
          v-if="cancelText"
          class="px-5 py-1.5 bg-gray-500 text-white rounded-md hover:bg-gray-600 active:bg-gray-700 transition-colors"
          @click="handleCancel"
        >
          {{ cancelText }}
        </button>
        <button
          v-if="!hideConfirm && showConfirm && confirmText"
          class="px-5 py-1.5 bg-purple-600 text-white rounded-md hover:bg-purple-700 active:bg-purple-800 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
          :class="{ 'pointer-events-none': loading }"
          :disabled="loading"
          @click="handleConfirm"
        >
          <span v-if="loading" class="inline-flex items-center gap-2">
            <i class="iconfont icon-loading animate-spin text-xs"></i>
          </span>
          {{ confirmText }}
        </button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
  import { computed, ref, watch } from 'vue'

  const props = defineProps({
    modelValue: Boolean,
    title: {
      type: String,
      default: '',
    },
    loading: {
      type: Boolean,
      default: false,
    },
    hideFooter: {
      type: Boolean,
      default: false,
    },
    hideConfirm: {
      type: Boolean,
      default: false,
    },
    confirmText: {
      type: String,
      default: '确定',
    },
    cancelText: {
      type: String,
      default: '取消',
    },
    width: {
      type: String,
      default: '500px',
    },
    showConfirm: {
      type: Boolean,
      default: true,
    },
  })
  const emits = defineEmits(['confirm', 'cancel', 'update:modelValue'])
  const visible = ref(props.modelValue)

  watch(
    () => props.modelValue,
    (newValue) => {
      visible.value = newValue
    }
  )

  const handleCancel = () => {
    visible.value = false
    emits('update:modelValue', false)
    emits('cancel')
  }

  const handleConfirm = () => {
    emits('confirm')
  }
</script>

<style lang="scss">
  .app-dialog {
    border-radius: 12px;
    position: relative;

    :deep(.el-dialog__header) {
      margin: 0;
      padding: 20px 24px 16px;
      border-bottom: 1px solid #f3f4f6;

      .el-dialog__title {
        font-size: 20px;
        font-weight: 700;
        color: #1f2937;
        line-height: 1.4;
      }
    }

    :deep(.el-dialog__body) {
      padding: 0;
    }
  }

  // 自定义关闭按钮
  .app-dialog__close {
    position: absolute;
    top: 20px;
    right: 24px;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: #9ca3af;
    transition: color 0.2s ease;
    z-index: 10;

    &:hover {
      color: #374151;
    }

    .iconfont {
      font-size: 16px;
    }
  }

  .app-dialog__body {
    max-height: 70vh;
    overflow-y: auto;

    .el-form-item--label-top {
      .el-form-item__label {
        font-weight: 700;
      }
    }
  }

  @media (max-width: 640px) {
    .app-dialog__body {
      max-height: 80vh;
      padding: 12px 16px;
    }
  }
</style>
