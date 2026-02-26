<template>
  <div
    class="alert rounded-md p-3 border-2 text-base mb-4 flex items-center"
    :class="typeClass"
  >
    <div :class="textColor">
      <slot name="icon">
        <i class="iconfont !text-xl" :class="typeIcon"></i>
      </slot>
    </div>
    <div class="ml-3 text-sm leading-relaxed">
      <slot>{{ message }}</slot>
    </div>
  </div>
</template>

<script setup>
  import { computed } from 'vue'

  const props = defineProps({
    type: {
      type: String,
      default: 'info',
    },
  })

  const typeClass = computed(() => {
    return {
      info: 'bg-blue-100 border-blue-500',
      danger: 'bg-red-100 border-red-500',
      warning: 'bg-yellow-100 border-yellow-500',
      success: 'bg-green-100 border-green-500',
      primary: 'bg-purple-100 border-purple-500',
    }[props.type]
  })
  const typeIcon = computed(() => {
    return {
      info: 'icon-info',
      success: 'icon-success',
      danger: 'icon-error',
      warning: 'icon-warning',
      primary: 'icon-linggan',
    }[props.type]
  })
  const textColor = computed(() => {
    return {
      info: 'text-blue-500',
      success: 'text-green-500',
      warning: 'text-yellow-500',
      danger: 'text-red-500',
      primary: 'text-purple-500',
    }[props.type]
  })
</script>

<style lang="scss">
  .alert {
    .iconfont {
      font-size: 16px;
    }
    a {
      color: var(--el-color-primary);
      &:hover {
        text-decoration: underline;
      }
    }
  }
</style>
