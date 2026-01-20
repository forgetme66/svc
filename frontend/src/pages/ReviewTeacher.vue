<template>
  <div class="review-container">
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h1>评价教师</h1>
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
            <el-menu-item v-if="!isTeacher || isAdmin" index="/review-teacher" route="/review-teacher">
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
          <!-- 教师列表卡片 -->
          <el-card class="teachers-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>我的教师</span>
              </div>
            </template>

            <!-- 教师列表 -->
            <el-empty v-if="teacherList.length === 0" description="暂无教师" />
            
            <el-row v-else :gutter="20">
              <el-col v-for="teacher in teacherList" :key="teacher.id" :xs="24" :sm="12" :md="8">
                <el-card class="teacher-card" shadow="hover">
                  <div class="teacher-info">
                    <div class="name">{{ teacher.real_name || teacher.username }}</div>
                    <div class="username">@{{ teacher.username }}</div>
                    <div class="status" v-if="teacher.reviewed">
                      <el-tag type="success">已评价</el-tag>
                    </div>
                    <div class="status" v-else>
                      <el-tag type="info">待评价</el-tag>
                    </div>
                  </div>
                  <el-button
                    v-if="!teacher.reviewed"
                    type="primary"
                    @click="openReviewDialog(teacher)"
                    style="width: 100%; margin-top: 12px"
                  >
                    去评价
                  </el-button>
                  <el-button
                    v-else
                    disabled
                    style="width: 100%; margin-top: 12px"
                  >
                    已完成
                  </el-button>
                </el-card>
              </el-col>
            </el-row>
          </el-card>
        </el-main>
      </el-container>
    </el-container>

    <!-- 评价表单对话框 -->
    <el-dialog v-model="showReviewDialog" title="评价教师" width="600px">
      <div v-if="selectedTeacher" class="review-form">
        <div class="teacher-display">
          <p><strong>教师：</strong>{{ selectedTeacher.real_name || selectedTeacher.username }}</p>
        </div>

        <el-form :model="reviewForm" label-width="80px">
          <el-form-item label="教学评分" required>
            <el-rate
              v-model="reviewForm.rating"
              :max="5"
              :colors="['#F7BA00', '#F7BA00', '#F7BA00', '#F7BA00', '#F7BA00']"
              style="font-size: 28px"
            />
            <span style="margin-left: 10px; color: #666">{{ reviewForm.rating }} 分</span>
          </el-form-item>

          <el-form-item label="文字评价" required>
            <el-input
              v-model="reviewForm.comment"
              type="textarea"
              placeholder="请输入至少20字的评价意见"
              :rows="6"
              maxlength="500"
              show-word-limit
            />
            <div v-if="reviewForm.comment.length > 0" style="margin-top: 8px; font-size: 12px; color: #909399">
              {{ reviewForm.comment.length }} / 500 字
            </div>
          </el-form-item>

          <el-form-item>
            <el-alert
              title="评价说明"
              type="info"
              :closable="false"
              description="您的评价对教师匿名展示，教师看不到您的身份信息。"
              style="margin-top: 12px"
            />
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <el-button @click="showReviewDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitReview" :loading="submitLoading">
          提交评价
        </el-button>
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
import { teacherAPI } from '@/api/teacher'
import { messagesAPI } from '@/api/messages'
import { Notification, User } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

// 权限检查
const isTeacher = computed(() => authStore.user?.user_type === 'teacher')
const isAdmin = computed(() => authStore.user?.user_type === 'admin')

// 状态
const activeMenu = ref('/review-teacher')
const unreadCount = ref(0)
const teacherList = ref([])
const loading = ref(false)

// 对话框状态
const showReviewDialog = ref(false)
const selectedTeacher = ref(null)
const submitLoading = ref(false)
const reviewForm = ref({
  rating: 5,
  comment: ''
})

// 加载我的教师列表
const loadMyTeachers = async () => {
  loading.value = true
  try {
    const response = await teacherAPI.getMyTeachers()
    
    if (response.data.code === 200) {
      teacherList.value = response.data.data.teachers
    } else {
      ElMessage.error(response.data.message || '加载失败')
    }
  } catch (error) {
    console.error('Load teachers error:', error)
    ElMessage.error(error.response?.data?.message || error.message || '加载失败')
  } finally {
    loading.value = false
  }
}

// 打开评价对话框
const openReviewDialog = (teacher) => {
  selectedTeacher.value = teacher
  reviewForm.value = {
    rating: 5,
    comment: ''
  }
  showReviewDialog.value = true
}

// 提交评价
const handleSubmitReview = async () => {
  // 验证
  if (reviewForm.value.rating < 1 || reviewForm.value.rating > 5) {
    ElMessage.warning('请选择1-5分的评分')
    return
  }

  if (!reviewForm.value.comment.trim()) {
    ElMessage.warning('请输入评价内容')
    return
  }

  if (reviewForm.value.comment.trim().length < 20) {
    ElMessage.warning('评价内容不少于20字')
    return
  }

  submitLoading.value = true
  try {
    const response = await teacherAPI.submitTeacherReview(
      selectedTeacher.value.id,
      reviewForm.value.rating,
      reviewForm.value.comment
    )

    if (response.data.code === 201) {
      ElMessage.success('评价提交成功')
      showReviewDialog.value = false
      // 更新教师列表
      await loadMyTeachers()
    } else {
      ElMessage.error(response.data.message || '提交失败')
    }
  } catch (error) {
    console.error('Submit review error:', error)
    ElMessage.error(error.response?.data?.message || error.message || '提交失败')
  } finally {
    submitLoading.value = false
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

// 导航
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

// 初始化
onMounted(() => {
  if (isTeacher.value || isAdmin.value) {
    ElMessage.warning('您没有权限访问此页面')
    router.push('/dashboard')
  } else {
    loadMyTeachers()
    loadUnreadCount()
  }
})
</script>

<style scoped lang="scss">
.review-container {
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
    background-color: #fafafa;
  }

  .teachers-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: bold;
      color: #333;
    }
  }

  .teacher-card {
    height: 100%;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s;

    &:hover {
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    .teacher-info {
      padding: 10px 0;

      .name {
        font-size: 16px;
        font-weight: bold;
        color: #333;
        margin-bottom: 4px;
      }

      .username {
        font-size: 12px;
        color: #909399;
        margin-bottom: 12px;
      }

      .status {
        margin-bottom: 12px;
      }
    }
  }

  .review-form {
    padding: 20px 0;

    .teacher-display {
      background-color: #f5f7fa;
      padding: 12px;
      border-radius: 4px;
      margin-bottom: 20px;

      p {
        margin: 0;
        color: #333;
      }
    }

    :deep(.el-form-item) {
      margin-bottom: 20px;
    }
  }
}
</style>