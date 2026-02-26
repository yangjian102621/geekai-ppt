import { validateForm } from '@/js/utils/common'
import { showMessageError, showMessageOK } from '@/js/utils/dialog'
import { adminLogin } from '@/js/services/api'
import { defineStore } from 'pinia'
import { useRouter } from 'vue-router'
export const useLoginStore = defineStore('login', {
  state: () => ({
    data: {
      username: import.meta.env.VITE_ADMIN_USER,
      password: import.meta.env.VITE_ADMIN_PASS,
    },
    errors: {
      username: '',
      password: '',
    },
    loading: false,
    title: import.meta.env.VITE_TITLE,
    logo: import.meta.env.VITE_LOGO,
    rules: {
      username: { required: true, message: '请输入用户名' },
      password: { required: true, message: '请输入密码' },
    },
    router: useRouter(),
  }),

  actions: {
    async handleSubmit() {
      if (!validateForm(this.data, this.rules, this.errors)) return
      await this.doLogin()
    },

    async doLogin() {
      this.loading = true
      try {
        const res = await adminLogin(this.data.username, this.data.password)
        // adminLogin 已经在 api.js 中处理了 token 保存
        this.loading = false
        showMessageOK('登录成功!')
        this.router.push('/admin/dashboard')
        return res
      } catch (e) {
        this.loading = false
        showMessageError('登录失败：' + (e.message || '未知错误'))
        throw e
      }
    },
  },
})
