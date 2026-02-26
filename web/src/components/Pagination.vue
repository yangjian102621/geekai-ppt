<template>
  <div v-if="shouldShow" class="app-pagination">
    <el-pagination
      :small="small"
      :hide-on-single-page="hideOnSinglePage"
      :current-page="currentPageInternal"
      :page-size="pageSizeInternal"
      :page-sizes="pageSizeOptionsInternal"
      :layout="layoutString"
      :total="totalInternal"
      background
      @current-change="handleCurrentChange"
      @size-change="handleSizeChange"
    />
  </div>
</template>

<script setup>
  const layoutTokenMap = {
    pages: 'pager',
    prev: 'prev',
    next: 'next',
    total: 'total',
    sizes: 'sizes',
    jumper: 'jumper',
  }

  const props = defineProps({
    small: {
      type: Boolean,
      default: false,
    },
    hideOnSinglePage: {
      type: Boolean,
      default: true,
    },
    total: {
      type: Number,
      required: true,
    },
    pageSize: {
      type: Number,
      default: 10,
    },
    currentPage: {
      type: Number,
      default: 1,
    },
    pageSizeOptions: {
      type: Array,
      default: () => [10, 20, 30, 50],
    },
    layout: {
      type: Array,
      default: () => ['total', 'prev', 'pages', 'next'],
    },
  })

  const emits = defineEmits(['update:currentPage', 'update:pageSize'])

  const currentPageInternal = ref(props.currentPage)
  const pageSizeInternal = ref(props.pageSize)
  const totalInternal = ref(props.total)
  const pageSizeOptionsInternal = ref(props.pageSizeOptions)

  const shouldShow = computed(() => {
    const pages = Math.ceil(totalInternal.value / pageSizeInternal.value)
    return pages > 1 || !props.hideOnSinglePage
  })

  const layoutString = computed(() => {
    return props.layout
      .map((token) => layoutTokenMap[token] || token)
      .join(', ')
  })

  function handleCurrentChange(page) {
    currentPageInternal.value = page
    emits('update:currentPage', page)
  }

  function handleSizeChange(size) {
    pageSizeInternal.value = size
    emits('update:pageSize', size)
    emits('update:currentPage', 1)
  }

  watch(
    () => props.currentPage,
    (value) => {
      currentPageInternal.value = value
    }
  )
  watch(
    () => props.pageSize,
    (value) => {
      pageSizeInternal.value = value
    }
  )
  watch(
    () => props.total,
    (value) => {
      totalInternal.value = value
    }
  )
  watch(
    () => props.pageSizeOptions,
    (value) => {
      pageSizeOptionsInternal.value = value
    }
  )
</script>

<style scoped lang="scss">
  .app-pagination {
    display: flex;
    justify-content: flex-end;
    padding-top: 12px;

    :deep(.el-pagination.is-background .el-pager li.is-active) {
      background-color: var(--el-color-primary);
      color: #fff;
    }

    :deep(.el-select) {
      min-width: 90px;
    }
  }
</style>
