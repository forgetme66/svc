<template>
  <div class="teacher-container">
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h1>学生管理</h1>
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
            <!-- <el-menu-item v-if="!isTeacher" index="/files" route="/files">
              <template #title>文件管理</template>
            </el-menu-item> -->
            <el-menu-item v-if="isStudent" index="/review-teacher" route="/review-teacher">
              <template #title>教师评价</template>
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
        <!-- 学生管理卡片 -->
        <el-card class="management-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>学生管理</span>
              <div>
                <el-button type="success" @click="showBroadcastDialog = true" style="margin-right:8px">
                  群发消息
                </el-button>
                <el-button type="primary" @click="showAddDialog = true">
                  添加学生
                </el-button>
              </div>
            </div>
          </template>

          <!-- 搜索栏 -->
          <el-row :gutter="20" style="margin-bottom: 20px">
            <el-col :xs="24" :sm="12" :md="8">
              <el-input
                v-model="searchKeyword"
                placeholder="搜索学生（用户名/姓名/学号）"
                clearable
                @input="handleSearch"
              >
                <template #prefix>
                  <el-icon><search /></el-icon>
                </template>
              </el-input>
            </el-col>
          </el-row>

          <!-- 学生列表 -->
          <el-table
            :data="studentList"
            stripe
            style="width: 100%"
            :loading="loading"
            :default-sort="{ prop: 'created_at', order: 'descending' }"
          >
            <el-table-column prop="student.username" label="用户名" width="120" />
            <el-table-column prop="student.real_name" label="姓名" width="120" />
            <el-table-column prop="student.email" label="邮箱" width="180" />
            <el-table-column prop="student.student_id" label="学号" width="120" />
            <el-table-column prop="student.college" label="学院" width="150" />
            <el-table-column prop="student.major" label="专业" width="120" />
            <el-table-column prop="student.phone" label="联系电话" width="130" />
            <el-table-column prop="created_at" label="添加时间" width="180" :formatter="formatTime" />
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button
                  link
                  type="primary"
                  size="small"
                  @click="handleViewStudent(row.student.id)"
                >
                  查看
                </el-button>
                <el-button
                  link
                  type="danger"
                  size="small"
                  @click="handleRemoveStudent(row.student.id)"
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 分页 -->
          <div style="margin-top: 20px; text-align: right">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50]"
              :total="total"
              layout="total, sizes, prev, pager, next, jumper"
              @change="loadStudents"
            />
          </div>
        </el-card>

        <!-- 添加学生对话框 -->
        <el-dialog v-model="showAddDialog" title="添加学生" width="600px">
          <el-form :model="addForm" label-width="100px">
            <el-form-item label="搜索学生">
              <el-select
                v-model="addForm.studentId"
                filterable
                remote
                clearable
                placeholder="搜索学生（用户名/姓名/学号）"
                :loading="searchLoading"
                :remote-method="handleRemoteSearch"
              >
                <el-option
                  v-for="student in availableStudents"
                  :key="student.id"
                  :label="`${student.username} - ${student.real_name || ''}（${student.student_id || ''}）`"
                  :value="student.id"
                />
              </el-select>
            </el-form-item>
          </el-form>

          <template #footer>
            <el-button @click="showAddDialog = false">取消</el-button>
            <el-button type="primary" @click="handleAddStudent" :loading="addLoading">
              确定
            </el-button>
          </template>
        </el-dialog>

        <!-- 群发消息对话框 -->
        <el-dialog v-model="showBroadcastDialog" title="群发消息（发给所有管理学生）" width="600px">
          <el-form :model="broadcastForm" label-width="100px">
            <el-form-item label="消息内容">
              <el-input
                type="textarea"
                rows="6"
                v-model="broadcastForm.content"
                placeholder="请输入要发送的消息"
              />
            </el-form-item>
          </el-form>

          <template #footer>
            <el-button @click="showBroadcastDialog = false">取消</el-button>
            <el-button type="primary" :loading="broadcastLoading" @click="handleSendBroadcast">
              发送
            </el-button>
          </template>
        </el-dialog>

        <!-- 学生详细信息对话框 -->
        <el-dialog v-model="showDetailDialog" title="学生详细信息" width="600px">
          <el-form v-if="selectedStudent" :model="selectedStudent" label-width="100px">
            <el-form-item label="用户名">
              <el-input v-model="selectedStudent.username" disabled />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="selectedStudent.email" disabled />
            </el-form-item>
            <el-form-item label="姓名">
              <el-input v-model="selectedStudent.real_name" disabled />
            </el-form-item>
            <el-form-item label="学号">
              <el-input v-model="selectedStudent.student_id" disabled />
            </el-form-item>
            <el-form-item label="学院">
              <el-input v-model="selectedStudent.college" disabled />
            </el-form-item>
            <el-form-item label="专业">
              <el-input v-model="selectedStudent.major" disabled />
            </el-form-item>
            <el-form-item label="联系电话">
              <el-input v-model="selectedStudent.phone" disabled />
            </el-form-item>
            <el-form-item label="账户状态">
              <el-tag :type="selectedStudent.is_active ? 'success' : 'danger'">
                {{ selectedStudent.is_active ? '激活' : '禁用' }}
              </el-tag>
            </el-form-item>
          </el-form>

          <template #footer>
            <el-button @click="showDetailDialog = false">关闭</el-button>
          </template>
        </el-dialog>

        <!-- 群发消息对话框 -->
        <el-dialog v-model="showBroadcastDialog" title="群发消息给所管理学生" width="600px">
          <el-form :model="broadcastForm" label-width="100px">
            <el-form-item label="消息内容" required>
              <el-input
                v-model="broadcastForm.content"
                type="textarea"
                :rows="4"
                placeholder="请输入要群发的消息内容"
              />
            </el-form-item>
            <el-alert 
              type="info" 
              :closable="false"
              description="消息将被群发给您所管理的所有学生"
              style="margin-bottom: 10px"
            />
          </el-form>

          <template #footer>
            <el-button @click="showBroadcastDialog = false">取消</el-button>
            <el-button type="primary" @click="handleBroadcastMessage" :loading="broadcastLoading">
              发送
            </el-button>
          </template>
        </el-dialog>
      </el-main>
        </el-container>
      </el-container>
    </div>
  </template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { authAPI } from '@/api/auth'
