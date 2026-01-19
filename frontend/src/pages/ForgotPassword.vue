<template>
  <div class="forgot-password-container">
    <div class="form-card">
      <h2>重置密码</h2>
      <p class="description">请输入您的邮箱地址，我们将发送密码重置链接到您的邮箱</p>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
      >
        <el-form-item prop="email">
          <el-input
            v-model="form.email"
            type="email"
            placeholder="请输入注册邮箱"
            size="large"
          />
        </el-form-item>

        <el-button
          type="primary"
          :loading="loading"
          @click="handleSubmit"
          style="width: 100%"
          size="large"
        >
          发送重置链接
        </el-button>
      </el-form>

      <p class="back-link">
        <router-link to="/login">返回登录</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { authAPI } from '@/api/auth'

const formRef = ref()
const loading = ref(false)

const form = reactive({
  email: ''
})

const rules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ]
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    
    loading.value = true
    const response = await authAPI.forgotPassword(form.email)

    if (response.data.code === 200) {
      ElMessage.success(response.data.message)
      form.email = ''
    } else {
      ElMessage.error(response.data.message || '操作失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '发送失败，请检查网络连接')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.forgot-password-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;

  .form-card {
    background: white;
    border-radius: 8px;
    padding: 40px;
    width: 100%;
    max-width: 400px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);

    h2 {
      text-align: center;
      color: #333;
      margin-bottom: 15px;
    }

    .description {
      text-align: center;
      color: #666;
      font-size: 14px;
      margin-bottom: 25px;
    }

    .back-link {
      text-align: center;
      margin-top: 20px;

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
</style>
