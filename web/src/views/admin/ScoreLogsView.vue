<template>
  <div class="card p-4">
    <div class="card-body">
      <div class="table-responsive" v-loading="loading">
        <div class="search-container space-y-2 mb-4">
          <div class="flex items-center gap-2">
            <span class="text-sm text-gray-600">筛选用户：</span>
            <el-input
              v-model="filterUserId"
              placeholder="输入用户ID或用户名"
              clearable
              style="width: 200px"
              @clear="handleFilterClear"
              @keyup.enter="handleFilter"
            />
            <el-button type="primary" @click="handleFilter">筛选</el-button>
            <el-button v-if="filterUserId" @click="handleFilterClear"
              >清除</el-button
            >
          </div>
        </div>

        <el-table
          :data="scoreLogs"
          border
          class="data-table"
          table-layout="auto"
        >
          <el-table-column prop="username" label="用户" width="150">
            <template #default="{ row }">
              <div class="font-medium">{{ row.username || '-' }}</div>
            </template>
          </el-table-column>
          <el-table-column
            prop="log_type"
            label="类型"
            width="100"
            align="center"
          >
            <template #default="{ row }">
              <el-tag v-if="row.log_type === 'recharge'" type="success">充值</el-tag>
              <el-tag v-else-if="row.log_type === 'consume'" type="danger">消费</el-tag>
              <span v-else class="text-sm text-gray-400">-</span>
            </template>
          </el-table-column>
          <el-table-column
            prop="amount"
            label="积分变动"
            width="120"
            align="center"
          >
            <template #default="{ row }">
              <span
                v-if="row.log_type === 'recharge'"
                class="text-green-600 font-semibold"
              >
                +{{ row.amount }}
              </span>
              <span
                v-else
                class="text-red-600 font-semibold"
              >
                -{{ row.amount }}
              </span>
            </template>
          </el-table-column>
          <el-table-column
            prop="balance"
            label="余额"
            width="100"
            align="center"
          >
            <template #default="{ row }">
              <span
                v-if="row.balance !== null && row.balance !== undefined"
                class="text-blue-600 font-semibold"
              >
                {{ row.balance }}
              </span>
              <span v-else class="text-sm text-gray-400">-</span>
            </template>
          </el-table-column>
          <el-table-column prop="prompt" label="提示词" min-width="200">
            <template #default="{ row }">
              <div class="prompt-cell">
                <span v-if="row.prompt" class="text-sm text-gray-700">
                  {{ truncatePrompt(row.prompt) }}
                </span>
                <span v-else class="text-sm text-gray-400">-</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column
            prop="image_path"
            label="图片"
            width="150"
            align="center"
          >
            <template #default="{ row }">
              <div v-if="row.image_path" class="flex justify-center">
                <el-image
                  :src="getImageUrl(row.image_path)"
                  :preview-src-list="[getImageUrl(row.image_path)]"
                  preview-teleported
                  fit="cover"
                  class="w-20 h-12 rounded cursor-pointer border border-gray-200"
                  lazy
                />
              </div>
              <span v-else class="text-sm text-gray-400">-</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="时间" width="180">
            <template #default="{ row }">
              <span class="text-sm text-gray-600">
                {{ formatTime(row.created_at) }}
              </span>
            </template>
          </el-table-column>
          <template #empty>
            <el-empty description="暂无积分日志记录" />
          </template>
        </el-table>
      </div>
    </div>

    <Pagination
      :total="total"
      v-model:currentPage="currentPage"
      v-model:pageSize="pageSize"
    />
  </div>
</template>

<script setup>
  import { ref, onMounted, watch } from 'vue'
  import { adminScoreLogs } from '@/js/services/api'
  import Pagination from '@/components/Pagination.vue'

  const loading = ref(false)
  const scoreLogs = ref([])
  const currentPage = ref(1)
  const pageSize = ref(20)
  const total = ref(0)
  const filterUserId = ref('')

  function formatTime(timestamp) {
    if (!timestamp) return '-'
    const date = new Date(timestamp * 1000)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  function truncatePrompt(prompt) {
    if (!prompt) return '-'
    return prompt.length > 100 ? prompt.substring(0, 100) + '...' : prompt
  }

  function getImageUrl(imagePath) {
    if (!imagePath) return ''
    // 如果已经是完整 URL，直接返回
    if (imagePath.startsWith('http')) return imagePath
    // 如果是相对路径，添加 API 基础 URL
    if (imagePath.startsWith('/images/')) {
      const apiBase = import.meta.env.VITE_API_BASE_URL || '/api'
      return `${apiBase}${imagePath}`
    }
    return imagePath
  }

  function handleFilter() {
    currentPage.value = 1
    loadList()
  }

  function handleFilterClear() {
    filterUserId.value = ''
    currentPage.value = 1
    loadList()
  }

  async function loadList() {
    loading.value = true
    try {
      const skip = (currentPage.value - 1) * pageSize.value
      const userId = filterUserId.value?.trim() || undefined
      const res = await adminScoreLogs(skip, pageSize.value, userId)
      scoreLogs.value = res.score_logs || []
      total.value = res.total || 0
    } catch (e) {
      console.error('加载积分日志失败', e)
      scoreLogs.value = []
      total.value = 0
    } finally {
      loading.value = false
    }
  }

  onMounted(() => {
    loadList()
  })

  watch(
    [currentPage, pageSize],
    () => {
      loadList()
    },
    { immediate: false },
  )
</script>

<style scoped lang="scss">
  @use '@/assets/css/admin/admin.scss';

  .prompt-cell {
    max-width: 300px;
    word-break: break-word;
    line-height: 1.5;
  }

  .search-container {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }
</style>
