/**
 * Util lib functions
 */
import { ElLoading, ElMessage, ElMessageBox } from 'element-plus'
import { isMobile } from './libs'

let loadingInstance = null

const messageOptions = {
  duration: 3000,
  showClose: true,
  grouping: true,
}

function notify(type, message) {
  closeLoading()
  const payload = {
    ...messageOptions,
    message,
    type,
    customClass: isMobile() ? 'el-message--mobile' : '',
  }
  if (type) {
    ElMessage(payload)
  } else {
    ElMessage({ ...payload, type: 'info' })
  }
}

export function showMessageOK(message) {
  notify('success', message)
}

export function showMessageInfo(message) {
  notify('info', message)
}

export function showMessageWarning(message) {
  notify('warning', message)
}

export function showMessageError(message) {
  notify('error', message)
}

export function showLoading(message = '正在处理...', appendTo = 'body') {
  closeLoading()
  const target =
    appendTo === 'body'
      ? document.body
      : document.querySelector(appendTo) || document.body
  loadingInstance = ElLoading.service({
    target,
    lock: true,
    text: message,
    background: 'rgba(255, 255, 255, 0.6)',
    customClass: 'loading-overlay',
  })
}

export function closeLoading() {
  if (loadingInstance) {
    loadingInstance.close()
    loadingInstance = null
  }
}

export function showConfirm(title, message, onConfirm, onCancel) {
  onConfirm = onConfirm || function () {}
  onCancel = onCancel || function () {}
  ElMessageBox.confirm(message, title, {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: '',
    center: true,
    closeOnClickModal: isMobile(),
  })
    .then(() => onConfirm())
    .catch(() => onCancel())
}

export function showMessageBox(title, message) {
  ElMessageBox.alert(message, title, {
    confirmButtonText: '确认',
    center: true,
    closeOnClickModal: isMobile(),
  })
}

export function showComingSoon() {
  showMessageInfo('当前功能正在开发中，敬请期待！')
}
