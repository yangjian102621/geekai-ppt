// 正则校验工具函数

export function validateEmail(email) {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return regex.test(email)
}

export function validateMobile(mobile) {
  const regex = /^1[3456789]\d{9}$/
  return regex.test(mobile)
}

// 适用于 Element Plus rules 的通用校验器
export function isRequired(message = '必填项不能为空') {
  return { required: true, message, trigger: ['blur', 'change'] }
}

export function minLength(min, message) {
  return {
    min,
    message: message || `长度不能少于 ${min} 个字符`,
    trigger: ['blur', 'change'],
  }
}

export function maxLength(max, message) {
  return {
    max,
    message: message || `长度不能超过 ${max} 个字符`,
    trigger: ['blur', 'change'],
  }
}

export function isUrlRule(message = '请输入合法的链接地址') {
  const urlRegex = /^(https?:\/\/)[^\s/$.?#].[^\s]*$/i
  return {
    validator: (_rule, value, callback) => {
      if (!value) return callback()
      if (urlRegex.test(value)) return callback()
      callback(new Error(message))
    },
    trigger: ['blur', 'change'],
  }
}

export function isEmailRule(message = '请输入合法的邮箱地址') {
  return {
    validator: (_rule, value, callback) => {
      if (!value) return callback()
      if (validateEmail(value)) return callback()
      callback(new Error(message))
    },
    trigger: ['blur', 'change'],
  }
}

export function isMobileRule(message = '请输入合法的手机号') {
  return {
    validator: (_rule, value, callback) => {
      if (!value) return callback()
      if (validateMobile(value)) return callback()
      callback(new Error(message))
    },
    trigger: ['blur', 'change'],
  }
}

export function passwordStrongRule(
  message = '密码需至少 6 位，包含字母和数字'
) {
  const strong = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d\W_]{6,}$/
  return {
    validator: (_rule, value, callback) => {
      if (!value) return callback(new Error(message))
      if (strong.test(value)) return callback()
      callback(new Error(message))
    },
    trigger: ['blur'],
  }
}

export function requiredArray(message = '至少填写一项') {
  return {
    validator: (_rule, value, callback) => {
      if (Array.isArray(value) && value.length > 0) return callback()
      callback(new Error(message))
    },
    trigger: ['change'],
  }
}

export function numberRange(min, max, message) {
  return {
    validator: (_rule, value, callback) => {
      if (value === undefined || value === null || value === '')
        return callback()
      const n = Number(value)
      if (Number.isNaN(n)) return callback(new Error('请输入数字'))
      if (n < min || n > max)
        return callback(new Error(message || `取值范围 ${min} ~ ${max}`))
      callback()
    },
    trigger: ['blur', 'change'],
  }
}
