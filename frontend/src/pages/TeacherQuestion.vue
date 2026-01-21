<template>
  <div class="common-layout">
    <el-container class="container">
      <el-header class="header">
        <div class="header-left">
          <h1>毕业设计指导网站</h1>
        </div>
        <div class="header-right">
          <el-tooltip content="消息箱" placement="bottom">
            <el-badge :value="unreadCount > 0 ? unreadCount : ''" class="header-icon" @click="goToInbox">
              <el-icon class="icon-button"><Notification /></el-icon>
            </el-badge>
          </el-tooltip>
          <el-dropdown>
            <el-icon class="user-icon"><User /></el-icon>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>{{ authStore.user?.username }}</el-dropdown-item>
                <el-dropdown-item divided @click="goToProfile">个人信息</el-dropdown-item>
                <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-container>
        <el-aside width="200px" class="aside">
          <el-menu router :default-active="activeMenu">
            <el-menu-item index="/dashboard" route="/dashboard">
              <template #title>首页</template>
            </el-menu-item>
            <el-menu-item v-if="isTeacher" index="/teacher-management" route="/teacher-management">
              <template #title>学生管理</template>
            </el-menu-item>
            <el-menu-item v-if="isTeacher" index="/student-documents" route="/student-documents">
              <template #title>毕设评阅</template>
            </el-menu-item>
            <el-menu-item v-if="isTeacher" index="/review-statistics" route="/review-statistics">
              <template #title>评价统计</template>
            </el-menu-item>
            <el-menu-item v-if="isAdmin || isStudent" index="/files" route="/files">
              <template #title>文件管理</template>
            </el-menu-item>
            <el-menu-item v-if="isAdmin" index="/admin-management" route="/admin-management">
              <template #title>用户管理</template>
            </el-menu-item>
            <el-menu-item v-if="isStudent" index="/teacher-ratings-display" route="/teacher-ratings-display">
              <template #title>教师评价</template>
            </el-menu-item>
            <el-menu-item v-if="isAdmin || isStudent" index="/teacher-ratings-display" route="/teacher-ratings-display">
              <template #title>评价浏览</template>
            </el-menu-item>
            <el-menu-item index="/questions" route="/questions">
              <template #title>问题中心</template>
            </el-menu-item>
          </el-menu>
        </el-aside>

        <el-main class="main">
          <div class="question-chat-layout">
            <!-- 左侧问题列表 -->
            <div class="question-list-panel">
              <div class="list-header">
                <h2>问题列表</h2>
                <el-button v-if="!isTeacher" type="primary" @click="newQuestionDialogVisible = true" :icon="Plus">
                  发起提问
                </el-button>
              </div>
              <el-scrollbar class="list-scrollbar">
                <div v-if="questions.length === 0" class="empty-list">
                  <el-empty description="暂无问题" />
                </div>
                <ul v-else class="question-list">
                  <li
                    v-for="q in questions"
                    :key="q.id"
                    class="question-item"
                    :class="{ active: selectedQuestion && selectedQuestion.id === q.id }"
                    @click="selectQuestion(q)"
                  >
                    <el-icon v-if="!isTeacher" class="delete-icon" @click.stop="confirmDeleteQuestion(q.id)">
                      <Close />
                    </el-icon>
                    <div class="q-item-title">{{ q.title }}</div>
                    <div class="q-item-info">
                      <span v-if="isTeacher" class="q-item-user">{{ q.user_name }}</span>
                      <span class="q-item-time">{{ formatDate(q.created_at) }}</span>
                    </div>
                    <el-tag :type="getStatusTagType(q.status)" size="small" class="q-item-status">
                      {{ q.status }}
                    </el-tag>
                  </li>
                </ul>
              </el-scrollbar>
            </div>

            <!-- 右侧聊天窗口 -->
            <div class="chat-panel">
              <template v-if="selectedQuestion">
                <div class="chat-header">
                  <h3>{{ selectedQuestion.title }}</h3>
                  <el-tag :type="getStatusTagType(selectedQuestion.status)" size="small">
                    {{ selectedQuestion.status }}
                  </el-tag>
                </div>
                <el-scrollbar ref="chatScrollbar" class="chat-body">
                  <div class="messages-container">
                    <div
                      v-for="message in selectedQuestion.messages"
                      :key="message.id"
                      class="message-item"
                      :class="{ 'my-message': message.sender_id === authStore.user.id, 'other-message': message.sender_id !== authStore.user.id }"
                    >
                      <el-avatar class="avatar">{{ message.sender_name ? message.sender_name.charAt(0) : '?' }}</el-avatar>
                      <div class="message-content">
                        <div class="sender-info">{{ message.sender_name || '未知用户' }} · {{ formatDate(message.created_at) }}</div>
                        <div class="text-bubble">{{ message.content }}</div>
                      </div>
                    </div>
                  </div>
                </el-scrollbar>
                <div class="chat-footer">
                  <el-input
                    v-model="newMessage"
                    type="textarea"
                    :rows="3"
                    placeholder="输入消息..."
                    :disabled="selectedQuestion.status === 'closed'"
                    @keyup.enter.prevent="sendMessage"
                  />
                  <el-button
                    type="primary"
                    @click="sendMessage"
                    :disabled="!newMessage.trim() || selectedQuestion.status === 'closed'"
                    class="send-button"
                  >
                    发送
                  </el-button>
                </div>
              </template>
              <template v-else>
                <div class="empty-chat">
                  <el-empty description="请从左侧选择一个问题开始对话" />
                </div>
              </template>
            </div>
          </div>
        </el-main>
      </el-container>
    </el-container>

    <!-- 新建问题弹窗 -->
    <el-dialog v-model="newQuestionDialogVisible" title="发起新的提问" width="500px">
      <el-form :model="newQuestionForm" label-position="top">
        <el-form-item label="问题标题">
          <el-input v-model="newQuestionForm.title" placeholder="请输入问题的简要标题" />
        </el-form-item>
        <el-form-item label="问题内容">
          <el-input v-model="newQuestionForm.content" type="textarea" :rows="5" placeholder="请详细描述您的问题" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="newQuestionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitNewQuestion">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useAuthStore } from '@/stores/auth';
