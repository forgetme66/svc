<template>
  <div class="common-layout-container">
    <el-container>
      <!-- Header -->
      <el-header class="header">
        <div class="header-left">
          <h1>毕业设计指导网站</h1>
        </div>
        <div class="header-right">
          <el-dropdown>
            <span class="user-info">
              {{ authStore.user?.username }}
              <el-icon class="icon"><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="goToProfile">个人信息</el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-container>
        <!-- 侧边栏 -->
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
            <el-menu-item index="/teacher-ratings-display" route="/teacher-ratings-display">
              <template #title>评价浏览</template>
            </el-menu-item>
            <el-menu-item index="/questions" route="/questions">
              <template #title>问题中心</template>
            </el-menu-item>
          </el-menu>
        </el-aside>

        <!-- 主体内容 -->
        <el-main class="main">
          <div class="teacher-question-dashboard">
            <el-container style="height: 100%;">
              <!-- 左侧学生问题列表 -->
              <el-aside width="300px" class="student-list-aside">
                <el-header class="aside-header">
                  <h3>学生问题列表</h3>
                </el-header>
                <el-scrollbar>
                  <div v-if="studentGroups.length === 0" class="empty-list">
                    <el-empty description="暂无学生提问"></el-empty>
                  </div>
                  <el-menu v-else>
                    <el-sub-menu v-for="group in studentGroups" :key="group.student_id" :index="String(group.student_id)">
                      <template #title>
                        <span>{{ group.student_name }}</span>
                      </template>
                      <el-menu-item 
                        v-for="question in group.questions" 
                        :key="question.id" 
                        :index="`${group.student_id}-${question.id}`"
                        @click="handleSelectQuestion(question)"
                      >
                        {{ question.title }}
                        <el-tag :type="question.status === '待回答' ? 'warning' : (question.status === '已回复' ? 'success' : 'info')" size="small" style="margin-left: 8px;">
                          {{ question.status }}
                        </el-tag>
                      </el-menu-item>
                    </el-sub-menu>
                  </el-menu>
                </el-scrollbar>
              </el-aside>

              <!-- 右侧对话界面 -->
              <el-container class="chat-container">
                <template v-if="selectedQuestion">
                  <!-- 对话框头部 -->
                  <el-header class="chat-header">
                    <div class="header-content">
                      <h4>{{ selectedQuestion.title }}</h4>
                      <div class="header-meta">
                        <span>学生: {{ selectedQuestion.author.username }}</span>
                        <el-tag :type="selectedQuestion.status === '待回答' ? 'warning' : (selectedQuestion.status === '已回复' ? 'success' : 'info')" size="small">
                          {{ selectedQuestion.status }}
                        </el-tag>
                      </div>
                    </div>
                  </el-header>

                  <!-- 消息区域 -->
                  <el-main class="chat-body">
                    <el-scrollbar ref="chatScrollbar">
                      <div class="messages-container">
                        <div
                          v-for="message in selectedQuestion.messages"
                          :key="message.id"
                          class="message-item"
                          :class="{ 'my-message': message.sender_id === authStore.user.id, 'other-message': message.sender_id !== authStore.user.id }"
                        >
                          <el-avatar class="avatar">{{ message.sender_name ? message.sender_name.charAt(0) : '?' }}</el-avatar>
                          <div class="message-content">
                            <div class="sender-info">{{ message.sender_name }} · {{ formatDate(message.created_at) }}</div>
                            <div class="text-bubble">{{ message.content }}</div>
                          </div>
                        </div>
                      </div>
                    </el-scrollbar>
                  </el-main>

                  <!-- 输入区域 -->
                  <el-footer class="chat-footer">
                    <el-input
                      v-model="newMessage"
                      type="textarea"
                      :rows="3"
                      placeholder="输入回复... (Enter 发送, Shift + Enter 换行)"
                      :disabled="selectedQuestion.status === 'closed'"
                      @keydown.enter.prevent="handleSendMessage"
                    />
                    <el-button
                      type="primary"
                      @click="handleSendMessage"
                      :disabled="!newMessage.trim() || selectedQuestion.status === 'closed'"
                      class="send-button"
                    >
                      发送
                    </el-button>
                  </el-footer>
                </template>
                <template v-else>
                  <div class="empty-chat">
                    <el-empty description="请从左侧选择一个问题开始对话"></el-empty>
                  </div>
                </template>
              </el-container>
            </el-container>
          </div>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { authAPI } from '@/api/auth';
import { getTeacherDashboardQuestions, getQuestionDetails, createMessage } from '@/api/questions';
import { ElMessage } from 'element-plus';
import { ArrowDown } from '@element-plus/icons-vue';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const activeMenu = ref(route.path);
const studentGroups = ref([]);
const selectedQuestion = ref(null);
const newMessage = ref('');
const chatScrollbar = ref(null);
// 检查用户身份
const isStudent = computed(() => authStore.user?.user_type === 'student');
const isAdmin = computed(() => authStore.user?.user_type === 'admin');
const isTeacher = computed(() => authStore.user?.user_type === 'teacher');

const formatDate = (dateString) => {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' });
};

const scrollToBottom = () => {
  nextTick(() => {
    const scrollbar = chatScrollbar.value;
    if (scrollbar) {
      // 尝试适配不同版本的 Element Plus
      const wrap = scrollbar.wrapRef || scrollbar.wrap$ || scrollbar.$refs.wrap;
      if (wrap) {
        scrollbar.setScrollTop(wrap.scrollHeight);
      }
    }
  });
};

