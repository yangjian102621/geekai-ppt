import { defineStore } from 'pinia'

const REDIRECT_KEY = 'geekai_ppt_redirect'

export const useAuthModalStore = defineStore('authModal', {
  state: () => ({
    visible: false,
    mode: 'login', // 'login' | 'register'
    redirectTo: null, // 与 getter redirect 区分，避免 Pinia 同名冲突
  }),
  getters: {
    redirect(state) {
      if (state.redirectTo) return state.redirectTo
      if (typeof localStorage !== 'undefined') {
        return localStorage.getItem(REDIRECT_KEY) || null
      }
      return null
    },
  },
  actions: {
    open(payload = {}) {
      this.visible = true
      this.mode = payload.mode ?? 'login'
      const redirect = payload.redirect ?? null
      this.redirectTo = redirect
      if (typeof redirect === 'string' && typeof localStorage !== 'undefined') {
        localStorage.setItem(REDIRECT_KEY, redirect)
      }
    },
    close() {
      this.visible = false
      this.mode = 'login'
      this.redirectTo = null
    },
  },
})
