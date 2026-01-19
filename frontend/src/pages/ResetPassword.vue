<template>
  <div class="reset-password-container">
    <div class="form-card">
      <h2>重置密码</h2>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
      >
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="新密码（至少8个字符，需含大小写字母和数字）"
            size="large"
            show-password
          />
        </el-form-item>

        <el-form-item prop="confirm_password">
          <el-input
            v-model="form.confirm_password"
            type="password"
            placeholder="确认密码"
            size="large"
            show-password
          />
        </el-form-item>

        <el-button
          type="primary"
          :loading="loading"
          @click="handleReset"
          style="width: 100%"
          size="large"
        >
          重置密码
        </el-button>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authAPI } from '@/api/auth'

const router = useRouter()
const route = useRoute()
const formRef = ref()
const loading = ref(false)

const form = reactive({
  password: '',
  confirm_password: ''
})

const validatePassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入新密码'))
  } else if (value.length < 8) {
    callback(new Error('密码至少需要8个字符'))
  } else if (!/[A-Z]/.test(value)) {
    callback(new Error('密码必须包含大写字母'))
  } else if (!/[a-z]/.test(value)) {
    callback(new Error('密码必须包含小写字母'))
  } else if (!/\d/.test(value)) {
    callback(new Error('密码必须包含数字'))
  } else {
    callback()
  }
}

const validateConfirmPassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请确认密码'))
  } else if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  password: [{ validator: validatePassword, trigger: 'blur' }],
  confirm_password: [{ validator: validateConfirmPassword, trigger: 'blur' }]
}

const handleReset = async () => {
  try {
    await formRef.value.validate()
    
    loading.value = true
    const token = route.params.token
    const response = await authAPI.resetPassword(token, form.password)

    if (response.data.code === 200) {
      ElMessage.success('密码重置成功，请登录')
      router.push('/login')
    } else {
      ElMessage.error(response.data.message || '重置失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '重置失败，请检查链接是否有效')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.reset-password-container {
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
      margin-bottom: 30px;
    }
  }
}
</style>