const fetchTeacherQuestions = async () => {
  try {
    const response = await getTeacherDashboardQuestions();
    if (response.data.code === 200) {
      studentGroups.value = response.data.data;
    } else {
      ElMessage.error('获取问题列表失败: ' + response.data.message);
    }
  } catch (error) {
    console.error('获取教师问题仪表盘数据失败:', error);
    ElMessage.error('无法连接到服务器以获取问题列表');
  }
};

onMounted(() => {
  fetchTeacherQuestions();
});

const removeQuestionFromList = (questionId) => {
  for (const group of studentGroups.value) {
    const index = group.questions.findIndex(q => q.id === questionId);
    if (index !== -1) {
      group.questions.splice(index, 1);
      // 如果该学生下没有问题了，可能需要移除该学生组？或者保留空组？这里选择保留空组但内容为空
      break;
    }
  }
};

const handleSelectQuestion = async (question) => {
  if (selectedQuestion.value?.id === question.id) return;
  try {
    const response = await getQuestionDetails(question.id);
    if (response.data.code === 200) {
      selectedQuestion.value = response.data.data;
      scrollToBottom();
    } else {
      ElMessage.error('获取问题详情失败: ' + response.data.message);
    }
  } catch (error) {
    console.error('获取问题详情失败:', error);
    if (error.response && error.response.status === 404) {
      ElMessage.warning('该问题已被学生删除');
      removeQuestionFromList(question.id);
      selectedQuestion.value = null;
    } else {
      ElMessage.error('无法加载问题详情');
    }
  }
};

const handleSendMessage = async (event) => {
  if (event.shiftKey) return; // 按下 Shift+Enter 时不发送，允许换行
  if (!newMessage.value.trim()) return;

  const content = newMessage.value;
  const questionId = selectedQuestion.value.id;

  // 乐观更新 UI
  const tempMessage = {
    id: Date.now(), // 临时 ID
    content,
    created_at: new Date().toISOString(),
    sender_id: authStore.user.id,
    sender_name: authStore.user.username,
    isSending: true, // 发送中状态
  };
  selectedQuestion.value.messages.push(tempMessage);
  newMessage.value = '';
  scrollToBottom();

  try {
    const response = await createMessage(questionId, { content });
    if (response.data.code === 201) {
      // 消息发送成功，用后端返回的真实数据替换临时消息
      const realMessage = response.data.data;
      const index = selectedQuestion.value.messages.findIndex(m => m.id === tempMessage.id);
      if (index !== -1) {
        selectedQuestion.value.messages.splice(index, 1, realMessage);
      }
      
      // 更新状态为 "已回复"
      selectedQuestion.value.status = "已回复";
      
      // 同时更新左侧列表中的状态
      for (const group of studentGroups.value) {
        const q = group.questions.find(q => q.id === questionId);
        if (q) {
          q.status = "已回复";
          break;
        }
      }

    } else {
      throw new Error(response.data.message);
    }
  } catch (error) {
    console.error('消息发送失败:', error);
    
    // 发送失败，从 UI 中移除临时消息
    const index = selectedQuestion.value.messages.findIndex(m => m.id === tempMessage.id);
    if (index !== -1) {
      selectedQuestion.value.messages.splice(index, 1);
    }

    if (error.response && error.response.status === 404) {
      ElMessage.warning('发送失败：该问题已被学生删除');
      removeQuestionFromList(questionId);
      selectedQuestion.value = null;
    } else {
      ElMessage.error('消息发送失败，请重试');
      // 恢复用户输入
      newMessage.value = content;
    }
  }
};

const goToProfile = () => {
  router.push('/profile');
};

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

</script>

<style scoped lang="scss">
.common-layout-container {
  height: 100vh;
  display: flex;
  flex-direction: column;

  :deep(.el-container) {
    height: 100%;
  }

  .header {
    background-color: #667eea;
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;

    .header-left h1 {
      margin: 0;
      font-size: 24px;
    }

    .header-right {
      .user-info {
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 8px;
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
    overflow-y: auto;
  }
}

.teacher-question-dashboard {
  height: 100%;
}

.student-list-aside {
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  background-color: white;
}

.aside-header {
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #e0e0e0;
  height: 60px;
}

.chat-main {
  padding: 0;
  display: flex;
  flex-direction: column;
}

.empty-chat {
  flex-grow: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  border-bottom: 1px solid #e0e0e0;
  height: 60px;
  flex-shrink: 0;

  .header-content h4 {
    margin: 0;
    font-weight: 600;
  }

  .header-meta {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 12px;
    color: #888;
  }
}

.chat-body {
  flex-grow: 1;
  padding: 10px 20px;
  background-color: #f5f7fa;
  overflow-y: hidden;
}

.messages-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message-item {
  display: flex;
  gap: 12px;
  max-width: 70%;

  .message-content {
    display: flex;
    flex-direction: column;
  }

  .sender-info {
    font-size: 12px;
    color: #666;
    margin-bottom: 4px;
  }

  .text-bubble {
    padding: 10px 15px;
    border-radius: 18px;
    background-color: white;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    word-break: break-word;
    line-height: 1.6;
  }
}

.my-message {
  align-self: flex-end;
  flex-direction: row-reverse;

  .text-bubble {
    background-color: #cce5ff;
  }
  
  .sender-info {
    text-align: right;
  }
}

.other-message {
  align-self: flex-start;
}

.chat-footer {
  padding: 10px 20px;
  border-top: 1px solid #e0e0e0;
  background-color: #ffffff;
  display: flex;
  align-items: flex-end;
  gap: 10px;
  height: auto;

  .send-button {
    height: 100%;
    align-self: flex-end;
  }
}
</style>
