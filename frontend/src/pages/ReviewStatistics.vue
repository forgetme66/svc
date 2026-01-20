<template>
  <div class="review-stats-container">
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h1>评价统计</h1>
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
            <el-menu-item v-if="isStudent" index="/review-teacher" route="/review-teacher">
              <template #title>教师评价</template>
            </el-menu-item>
            <el-menu-item v-if="!isTeacher && !isAdmin" index="/files" route="/files">
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
          <!-- 统计概览 -->
          <el-row :gutter="20" style="margin-bottom: 20px">
            <el-col :xs="24" :sm="12" :md="6">
              <el-statistic title="总评价数" :value="stats.total_count" />
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <el-statistic title="平均评分" :value="stats.avg_rating" :precision="1" suffix="分" />
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <el-statistic
                title="好评占比"
                :value="goodRatePercent"
                :precision="1"
                suffix="%"
              />
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <el-card class="rating-display">
                <template #header>
                  <div style="display: flex; justify-content: space-between; align-items: center">
                    <span>评分分布</span>
                  </div>
                </template>
                <el-progress
                  v-for="(count, rating) in stats.rating_distribution"
                  :key="rating"
                  :percentage="getPercentage(count)"
                  :label="`${rating}分: ${count}人`"
                  style="margin-bottom: 8px"
                />
              </el-card>
            </el-col>
          </el-row>

          <!-- 评价列表 -->
          <el-card class="reviews-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>学生评价列表</span>
                <span style="color: #909399; font-size: 12px">（学生身份已隐藏）</span>
              </div>
            </template>

            <el-empty v-if="reviewList.length === 0" description="暂无评价" />

            <div v-else class="review-list">
              <div v-for="(review, index) in reviewList" :key="review.id" class="review-item">
                <div class="review-header">
                  <div class="rating">
                    <el-rate
                      v-model="review.rating"
                      :max="5"
                      disabled
                      :colors="['#F7BA00', '#F7BA00', '#F7BA00', '#F7BA00', '#F7BA00']"
                    />
                    <span style="margin-left: 10px; color: #666">{{ review.rating }} 分</span>
                  </div>
                  <span class="time">{{ formatDate(review.created_at) }}</span>
                </div>
                <div class="review-content">
                  {{ review.comment }}
                </div>
                <el-divider v-if="index < reviewList.length - 1" style="margin: 16px 0" />
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
                @change="loadReviews"
              />
            </div>
          </el-card>
        </el-main>
      </el-container>
    </el-container>
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

// 状态
const activeMenu = ref('/review-statistics')
const unreadCount = ref(0)
const reviewList = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)

// 检查权限
const isStudent = computed(() => authStore.user?.user_type === 'student')
// 统计数据
const stats = ref({
  total_count: 0,
  avg_rating: 0,
  rating_distribution: {
    1: 0,
    2: 0,
    3: 0,
    4: 0,
    5: 0
  }
})

// 计算好评占比（4-5分）
const goodRatePercent = computed(() => {
  if (stats.value.total_count === 0) return 0
  const goodCount = (stats.value.rating_distribution[4] || 0) + (stats.value.rating_distribution[5] || 0)
  return (goodCount / stats.value.total_count * 100).toFixed(1)
})

// 计算百分比
const getPercentage = (count) => {
  if (stats.value.total_count === 0) return 0
  return Math.round((count / stats.value.total_count) * 100)
}

// 加载我的评价
const loadReviews = async () => {
  loading.value = true
  try {
    const response = await teacherAPI.getMyReviews()

    if (response.data.code === 200) {
      stats.value = {
        total_count: response.data.data.total_count,
        avg_rating: response.data.data.avg_rating,
        rating_distribution: response.data.data.rating_distribution
      }
      
      // 分页处理
      const allReviews = response.data.data.reviews
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      reviewList.value = allReviews.slice(start, end)
      total.value = allReviews.length
    } else {
      ElMessage.error(response.data.message || '加载失败')
    }
  } catch (error) {
    console.error('Load reviews error:', error)
    ElMessage.error(error.response?.data?.message || error.message || '加载失败')
  } finally {
    loading.value = false
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
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
  if (!isTeacher.value) {
    ElMessage.warning('您没有权限访问此页面')
    router.push('/dashboard')
  } else {
    loadReviews()
    loadUnreadCount()
  }
})
</script>

<style scoped lang="scss">
.review-stats-container {
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

  .rating-display {
    height: 100%;

    :deep(.el-card__body) {
      padding: 12px;
    }
  }

  .reviews-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: bold;
      color: #333;
    }
  }

  .review-list {
    .review-item {
      padding: 16px 0;

      .review-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;

        .rating {
          display: flex;
          align-items: center;
        }

        .time {
          color: #909399;
          font-size: 12px;
        }
      }

      .review-content {
        color: #666;
        line-height: 1.6;
        white-space: pre-wrap;
        word-wrap: break-word;
      }
    }
  }
}
</style>
