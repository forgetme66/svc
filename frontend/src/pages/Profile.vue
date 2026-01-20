<template>
  <div class="profile-container">
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h1>个人信息</h1>
        </div>
        <div class="header-right">
          <el-dropdown>
            <span class="user-info">
              {{ authStore.user?.username }}
              <el-icon class="icon"><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
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
        <div class="profile-content">
          <!-- 个人信息卡片 -->
          <el-card class="info-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>个人信息</span>
              </div>
            </template>

            <el-form
              ref="profileFormRef"
              :model="profileForm"
              :rules="profileRules"
              label-width="100px"
              @submit.prevent="handleUpdateProfile"
            >
              <el-row :gutter="20">
                <el-col :xs="24" :sm="12" :md="12">
                  <el-form-item label="用户名" prop="username">
                    <el-input v-model="profileForm.username" disabled />
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="12" :md="12">
                  <el-form-item label="邮箱" prop="email">
                    <el-input v-model="profileForm.email" disabled />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :xs="24" :sm="12" :md="12">
                  <el-form-item label="姓名" prop="real_name">
                    <el-input v-model="profileForm.real_name" placeholder="请输入真实姓名" />
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="12" :md="12">
                  <el-form-item label="联系电话" prop="phone">
                    <el-input v-model="profileForm.phone" placeholder="请输入联系电话" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :xs="24" :sm="12" :md="12">
                  <el-form-item label="学院" prop="college">
                    <el-input v-model="profileForm.college" placeholder="请输入学院" />
                  </el-form-item>
                </el-col>
                <el-col :xs="24" :sm="12" :md="12">
                  <el-form-item label="专业" prop="major">
                    <el-input v-model="profileForm.major" placeholder="请输入专业" />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row v-if="profileForm.student_id" :gutter="20">
                <el-col :xs="24" :sm="12" :md="12">
                  <el-form-item label="学号" prop="student_id">
                    <el-input v-model="profileForm.student_id" disabled />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row v-if="profileForm.teacher_id" :gutter="20">
                <el-col :xs="24" :sm="12" :md="12">
                  <el-form-item label="工号" prop="teacher_id">
                    <el-input v-model="profileForm.teacher_id" disabled />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :xs="24">
                  <el-form-item>
                    <el-button type="primary" native-type="submit" :loading="updateLoading">
                      保存信息
                    </el-button>
                    <el-button @click="handleResetProfile">
                      重置
                    </el-button>
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </el-card>

          <!-- 修改密码卡片 -->
          <el-card class="password-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>修改密码</span>
              </div>
            </template>

            <el-form
              ref="passwordFormRef"
              :model="passwordForm"
              :rules="passwordRules"
              label-width="100px"
              @submit.prevent="handleChangePassword"
            >
              <el-row :gutter="20">
                <el-col :xs="24" :sm="12">
                  <el-form-item label="旧密码" prop="oldPassword">
                    <el-input
                      v-model="passwordForm.oldPassword"
                      type="password"
                      placeholder="请输入旧密码"
                      show-password
                    />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :xs="24" :sm="12">
                  <el-form-item label="新密码" prop="newPassword">
                    <el-input
                      v-model="passwordForm.newPassword"
                      type="password"
                      placeholder="请输入新密码（至少8位，包含大小写字母和数字）"
                      show-password
                    />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :xs="24" :sm="12">
                  <el-form-item label="确认密码" prop="confirmPassword">
                    <el-input
                      v-model="passwordForm.confirmPassword"
                      type="password"
                      placeholder="请再次输入新密码"
                      show-password
                    />
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :xs="24">
                  <el-form-item>
                    <el-button type="danger" native-type="submit" :loading="passwordLoading">
                      修改密码
                    </el-button>
                    <el-button @click="handleResetPassword">
                      重置
                    </el-button>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-alert
                title="密码要求"
                :description="passwordRequirement"
                type="info"
                :closable="false"
                style="margin-top: 20px"
              />
            </el-form>
          </el-card>
        </div>
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
import { ArrowDown } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const isTeacher = computed(() => authStore.user?.user_type === 'teacher' || authStore.user?.user_type === 'admin')

// 状态
const activeMenu = ref('/profile')
const updateLoading = ref(false)
const passwordLoading = ref(false)
const originalProfile = ref({})

const profileForm = ref({
  username: '',
  email: '',
  real_name: '',
  phone: '',
  college: '',
  major: '',
  student_id: '',
  teacher_id: ''
})

