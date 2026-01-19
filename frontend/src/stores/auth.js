import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')
  
  function setUser(userData) {
    user.value = userData
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
  }
  
  function isLoggedIn() {
    return !!accessToken.value
  }
  
  return {
    user,
    accessToken,
    refreshToken,
    setUser,
    setTokens,
    clearAuth,
    isLoggedIn
  }
})
