<template>
  <div class="card p-4">
    <div class="card-body">
      <div class="table-responsive" v-loading="loading">
        <div class="search-container space-y-2">
          <span class="search-item">
            <el-button type="primary" @click="add">
              <i class="iconfont icon-plus text-sm mr-1"></i> 添加用户
            </el-button>
          </span>
        </div>

        <el-table
          :data="users"
          border
          class="data-table"
          :row-key="(row) => row.id"
          @selection-change="handleSelectionChange"
          table-layout="auto"
        >
          <el-table-column type="selection" width="38" />
          <el-table-column prop="username" label="用户名" />
          <el-table-column prop="points" label="积分" width="100" />
          <el-table-column
            prop="id"
            label="ID"
            width="280"
            show-overflow-tooltip
          />
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
                    <el-dropdown-item @click="editUser(scope.row)">
                      <i class="iconfont icon-edit"></i> 编辑
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

      <Pagination
        :total="total"
        v-model:currentPage="currentPage"
        v-model:pageSize="pageSize"
      />
    </div>

    <model-dialog
      :modelValue="showUserFormDialog"
      :title="editingUser ? '编辑用户' : '添加用户'"
      :loading="createUserLoading"
      confirm-text="确定"
      cancel-text="关闭"
      @cancel="showUserFormDialog = false"
      @confirm="handleSaveUser"
    >
      <el-form :model="userForm" label-position="top" ref="formRef">
        <el-form-item label="用户名" required>
          <el-input v-model="userForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item
          :label="editingUser ? '新密码（不填则不修改）' : '密码'"
          :required="!editingUser"
        >
          <el-input
            v-model="userForm.password"
            type="password"
            :placeholder="editingUser ? '留空则不修改' : '请输入密码'"
            show-password
          />
        </el-form-item>
        <el-form-item label="积分">
          <el-input-number
            v-model="userForm.points"
            :min="0"
            placeholder="积分"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
    </model-dialog>
  </div>
</template>

<script setup>
  import { ref, onMounted, watch } from 'vue'
  import { ElMessage } from 'element-plus'
  import ModelDialog from '@/components/ModelDialog.vue'
  import Pagination from '@/components/Pagination.vue'
  import { adminListUsers, adminCreateUser } from '@/js/services/api'

  const loading = ref(false)
  const users = ref([])
  const currentPage = ref(1)
  const pageSize = ref(15)
  const total = ref(0)
  const showUserFormDialog = ref(false)
  const createUserLoading = ref(false)
  const editingUser = ref(null)
  const formRef = ref(null)

  const userForm = ref({
    username: '',
    password: '',
    points: 0,
  })

  function formatTime(ts) {
    if (!ts) return '-'
    return new Date(ts * 1000).toLocaleString('zh-CN')
  }

  async function loadUsers() {
    loading.value = true
    try {
      const skip = (currentPage.value - 1) * pageSize.value
      const limit = pageSize.value
      const res = await adminListUsers(skip, limit)
      users.value = res.users || []
      total.value = res.total ?? (res.users ? res.users.length : 0)
    } catch {
      users.value = []
    } finally {
      loading.value = false
    }
  }

  function add() {
    editingUser.value = null
    userForm.value = { username: '', password: '', points: 0 }
    showUserFormDialog.value = true
  }

  function editUser(user) {
    editingUser.value = user
    userForm.value = {
      username: user.username,
      password: '',
      points: user.points || 0,
    }
    showUserFormDialog.value = true
  }

  async function handleSaveUser() {
    if (!userForm.value.username.trim()) {
      ElMessage.warning('请输入用户名')
      return
    }
    if (!editingUser.value && !userForm.value.password) {
      ElMessage.warning('请输入密码')
      return
    }
    createUserLoading.value = true
    try {
      if (editingUser.value) {
        ElMessage.info('编辑用户功能待实现')
      } else {
        await adminCreateUser(
          userForm.value.username.trim(),
          userForm.value.password,
          userForm.value.points,
        )
        ElMessage.success('已添加用户')
      }
      showUserFormDialog.value = false
      await loadUsers()
    } catch (e) {
      ElMessage.error(e?.message || '操作失败')
    } finally {
      createUserLoading.value = false
    }
  }

  function handleSelectionChange() {}

  watch(
    [currentPage, pageSize],
    () => {
      loadUsers()
    },
    { immediate: true },
  )
</script>

<style scoped lang="scss">
  @use '@/assets/css/admin/admin.scss';
</style>
