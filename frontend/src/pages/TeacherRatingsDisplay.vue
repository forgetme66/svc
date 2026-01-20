<template>
  <div class="ratings-display-container">
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h1>教师评价</h1>
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
            <el-menu-item v-if="isStudent || isAdmin" index="/files" route="/files">
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

        <el-main>
          <!-- 搜索和排序 -->
          <div class="controls">
            <el-input v-model="searchKeyword" placeholder="搜索教师名称" class="search-input">
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            
            <el-select v-model="sortBy" class="sort-select">
              <el-option label="最高评分" value="rating" />
              <el-option label="评价最多" value="count" />
              <el-option label="最新添加" value="newest" />
            </el-select>
          </div>

          <!-- 教师卡片网格 -->
          <el-row :gutter="20" class="teachers-grid">
            <el-col
              v-for="teacher in filteredTeachers"
              :key="teacher.id"
              :xs="24"
              :sm="12"
              :md="8"
              :lg="6"
              class="teacher-col"
            >
              <el-card class="teacher-card" shadow="hover">
                <!-- 教师基本信息 -->
                <div class="teacher-header">
                  <div class="teacher-info">
                    <h3 class="teacher-name">{{ teacher.real_name }}</h3>
                    <p class="teacher-username">@{{ teacher.username }}</p>
                  </div>
                  
                  <!-- 是否是我的教师标记 -->
                  <el-tag v-if="teacher.is_my_teacher" type="success" size="small">
                    我的教师
                  </el-tag>
                </div>

                <!-- 评分显示 -->
                <div class="rating-section">
                  <div class="avg-rating">
                    <span class="rating-value">{{ teacher.avg_rating }}</span>
                    <span class="rating-unit">分</span>
                  </div>
                  <el-rate
                    v-model="teacher.avg_rating"
                    :max="5"
                    disabled
                    :colors="['#F7BA00', '#F7BA00', '#F7BA00', '#F7BA00', '#F7BA00']"
                  />
                  <p class="review-count">{{ teacher.total_count }} 条评价</p>
                </div>

                <!-- 评分分布 -->
                <div class="distribution">
                  <div v-for="(count, rating) in [5, 4, 3, 2, 1]" :key="rating" class="dist-row">
                    <span class="dist-label">{{ rating }}分</span>
                    <el-progress
                      :percentage="getPercentage(teacher.total_count, teacher.rating_distribution[rating])"
                      :color="getProgressColor(rating)"
                      :show-text="false"
                      class="dist-progress"
                    />
                    <span class="dist-count">{{ teacher.rating_distribution[rating] }}</span>
                  </div>
                </div>

                <!-- 最新评价摘要 -->
                <div class="reviews-preview">
                  <p class="preview-title">最新评价</p>
                  <div v-if="teacher.reviews.length > 0" class="review-items">
                    <div v-for="(review, idx) in teacher.reviews" :key="idx" class="review-item">
                      <div class="review-rating">
                        <el-rate v-model="review.rating" :max="5" disabled size="small" />
                      </div>
                      <p class="review-text">{{ review.comment.substring(0, 50) }}...</p>
                      <p class="review-time">{{ formatDate(review.created_at) }}</p>
                    </div>
                  </div>
                  <div v-else class="no-reviews">
                    暂无评价
                  </div>
                </div>

                <!-- 操作按钮 -->
                <div class="actions">
                  <el-button
                    v-if="teacher.is_my_teacher && !isTeacher && !isAdmin"
                    type="primary"
                    @click="goToReviewTeacher(teacher.id)"
                  >
                    去评价
                  </el-button>
                  <el-button v-else type="info" plain>查看详情</el-button>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <!-- 空状态 -->
          <el-empty v-if="filteredTeachers.length === 0" description="暂无教师评价数据" />
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
import { Notification, User, Search } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

// 权限检查
const isTeacher = computed(() => authStore.user?.user_type === 'teacher')
const isAdmin = computed(() => authStore.user?.user_type === 'admin')

// 状态
const activeMenu = ref('/teacher-ratings-display')
const unreadCount = ref(0)
const teachersList = ref([])
const searchKeyword = ref('')
const sortBy = ref('rating')
const loading = ref(false)
// 检查是否为学生
const isStudent = computed(() => authStore.user?.user_type === 'student')

// 计算排序和过滤后的教师列表
const filteredTeachers = computed(() => {
  let result = [...teachersList.value]

  // 按关键字过滤
  if (searchKeyword.value) {
    result = result.filter(
      t =>
        t.real_name.includes(searchKeyword.value) ||
        t.username.includes(searchKeyword.value)
    )
  }

  // 排序
  if (sortBy.value === 'rating') {
    result.sort((a, b) => b.avg_rating - a.avg_rating)
  } else if (sortBy.value === 'count') {
    result.sort((a, b) => b.total_count - a.total_count)
  } else if (sortBy.value === 'newest') {
    // 按最新评价时间排序
    result.sort((a, b) => {
      const aTime = a.reviews[0]?.created_at || ''
      const bTime = b.reviews[0]?.created_at || ''
      return new Date(bTime) - new Date(aTime)
    })
  }

  return result
})

