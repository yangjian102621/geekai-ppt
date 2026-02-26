<template>
  <el-dialog
    :model-value="authModalStore.visible"
    class="auth-modal-dialog"
    width="900px"
    :show-close="true"
    destroy-on-close
    align-center
    @update:model-value="onDialogVisibleChange"
  >
    <div class="auth-modal-body grid grid-cols-1 md:grid-cols-2 min-h-[420px]">
      <!-- 左侧：banner 图 -->
      <section
        class="auth-modal-left relative min-h-[200px] md:min-h-[420px] rounded-l-lg overflow-hidden"
        aria-hidden="true"
      >
        <el-image
          :src="bannerUrl"
          fit="cover"
          class="w-full h-full"
          :lazy="false"
        />
      </section>
      <!-- 右侧：表单区 -->
      <section
        class="auth-modal-right flex flex-col justify-center bg-white md:bg-slate-50 px-6 py-8 md:px-8 md:py-10 rounded-r-lg"
      >
        <div class="w-full max-w-sm mx-auto">
          <!-- 登录表单 -->
          <div
            v-show="authModalStore.mode === 'login'"
            class="login-form-card rounded-2xl border border-slate-200/80 bg-white px-8 py-10 shadow-lg shadow-slate-200/20"
          >
            <div class="mb-10">
              <h1
                class="text-xl font-semibold tracking-tight text-[var(--tech-slate-900)]"
              >
                {{ zh.auth.loginTitle }}
              </h1>
              <p class="mt-1.5 text-sm text-[var(--tech-slate-600)]">
                {{ zh.auth.loginSubtitle }}
              </p>
            </div>
            <el-form
              @submit.prevent="handleLogin"
              label-position="top"
              class="login-form"
            >
              <el-form-item :label="zh.auth.username" class="login-form-item">
                <el-input
                  v-model="loginUsername"
                  type="text"
                  :placeholder="zh.auth.username"
                  autocomplete="username"
                  size="large"
                  class="login-input"
                >
                  <template #prefix>
                    <User class="login-input-icon" aria-hidden="true" />
                  </template>
                </el-input>
              </el-form-item>
              <el-form-item :label="zh.auth.password" class="login-form-item">
                <el-input
                  v-model="loginPassword"
                  type="password"
                  :placeholder="zh.auth.password"
                  autocomplete="current-password"
                  show-password
                  size="large"
                  class="login-input"
                  @keyup.enter="handleLogin"
                >
                  <template #prefix>
                    <Lock class="login-input-icon" aria-hidden="true" />
                  </template>
                </el-input>
              </el-form-item>
              <el-form-item class="login-form-item mb-0">
                <el-button
                  type="primary"
                  size="large"
                  class="login-submit-btn w-full"
                  :loading="loginLoading"
                  @click="handleLogin"
                >
                  {{ zh.auth.login }}
                </el-button>
              </el-form-item>
            </el-form>
            <p
              class="text-sm text-center text-[var(--tech-slate-600)] mt-8 pt-6 border-t border-slate-100"
            >
              {{ zh.auth.noAccount }}
              <a
                href="javascript:void(0)"
                class="text-[var(--tech-blue-600)] hover:text-[var(--tech-blue-700)] hover:underline transition-colors duration-200 cursor-pointer"
                @click="
                  authModalStore.open({
                    mode: 'register',
                    redirect: authModalStore.redirect,
                  })
                "
              >
                {{ zh.auth.useInviteToRegister }}
              </a>
            </p>
          </div>

          <!-- 注册表单 -->
          <div
            v-show="authModalStore.mode === 'register'"
            class="login-form-card rounded-2xl border border-slate-200/80 bg-white px-8 py-10 shadow-lg shadow-slate-200/20"
          >
            <div class="mb-10">
              <h1
                class="text-xl font-semibold tracking-tight text-[var(--tech-slate-900)]"
              >
                {{ zh.auth.registerTitle }}
              </h1>
              <p class="mt-1.5 text-sm text-[var(--tech-slate-600)]">
                {{ zh.auth.loginSubtitle }}
              </p>
            </div>
            <el-form
              @submit.prevent="handleRegister"
              label-position="top"
              class="login-form"
            >
              <el-form-item :label="zh.auth.username" class="login-form-item">
                <el-input
                  v-model="registerUsername"
                  type="text"
                  :placeholder="
                    zh.auth.placeholder.replace('{label}', zh.auth.username)
                  "
                  autocomplete="username"
                  size="large"
                  class="login-input"
                >
                  <template #prefix>
                    <User class="login-input-icon" aria-hidden="true" />
                  </template>
                </el-input>
              </el-form-item>
              <el-form-item :label="zh.auth.password" class="login-form-item">
                <el-input
                  v-model="registerPassword"
                  type="password"
                  :placeholder="
                    zh.auth.placeholder.replace('{label}', zh.auth.password)
                  "
                  autocomplete="new-password"
                  show-password
                  size="large"
                  class="login-input"
                  @keyup.enter="handleRegister"
                >
                  <template #prefix>
                    <Lock class="login-input-icon" aria-hidden="true" />
                  </template>
                </el-input>
              </el-form-item>
              <el-form-item :label="zh.auth.inviteCode" class="login-form-item">
                <el-input
                  v-model="registerInviteCode"
                  type="text"
                  :placeholder="
                    zh.auth.placeholder.replace('{label}', zh.auth.inviteCode)
                  "
                  autocomplete="off"
                  size="large"
                  class="login-input"
                >
                  <template #prefix>
                    <KeyRound class="login-input-icon" aria-hidden="true" />
                  </template>
                </el-input>
              </el-form-item>
              <el-form-item class="login-form-item mb-0">
                <el-button
                  type="primary"
                  size="large"
                  class="login-submit-btn w-full"
                  :loading="registerLoading"
                  @click="handleRegister"
                >
                  {{ zh.auth.register }}
                </el-button>
              </el-form-item>
            </el-form>
            <p
              class="text-sm text-center text-[var(--tech-slate-600)] mt-8 pt-6 border-t border-slate-100"
            >
              {{ zh.auth.hasAccount }}
              <a
                href="javascript:void(0)"
                class="text-[var(--tech-blue-600)] hover:text-[var(--tech-blue-700)] hover:underline transition-colors duration-200 cursor-pointer"
                @click="
                  authModalStore.open({
                    mode: 'login',
                    redirect: authModalStore.redirect,
                  })
                "
              >
                {{ zh.auth.goLogin }}
              </a>
            </p>
          </div>
        </div>
      </section>
    </div>
  </el-dialog>