import { authAPI } from '@/api/auth';
import { getQuestions, createQuestion, getQuestionDetails, createMessage, deleteQuestion as deleteQuestionAPI } from '@/api/questions';
import { Notification, User, Search, Plus, Close } from '@element-plus/icons-vue'

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const isTeacher = computed(() => authStore.user?.user_type === 'teacher');
const activeMenu = ref(route.path);

const questions = ref([]);
const selectedQuestion = ref(null);
const newMessage = ref('');
const chatScrollbar = ref(null);

const newQuestionDialogVisible = ref(false);
const newQuestionForm = ref({
  title: '',
  content: '',
});

// 检查用户身份
const isStudent = computed(() => authStore.user?.user_type === 'student');
const isAdmin = computed(() => authStore.user?.user_type === 'admin');
const fetchQuestions = async () => {
  try {
    const response = await getQuestions();
    questions.value = response.data.data.questions;
  } catch (error) {
    console.error('获取问题列表失败:', error);
    ElMessage.error('无法加载问题列表');
  }
};

const selectQuestion = async (question) => {
  if (selectedQuestion.value?.id === question.id) return;
  try {
    console.log(`Fetching details for question ID: ${question.id}`);
    const response = await getQuestionDetails(question.id);
    console.log('Question details received:', response);

    const data = response.data?.data;
    if (!data) {
      throw new Error('返回的数据为空');
    }

    // 确保 messages 是一个数组
    if (!Array.isArray(data.messages)) {
      console.warn('Warning: messages is not an array, initializing to empty array.');
      data.messages = [];
    }

    // 预处理消息，防止渲染时崩溃
    data.messages = data.messages.map(msg => ({
      ...msg,
      sender_name: msg.sender_name || '未知用户',
      content: msg.content || '',
      created_at: msg.created_at || new Date().toISOString()
    }));

    selectedQuestion.value = data;
    
    // 列表状态更新：将当前选中的问题状态更新为接口返回的最新状态（通常是“已回复”，因为如果是待查看状态，点进来后变成已回复）
    // 注意：如果是学生端，点进来查看后，后端会标记为已读，状态自然变成已回复
    if (data.status) {
        const listItem = questions.value.find(q => q.id === data.id);
        if (listItem) {
            listItem.status = data.status;
        }
    }
    
    scrollToBottom();
  } catch (error) {
    console.error('获取问题详情失败:', error);
    ElMessage.error('无法加载问题详情: ' + (error.message || '未知错误'));
  }
};

