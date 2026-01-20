<template>
  <div class="admin-container">
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h1>用户管理</h1>
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
            <el-menu-item index="/files" route="/files">
              <template #title>文件管理</template>
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

        <el-main>
          <!-- 标签页 -->
          <el-tabs v-model="activeTab" type="border-card">
            <!-- 教师及学生关系标签页 -->
            <el-tab-pane label="教师管理" name="teachers">
              <div class="tab-content">
                <el-button type="primary" @click="loadTeacherStudents" style="margin-bottom: 20px">
                  刷新
                </el-button>
                
                <el-collapse v-if="teacherList.length > 0">
                  <el-collapse-item v-for="teacherData in teacherList" :key="teacherData.teacher.id" :title="`${teacherData.teacher.username} (${teacherData.teacher.real_name || '未设置'}) - ${teacherData.student_count} 个学生`">
                    <div class="teacher-info">
                      <el-descriptions :column="2" border>
                        <el-descriptions-item label="用户名">{{ teacherData.teacher.username }}</el-descriptions-item>
                        <el-descriptions-item label="邮箱">{{ teacherData.teacher.email }}</el-descriptions-item>
                        <el-descriptions-item label="姓名">{{ teacherData.teacher.real_name || '未设置' }}</el-descriptions-item>
                        <el-descriptions-item label="电话">{{ teacherData.teacher.phone || '未设置' }}</el-descriptions-item>
                      </el-descriptions>

                      <h4 style="margin-top: 15px; margin-bottom: 10px;">管理的学生 ({{ teacherData.student_count }})</h4>
                      
                      <el-table v-if="teacherData.students.length > 0" :data="teacherData.students" stripe size="small">
                        <el-table-column prop="username" label="用户名" width="100" />
                        <el-table-column prop="real_name" label="姓名" width="100" />
                        <el-table-column prop="student_id" label="学号" width="100" />
                        <el-table-column prop="college" label="学院" width="120" />
                        <el-table-column prop="major" label="专业" width="100" />
                        <el-table-column prop="phone" label="电话" width="120" />
                        <el-table-column prop="email" label="邮箱" width="150" />
                      </el-table>
                      
                      <el-empty v-else description="该教师暂无管理的学生" />
                    </div>
                  </el-collapse-item>
                </el-collapse>
                
                <el-empty v-else description="暂无教师数据" />
              </div>
            </el-tab-pane>

            <!-- 所有用户标签页 -->
            <el-tab-pane label="所有用户" name="users">
              <div class="tab-content">
                <!-- 搜索与操作栏 -->
                <el-row :gutter="20" style="margin-bottom: 12px; align-items: center">
                  <el-col :xs="24" :sm="12" :md="6">
                    <el-input
                      v-model="userSearchKeyword"
                      placeholder="搜索用户"
                      clearable
                      @input="handleUserSearch"
                    >
                      <template #prefix>
                        <el-icon><search /></el-icon>
                      </template>
                    </el-input>
                  </el-col>
                  <el-col :xs="24" :sm="12" :md="6">
                    <el-select
                      v-model="userTypeFilter"
                      placeholder="用户类型"
                      clearable
                      @change="handleUserSearch"
                    >
                      <el-option label="学生" value="student" />
                      <el-option label="教师" value="teacher" />
                      <el-option label="管理员" value="admin" />
                    </el-select>
                  </el-col>
                  <el-col :xs="24" :sm="24" :md="12" style="text-align: right">
                    <el-button type="primary" @click="openCreateUser">添加用户</el-button>
                  </el-col>
                </el-row>

                <!-- 用户列表 -->
                <el-table
                  :data="userList"
                  stripe
                  style="width: 100%"
                  :loading="userLoading"
                  :default-sort="{ prop: 'created_at', order: 'descending' }"
                >
                  <el-table-column prop="username" label="用户名" width="140" />
                  <el-table-column prop="real_name" label="姓名" width="110" />
                  <el-table-column prop="student_id" label="学号" width="110" />
                  <el-table-column prop="user_type" label="用户类型" width="100" :formatter="formatUserType" />
                  <el-table-column prop="email" label="邮箱" width="180" />
                  <el-table-column prop="phone" label="电话" width="130" />
                  <el-table-column prop="college" label="学院" width="140" />
                  <el-table-column prop="major" label="专业" width="110" />
                  <el-table-column prop="created_at" label="创建时间" width="180" :formatter="formatTime" />
                  <el-table-column label="操作" width="160" fixed="right">
                    <template #default="{ row }">
                      <el-button type="primary" link size="small" @click="openEditUser(row)">编辑</el-button>
                      <el-button type="danger" link size="small" @click="confirmDeleteUser(row.id)">删除</el-button>
                    </template>
                  </el-table-column>
                </el-table>

                <!-- 分页 -->
                <div style="margin-top: 20px; text-align: right">
                  <el-pagination
                    v-model:current-page="userCurrentPage"
                    v-model:page-size="userPageSize"
                    :page-sizes="[10, 20, 50]"
                    :total="userTotal"
                    layout="total, sizes, prev, pager, next, jumper"
                    @change="loadUsers"
                  />
                </div>
              
                <!-- 新增/编辑用户对话框 -->
                <el-dialog v-model="userDialogVisible" :title="editingUserId ? '编辑用户' : '添加用户'" width="600px">
                  <el-form :model="userForm" label-width="120px">
                    <el-form-item label="用户名">
                      <el-input v-model="userForm.username" />
                    </el-form-item>
                    <el-form-item label="邮箱">
                      <el-input v-model="userForm.email" />
                    </el-form-item>
                    <el-form-item label="密码" v-if="!editingUserId">
                      <el-input v-model="userForm.password" show-password />
                    </el-form-item>
                    <el-form-item label="用户类型">
                      <el-select v-model="userForm.user_type" placeholder="选择类型">
                        <el-option label="学生" value="student" />
                        <el-option label="教师" value="teacher" />
                        <el-option label="管理员" value="admin" />
                      </el-select>
                    </el-form-item>
                    <el-form-item label="学号/工号">
                      <el-input v-model="userForm.student_id" placeholder="学生填写学号；教师填写工号" />
                    </el-form-item>
                    <el-form-item label="姓名">
                      <el-input v-model="userForm.real_name" />
                    </el-form-item>
                    <el-form-item label="联系电话">
                      <el-input v-model="userForm.phone" />
                    </el-form-item>
                    <el-form-item label="学院">
                      <el-input v-model="userForm.college" />
                    </el-form-item>
                    <el-form-item label="专业">
                      <el-input v-model="userForm.major" />
                    </el-form-item>
                  </el-form>
                  <template #footer>
                    <el-button @click="userDialogVisible = false">取消</el-button>
                    <el-button type="primary" :loading="userDialogLoading" @click="submitUserForm">确定</el-button>
                  </template>
                </el-dialog>

              </div>
            </el-tab-pane>

            <!-- 通报发布标签页 -->
            <el-tab-pane label="通报发布" name="broadcast">
              <div class="tab-content">
                <el-card class="broadcast-card" shadow="hover">
                  <template #header>
                    <div class="card-header">
                      <span>发布系统通报</span>
                    </div>
                  </template>

                  <el-form :model="broadcastForm" label-width="100px" style="max-width: 800px">
                    <el-form-item label="通报标题" required>
                      <el-input
                        v-model="broadcastForm.title"
                        placeholder="请输入通报标题"
                        maxlength="100"
                        show-word-limit
                      />
                    </el-form-item>

                    <el-form-item label="通报内容" required>
                      <el-input
                        v-model="broadcastForm.content"
                        type="textarea"
                        placeholder="请输入通报内容"
                        :rows="8"
                        maxlength="2000"
                        show-word-limit
                      />
                    </el-form-item>

                    <el-form-item label="接收对象" required>
                      <el-radio-group v-model="broadcastForm.recipientType">
                        <el-radio-button label="all">所有人</el-radio-button>
                        <el-radio-button label="teacher">所有教师</el-radio-button>
                        <el-radio-button label="student">所有学生</el-radio-button>
                      </el-radio-group>
                    </el-form-item>

                    <el-form-item>
                      <el-button type="primary" @click="handleSendBroadcast" :loading="broadcastLoading">
                        发布通报
                      </el-button>
                      <el-button @click="handleResetBroadcast">重置</el-button>
                    </el-form-item>
                  </el-form>

                  <!-- 发送成功提示 -->
                  <el-result
                    v-if="broadcastSuccess"
                    icon="success"
                    title="通报发布成功"
                    :sub-title="`已发送给 ${broadcastSuccessCount} 名用户`"
                  >
                    <template #extra>
                      <el-button type="primary" @click="broadcastSuccess = false">关闭</el-button>
                    </template>
                  </el-result>
                </el-card>

                <!-- 通报说明 -->
                <el-alert
                  title="通报发布说明"
                  type="info"
                  :closable="false"
                  style="margin-top: 20px"
                >
                  <ul style="margin: 10px 0 0 20px; padding: 0">
                    <li>通报将发送给系统中的所有活跃用户</li>
                    <li>用户可在消息箱中查看和阅读通报</li>
                    <li>通报发布后无法撤回，请谨慎编辑内容</li>
                  </ul>
                </el-alert>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { teacherAPI } from '@/api/teacher'
