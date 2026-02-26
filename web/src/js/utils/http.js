// * +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
// * Copyright 2023 The Geek-AI Authors. All rights reserved.
// * Use of this source code is governed by a Apache-2.0 license
// * that can be found in the LICENSE file.
// * @Author yangjian102621@163.com
// * +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import axios from 'axios'
import { ElMessage } from 'element-plus'
import {
  getAdminToken,
  getUserToken,
  removeAdminToken,
  removeUserToken,
} from '@/js/cache/session'

axios.defaults.timeout = 180000
axios.defaults.withCredentials = true
// HTTP拦截器
axios.interceptors.request.use(
  (config) => {
    // set token
    const userToken = getUserToken()
    const adminToken = getAdminToken()
    const isAdminUrl =
      typeof config.url === 'string' && config.url.indexOf('/api/admin') !== -1

    // 后端 HTTPBearer 只读取 Authorization，admin 接口也需把 token 放在 Authorization
    const adminTokenFormatted = adminToken
      ? adminToken.startsWith('Bearer ')
        ? adminToken
        : `Bearer ${adminToken}`
      : ''
    const userTokenFormatted = userToken
      ? userToken.startsWith('Bearer ')
        ? userToken
        : `Bearer ${userToken}`
      : ''

    if (isAdminUrl && adminTokenFormatted) {
      config.headers['Authorization'] = adminTokenFormatted
    } else if (userTokenFormatted) {
      config.headers['Authorization'] = userTokenFormatted
    }
    if (adminTokenFormatted) {
      config.headers['Admin-Authorization'] = adminTokenFormatted
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)
axios.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // 如果没有 response，可能是网络错误，直接返回
    if (!error.response) {
      return Promise.reject(error)
    }

    if (error.response.status === 401) {
      if (error.response.request.responseURL.indexOf('/api/admin') !== -1) {
        removeAdminToken()
      } else {
        removeUserToken()
      }
      error.response.data.message = '请先登录'
      return Promise.reject(error.response.data)
    }
    if (error.response.status === 400) {
      return Promise.reject(new Error(error.response.data.detail))
    } else if (error.response.status === 402) {
      // 402 Payment Required - 积分余额不足
      const errorMessage =
        error.response.data?.detail ||
        error.response.data?.message ||
        '积分余额不足'
      return Promise.reject(new Error(errorMessage))
    } else if (error.response.status === 429) {
      return Promise.reject(new Error('请求过于频繁，请稍后重试'))
    } else {
      return Promise.reject(error)
    }
  },
)

// send a http get request
export function httpGet(url, params = {}) {
  return new Promise((resolve, reject) => {
    axios
      .get(url, {
        params: params,
      })
      .then((response) => {
        resolve(response.data)
      })
      .catch((err) => {
        reject(err)
      })
  })
}

// send a http post request
export function httpPost(url, data = {}, options = {}) {
  return new Promise((resolve, reject) => {
    axios
      .post(url, data, options)
      .then((response) => {
        resolve(response.data)
      })
      .catch((err) => {
        reject(err)
      })
  })
}

export function httpDownload(url) {
  return new Promise((resolve, reject) => {
    axios({
      method: 'GET',
      url: url,
      responseType: 'blob', // 将响应类型设置为 `blob`
    })
      .then((response) => {
        resolve(response)
      })
      .catch((err) => {
        reject(err)
      })
  })
}

export function httpPostDownload(url, data) {
  return new Promise((resolve, reject) => {
    axios({
      method: 'POST',
      url: url,
      data: data,
      responseType: 'blob', // 将响应类型设置为 `blob`
    })
      .then((response) => {
        resolve(response)
      })
      .catch((err) => {
        reject(err)
      })
  })
}

export function httpDelete(url) {
  return new Promise((resolve, reject) => {
    axios({
      method: 'DELETE',
      url: url,
    })
      .then((response) => {
        resolve(response)
      })
      .catch((err) => {
        reject(err)
      })
  })
}

export function httpPatch(url, data = {}, options = {}) {
  return new Promise((resolve, reject) => {
    axios({
      method: 'PATCH',
      url: url,
      data: data,
      ...options,
    })
      .then((response) => {
        resolve(response.data)
      })
      .catch((err) => {
        reject(err)
      })
  })
}
