<template>
  <div class="login-container">
    <div class="login-card">
      <h1 class="title">毕业设计指导网站</h1>
      <h2 class="subtitle">用户登录</h2>
      
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名或邮箱"
            size="large"
            prefix-icon="User"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            size="large"
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            @click="handleLogin"
            style="width: 100%"
            size="large"
          >
            登录
          </el-button>
        </el-form-item>

        <div class="form-links">
          <router-link to="/forgot-password">忘记密码？</router-link>
          <router-link to="/register">新用户注册</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { authAPI } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'
import { messagesAPI } from '@/api/messages'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名或邮箱', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  try {
    await formRef.value.validate()
    
    loading.value = true
    const response = await authAPI.login(form.username, form.password)

    if (response.data.code === 200) {
      const { access_token, refresh_token, user } = response.data.data
      authStore.setTokens(access_token, refresh_token)
      authStore.setUser(user)
      ElMessage.success('登录成功')
      // 直接跳转到首页，在首页检查消息
      router.push('/dashboard')
    } else {
      ElMessage.error(response.data.message || '登录失败')
    }
  } catch (error) {
    if (error.response?.data?.message) {
      ElMessage.error(error.response.data.message)
    } else {
      ElMessage.error('登录失败，请检查网络连接')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;

  .login-card {
    background: white;
    border-radius: 8px;
    padding: 50px 40px;
    width: 100%;
    max-width: 400px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);

    .title {
      text-align: center;
      color: #333;
      font-size: 28px;
      margin-bottom: 10px;
    }

    .subtitle {
      text-align: center;
      color: #666;
      font-size: 18px;
      margin-bottom: 30px;
    }

    .form-links {
      display: flex;
      justify-content: space-between;
      color: #667eea;
      font-size: 14px;

      a {
        color: #667eea;
        text-decoration: none;

        &:hover {
          text-decoration: underline;
        }
      }
    }
  }
}

:deep(.el-form-item) {
  margin-bottom: 22px;
}
</style>