import { authAPI } from '@/api/auth'
import { messagesAPI } from '@/api/messages'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, ArrowDown, Notification, User } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

// 权限检查
const isAdmin = computed(() => authStore.user?.user_type === 'admin')

// 状态
const activeTab = ref('teachers')
const activeMenu = ref('/admin-management')
const unreadCount = ref(0)

// 教师标签页状态
const teacherList = ref([])
const teacherLoading = ref(false)

// 用户标签页状态
const userList = ref([])
const userLoading = ref(false)
const userCurrentPage = ref(1)
const userPageSize = ref(10)
const userTotal = ref(0)
const userSearchKeyword = ref('')
const userTypeFilter = ref('')

// 加载教师及学生列表
const loadTeacherStudents = async () => {
  teacherLoading.value = true
  try {
    const response = await teacherAPI.adminGetTeacherStudents()
    
    if (response.data.code === 200) {
      teacherList.value = response.data.data.teachers
    } else {
      ElMessage.error(response.data.message || '加载失败')
    }
  } catch (error) {
    console.error('Load teacher students error:', error)
    ElMessage.error(error.response?.data?.message || error.message || '加载失败')
  } finally {
    teacherLoading.value = false
  }
}

// 加载用户列表
const loadUsers = async () => {
  userLoading.value = true
  try {
    const response = await teacherAPI.adminGetUsers(
      userCurrentPage.value,
      userPageSize.value,
      userSearchKeyword.value,
      userTypeFilter.value
    )
    
    if (response.data.code === 200) {
      userList.value = response.data.data.users
      userTotal.value = response.data.data.total
    } else {
      ElMessage.error(response.data.message || '加载失败')
    }
  } catch (error) {
    console.error('Load users error:', error)
    ElMessage.error(error.response?.data?.message || error.message || '加载失败')
  } finally {
    userLoading.value = false
  }
}