import { teacherAPI } from '@/api/teacher'
import { messagesAPI } from '@/api/messages'
import { ArrowDown, Notification, User } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

// 检查是否是教师
const isTeacher = computed(() => authStore.user?.user_type === 'teacher')

// 状态
const loading = ref(false)
const searchLoading = ref(false)
const addLoading = ref(false)
const activeMenu = ref('/teacher-management')
const unreadCount = ref(0)
const studentList = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchKeyword = ref('')
const showAddDialog = ref(false)
const showDetailDialog = ref(false)
const availableStudents = ref([])
const selectedStudent = ref(null)
const showBroadcastDialog = ref(false)
const broadcastLoading = ref(false)

const addForm = ref({
  studentId: null
})

const broadcastForm = ref({
  content: ''
})

// 加载学生列表
const loadStudents = async () => {
  loading.value = true
  try {
    const response = await teacherAPI.getStudents(currentPage.value, pageSize.value, searchKeyword.value)
    
    if (response.data.code === 200) {
      studentList.value = response.data.data.students
      total.value = response.data.data.total
    } else {
      ElMessage.error(response.data.message || '加载失败')
    }
  } catch (error) {
    console.error('Load students error:', error)
    ElMessage.error(error.response?.data?.message || error.message || '加载失败')
  } finally {
    loading.value = false
  }
}

// 搜索学生
const handleSearch = () => {
  currentPage.value = 1
  loadStudents()
}

