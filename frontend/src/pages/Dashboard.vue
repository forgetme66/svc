<template>
  <div class="dashboard-container">
    <el-container>
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
        <el-aside width="200px" class="aside">
          <el-menu router :default-active="activeMenu">
            <el-menu-item index="/dashboard" route="/dashboard">
              <template #title>首页</template>
            </el-menu-item>
            <el-menu-item index="/files" route="/files">
              <template #title>文件管理</template>
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
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { authAPI } from '@/api/auth'
import { ArrowDown } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const activeMenu = ref('/dashboard')

const userTypeText = ref({
  'student': '学生',
  'teacher': '教师',
  'admin': '管理员'
}[authStore.user?.user_type] || '用户')

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('zh-CN')
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
</style>
