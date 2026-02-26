<template>
  <div class="login-container">
    <div class="login-content">
      <div class="login-form-container">
        <div class="card shadow-lg border-0">
          <div class="card-body p-8">
            <!-- Logo and Title -->
            <div class="flex flex-col items-center mb-8">
              <img
                :src="logo"
                class="logo mb-4"
                height="100"
                width="100"
                alt="GeekAI-PPT"
              />
              <h1 class="font-bold text-gray-800 mb-2 text-4xl">欢迎登录</h1>
              <p class="text-gray-500 text-sm">登录 {{ title }} 管理控制台</p>
            </div>

            <!-- Login Form -->
            <form @submit.prevent="handleSubmit" class="space-y-6">
              <!-- Username Field -->
              <div class="form-group">
                <label
                  for="username"
                  class="block text-sm font-medium text-gray-700 mb-2"
                >
                  用户名
                </label>
                <input
                  id="username"
                  v-model="data.username"
                  type="text"
                  placeholder="请输入用户名"
                  class="form-input w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                  :class="{ 'border-red-500': errors.username }"
                />
                <div v-if="errors.username" class="text-red-500 text-sm mt-1">
                  {{ errors.username }}
                </div>
              </div>

              <!-- Password Field -->
              <div class="form-group">
                <label
                  for="password"
                  class="block text-sm font-medium text-gray-700 mb-2"
                >
                  密码
                </label>
                <div class="relative">
                  <input
                    id="password"
                    v-model="data.password"
                    :type="showPassword ? 'text' : 'password'"
                    placeholder="请输入密码"
                    class="form-input w-full px-4 py-2.5 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                    :class="{ 'border-red-500': errors.password }"
                  />
                  <button
                    type="button"
                    @click="showPassword = !showPassword"
                    class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <i
                      :class="showPassword ? 'icon-eye-slash' : 'icon-eye'"
                      class="text-lg"
                    ></i>
                  </button>
                </div>
                <div v-if="errors.password" class="text-red-500 text-sm mt-1">
                  {{ errors.password }}
                </div>
              </div>

              <!-- Submit Button -->
              <button
                type="submit"
                :disabled="loading"
                class="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500 text-white font-medium py-3 px-6 rounded-lg transition-all duration-200 transform hover:scale-[1.02] disabled:scale-100 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
              >
                <span v-if="loading" class="flex items-center justify-center">
                  <svg
                    class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      class="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      stroke-width="4"
                    ></circle>
                    <path
                      class="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                  登录中...
                </span>
                <span v-else>登 录</span>
              </button>
            </form>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="text-white footer-container">
        <Footer />
      </div>
    </div>
  </div>
</template>

<script setup>
  import Footer from '@/components/Footer.vue'
  import { checkAdminSession } from '@/js/cache/session'
  import { useLoginStore } from '@/stores/admin/useLoginStore'
  import { storeToRefs } from 'pinia'

  const router = useRouter()
  const indexURL = '/admin/dashboard'
  checkAdminSession().then(() => {
    router.push(indexURL)
  })

  const loginStore = useLoginStore()
  const { loading, data, errors, title, logo } = storeToRefs(loginStore)

  // 密码显示/隐藏状态
  const showPassword = ref(false)

  const handleSubmit = async () => {
    // 手动验证表单
    const validationErrors = {}

    // 验证用户名
    if (!data.value.username) {
      validationErrors.username = '请输入用户名'
    }

    // 验证密码
    if (!data.value.password) {
      validationErrors.password = '请输入密码'
    } else if (data.value.password.length < 6) {
      validationErrors.password = '至少 6 位'
    }

    // 如果有验证错误，更新错误状态
    if (Object.keys(validationErrors).length > 0) {
      errors.value = validationErrors
      return
    }

    // 清除错误状态
    errors.value = {}

    loginStore.handleSubmit()
  }
</script>

<style scoped lang="scss">
  @use '@/assets/css/admin/login.scss';

  .login-container {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    position: relative;

    .login-content {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 20px;

      .login-form-container {
        width: 100%;
        max-width: 400px;
        min-width: 320px;
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;

        .card {
          width: 100%;
          max-width: 100%;
        }
      }
    }

    .form-input {
      &:focus {
        outline: none;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
      }

      &::placeholder {
        color: #9ca3af;
        opacity: 1;
      }
    }

    .form-group {
      .form-input {
        transition: all 0.2s ease-in-out;

        &:hover {
          border-color: #d1d5db;
        }

        &:focus {
          border-color: #3b82f6;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
      }
    }
  }

  // 响应式媒体查询
  @media (min-width: 1024px) {
    .login-container .login-content .login-form-container {
      max-width: 500px;
    }
  }

  .footer-container {
    text-align: center;
    padding: 15px 0;
    flex-shrink: 0;

    .footer {
      .version {
        color: #fff;
      }
    }
  }

  /* 自定义滚动条样式 */
  .form-input::-webkit-scrollbar {
    width: 4px;
  }

  .form-input::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
  }

  .form-input::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 4px;
  }

  .form-input::-webkit-scrollbar-thumb:hover {
    background: #a8a8a8;
  }
</style>
