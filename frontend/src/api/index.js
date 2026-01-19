import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

// 动态生成API基础URL
const getAPIBaseURL = () => {
  // 开发环境使用相对路径（会被Vite代理）
  if (import.meta.env.DEV) {
    return '/api'
  }
  
  // 生产环境和其他情况，使用完整URL
  const protocol = window.location.protocol
  const hostname = window.location.hostname
  const port = 5000
  
  return `${protocol}//${hostname}:${port}/api`
}

const API_BASE_URL = getAPIBaseURL()

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    const authStore = useAuthStore()
    if (authStore.accessToken) {
      config.headers.Authorization = `Bearer ${authStore.accessToken}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      const authStore = useAuthStore()
      authStore.clearAuth()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
