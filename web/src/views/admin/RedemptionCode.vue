<template>
  <div class="card p-4">
    <div class="card-body">
      <div class="table-responsive" v-loading="loading">
        <div class="search-container space-y-2">
          <span class="search-item">
            <el-button type="primary" @click="showDialog = true">
              <i class="iconfont icon-plus text-sm mr-1"></i> 生成兑换码
            </el-button>
          </span>
          <span class="search-item">
            <el-button
              type="danger"
              :disabled="!multipleSelection.length || deleteLoading"
              @click="handleBatchDelete"
            >
              批量删除
            </el-button>
          </span>
        </div>

        <el-table
          :data="redemptionCodes"
          border
          class="data-table"
          table-layout="auto"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="50" />
          <el-table-column label="兑换码" min-width="140">
            <template #default="{ row }">
              <span class="inline-flex items-center gap-1">
                <span>{{ row.code }}</span>
                <el-button
                  link
                  type="primary"
                  size="small"
                  class="copy-key p-0.5"
                  :data-clipboard-text="row.code"
                >
                  <i class="iconfont icon-copy text-sm" />
                </el-button>
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="scores" label="积分" />
          <el-table-column label="状态">
            <template #default="{ row }">
              <el-tag v-if="row.used_by_id" type="success" size="small">
                已使用
              </el-tag>
              <el-tag v-else type="primary" size="small"> 未使用 </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="创建时间">
            <template #default="{ row }">
              {{ formatTime(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" align="right">
            <template #default="{ row }">
              <el-button
                type="danger"
                size="small"
                :disabled="!!row.used_by_id || deleteLoading"
                @click="handleDelete(row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
          <template #empty>
            <el-empty description="暂无数据" />
          </template>
        </el-table>
      </div>
    </div>

    <model-dialog
      :modelValue="showDialog"
      title="生成积分兑换码"
      confirm-text="生成"
      cancel-text="关闭"
      :loading="submitLoading"
      @cancel="showDialog = false"
      @confirm="handleGenerate"
    >
      <el-form :model="form" label-position="top">
        <el-form-item label="积分数量" required>
          <el-input-number
            v-model="form.points"
            :min="1"
            placeholder="积分"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="生成数量" required>
          <el-input-number
            v-model="form.count"
            :min="1"
            :max="100"
            placeholder="数量"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
    </model-dialog>

    <Pagination
      :total="total"
      v-model:currentPage="currentPage"
      v-model:pageSize="pageSize"
    />
  </div>
</template>

<script setup>
  import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
  import Clipboard from 'clipboard'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import ModelDialog from '@/components/ModelDialog.vue'
  import Pagination from '@/components/Pagination.vue'
  import {
    adminCreateRedemptionCodes,
    adminListRedemptionCodes,
    adminDeleteRedemptionCode,
  } from '@/js/services/api'

  const loading = ref(false)
  const submitLoading = ref(false)
  const redemptionCodes = ref([])
  const currentPage = ref(1)
  const pageSize = ref(15)
  const total = ref(0)
  const showDialog = ref(false)
  const form = ref({ points: 10, count: 5 })
  const deleteLoading = ref(false)
  const multipleSelection = ref([])
  const clipboard = ref(null)

  function formatTime(ts) {
    if (!ts) return '-'
    return new Date(ts * 1000).toLocaleString('zh-CN')
  }

  function initClipboard() {
    clipboard.value?.destroy()
    clipboard.value = new Clipboard('.copy-key')
    clipboard.value.on('success', () => {
      ElMessage.success('复制成功！')
    })
    clipboard.value.on('error', () => {
      ElMessage.error('复制失败！')
    })
  }

  async function loadList() {
    loading.value = true
    try {
      const skip = (currentPage.value - 1) * pageSize.value
      const limit = pageSize.value
      const res = await adminListRedemptionCodes(undefined, skip, limit)
      redemptionCodes.value = res.redemption_codes || []
      total.value =
        res.total ?? (res.redemption_codes ? res.redemption_codes.length : 0)
    } catch {
      redemptionCodes.value = []
    } finally {
      loading.value = false
    }
  }

  async function handleGenerate() {
    if (!form.value.points || !form.value.count) {
      ElMessage.warning('请填写完整信息')
      return
    }
    submitLoading.value = true
    try {
      const res = await adminCreateRedemptionCodes(
        form.value.points,
        form.value.count,
      )
      ElMessage.success(`已生成 ${res.codes.length} 个兑换码`)
      showDialog.value = false
      form.value = { points: 10, count: 5 }
      await loadList()
    } catch (e) {
      ElMessage.error(e?.message || '生成失败')
    } finally {
      submitLoading.value = false
    }
  }

  function handleSelectionChange(val) {
    multipleSelection.value = val || []
  }

  async function handleBatchDelete() {
    const selected = multipleSelection.value || []
    const deletable = selected.filter((item) => !item.used_by_id)
    const blocked = selected.filter((item) => item.used_by_id)

    if (!deletable.length) {
      ElMessage.warning('选中的兑换码均已使用，无法删除')
      return
    }

    const msg =
      blocked.length > 0
        ? `选中 ${selected.length} 条记录，其中 ${blocked.length} 条已使用，将跳过。确认删除未使用的 ${deletable.length} 条兑换码吗？`
        : `确认删除选中的 ${deletable.length} 条未使用兑换码吗？`

    try {
      await ElMessageBox.confirm(msg, '批量删除确认', {
        type: 'warning',
        confirmButtonText: '删除',
        cancelButtonText: '取消',
      })
    } catch {
      return
    }

    deleteLoading.value = true
    try {
      for (const row of deletable) {
        try {
          await adminDeleteRedemptionCode(row.id)
        } catch (e) {
          console.error('删除兑换码失败', row, e)
        }
      }
      ElMessage.success('批量删除完成')
      multipleSelection.value = []
      await loadList()
    } finally {
      deleteLoading.value = false
    }
  }

  async function handleDelete(row) {
    if (row.used_by_id) {
      ElMessage.warning('已使用的兑换码不能删除')
      return
    }
    try {
      await ElMessageBox.confirm(
        `确定要删除兑换码「${row.code}」吗？`,
        '删除确认',
        {
          type: 'warning',
          confirmButtonText: '删除',
          cancelButtonText: '取消',
        },
      )
    } catch {
      return
    }

    deleteLoading.value = true
    try {
      await adminDeleteRedemptionCode(row.id)
      ElMessage.success('删除成功')
      await loadList()
    } catch (e) {
      ElMessage.error(e?.message || '删除失败')
    } finally {
      deleteLoading.value = false
    }
  }

  onMounted(() => {
    loadList()
    nextTick(initClipboard)
  })

  onBeforeUnmount(() => {
    clipboard.value?.destroy()
  })

  watch(
    redemptionCodes,
    () => nextTick(initClipboard),
    { deep: true },
  )

  watch(
    [currentPage, pageSize],
    () => {
      loadList()
    },
    { immediate: true },
  )
</script>

<style scoped lang="scss">
  @use '@/assets/css/admin/admin.scss';
</style>
