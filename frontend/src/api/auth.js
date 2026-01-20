import api from './index'

export const authAPI = {
  register(data) {
    return api.post('/auth/register', data)
  },
  login(username, password) {
    return api.post('/auth/login', { username, password })
  },
  refresh() {
    return api.post('/auth/refresh')
  },
  forgotPassword(email) {
    return api.post('/auth/forgot-password', { email })
  },
  resetPassword(token, password) {
    return api.post('/auth/reset-password', { token, password })
  },
  getProfile() {
    return api.get('/auth/profile')
  },
  updateProfile(data) {
    return api.put('/auth/profile', data)
  },
  changePassword(oldPassword, newPassword, confirmPassword) {
    return api.post('/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
      confirm_password: confirmPassword
    })
  },
  logout() {
    return api.post('/auth/logout')
  }
}

export default api
