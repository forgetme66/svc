import api from './index'

export const teacherAPI = {
  // 获取管理的学生列表
  getStudents(page = 1, perPage = 10, keyword = '') {
    return api.get('/teacher/students', {
      params: { page, per_page: perPage, keyword }
    })
  },

  // 添加学生
  addStudent(studentId) {
    return api.post('/teacher/students', { student_id: studentId })
  },

  // 删除学生
  removeStudent(studentId) {
    return api.delete(`/teacher/students/${studentId}`)
  },

  // 获取可以添加的学生列表
  getAvailableStudents(page = 1, perPage = 10, keyword = '') {
    return api.get('/teacher/available-students', {
      params: { page, per_page: perPage, keyword }
    })
  },

  // 获取学生详细信息
  getStudentInfo(studentId) {
    return api.get(`/teacher/student-info/${studentId}`)
  },

  // ==================== 管理员接口 ====================
  
  // 管理员获取所有用户
  adminGetUsers(page = 1, perPage = 10, keyword = '', userType = '') {
    return api.get('/teacher/admin/users', {
      params: { page, per_page: perPage, keyword, user_type: userType }
    })
  },

  // 管理员获取所有教师及其学生
  adminGetTeacherStudents() {
    return api.get('/teacher/admin/teacher-students')
  },

  // 管理员创建用户
  adminCreateUser(payload) {
    return api.post('/teacher/admin/users', payload)
  },

  // 管理员更新用户
  adminUpdateUser(userId, payload) {
    return api.put(`/teacher/admin/users/${userId}`, payload)
  },

  // 管理员删除用户
  adminDeleteUser(userId) {
    return api.delete(`/teacher/admin/users/${userId}`)
  },

  // ==================== 学生文档管理接口 ====================

  // 获取学生上交的文档列表
  getStudentDocuments(page = 1, perPage = 10, studentId = null, documentType = '', submissionStage = '') {
    return api.get('/teacher/student-documents', {
      params: { page, per_page: perPage, student_id: studentId, document_type: documentType, submission_stage: submissionStage }
    })
  },

  // 添加文档评价
  addDocumentFeedback(docId, feedback) {
    return api.put(`/teacher/student-documents/${docId}/feedback`, { feedback })
  },

  // 催交文档
  remindStudentSubmission(docId) {
    return api.post(`/teacher/student-documents/${docId}/remind`)
  },

  // 下载学生文档
  downloadStudentDocument(docId) {
    return api.get(`/teacher/student-documents/${docId}/download`, {
      responseType: 'blob'
    })
  },

  // ==================== 消息接口 ====================

  // 发送消息（支持全体公告或指定用户）
  sendMessage(payload) {
    return api.post('/teacher/messages/send', payload)
  },

  // ==================== 教师评价接口 ====================

  // 学生获取自己的教师列表
  getMyTeachers() {
    return api.get('/teacher/my-teachers')
  },

  // 学生提交对教师的评价
  submitTeacherReview(teacherId, rating, comment) {
    return api.post('/teacher/reviews', {
      teacher_id: teacherId,
      rating: rating,
      comment: comment
    })
  },

  // 教师查看自己收到的评价汇总
  getMyReviews() {
    return api.get('/teacher/reviews/for-me')
  },

  // 学生检查对某教师的评价状态
  checkReviewStatus(teacherId) {
    return api.get('/teacher/reviews/check-status', {
      params: { teacher_id: teacherId }
    })
  },

  // 获取所有教师的评价统计（公开展示）
  getAllTeachersRatings() {
    return api.get('/teacher/reviews/all-teachers')
  }

}

