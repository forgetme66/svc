<template>
  <div class="inbox-container">
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h1>消息箱</h1>
        </div>
        <div class="header-right">
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
            <el-menu-item v-if="isTeacher" index="/teacher-management" route="/teacher-management">
              <template #title>学生管理</template>
            </el-menu-item>
            <el-menu-item v-if="isAdmin" index="/admin-management" route="/admin-management">
              <template #title>用户管理</template>
            </el-menu-item>
            <el-menu-item index="/teacher-ratings-display" route="/teacher-ratings-display">
              <template #title>评价浏览</template>
            </el-menu-item>
            <el-menu-item index="/questions" route="/questions">
              <template #title>问题中心</template>
            </el-menu-item>
          </el-menu>
        </el-aside>

        <el-main>
          <!-- 消息箱卡片 -->
          <el-card class="inbox-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>消息箱</span>
                <el-button 
                  type="primary" 
                  @click="markAllAsRead" 
                  :disabled="unreadCount === 0"
                  size="small"
                >
                  全部标记已读（{{ unreadCount }}）
                </el-button>
              </div>
            </template>

            <!-- 消息列表 -->
            <el-empty v-if="messageList.length === 0" description="暂无消息" />
            
            <div v-else class="message-list">
              <div 
                v-for="msg in messageList" 
                :key="msg.id"
                class="message-item"
                :class="{ 'unread': !msg.is_read }"
                @click="handleViewMessage(msg)"
              >
                <div class="message-header">
                  <span class="sender">
                    <el-tag v-if="msg.sender_user_type === 'admin'" type="warning" size="small" style="margin-right: 8px">
                      【管理员公告】
                    </el-tag>
                    <span>{{ msg.sender_username }}</span>
                    <el-tag v-if="!msg.is_read" type="danger" size="small" style="margin-left: 8px">未读</el-tag>
                  </span>
                  <span class="time">{{ formatTime(msg.created_at) }}</span>
                </div>
                <div class="message-content">
                  {{ msg.content.substring(0, 100) }}{{ msg.content.length > 100 ? '...' : '' }}
                </div>
              </div>
            </div>

            <!-- 分页 -->
            <div v-if="total > 0" style="margin-top: 20px; text-align: right">
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[10, 20, 50]"
                :total="total"
                layout="total, sizes, prev, pager, next, jumper"
                @change="loadMessages"
              />
            </div>
          </el-card>
        </el-main>
      </el-container>
    </el-container>

    <!-- 消息详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="消息详情" width="600px">
      <div v-if="selectedMessage" class="message-detail">
        <el-form label-width="100px">
          <el-form-item label="发送者">
            <div>
              <el-tag v-if="selectedMessage.sender_user_type === 'admin'" type="warning" style="margin-right: 8px">
                【管理员公告】
              </el-tag>
              <span>{{ selectedMessage.sender_username }}</span>
            </div>
          </el-form-item>
          <el-form-item label="发送时间">
            <span>{{ formatDateTime(selectedMessage.created_at) }}</span>
          </el-form-item>
          <el-form-item label="状态">
            <el-tag :type="selectedMessage.is_read ? 'success' : 'info'">
              {{ selectedMessage.is_read ? '已读' : '未读' }}
            </el-tag>
          </el-form-item>
          <el-form-item label="内容" class="message-content-form">
            <el-input 
              v-model="selectedMessage.content" 
              type="textarea"
              :rows="8"
              disabled
            />
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <el-button v-if="selectedMessage && !selectedMessage.is_read" type="primary" @click="handleMarkAsRead">
          标记已读
        </el-button>
        <el-button @click="showDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { authAPI } from '@/api/auth'
import { messagesAPI } from '@/api/messages'
import { ArrowDown, User } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

// 检查用户类型
const isTeacher = computed(() => authStore.user?.user_type === 'teacher')
const isAdmin = computed(() => authStore.user?.user_type === 'admin')

// 状态
const loading = ref(false)
const activeMenu = ref('/inbox')
const messageList = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const unreadCount = ref(0)
const showDetailDialog = ref(false)
const selectedMessage = ref(null)

