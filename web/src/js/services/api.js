// API 服务层 - Presentations REST API
// 将 TypeScript fetch API 转换为 JavaScript axios 调用

import { httpGet, httpPost, httpDelete, httpPatch } from '../utils/http'
import { getUserToken, setUserToken, removeUserToken, getAdminToken, setAdminToken, removeAdminToken } from '../cache/session'

// API 基础 URL - web 框架使用代理，所以使用 /api 前缀
// 如果需要完整 URL，可以通过环境变量 VITE_API_BASE_URL 配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

// 未授权回调
let onUnauthorized = null
export function setOnUnauthorized(cb) {
  onUnauthorized = cb
}

// 构建完整 URL
function buildUrl(endpoint) {
  if (endpoint.startsWith('http')) return endpoint
  // 如果 endpoint 已经以 /api 开头，直接返回
  if (endpoint.startsWith('/api')) return endpoint
  // 否则添加 API_BASE_URL 前缀
  return `${API_BASE_URL}${endpoint}`
}

// 处理错误响应
function handleErrorResponse(error) {
  if (error.response) {
    const status = error.response.status
    const data = error.response.data || {}
    
    if (status === 401) {
      // 401 错误已在 http.js 拦截器中处理
      onUnauthorized?.()
      throw new Error(data.detail || data.message || 'Unauthorized')
    }
    if (status === 402) {
      throw new Error(data.detail || 'Insufficient points')
    }
    throw new Error(data.detail || data.message || `HTTP ${status}`)
  }
  throw error
}

// ============ 系统 ============
export async function healthCheck() {
  try {
    return await httpGet(buildUrl('/'))
  } catch (error) {
    handleErrorResponse(error)
  }
}

