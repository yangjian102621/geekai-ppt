/**
 * 用户认证：登录、注册、登出、token 与用户信息持久化。
 * 与 session（axios 请求头）同步：setToken 时同时写入/清除 session，保证用户中心等 axios 请求带同一 token。
 */
import { ref, computed, onMounted } from 'vue'
import { API_BASE_URL } from '@/config'
import { useAuthStore } from '@/stores/auth'
import { setUserToken, removeUserToken, getUserToken } from '@/js/cache/session'

const TOKEN_KEY = 'geekai_ppt_token'
const ADMIN_TOKEN_KEY = 'geekai_ppt_admin_token'

const token = ref(localStorage.getItem(TOKEN_KEY))
const adminToken = ref(localStorage.getItem(ADMIN_TOKEN_KEY))
const user = ref(null)

async function request(endpoint, options = {}) {
  const { token: t, ...rest } = options
  const headers = { ...(rest.headers || {}) }
  if (rest.body && !(rest.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json'
  }
  if (t) {
    headers['Authorization'] = `Bearer ${t}`
  }
  const res = await fetch(`${API_BASE_URL}${endpoint}`, { ...rest, headers })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    throw new Error(data.detail || data.message || `HTTP ${res.status}`)
  }
  return data
}

export function useAuth() {
  const isLoggedIn = computed(() => !!token.value)

  function setToken(t) {
    token.value = t
    if (t) {
      localStorage.setItem(TOKEN_KEY, t)
      setUserToken(t)
    } else {
      localStorage.removeItem(TOKEN_KEY)
      removeUserToken()
    }
  }

  async function loadUser() {
    if (!token.value) {
      user.value = null
      return
    }
    try {
      const data = await request('/auth/me', {
        method: 'GET',
        token: token.value,
      })
      user.value = data
      const authStore = useAuthStore()
      authStore.setAuthenticated(true)
      return data
    } catch {
      setToken(null)
      user.value = null
      const authStore = useAuthStore()
      authStore.setAuthenticated(false)
    }
  }

  async function login(username, password) {
    const data = await request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })
    setToken(data.access_token)
    user.value = data.user
    const authStore = useAuthStore()
    authStore.setAuthenticated(true)
    return data
  }

  async function register(inviteCode, username, password) {
    const data = await request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ invite_code: inviteCode, username, password }),
    })
    setToken(data.access_token)
    user.value = data.user
    const authStore = useAuthStore()
    authStore.setAuthenticated(true)
    return data
  }

  function logout() {
    setToken(null)
    user.value = null
    const authStore = useAuthStore()
    authStore.setAuthenticated(false)
  }

  function getToken() {
    return token.value
  }

  onMounted(() => {
    if (token.value && !getUserToken()) {
      setUserToken(token.value)
    }
    if (token.value && !user.value) {
      loadUser()
    }
  })

  return {
    user,
    token: computed(() => token.value),
    isLoggedIn,
    login,
    register,
    logout,
    loadUser,
    getToken,
  }
}

export function clearTokenAndUser() {
  token.value = null
  user.value = null
  if (typeof localStorage !== 'undefined') {
    localStorage.removeItem(TOKEN_KEY)
  }
  removeUserToken()
  const authStore = useAuthStore()
  authStore.setAuthenticated(false)
}

export function useAdminAuth() {
  const isAdminLoggedIn = computed(() => !!adminToken.value)

  function setAdminToken(t) {
    adminToken.value = t
    if (t) localStorage.setItem(ADMIN_TOKEN_KEY, t)
    else localStorage.removeItem(ADMIN_TOKEN_KEY)
  }

  function getAdminToken() {
    return adminToken.value
  }

  function adminLogout() {
    setAdminToken(null)
  }

  return {
    isAdminLoggedIn,
    setAdminToken,
    getAdminToken,
    adminLogout,
  }
}
