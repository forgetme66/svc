<template>
  <div class="dashboard-container">
    <el-container>
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
            <el-menu-item v-if="!isTeacher" index="/files" route="/files">
              <template #title>文件管理</template>
            </el-menu-item>
            <el-menu-item v-if="isStudent" index="/review-teacher" route="/review-teacher">
              <template #title>教师评价</template>
            </el-menu-item>
            <el-menu-item v-if="isTeacher" index="/teacher-management" route="/teacher-management">
              <template #title>学生管理</template>
            </el-menu-item>
            <el-menu-item v-if="isTeacher" index="/student-documents" route="/student-documents">
              <template #title>毕设评阅</template>
            </el-menu-item>
            <el-menu-item v-if="isAdmin" index="/admin-management" route="/admin-management">
              <template #title>用户管理</template>
            </el-menu-item>
            <el-menu-item v-if="isTeacher" index="/review-statistics" route="/review-statistics">
              <template #title>评价统计</template>
            </el-menu-item>
            <el-menu-item index="/teacher-ratings-display" route="/teacher-ratings-display">
              <template #title>评价浏览</template>
            </el-menu-item>
            <el-menu-item index="/questions" route="/questions">
              <template #title>问题中心</template>
            </el-menu-item>
            
          </el-menu>
        </el-aside>

        <el-main class="main">
          <div class="welcome-card">
            <h2>欢迎回来</h2>
            <p>用户类型: <el-tag>{{ userTypeText }}</el-tag></p>
            <p>注册时间: {{ formatDate(authStore.user?.created_at) }}</p>
          </div>
        </el-main>
      </el-container>
    </el-container>

    <!-- 管理员公告弹窗 -->
    <el-dialog 
      v-model="showAnnouncementDialog"
      title="管理员公告"
      width="600px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      destroy-on-close
    >
      <div v-if="announcementList.length > 0" class="announcement-content">
        <div class="announcement-header">
          <span class="title">
            {{ announcementList[currentAnnouncementIndex].content.split('\n')[0] }}
          </span>
          <span class="page-info">
            {{ currentAnnouncementIndex + 1 }} / {{ announcementList.length }}
          </span>
        </div>
        
        <el-divider />
        
        <div class="announcement-body">
          <p class="time">
            发送于: {{ new Date(announcementList[currentAnnouncementIndex].created_at).toLocaleString('zh-CN') }}
          </p>
          <p class="content">
            {{ announcementList[currentAnnouncementIndex].content }}
          </p>
        </div>
      </div>

      <template #footer>
        <el-button @click="closeAnnouncementDialog">关闭</el-button>
        <el-button 
          type="primary" 
          @click="markCurrentAsRead"
          v-if="currentAnnouncementIndex < announcementList.length - 1"
        >
          下一条
        </el-button>
        <el-button 
          type="primary" 
          @click="closeAnnouncementDialog"
          v-else
        >
          完成
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { authAPI } from '@/api/auth'
import { messagesAPI } from '@/api/messages'
import { ArrowDown, Notification, User } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const activeMenu = ref('/dashboard')
const unreadCount = ref(0)

// 公告弹窗状态
const showAnnouncementDialog = ref(false)
const announcementList = ref([])
const currentAnnouncementIndex = ref(0)
const checkedAnnouncementIds = ref(new Set())

// 检查是否是教师
const isTeacher = computed(() => authStore.user?.user_type === 'teacher')

// 检查是否是管理员
const isAdmin = computed(() => authStore.user?.user_type === 'admin')

// 检查是否为学生
const isStudent = computed(() => authStore.user?.user_type === 'student')

const userTypeText = ref({
  'student': '学生',
  'teacher': '教师',
  'admin': '管理员'
}[authStore.user?.user_type] || '用户')

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 加载未读消息数
const loadUnreadCount = async () => {
  try {
    const response = await messagesAPI.getUnreadCount()
    if (response.data.code === 200) {
      unreadCount.value = response.data.data.unread
    }
  } catch (error) {
    console.error('Get unread count error:', error)
  }
}

const goToInbox = () => {
  router.push('/inbox')
}

const goToProfile = () => {
  router.push('/profile')
}

const handleLogout = async () => {
  try {
    await authAPI.logout()
  } catch (error) {
    console.error('登出请求失败:', error)
  } finally {
    authStore.clearAuth()
    ElMessage.success('已退出登录')
    router.push('/login')
  }
}

// 检查是否有新的管理员公告
const checkAdminAnnouncements = async () => {
  try {
    const response = await messagesAPI.getMessages(1, 100)
    if (response.data.code === 200) {
      const messages = response.data.data.messages || []
      // 只获取来自管理员且未读的公告
      const adminAnnouncements = messages.filter(
        msg => msg.sender_user_type === 'admin' && !msg.is_read
      )
      
      if (adminAnnouncements.length > 0) {
        announcementList.value = adminAnnouncements
        currentAnnouncementIndex.value = 0
        showAnnouncementDialog.value = true
      }
    }
  } catch (error) {
    console.error('Check announcements error:', error)
  }
}

// 标记当前公告为已读
const markCurrentAsRead = async () => {
  if (announcementList.value.length === 0) return
  
  const currentMsg = announcementList.value[currentAnnouncementIndex.value]
  try {
    await messagesAPI.markRead(currentMsg.message_id)
    checkedAnnouncementIds.value.add(currentMsg.message_id)
    
    // 如果还有其他未读公告，显示下一个
    const nextIndex = announcementList.value.findIndex(
      (msg, idx) => idx > currentAnnouncementIndex.value && !checkedAnnouncementIds.value.has(msg.message_id)
    )
    
    if (nextIndex !== -1) {
      currentAnnouncementIndex.value = nextIndex
    } else {
      // 没有更多公告，关闭弹窗
      showAnnouncementDialog.value = false
      await loadUnreadCount()
    }
  } catch (error) {
    console.error('Mark as read error:', error)
  }
}

// 关闭公告并标记所有已读
const closeAnnouncementDialog = async () => {
  const currentMsg = announcementList.value[currentAnnouncementIndex.value]
  if (currentMsg && !checkedAnnouncementIds.value.has(currentMsg.message_id)) {
    await markCurrentAsRead()
  } else {
    showAnnouncementDialog.value = false
    await loadUnreadCount()
  }
}

// 初始化
onMounted(async () => {
  await loadUnreadCount()
  // 延迟检查公告，让页面先完全加载
  setTimeout(() => {
    checkAdminAnnouncements()
  }, 500)
})
</script>

<style scoped lang="scss">
.dashboard-container {
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
    padding: 20px;
    background-color: #fafafa;
    overflow-y: auto;

    .welcome-card {
      background: white;
      padding: 30px;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

      h2 {
        color: #333;
        margin-bottom: 20px;
      }

      p {
        color: #666;
        margin: 10px 0;
      }
    }
  }
}
.announcement-content {
  .announcement-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    .title {
      font-size: 18px;
      font-weight: bold;
      color: #333;
      flex: 1;
    }

    .page-info {
      color: #999;
      font-size: 12px;
    }
  }

  .announcement-body {
    padding: 20px 0;

    .time {
      color: #999;
      font-size: 12px;
      margin-bottom: 12px;
    }

    .content {
      color: #666;
      line-height: 1.6;
      white-space: pre-wrap;
      word-wrap: break-word;
    }
  }
}
</style>