// 计算百分比
const getPercentage = (total, count) => {
  if (total === 0) return 0
  return Math.round((count / total) * 100)
}

// 获取进度条颜色
const getProgressColor = (rating) => {
  if (rating === 5) return '#67C23A'
  if (rating === 4) return '#85CE61'
  if (rating === 3) return '#E6A23C'
  if (rating === 2) return '#F56C6C'
  return '#F56C6C'
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

// 加载所有教师评价
const loadTeachersRatings = async () => {
  loading.value = true
  try {
    const response = await teacherAPI.getAllTeachersRatings()

    if (response.data.code === 200) {
      teachersList.value = response.data.data.teachers
    } else {
      ElMessage.error(response.data.message || '加载失败')
    }
  } catch (error) {
    console.error('Load teachers ratings error:', error)
    ElMessage.error(error.response?.data?.message || error.message || '加载失败')
  } finally {
    loading.value = false
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

const goToReviewTeacher = (teacherId) => {
  router.push('/review-teacher')
  // 可以在这里添加逻辑来处理特定教师的评价
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
  loadTeachersRatings()
  loadUnreadCount()
})
</script>

<style scoped lang="scss">
.ratings-display-container {
  height: 100vh;
  display: flex;
  flex-direction: column;

  :deep(.el-container) {
    height: 100%;
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
    background-color: #f5f7fa;
    border-right: 1px solid #dcdfe6;
    overflow-y: auto;
  }

  :deep(.el-main) {
    padding: 30px;
    overflow-y: auto;
    background-color: #fafafa;
  }

  .controls {
    display: flex;
    gap: 12px;
    margin-bottom: 30px;

    .search-input {
      width: 250px;
    }

    .sort-select {
      width: 150px;
    }
  }

  .teachers-grid {
    margin-bottom: 30px;

    .teacher-col {
      .teacher-card {
        height: 100%;
        transition: all 0.3s;
        display: flex;
        flex-direction: column;

        &:hover {
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
          transform: translateY(-4px);
        }

        :deep(.el-card__body) {
          padding: 16px;
          display: flex;
          flex-direction: column;
          flex: 1;
        }

        .teacher-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 16px;
          border-bottom: 1px solid #f0f0f0;
          padding-bottom: 12px;

          .teacher-info {
            flex: 1;

            .teacher-name {
              margin: 0 0 4px 0;
              font-size: 16px;
              font-weight: bold;
              color: #333;
            }

            .teacher-username {
              margin: 0;
              font-size: 12px;
              color: #909399;
            }
          }
        }

        .rating-section {
          text-align: center;
          padding: 16px 0;
          margin-bottom: 12px;

          .avg-rating {
            display: flex;
            align-items: baseline;
            justify-content: center;
            margin-bottom: 8px;

            .rating-value {
              font-size: 28px;
              font-weight: bold;
              color: #667eea;
            }

            .rating-unit {
              margin-left: 4px;
              font-size: 14px;
              color: #666;
            }
          }

          :deep(.el-rate) {
            justify-content: center;
            margin-bottom: 8px;
          }

          .review-count {
            margin: 0;
            font-size: 12px;
            color: #909399;
          }
        }

        .distribution {
          margin-bottom: 16px;
          padding: 12px;
          background-color: #f5f7fa;
          border-radius: 4px;

          .dist-row {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 6px;

            &:last-child {
              margin-bottom: 0;
            }

            .dist-label {
              width: 30px;
              font-size: 12px;
              color: #666;
            }

            .dist-progress {
              flex: 1;
            }

            .dist-count {
              width: 24px;
              text-align: right;
              font-size: 12px;
              color: #666;
            }
          }
        }

        .reviews-preview {
          flex: 1;
          margin-bottom: 16px;

          .preview-title {
            margin: 0 0 8px 0;
            font-size: 12px;
            font-weight: bold;
            color: #333;
          }

          .review-items {
            .review-item {
              padding: 8px 0;
              border-bottom: 1px solid #f0f0f0;

              &:last-child {
                border-bottom: none;
              }

              .review-rating {
                margin-bottom: 4px;
              }

              .review-text {
                margin: 0 0 4px 0;
                font-size: 12px;
                color: #666;
                line-height: 1.4;
              }

              .review-time {
                margin: 0;
                font-size: 11px;
                color: #bfbfbf;
              }
            }
          }

          .no-reviews {
            padding: 16px 0;
            text-align: center;
            color: #bfbfbf;
            font-size: 12px;
          }
        }

        .actions {
          display: flex;
          gap: 8px;

          :deep(.el-button) {
            flex: 1;
          }
        }
      }
    }
  }
}
</style>