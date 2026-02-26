<template>
  <div
    class="callout rounded-md p-4 border-l-4 text-base mb-4 flex items-center"
    :class="typeClass"
  >
    <div :class="textColor" class="flex-shrink-0">
      <slot name="icon">
        <i class="iconfont !text-xl" :class="typeIcon"></i>
      </slot>
    </div>
    <div class="ml-3 text-sm leading-relaxed flex-1 text-wrap">
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
      validator: (value) =>
        ['info', 'warning', 'danger', 'primary', 'success'].includes(value),
    },
    message: {
      type: String,
      default: '',
    },
  })

  const typeClass = computed(() => {
    return {
      info: 'callout-info',
      warning: 'callout-warning',
      danger: 'callout-danger',
      primary: 'callout-primary',
      success: 'callout-success',
    }[props.type]
  })

  const typeIcon = computed(() => {
    return {
      info: 'icon-info',
      warning: 'icon-warning',
      danger: 'icon-error',
      primary: 'icon-linggan',
      success: 'icon-success',
    }[props.type]
  })

  const textColor = computed(() => {
    return {
      info: 'text-blue-500',
      warning: 'text-yellow-500',
      danger: 'text-red-500',
      primary: 'text-purple-500',
      success: 'text-green-500',
    }[props.type]
  })
</script>

<style scoped lang="scss">
  .callout-info {
    --bd-callout-color: #087990;
    --bd-callout-bg: #cff4fc;
    --bd-callout-border: #63b3c7;
  }

  .callout-warning {
    --bd-callout-color: #997404;
    --bd-callout-bg: #fff3cd;
    --bd-callout-border: #ffe38c;
  }

  .callout-danger {
    --bd-callout-color: #b02a37;
    --bd-callout-bg: #f8d7da;
    --bd-callout-border: #e297a6;
  }

  .callout-primary {
    --bd-callout-color: #7c39ed;
    --bd-callout-bg: #e6d5ff;
    --bd-callout-border: #cebafa;
  }

  .callout-success {
    --bd-callout-color: #16a34a;
    --bd-callout-bg: #d1fadf;
    --bd-callout-border: #6ee7b7;
  }

  .callout {
    padding: 1.25rem;
    margin-top: 1.25rem;
    margin-bottom: 1.25rem;
    color: var(--bd-callout-color, inherit);
    background-color: var(--bd-callout-bg, var(--bs-gray-100));
    border-left: 0.25rem solid var(--bd-callout-border, var(--bs-gray-300));

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