</template>

<script setup lang="js">
  import { ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { User, Lock, KeyRound } from 'lucide-vue-next'
  import { useAuth } from '@/composables/useAuth'
  import { useAuthModalStore } from '@/stores/authModal'
  import { useAuthStore } from '@/stores/auth'
  import { zh } from '@/locale/zh'
  import { ElMessage } from 'element-plus'
  const bannerUrl = '/images/banner.png'

  const router = useRouter()
  const auth = useAuth()
  const authModalStore = useAuthModalStore()
  const authStore = useAuthStore()

  const loginUsername = ref('')
  const loginPassword = ref('')
  const loginLoading = ref(false)

  const registerInviteCode = ref('')
  const registerUsername = ref('')
  const registerPassword = ref('')
  const registerLoading = ref(false)

  function onDialogVisibleChange(visible) {
    if (!visible) {
      authModalStore.close()
    }
  }

  function finishAuth() {
    authStore.setAuthenticated(true)
    authModalStore.close()

    // 从 localStorage 读取 redirect 并跳转
    const REDIRECT_KEY = 'geekai_ppt_redirect'
    if (typeof localStorage !== 'undefined') {
      const redirect = localStorage.getItem(REDIRECT_KEY)
      if (redirect) {
        localStorage.removeItem(REDIRECT_KEY)
        router.push(redirect)
        return
      }
    }

    // 如果没有 localStorage 中的 redirect，使用 store 中的 redirect（向后兼容）
    const redirect = authModalStore.redirect
    if (redirect) {
      router.push(redirect)
    }
  }

  // 移除 watch 监听，改为通过全局 API 显式控制弹窗显示/隐藏
  // 这样更可控，避免状态变化导致的意外弹窗

  async function handleLogin() {
    if (!loginUsername.value.trim() || !loginPassword.value) {
      ElMessage.warning('请输入用户名和密码')
      return
    }
    loginLoading.value = true
    try {
      await auth.login(loginUsername.value.trim(), loginPassword.value)
      finishAuth()
    } catch (e) {
      ElMessage.error(e?.message || zh.auth.loginFailed)
    } finally {
      loginLoading.value = false
    }
  }

  async function handleRegister() {
    if (
      !registerInviteCode.value.trim() ||
      !registerUsername.value.trim() ||
      !registerPassword.value
    ) {
      ElMessage.warning('请填写用户名和密码，并输入邀请码')
      return
    }
    registerLoading.value = true
    try {
      await auth.register(
        registerInviteCode.value.trim(),
        registerUsername.value.trim(),
        registerPassword.value,
      )
      finishAuth()
    } catch (e) {
      ElMessage.error(e?.message || zh.auth.registerFailed)
    } finally {
      registerLoading.value = false
    }
  }
</script>

<style scoped>
  .auth-modal-dialog :deep(.el-dialog__body) {
    padding: 0;
    overflow: hidden;
  }

  .auth-modal-body {
    max-height: 85vh;
  }

  .auth-modal-left {
    background-color: var(--tech-blue-50);
  }

  .auth-modal-left :deep(.el-image) {
    width: 100%;
    height: 100%;
  }

  .auth-modal-left :deep(.el-image__inner) {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .login-form-card {
    transition: box-shadow 0.2s ease;
  }
  .login-form-card:focus-within {
    box-shadow: 0 20px 40px -12px rgba(15, 23, 42, 0.08);
  }

  .login-form :deep(.el-form-item) {
    margin-bottom: 1.25rem;
  }
  .login-form :deep(.el-form-item__label) {
    color: var(--tech-slate-700);
    font-weight: 500;
    font-size: 0.875rem;
    margin-bottom: 0.375rem;
  }
  .login-form :deep(.el-input__wrapper) {
    border-radius: 10px;
    box-shadow: 0 0 0 1px var(--tech-slate-200);
    transition:
      box-shadow 0.2s ease,
      border-color 0.2s ease;
    padding: 0.625rem 1rem 0.625rem 1rem;
  }
  .login-form :deep(.el-input__wrapper:hover) {
    box-shadow: 0 0 0 1px var(--tech-slate-300);
  }
  .login-form :deep(.el-input__wrapper.is-focus) {
    box-shadow: 0 0 0 2px var(--tech-blue-500);
  }
  .login-form :deep(.el-input__inner) {
    color: var(--tech-slate-900);
  }
  .login-form :deep(.el-input__inner::placeholder) {
    color: var(--tech-slate-400);
  }

  .login-input-icon {
    width: 1.125rem;
    height: 1.125rem;
    color: var(--tech-slate-500);
    flex-shrink: 0;
  }

  .login-submit-btn {
    font-weight: 500;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    transition:
      background-color 0.2s ease,
      box-shadow 0.2s ease;
  }
  .login-submit-btn:hover {
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
  }
</style>