// 处理用户搜索
const handleUserSearch = () => {
  userCurrentPage.value = 1
  loadUsers()
}

// 新增/编辑用户对话状态
const userDialogVisible = ref(false)
const userDialogLoading = ref(false)
const editingUserId = ref(null)
const userForm = ref({
  username: '',
  email: '',
  password: '',
  user_type: 'student',
  student_id: '',
  real_name: '',
  phone: '',
  college: '',
  major: ''
})

// 通报相关状态
const broadcastForm = ref({
  title: '',
  content: '',
  recipientType: 'all'
})
const broadcastLoading = ref(false)
const broadcastSuccess = ref(false)
const broadcastSuccessCount = ref(0)

const openCreateUser = () => {
  editingUserId.value = null
  userForm.value = {
    username: '',
    email: '',
    password: '',
    user_type: 'student',
    student_id: '',
    real_name: '',
    phone: '',
    college: '',
    major: ''
  }
  userDialogVisible.value = true
}

const openEditUser = (row) => {
  editingUserId.value = row.id
  userForm.value = {
    username: row.username || '',
    email: row.email || '',
    password: '',
    user_type: row.user_type || 'student',
    student_id: row.student_id || '',
    real_name: row.real_name || '',
    phone: row.phone || '',
    college: row.college || '',
    major: row.major || ''
  }
  userDialogVisible.value = true
}

