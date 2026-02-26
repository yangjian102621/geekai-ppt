<template>
  <div class="score-logs-view min-h-full bg-[var(--tech-slate-25)]">
    <section class="max-w-6xl mx-auto px-4 py-8">
      <header class="mb-6">
        <h1 class="text-2xl font-semibold text-[var(--tech-slate-900)]">
          积分日志
        </h1>
        <p class="text-sm text-[var(--tech-slate-500)] mt-1">
          查看你的积分变动记录，包括充值、消费的积分、提示词和生成的图片
        </p>
      </header>

      <div
        v-loading="loading"
        class="bg-white rounded-lg shadow-sm border border-[var(--tech-slate-200)]"
      >
        <el-table
          :data="scoreLogs"
          border
          class="data-table"
          table-layout="auto"
        >
          <el-table-column
            prop="log_type"
            label="类型"
            width="100"
            align="center"
          >
            <template #default="{ row }">
              <el-tag v-if="row.log_type === 'recharge'" type="success">充值</el-tag>
              <el-tag v-else-if="row.log_type === 'consume'" type="danger">消费</el-tag>
              <span v-else class="text-sm text-[var(--tech-slate-400)]">-</span>
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
                class="text-[var(--tech-green-600)] font-semibold"
              >
                +{{ row.amount }}
              </span>
              <span
                v-else
                class="text-[var(--tech-red-600)] font-semibold"
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
                class="text-[var(--tech-blue-600)] font-semibold"
              >
                {{ row.balance }}
              </span>
              <span v-else class="text-sm text-[var(--tech-slate-400)]">-</span>
            </template>
          </el-table-column>
          <el-table-column prop="prompt" label="提示词" min-width="200">
            <template #default="{ row }">
              <div class="prompt-cell">
                <span
                  v-if="row.prompt"
                  class="text-sm text-[var(--tech-slate-700)]"
                >
                  {{ truncatePrompt(row.prompt) }}
                </span>
                <span v-else class="text-sm text-[var(--tech-slate-400)]"
                  >-</span
                >
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
                  class="w-20 h-12 rounded cursor-pointer border border-[var(--tech-slate-200)]"
                  lazy
                />
              </div>
              <span v-else class="text-sm text-[var(--tech-slate-400)]">-</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="时间" width="180">
            <template #default="{ row }">
              <span class="text-sm text-[var(--tech-slate-600)]">
                {{ formatTime(row.created_at) }}
              </span>
            </template>
          </el-table-column>
          <template #empty>
            <el-empty description="暂无积分使用记录" />
          </template>
        </el-table>

        <div class="p-4 border-t border-[var(--tech-slate-200)]">
          <Pagination
            :total="total"
            v-model:currentPage="currentPage"
            v-model:pageSize="pageSize"
          />
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="js">
  import { ref, onMounted, watch } from 'vue'
  import { userScoreLogs } from '@/js/services/api'
  import Pagination from '@/components/Pagination.vue'

  const loading = ref(false)
  const scoreLogs = ref([])
  const currentPage = ref(1)
  const pageSize = ref(20)
  const total = ref(0)

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

  async function loadList() {
    loading.value = true
    try {
      const skip = (currentPage.value - 1) * pageSize.value
      const res = await userScoreLogs(skip, pageSize.value)
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

<style scoped>
  .score-logs-view {
    min-height: 100%;
  }

  .prompt-cell {
    max-width: 300px;
    word-break: break-word;
    line-height: 1.5;
  }

  .data-table {
    width: 100%;
  }
</style>