const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 表单规则
const profileRules = {
  real_name: [
    { max: 100, message: '姓名长度不能超过100个字符', trigger: 'blur' }
  ],
  phone: [
    { pattern: /^[0-9\-\+\(\)]{0,20}$/, message: '联系电话格式不正确', trigger: 'blur' }
  ],
  college: [
    { max: 100, message: '学院长度不能超过100个字符', trigger: 'blur' }
  ],
  major: [
    { max: 100, message: '专业长度不能超过100个字符', trigger: 'blur' }
  ]
}

const passwordRules = {
  oldPassword: [
    { required: true, message: '旧密码不能为空', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '新密码不能为空', trigger: 'blur' },
    { min: 8, message: '新密码至少需要8个字符', trigger: 'blur' },
    { pattern: /[A-Z]/, message: '新密码必须包含大写字母', trigger: 'blur' },
    { pattern: /[a-z]/, message: '新密码必须包含小写字母', trigger: 'blur' },
    { pattern: /[0-9]/, message: '新密码必须包含数字', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '确认密码不能为空', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.value.newPassword) {
          callback(new Error('两次密码输入不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const passwordRequirement = '密码至少需要8个字符，且必须包含大小写字母和数字'

// 加载用户个人信息
const loadProfile = async () => {
  try {
    const response = await authAPI.getProfile()

    if (response.data.code === 200) {
      const userInfo = response.data.data
      profileForm.value = {
        username: userInfo.username,
        email: userInfo.email,
        real_name: userInfo.real_name || '',
        phone: userInfo.phone || '',
        college: userInfo.college || '',
        major: userInfo.major || '',
        student_id: userInfo.student_id || '',
        teacher_id: userInfo.teacher_id || ''
      }
      originalProfile.value = { ...profileForm.value }
    } else {
      ElMessage.error(response.data.message || '加载个人信息失败')
    }
  } catch (error) {
    console.error('Load profile error:', error)
    ElMessage.error(error.response?.data?.message || error.message || '加载个人信息失败')
  }
}

// 更新个人信息
const handleUpdateProfile = async () => {
  if (!profileFormRef.value) return

  await profileFormRef.value.validate()

  updateLoading.value = true
  try {
    const response = await authAPI.updateProfile({
      real_name: profileForm.value.real_name,
      phone: profileForm.value.phone,
      college: profileForm.value.college,
      major: profileForm.value.major
    })

    if (response.data.code === 200) {
      ElMessage.success('个人信息更新成功')
      originalProfile.value = { ...profileForm.value }
      // 更新本地用户信息
      authStore.user = response.data.data
    } else {
      ElMessage.error(response.data.message || '更新失败')
    }
  } catch (error) {
    console.error('Update profile error:', error)
    ElMessage.error(error.response?.data?.message || error.message || '更新失败')
  } finally {
    updateLoading.value = false
  }
}

// 重置个人信息表单
const handleResetProfile = () => {
  profileForm.value = { ...originalProfile.value }
}

// 修改密码
const handleChangePassword = async () => {
  if (!passwordFormRef.value) return

  await passwordFormRef.value.validate()

  passwordLoading.value = true
  try {
    const response = await authAPI.changePassword(
      passwordForm.value.oldPassword,
      passwordForm.value.newPassword,
      passwordForm.value.confirmPassword
    )

    if (response.data.code === 200) {
      ElMessage.success('密码修改成功，请重新登录')
      // 清除auth并重定向到登录页
      authStore.clearAuth()
      router.push('/login')
    } else {
      ElMessage.error(response.data.message || '修改失败')
    }
  } catch (error) {
    console.error('Change password error:', error)
    ElMessage.error(error.response?.data?.message || error.message || '修改失败')
  } finally {
    passwordLoading.value = false
  }
}

// 重置密码表单
const handleResetPassword = () => {
  passwordForm.value = {
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  }
  if (passwordFormRef.value) {
    passwordFormRef.value.clearValidate()
  }
}

const profileFormRef = ref()
const passwordFormRef = ref()

// 登出
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
  loadProfile()
})
</script>

<style scoped>
.profile-container {
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
    background-color: #f5f7fa;
    border-right: 1px solid #dcdfe6;
  }

  :deep(.el-main) {
    padding: 20px;
    overflow-y: auto;
  }

  .profile-content {
    padding: 0;
    max-width: 100%;
  }

  .info-card,
  .password-card {
    margin-bottom: 20px;
    border-radius: 6px;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
  }

  :deep(.el-form-item) {
    margin-bottom: 18px;
  }

  :deep(.el-alert) {
    padding: 12px 16px;
  }
}
</style>