// 远程搜索可用学生
const handleRemoteSearch = async (keyword) => {
  console.log('🔍 handleRemoteSearch called with keyword:', keyword)
  if (keyword === '') {
    availableStudents.value = []
    return
  }

  searchLoading.value = true
  try {
    console.log('📡 Calling getAvailableStudents API with keyword:', keyword)
    const response = await teacherAPI.getAvailableStudents(1, 10, keyword)
    console.log('✅ API Response:', response.data)
    
    if (response.data.code === 200) {
      availableStudents.value = response.data.data.students
      console.log('📋 Available students updated:', availableStudents.value)
    } else {
      ElMessage.error(response.data.message || '搜索失败')
    }
  } catch (error) {
    console.error('❌ Search students error:', error)
    ElMessage.error(error.response?.data?.message || error.message || '搜索失败')
  } finally {
    searchLoading.value = false
  }
}

// 添加学生
const handleAddStudent = async () => {
  if (!addForm.value.studentId) {
    ElMessage.warning('请选择学生')
    return
  }

  addLoading.value = true
  try {
    const response = await teacherAPI.addStudent(addForm.value.studentId)
    
    if (response.data.code === 201) {
      ElMessage.success('学生添加成功')
      showAddDialog.value = false
      addForm.value.studentId = null
      availableStudents.value = []
      currentPage.value = 1
      await loadStudents()
    } else {
      ElMessage.error(response.data.message || '添加失败')
    }
  } catch (error) {
    console.error('Add student error:', error)
    ElMessage.error(error.response?.data?.message || error.message || '添加失败')
  } finally {
    addLoading.value = false
  }
}

// 删除学生
const handleRemoveStudent = (studentId) => {
  ElMessageBox.confirm(
    '确定要删除此学生吗？',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const response = await teacherAPI.removeStudent(studentId)
      
      if (response.data.code === 200) {
        ElMessage.success('学生删除成功')
        await loadStudents()
      } else {
        ElMessage.error(response.data.message || '删除失败')
      }
    } catch (error) {
      console.error('Remove student error:', error)
      ElMessage.error(error.response?.data?.message || error.message || '删除失败')
    }
  }).catch(() => {
    // 取消删除
  })
}

// 查看学生详情
const handleViewStudent = async (studentId) => {
  try {
    const response = await teacherAPI.getStudentInfo(studentId)
    
    if (response.data.code === 200) {
      selectedStudent.value = response.data.data
      showDetailDialog.value = true
    } else {
      ElMessage.error(response.data.message || '获取学生信息失败')
    }
  } catch (error) {
    console.error('Get student info error:', error)
    ElMessage.error(error.response?.data?.message || error.message || '获取学生信息失败')
  }
}

// 群发消息
const handleBroadcastMessage = async () => {
  if (!broadcastForm.value.content.trim()) {
    ElMessage.warning('请输入消息内容')
    return
  }

  broadcastLoading.value = true
  try {
    const response = await messagesAPI.sendMessage({
      content: broadcastForm.value.content,
      target: 'teacher_students'
    })
    
    if (response.data.code === 201) {
      ElMessage.success(`消息已发送给 ${response.data.data.recipient_count} 名学生`)
      showBroadcastDialog.value = false
      broadcastForm.value.content = ''
    } else {
      ElMessage.error(response.data.message || '发送失败')
    }
  } catch (error) {
    console.error('Broadcast message error:', error)
    ElMessage.error(error.response?.data?.message || error.message || '发送失败')
  } finally {
    broadcastLoading.value = false
  }
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
    authStore.clearAuth()
    router.push('/login')
  } catch (error) {
    console.error('Logout error:', error)
    authStore.clearAuth()
    router.push('/login')
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

// 初始化
onMounted(() => {
  if (!isTeacher.value) {
    ElMessage.warning('您没有权限访问此页面')
    router.push('/dashboard')
  } else {
    loadStudents()
    loadUnreadCount()
  }
})
</script>

<style scoped>
.teacher-container {
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

  .management-card {
    margin: 0;
    border-radius: 6px;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
  }

  .el-table {
    margin-top: 10px;
  }

  :deep(.el-pagination) {
    margin-top: 20px;
  }
}
</style>
