import React from "react";
import axios from 'axios'
import { message } from 'antd'
import { useAuthStore } from '../store/authStore'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    // 检查是否是文件下载请求
    const contentType = response.headers?.['content-type'] || '';
    const contentDisposition = response.headers?.['content-disposition'] || '';
    const isFileDownload = contentType.includes('application/') &&
                        (contentDisposition.includes('attachment') ||
                         contentType.includes('application/octet-stream') ||
                         contentType.includes('pdf') ||
                         contentType.includes('docx') ||
                         contentType.includes('xlsx'));

    if (isFileDownload) {
      // 文件下载请求直接返回，不进行错误处理
      return response;
    }

    return response
  },
  (error) => {
    // 对于文件下载请求的特殊处理
    if (error.response?.config?.responseType === 'blob') {
      // 文件下载错误也不显示通用错误消息
      return Promise.reject(error);
    }

    if (error.response) {
      switch (error.response.status) {
        case 401:
          message.error('未授权，请重新登录')
          useAuthStore.getState().logout()
          window.location.href = '/login'
          break
        case 403:
          message.error('无权限访问')
          break
        case 404:
          message.error('请求的资源不存在')
          break
        case 500:
          message.error('服务器错误')
          break
        default:
          message.error(error.response.data.detail || '请求失败')
      }
    } else {
      message.error('网络错误，请检查网络连接')
    }
    return Promise.reject(error)
  }
)

export default api
