import api from './index';

/**
 * 获取问题列表（对话线程）
 * @param {object} params - 查询参数，例如 { page, per_page, search }
 * @returns {Promise}
 */
export const getQuestions = (params) => {
  return api.get('/questions', { params });
};

/**
 * 获取单个问题（对话线程）的详细信息，包括所有消息
 * @param {number} questionId - 问题ID
 * @returns {Promise}
 */
export const getQuestionDetails = (questionId) => {
  return api.get(`/questions/${questionId}`);
};

/**
 * 创建一个新问题（对话线程）
 * @param {object} data - 问题数据，例如 { title: '问题标题', content: '这是第一条消息' }
 * @returns {Promise}
 */
export const createQuestion = (data) => {
  return api.post('/questions', data);
};

/**
 * 在指定问题（对话线程）下发表新消息
 * @param {number} questionId - 问题ID
 * @param {object} data - 消息数据，例如 { content: '这是追问或回复' }
 * @returns {Promise}
 */
export const createMessage = (questionId, data) => {
  return api.post(`/questions/${questionId}/messages`, data);
};

/**
 * 获取教师仪表盘的问题数据（按学生分组）
 * @returns {Promise}
 */
export const getTeacherDashboardQuestions = () => {
  return api.get('/questions/teacher-dashboard');
};

/**
 * 删除一个问题（对话线程）
 * @param {number} questionId - 问题ID
 * @returns {Promise}
 */
export const deleteQuestion = (questionId) => {
  return api.delete(`/questions/${questionId}`);
};
