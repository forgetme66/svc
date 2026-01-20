import api from './index'

export const messagesAPI = {
  getMessages(page = 1, perPage = 10) {
    return api.get('/teacher/messages', { params: { page, per_page: perPage }})
  },

  getUnreadCount() {
    return api.get('/teacher/messages/unread-count')
  },

  markRead(messageId) {
    return api.put(`/teacher/messages/${messageId}/read`)
  },

  sendMessage(payload) {
    return api.post('/teacher/messages/send', payload)
  }
}
