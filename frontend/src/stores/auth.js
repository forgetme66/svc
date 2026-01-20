import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')
  
  // 从 localStorage 恢复用户信息
  function restoreUser() {
    const userData = localStorage.getItem('user')
    if (userData) {
      try {
        user.value = JSON.parse(userData)
      } catch (e) {
        console.error('Failed to parse user data from localStorage', e)
      }
    }
  }
  
  function setUser(userData) {
    user.value = userData
    // 保存用户信息到 localStorage
    if (userData) {
      localStorage.setItem('user', JSON.stringify(userData))
    }
  }
  
  function setTokens(access, refresh) {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  }
  
  function clearAuth() {
    user.value = null
    accessToken.value = ''
    refreshToken.value = ''
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }
  
  function isLoggedIn() {
    return !!accessToken.value
  }
  
  // 初始化时恢复用户信息
  restoreUser()
  
  return {
    user,
    accessToken,
    refreshToken,
    setUser,
    setTokens,
    clearAuth,
    isLoggedIn,
    restoreUser
  }
})