const sendMessage = async () => {
  console.log('--- Initiating sendMessage ---');
  if (!newMessage.value.trim() || !selectedQuestion.value) {
    console.warn('Message is empty or no question is selected.');
    return;
  }

  const tempMessageId = Date.now(); // 创建一个临时的唯一ID
  const payload = {
    content: newMessage.value,
  };

  // 立即将消息添加到UI，但标记为“发送中”状态
  const optimisticMessage = {
    id: tempMessageId,
    content: payload.content,
    sender_id: authStore.user.id,
    sender_name: authStore.user.username,
    created_at: new Date().toISOString(),
    sending: true, // 临时状态
  };
  selectedQuestion.value.messages.push(optimisticMessage);
  const messageIndex = selectedQuestion.value.messages.length - 1;

  const originalMessage = newMessage.value;
  newMessage.value = '';
  scrollToBottom();

  try {
    console.log(`Sending message for question ID: ${selectedQuestion.value.id}`, payload);
    const response = await createMessage(selectedQuestion.value.id, payload);
    console.log('API response received:', response);

    if (!response.data?.data) {
      throw new Error('服务器返回的响应数据格式不正确');
    }

    // 用服务器返回的真实消息替换临时消息
    selectedQuestion.value.messages[messageIndex] = response.data.data;
    console.log('Message state updated with server data.');

    // 自动更新状态为 "等待回答"
    if (selectedQuestion.value) {
      selectedQuestion.value.status = '等待回答';
      // 更新左侧列表状态
      const listItem = questions.value.find(q => q.id === selectedQuestion.value.id);
      if (listItem) {
        listItem.status = '等待回答';
      }
    }

  } catch (error) {
    console.error('发送消息失败 (API Error):', error.response?.data || error.message);
    ElMessage.error('发送消息失败，消息已撤回');

    // 发送失败，从UI中移除或标记为失败
    selectedQuestion.value.messages.splice(messageIndex, 1);
    newMessage.value = originalMessage; // 恢复用户输入
  } finally {
    scrollToBottom();
  }
};

const submitNewQuestion = async () => {
  if (!newQuestionForm.value.title.trim() || !newQuestionForm.value.content.trim()) {
    ElMessage.warning('请输入标题和内容');
    return;
  }
  try {
    const response = await createQuestion(newQuestionForm.value);
    newQuestionDialogVisible.value = false;
    newQuestionForm.value = { title: '', content: '' };
    ElMessage.success('问题已提交');
    await fetchQuestions();
    // 自动选中新创建的问题
    selectQuestion(response.data.data);
  } catch (error) {
    console.error('创建问题失败:', error);
    ElMessage.error('创建问题失败');
  }
};

const confirmDeleteQuestion = (questionId) => {
  ElMessageBox.confirm(
    '确定要删除这个问题及其所有对话吗？此操作不可撤销。',
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    deleteQuestion(questionId);
  }).catch(() => {
    // 用户取消了删除
  });
};

const deleteQuestion = async (questionId) => {
  try {
    await deleteQuestionAPI(questionId);
    ElMessage.success('问题已删除');
    
    // 如果删除的是当前选中的问题，则清空右侧
    if (selectedQuestion.value && selectedQuestion.value.id === questionId) {
      selectedQuestion.value = null;
    }
    
    // 重新加载问题列表
    await fetchQuestions();

  } catch (error) {
    console.error('删除问题失败:', error);
    ElMessage.error('删除问题失败');
  }
};

const getStatusTagType = (status) => {
  if (isTeacher.value) {
    switch (status) {
      case '待回答': return 'warning';
      case '已回复': return 'success';
      default: return 'info';
    }
  } else {
    switch (status) {
      case '等待回答': return 'primary';
      case '待查看': return 'warning';
      case '已回复': return 'success';
      default: return 'info';
    }
  }
};

const scrollToBottom = () => {
  nextTick(() => {
    chatScrollbar.value?.wrap$?.scrollTo({
      top: chatScrollbar.value.wrap$.scrollHeight,
      behavior: 'smooth',
    });
  });
};