const submitUserForm = async () => {
  userDialogLoading.value = true
  try {
    if (editingUserId.value) {
      const payload = { ...userForm.value }
      // 不发送空密码字段
      if (!payload.password) delete payload.password
      const res = await teacherAPI.adminUpdateUser(editingUserId.value, payload)
      if (res.data.code === 200) {
        ElMessage.success('更新成功')
        userDialogVisible.value = false
        loadUsers()
      } else {
        ElMessage.error(res.data.message || '更新失败')
      }
    } else {
      const payload = { ...userForm.value }
      const res = await teacherAPI.adminCreateUser(payload)
      if (res.data.code === 201) {
        ElMessage.success('创建成功')
        userDialogVisible.value = false
        loadUsers()
      } else {
        ElMessage.error(res.data.message || '创建失败')
      }
    }
  } catch (error) {
    console.error('User save error:', error)
    ElMessage.error(error.response?.data?.message || error.message || '请求失败')
  } finally {
    userDialogLoading.value = false
  }
}

const confirmDeleteUser = (userId) => {
  ElMessageBox.confirm('确认删除该用户？此操作无法撤销。', '删除确认', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await teacherAPI.adminDeleteUser(userId)
      if (res.data.code === 200) {
        ElMessage.success('删除成功')
        loadUsers()
      } else {
        ElMessage.error(res.data.message || '删除失败')
      }
    } catch (error) {
      console.error('Delete user error:', error)
      ElMessage.error(error.response?.data?.message || error.message || '删除失败')
    }
  }).catch(() => {})
}

// 格式化用户类型
const formatUserType = (row) => {
  const typeMap = {
    'student': '学生',
    'teacher': '教师',
    'admin': '管理员'
  }
  return typeMap[row.user_type] || row.user_type
}

// 格式化时间
const formatTime = (row) => {
  if (!row.created_at) return ''
  const date = new Date(row.created_at)
  return date.toLocaleString('zh-CN')
}

// 导航和登出
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
    // 使用replace而不是push，避免返回到当前页面
    router.replace('/login')
  }
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

// 发送通报
const handleSendBroadcast = async () => {
  if (!broadcastForm.value.title.trim()) {
    ElMessage.warning('请输入通报标题')
    return
  }
  if (!broadcastForm.value.content.trim()) {
    ElMessage.warning('请输入通报内容')
    return
  }

  broadcastLoading.value = true
  try {
    // 根据接收对象类型构建参数
    let payload = {
      title: broadcastForm.value.title,
      content: `【管理员公告】${broadcastForm.value.title}\n\n${broadcastForm.value.content}`,
      target: 'all',
      recipient_type: broadcastForm.value.recipientType
    }

    const response = await teacherAPI.sendMessage(payload)

    if (response.data.code === 201) {
      broadcastSuccessCount.value = response.data.data.recipient_count
      broadcastSuccess.value = true
      const typeText = {
        'all': '所有用户',
        'teacher': '所有教师',
        'student': '所有学生'
      }[broadcastForm.value.recipientType]
      ElMessage.success(`通报已发送给${typeText}，共 ${response.data.data.recipient_count} 人收到`)
      handleResetBroadcast()
    } else {
      ElMessage.error(response.data.message || '发送失败')
    }
  } catch (error) {
    console.error('Send broadcast error:', error)
    ElMessage.error(error.response?.data?.message || error.message || '发送失败')
  } finally {
    broadcastLoading.value = false
  }
}

// 重置通报表单
const handleResetBroadcast = () => {
  broadcastForm.value = {
    title: '',
    content: '',
    recipientType: 'all'
  }
}

// 初始化
onMounted(() => {
  if (!isAdmin.value) {
    ElMessage.warning('您没有权限访问此页面')
    router.push('/dashboard')
  } else {
    loadTeacherStudents()
    loadUsers()
    loadUnreadCount()
  }
})
</script>

<style scoped lang="scss">
.admin-container {
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
    background-color: #f5f7fa;
    border-right: 1px solid #dcdfe6;
  }

  :deep(.el-main) {
    padding: 20px;
    overflow-y: auto;
  }

  .tab-content {
    padding: 20px 0;
  }

  .teacher-info {
    padding: 10px 0;
  }

  :deep(.el-table) {
    margin-top: 10px;
  }

  :deep(.el-collapse) {
    border: 1px solid #dcdfe6;
    border-radius: 4px;
  }

  :deep(.el-pagination) {
    margin-top: 20px;
  }

  .broadcast-card {
    :deep(.el-card__header) {
      border-bottom: 1px solid #e4e7eb;
    }

    :deep(.el-form-item) {
      margin-bottom: 22px;
    }
  }
}
</style>