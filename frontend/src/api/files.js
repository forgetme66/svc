import api from './index'

export const filesAPI = {
  // 上传文件
  uploadFile(file, description = '', isPublic = false) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('description', description)
    formData.append('is_public', isPublic)
    
    return api.post('/files/upload', formData)
  },

  // 获取文件列表
  getFiles(page = 1, perPage = 10) {
    return api.get('/files/list', {
      params: { page, per_page: perPage }
    })
  },

  // 下载文件
  downloadFile(fileId) {
    return api.get(`/files/${fileId}/download`, {
      responseType: 'blob'
    })
  },

  // 获取文件信息
  getFileInfo(fileId) {
    return api.get(`/files/${fileId}`)
  },

  // 更新文件信息
  updateFile(fileId, data) {
    return api.put(`/files/${fileId}`, data)
  },

  // 删除文件
  deleteFile(fileId) {
    return api.delete(`/files/${fileId}`)
  },

  // 搜索文件
  searchFiles(keyword = '', fileType = '', page = 1, perPage = 10) {
    return api.get('/files/search', {
      params: {
        keyword,
        file_type: fileType,
        page,
        per_page: perPage
      }
    })
  }
}

export default filesAPI