// ============ 用户认证与会员 ============
export async function authMe() {
  try {
    return await httpGet(buildUrl('/auth/me'))
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function redeemCode(code) {
  try {
    return await httpPost(buildUrl('/user/redeem'), { code })
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function createInviteCode() {
  try {
    return await httpPost(buildUrl('/user/invite-codes'))
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function listMyInviteCodes() {
  try {
    return await httpGet(buildUrl('/user/invite-codes'))
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function userChangePassword(oldPassword, newPassword) {
  try {
    return await httpPatch(buildUrl('/user/me/password'), {
      old_password: oldPassword,
      new_password: newPassword
    })
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function userScoreLogs(skip = 0, limit = 20) {
  try {
    return await httpGet(buildUrl('/user/score-logs'), { skip, limit })
  } catch (error) {
    handleErrorResponse(error)
  }
}

// ============ 管理员 API ============
export async function adminLogin(username, password) {
  try {
    const data = await httpPost(buildUrl('/admin/auth/login'), { username, password })
    // 保存 token
    if (data.access_token) {
      setAdminToken(`Bearer ${data.access_token}`)
    }
    return data
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function adminMe() {
  try {
    return await httpGet(buildUrl('/admin/me'))
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function adminChangePassword(oldPassword, newPassword) {
  try {
    return await httpPatch(buildUrl('/admin/me/password'), {
      old_password: oldPassword,
      new_password: newPassword
    })
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function adminListUsers(skip = 0, limit = 100) {
  try {
    return await httpGet(buildUrl('/admin/users'), { skip, limit })
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function adminCreateUser(username, password, initialScores = 0) {
  try {
    return await httpPost(buildUrl('/admin/users'), {
      username,
      password,
      initial_scores: initialScores
    })
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function adminListPresentations(userId, skip = 0, limit = 100) {
  try {
    const params = { skip, limit }
    if (userId) params.user_id = userId
    return await httpGet(buildUrl('/admin/presentations'), params)
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function adminGetPresentation(id) {
  try {
    return await httpGet(buildUrl(`/admin/presentations/${id}`))
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function adminGetConfig() {
  try {
    return await httpGet(buildUrl('/admin/config'))
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function adminUpdateConfig(config) {
  try {
    return await httpPatch(buildUrl('/admin/config'), {
      scores_per_slide: config.scores_per_slide,
      register_bonus_scores: config.register_bonus_scores
    })
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function adminCreateRedemptionCodes(scores, count) {
  try {
    return await httpPost(buildUrl('/admin/redemption-codes'), { scores, count })
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function adminListRedemptionCodes(used, skip = 0, limit = 100) {
  try {
    const params = { skip, limit }
    if (used !== undefined) params.used = used
    return await httpGet(buildUrl('/admin/redemption-codes'), params)
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function adminDeleteRedemptionCode(id) {
  try {
    return await httpDelete(buildUrl(`/admin/redemption-codes/${id}`))
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function adminCreateInviteCodes(count) {
  try {
    return await httpPost(buildUrl('/admin/invite-codes'), { count })
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function adminListInviteCodes(used, skip = 0, limit = 100) {
  try {
    const params = { skip, limit }
    if (used !== undefined) params.used = used
    return await httpGet(buildUrl('/admin/invite-codes'), params)
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function adminDeleteInviteCode(id) {
  try {
    return await httpDelete(buildUrl(`/admin/invite-codes/${id}`))
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function adminScoreLogs(skip = 0, limit = 20, userId) {
  try {
    const params = { skip, limit }
    if (userId) params.user_id = userId
    return await httpGet(buildUrl('/admin/score-logs'), params)
  } catch (error) {
    handleErrorResponse(error)
  }
}

// ============ 演示文稿（原 Session） ============
export async function listPresentations() {
  try {
    return await httpGet(buildUrl('/presentations'))
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function createPresentation(topic) {
  try {
    return await httpPost(buildUrl('/presentations'), { topic })
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function getPresentation(presentationId) {
  try {
    return await httpGet(buildUrl(`/presentations/${presentationId}`))
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function updatePresentation(presentationId, title) {
  try {
    return await httpPatch(buildUrl(`/presentations/${presentationId}`), { title })
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function deletePresentation(presentationId) {
  try {
    return await httpDelete(buildUrl(`/presentations/${presentationId}`))
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function restorePresentation(presentationId) {
  try {
    return await httpPost(buildUrl(`/presentations/${presentationId}/restore`))
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function permanentlyDeletePresentation(presentationId) {
  try {
    return await httpDelete(buildUrl(`/presentations/${presentationId}/permanent`))
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function clearRecycleBin() {
  try {
    return await httpDelete(buildUrl('/presentations/deleted'))
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function listDeletedPresentations() {
  try {
    const response = await httpGet(buildUrl('/presentations/deleted'))
    return response.presentations || response
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function publishPresentation(presentationId) {
  try {
    return await httpPost(buildUrl(`/presentations/${presentationId}/publish`))
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function listGalleryPresentations(skip = 0, limit = 20) {
  try {
    const response = await httpGet(buildUrl('/gallery'), { skip, limit })
    return response.presentations || response
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function getGalleryPresentation(presentationId) {
  try {
    return await httpGet(buildUrl(`/gallery/${presentationId}`))
  } catch (error) {
    handleErrorResponse(error)
  }
}

// ============ 幻灯片 ============
export async function deleteSlide(presentationId, slideId) {
  try {
    return await httpDelete(buildUrl(`/presentations/${presentationId}/slides/${slideId}`))
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function listDeletedSlides(presentationId) {
  try {
    const res = await httpGet(buildUrl(`/presentations/${presentationId}/slides/deleted`))
    return res.slides || res
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function restoreSlide(presentationId, slideId) {
  try {
    return await httpPost(buildUrl(`/presentations/${presentationId}/slides/${slideId}/restore`))
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function setActiveVersion(presentationId, slideId, versionId) {
  try {
    return await httpPatch(buildUrl(`/presentations/${presentationId}/slides/${slideId}/active-version`), {
      version_id: versionId
    })
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function deleteVersion(presentationId, slideId, versionId) {
  try {
    return await httpDelete(buildUrl(`/presentations/${presentationId}/slides/${slideId}/versions/${versionId}`))
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function listVersions(presentationId, slideId) {
  try {
    return await httpGet(buildUrl(`/presentations/${presentationId}/slides/${slideId}/versions`))
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function createVersion(presentationId, slideId, req) {
  try {
    return await httpPost(buildUrl(`/presentations/${presentationId}/slides/${slideId}/versions`), req)
  } catch (error) {
    handleErrorResponse(error)
  }
}

// ============ 规划与批量生成 ============
export async function planPPT(request) {
  const {
    presentation_id,
    topic,
    page_count = 12,
    context_text = '',
    language = 'zh',
    presentation_mode = 'slides',
    style_preset_id,
    audience,
    scene,
    attention,
    purpose
  } = request
  
  try {
    return await httpPost(buildUrl(`/presentations/${presentation_id}/plan`), {
      topic,
      page_count: page_count ?? 12,
      context_text,
      language,
      presentation_mode,
      style_preset_id,
      audience,
      scene,
      attention,
      purpose
    })
  } catch (error) {
    handleErrorResponse(error)
  }
}

export function getPlanProgressStream(presentationId) {
  return new EventSource(`${API_BASE_URL || ''}/presentations/${presentationId}/plan-progress`)
}

export async function resumeGenerate(presentationId) {
  try {
    const response = await httpPost(buildUrl(`/presentations/${presentationId}/resume-generate`))
    return response
  } catch (error) {
    if (error.response?.status === 402) {
      const err = error.response.data || {}
      throw new Error(err.detail || 'Insufficient points')
    }
    handleErrorResponse(error)
  }
}

export async function startGenerate(presentationId, slides) {
  try {
    return await httpPost(buildUrl(`/presentations/${presentationId}/generate`), { slides }, {
      headers: {
        'Content-Type': 'application/json'
      }
    })
  } catch (error) {
    if (error.response?.status === 402) {
      const err = error.response.data || {}
      throw new Error(err.detail || 'Insufficient points')
    }
    handleErrorResponse(error)
  }
}

export async function insertSlideByOutline(presentationId, payload) {
  try {
    return await httpPost(buildUrl(`/presentations/${presentationId}/slides/insert`), payload)
  } catch (error) {
    handleErrorResponse(error)
  }
}

export async function generateFromOutline(presentationId, payload) {
  try {
    return await httpPost(buildUrl(`/presentations/${presentationId}/generate-from-outline`), payload, {
      headers: {
        'Content-Type': 'application/json'
      }
    })
  } catch (error) {
    if (error.response?.status === 402) {
      const err = error.response.data || {}
      throw new Error(err.detail || 'Insufficient points')
    }
    handleErrorResponse(error)
  }
}

export async function getGenerationProgress(presentationId) {
  try {
    return await httpGet(buildUrl(`/presentations/${presentationId}/generation-progress`))
  } catch (error) {
    handleErrorResponse(error)
  }
}

// ============ 文件 ============
export async function uploadDoc(file) {
  try {
    const formData = new FormData()
    formData.append('file', file)
    return await httpPost(buildUrl('/upload/doc'), formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  } catch (error) {
    handleErrorResponse(error)
  }
}

// ============ 工具 ============
export function getImageUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `${API_BASE_URL || ''}${path}`
}

export function formatTimestamp(timestamp) {
  const date = new Date(timestamp * 1000)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes} mins ago`
  if (hours < 24) return `${hours} hours ago`
  if (days < 7) return `${days} days ago`
  return date.toLocaleDateString()
}