// 加载消息列表
const loadMessages = async () => {
  loading.value = true
  try {
    const response = await messagesAPI.getMessages(currentPage.value, pageSize.value)
    
    if (response.data.code === 200) {
      // 将消息记录转换为消息项，并添加发送者信息
      messageList.value = response.data.data.messages.map(msg => ({
        id: msg.id,
        message_id: msg.message_id,
        sender_id: msg.sender_id,
        sender_username: msg.sender?.username || '系统消息',
        sender_user_type: msg.sender?.user_type || 'system',
        content: msg.message?.content || msg.content || '',
        created_at: msg.message?.created_at || msg.created_at,
        is_read: msg.is_read,
        read_at: msg.read_at
      }))
      total.value = response.data.data.total
      
      // 更新未读计数
      await loadUnreadCount()
    } else {
      ElMessage.error(response.data.message || '加载失败')
    }
  } catch (error) {
    console.error('Load messages error:', error)
    ElMessage.error(error.response?.data?.message || error.message || '加载失败')
  } finally {
    loading.value = false
  }
}

// 获取未读计数
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

// 查看消息详情
const handleViewMessage = async (msg) => {
  selectedMessage.value = msg
  showDetailDialog.value = true
  
  // 如果未读，自动标记为已读
  if (!msg.is_read) {
    try {
      const response = await messagesAPI.markRead(msg.message_id)
      if (response.data.code === 200) {
        msg.is_read = true
        await loadUnreadCount()
      }
    } catch (error) {
      console.error('Mark as read error:', error)
    }
  }
}

// 标记单条消息为已读
const handleMarkAsRead = async () => {
  if (!selectedMessage.value || selectedMessage.value.is_read) return
  
  try {
    const response = await messagesAPI.markRead(selectedMessage.value.message_id)
    if (response.data.code === 200) {
      selectedMessage.value.is_read = true
      ElMessage.success('已标记为已读')
      await loadUnreadCount()
    } else {
      ElMessage.error(response.data.message || '标记失败')
    }
  } catch (error) {
    console.error('Mark as read error:', error)
    ElMessage.error(error.response?.data?.message || error.message || '标记失败')
  }
}

// 全部标记已读
const markAllAsRead = async () => {
  if (unreadCount.value === 0) return
  
  try {
    for (const msg of messageList.value) {
      if (!msg.is_read) {
        const response = await messagesAPI.markRead(msg.message_id)
        if (response.data.code === 200) {
          msg.is_read = true
        }
      }
    }
    ElMessage.success('已全部标记为已读')
    await loadUnreadCount()
  } catch (error) {
    console.error('Mark all as read error:', error)
    ElMessage.error(error.response?.data?.message || error.message || '标记失败')
  }
}

// 格式化时间
const formatTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  
  if (date.toDateString() === today.toDateString()) {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } else if (date.toDateString() === yesterday.toDateString()) {
    return '昨天 ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } else {
    return date.toLocaleDateString('zh-CN')
  }
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

// 导航和登出
const goToProfile = () => {
  router.push('/profile')
}

const handleLogout = async () => {
  try {
    await authAPI.logout()
    authStore.clearAuth()
    router.push('/login')
  } catch (error) {
    console.error('Logout error:', error)
    authStore.clearAuth()
    router.push('/login')
  }
}

// 初始化
onMounted(() => {
  loadMessages()
})
</script>

<style scoped>
.inbox-container {
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
    background-color: #f5f7fa;
    border-right: 1px solid #dcdfe6;
  }

  :deep(.el-main) {
    padding: 20px;
    overflow-y: auto;
  }

  .inbox-card {
    margin: 0;
    border-radius: 6px;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
  }

  .message-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .message-item {
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 16px;
    cursor: pointer;
    transition: all 0.3s;

    &:hover {
      background-color: #f5f7fa;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    &.unread {
      background-color: #f0f4ff;
      border-left: 4px solid #667eea;
    }

    .message-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;

      .sender {
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 8px;
      }

      .time {
        color: #909399;
        font-size: 12px;
      }
    }

    .message-content {
      color: #606266;
      font-size: 14px;
      line-height: 1.5;
      overflow: hidden;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      word-break: break-word;
    }
  }

  .message-detail {
    .message-content-form :deep(.el-input__inner) {
      background-color: #f5f7fa;
    }
  }

  :deep(.el-pagination) {
    margin-top: 20px;
  }
}
</style>