const formatDate = (dateString) => {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', { hour12: false });
};

const goToProfile = () => router.push('/profile');

const handleLogout = async () => {
  try {
    await authAPI.logout();
  } catch (error) {
    console.error('登出请求失败:', error);
  } finally {
    authStore.clearAuth();
    ElMessage.success('已退出登录');
    router.push('/login');
  }
};

onMounted(() => {
  fetchQuestions();
});
</script>

<style scoped>
.common-layout, .container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}
.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);

    .header-left h1 {
      margin: 0;
      font-size: 24px;
      font-weight: bold;
    }

    .header-right {
      display: flex;
      align-items: center;
      gap: 20px;

      .header-icon {
        cursor: pointer;
        font-size: 20px;
        transition: all 0.3s;

        .icon-button {
          color: white;
          transition: transform 0.3s;

          &:hover {
            transform: scale(1.2);
          }
        }

        :deep(.el-badge__content) {
          background-color: #f56c6c;
        }
      }

      .user-icon {
        cursor: pointer;
        font-size: 24px;
        color: white;
        transition: transform 0.3s;

        &:hover {
          transform: scale(1.1);
        }
      }
    }
  }
.aside {
  background-color: #f5f5f5;
  border-right: 1px solid #e0e0e0;
}
.main {
  padding: 0;
  background-color: #fafafa;
  overflow: hidden;
}
.question-chat-layout {
  display: flex;
  height: 100%;
}
.question-list-panel {
  width: 320px;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  background-color: #fff;
}
.list-header {
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e0e0e0;
  flex-shrink: 0;
}
.list-header h2 {
  margin: 0;
  font-size: 18px;
}
.list-scrollbar {
  flex-grow: 1;
}
.empty-list {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}
.question-list {
  list-style: none;
  padding: 8px;
  margin: 0;
}
.question-item {
  padding: 12px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-bottom: 8px;
  position: relative;
}
.question-item:hover {
  background-color: #f5f5f5;
}
.question-item.active {
  background-color: #e8f0ff;
}
.question-item:hover .delete-icon {
  opacity: 1;
}

.delete-icon {
  position: absolute;
  top: 12px;
  left: 12px; /* 改为左边 */
  opacity: 0;
  transition: opacity 0.2s;
  cursor: pointer;
  color: #F56C6C;
  font-size: 16px;
}

.delete-icon:hover {
  color: #E13C3C;
}

.q-item-title {
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding-left: 20px; /* 为图标留出空间 */
}
.q-item-info {
  font-size: 12px;
  color: #888;
  display: flex;
  justify-content: space-between;
}
.q-item-status {
  position: absolute;
  top: 12px;
  right: 12px;
}
.chat-panel {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  background-color: #f9f9f9;
}
.chat-header {
  padding: 16px 24px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fff;
  flex-shrink: 0;
}
.chat-header h3 {
  margin: 0;
  font-size: 18px;
}
.chat-body {
  flex-grow: 1;
  padding: 24px;
}
.messages-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.message-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  max-width: 75%;
}

.avatar {
  flex-shrink: 0;
  margin-top: 4px; /* 微调头像位置 */
}

.message-content {
  display: flex;
  flex-direction: column;
}

.sender-info {
  font-size: 12px;
  color: #888;
  margin-bottom: 8px;
}

.text-bubble {
  padding: 10px 16px;
  border-radius: 18px;
  background-color: #fff;
  box-shadow: 0 2px 5px rgba(0,0,0,0.06);
  line-height: 1.6;
  word-break: break-word;
}

/* 我的消息 - 靠右 */
.my-message {
  align-self: flex-end;
  flex-direction: row-reverse; /* 关键：头像和内容反向 */
}

.my-message .message-content {
  align-items: flex-end;
}

.my-message .text-bubble {
  background-color: #7189f1; /* Element Plus 蓝色 */
  color: white;
}

/* 对方消息 - 靠左 */
.other-message {
  align-self: flex-start;
}

.chat-footer {
  padding: 16px 24px;
  border-top: 1px solid #e0e0e0;
  background-color: #fff;
  display: flex;
  align-items: flex-end;
  gap: 12px;
}
.send-button {
  flex-shrink: 0;
}
.empty-chat {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  text-align: center;
  color: #aaa;
}
</style>
