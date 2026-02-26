<template>
  <!-- 顶部导航栏 -->
  <nav class="navbar">
    <div class="container-fluid flex p-2 justify-between lg:justify-end">
      <button
        class="btn-toggle px-3 py-2 rounded-md"
        type="button"
        @click="toggleSidebar()"
      >
        <i class="iconfont icon-sub-menu"></i>
      </button>

      <div class="flex items-center pr-2" v-if="!store.collapsed">
        <el-dropdown trigger="click">
          <a class="flex items-center gap-1" role="button">
            <img
              :src="avatar"
              class="rounded-full"
              alt="用户头像"
              width="30"
              height="30"
            />
            <span class="nav-profile-name">极客学长</span>
            <el-icon><ArrowDown /></el-icon>
          </a>

          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item>
                <i class="iconfont icon-version"></i> 当前版本-{{ version }}
              </el-dropdown-item>
              <el-dropdown-item @click="showPasswordModal = true">
                <i class="iconfont icon-password"></i>
                <span>修改密码</span>
              </el-dropdown-item>
              <el-dropdown-item divided @click="logout">
                <i class="iconfont icon-logout"></i>
                <span>退出登录</span>
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="showPasswordModal"
      title="修改密码"
      width="400px"
      destroy-on-close
    >
      <el-form label-position="top">
        <el-form-item label="当前密码">
          <el-input v-model="oldPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="newPassword" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPasswordModal = false">取消</el-button>
        <el-button
          type="primary"
          :loading="passwordLoading"
          @click="changePassword"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
  </nav>
</template>

<script setup>
  import { removeAdminToken } from '@/js/cache/session'
  import { useSharedStore } from '@/js/cache/sharedata'
  import { showMessageError, showMessageOK } from '@/js/utils/dialog'
  import { adminChangePassword } from '@/js/services/api'
  import { ArrowDown } from '@element-plus/icons-vue'
  import { ElMessage } from 'element-plus'

  const avatar = ref('/images/admin/avatar.png')
  const store = useSharedStore()
  const showPasswordModal = ref(false)
  const oldPassword = ref('')
  const newPassword = ref('')
  const passwordLoading = ref(false)

  const toggleSidebar = () => {
    store.collapsed = !store.collapsed
  }

  const router = useRouter()
  const version = import.meta.env.VITE_APP_VERSION

  const logout = () => {
    removeAdminToken()
    router.push('/admin/login')
  }

  const changePassword = async () => {
    if (!oldPassword.value || !newPassword.value) {
      ElMessage.warning('请填写当前密码和新密码')
      return
    }
    passwordLoading.value = true
    try {
      await adminChangePassword(oldPassword.value, newPassword.value)
      ElMessage.success('密码已修改')
      showPasswordModal.value = false
      oldPassword.value = ''
      newPassword.value = ''
    } catch (e) {
      ElMessage.error(e?.message || '修改失败')
    } finally {
      passwordLoading.value = false
    }
  }
</script>

<style scoped lang="scss">
  .navbar {
    background: #fff;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

    .btn-toggle {
      border: 1px solid #5a23c8;
      background-color: rgba(124, 57, 237, 0.08);
      color: #5a23c8;
      display: none;
    }
  }

  @media (max-width: 768px) {
    .navbar {
      .btn-toggle {
        display: block;
      }
    }
  }
</style>
