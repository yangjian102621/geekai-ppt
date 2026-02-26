<template>
  <div class="card p-4">
    <div class="card-body">
      <div class="table-responsive" v-loading="loading">
        <el-table
          :data="presentations"
          border
          class="data-table"
          :row-key="(row) => row.id"
          @selection-change="handleSelectionChange"
          table-layout="auto"
        >
          <el-table-column type="selection" width="38" />
          <el-table-column
            prop="id"
            label="任务ID"
            width="280"
            show-overflow-tooltip
          />
          <el-table-column prop="username" label="用户名" width="120" />
          <el-table-column prop="topic" label="主题" show-overflow-tooltip />
          <el-table-column prop="title" label="标题" show-overflow-tooltip />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.generation_status)" size="small">
                {{ getStatusText(row.generation_status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatTime(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" fixed="right" width="80">
            <template #default="scope">
              <el-dropdown placement="bottom" trigger="click">
                <el-button type="primary" class="btn-operation">
                  <i class="iconfont icon-more-vertical"></i>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="openPreview(scope.row.id)">
                      <i class="iconfont icon-eye-open"></i> 详情
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </el-table-column>
          <template #empty>
            <el-empty description="暂无数据" />
          </template>
        </el-table>
      </div>
    </div>

    <model-dialog
      :modelValue="showPreview"
      :title="previewDetail?.title ?? '详情'"
      width="80%"
      hide-footer
      @cancel="showPreview = false"
    >
      <div v-if="previewDetail" class="max-h-[70vh] overflow-auto">
        <div class="grid grid-cols-2 sm:grid-cols-3 gap-4">
          <div
            v-for="(slide, i) in previewDetail.slides || []"
            :key="i"
            class="border rounded overflow-hidden bg-gray-50"
          >
            <el-image
              v-if="slide.versions?.length"
              :src="
                getImageUrl(
                  slide.versions[slide.versions.length - 1]?.image_url,
                )
              "
              :preview-src-list="
                slide.versions.map((v) => getImageUrl(v.image_url))
              "
              class="w-full aspect-video object-contain"
              alt=""
            />
          </div>
        </div>
      </div>
    </model-dialog>

    <Pagination
      :total="total"
      v-model:currentPage="currentPage"
      v-model:pageSize="pageSize"
    />
  </div>
</template>

<script setup>
  import { ref, onMounted, watch } from 'vue'
  import { ElMessage } from 'element-plus'
  import ModelDialog from '@/components/ModelDialog.vue'
  import Pagination from '@/components/Pagination.vue'
  import {
    adminListPresentations,
    adminGetPresentation,
    getImageUrl,
  } from '@/js/services/api'

  const loading = ref(false)
  const presentations = ref([])
  const currentPage = ref(1)
  const pageSize = ref(15)
  const total = ref(0)
  const filterCategory = ref('')
  const filterStatus = ref('')
  const showPreview = ref(false)
  const previewDetail = ref(null)

  function formatTime(ts) {
    if (!ts) return '-'
    return new Date(ts * 1000).toLocaleString('zh-CN')
  }

  function getStatusType(status) {
    if (status === 'completed') return 'success'
    if (status === 'failed') return 'danger'
    if (status === 'generating' || status === 'planning') return 'warning'
    return 'info'
  }

  function getStatusText(status) {
    const statusMap = {
      completed: '已完成',
      failed: '失败',
      generating: '生成中',
      planning: '规划中',
      idle: '待处理',
    }
    return statusMap[status] || status || '未知'
  }

  function handleSearch() {
    ElMessage.info('搜索功能待实现')
    currentPage.value = 1
    loadPresentations()
  }

  function handleReset() {
    filterCategory.value = ''
    filterStatus.value = ''
    currentPage.value = 1
    loadPresentations()
  }

  async function loadPresentations() {
    loading.value = true
    try {
      const skip = (currentPage.value - 1) * pageSize.value
      const limit = pageSize.value
      const res = await adminListPresentations(undefined, skip, limit)
      presentations.value = res.presentations || []
      total.value =
        res.total ?? (res.presentations ? res.presentations.length : 0)
    } catch {
      presentations.value = []
    } finally {
      loading.value = false
    }
  }

  async function openPreview(id) {
    try {
      previewDetail.value = await adminGetPresentation(id)
      showPreview.value = true
    } catch {
      ElMessage.error('加载失败')
    }
  }

  function handleSelectionChange() {
    // 预留批量操作
  }

  watch(
    [currentPage, pageSize],
    () => {
      loadPresentations()
    },
    { immediate: true },
  )
</script>

<style scoped lang="scss">
  @use '@/assets/css/admin/admin.scss';
</style>
