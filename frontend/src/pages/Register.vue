<template>
  <div class="register-container">
    <div class="register-card">
      <h1 class="title">毕业设计指导网站</h1>
      <h2 class="subtitle">新用户注册</h2>
      
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        @submit.prevent="handleRegister"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名（3-80个字符）"
          />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="form.email"
            type="email"
            placeholder="请输入邮箱地址"
          />
        </el-form-item>

        <el-form-item label="真实姓名" prop="real_name">
          <el-input
            v-model="form.real_name"
            placeholder="请输入真实姓名"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="至少8个字符，需含大小写字母和数字"
            show-password
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirm_password">
          <el-input
            v-model="form.confirm_password"
            type="password"
            placeholder="请再次输入密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="身份" prop="user_type">
          <el-select v-model="form.user_type" placeholder="请选择身份">
            <el-option label="学生" value="student" />
            <el-option label="教师" value="teacher" />
          </el-select>
        </el-form-item>

        <el-form-item v-if="form.user_type === 'student'" label="学号" prop="student_id">
          <el-input
            v-model="form.student_id"
            placeholder="请输入学号"
          />
        </el-form-item>

        <el-form-item v-if="form.user_type === 'teacher'" label="工号" prop="teacher_id">
          <el-input
            v-model="form.teacher_id"
            placeholder="请输入工号"
          />
        </el-form-item>

        <el-form-item label="学院" prop="college">
          <el-input
            v-model="form.college"
            placeholder="请输入学院"
          />
        </el-form-item>

        <el-form-item v-if="form.user_type === 'student'" label="专业" prop="major">
          <el-input
            v-model="form.major"
            placeholder="请输入专业"
          />
        </el-form-item>

        <el-form-item label="手机号" prop="phone">
          <el-input
            v-model="form.phone"
            placeholder="请输入手机号"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            @click="handleRegister"
            style="width: 100%"
          >
            注册
          </el-button>
        </el-form-item>

        <p class="footer-text">
          已有账号？
          <router-link to="/login">立即登录</router-link>
        </p>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authAPI } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  email: '',
  real_name: '',
  password: '',
  confirm_password: '',
  user_type: 'student',
  student_id: '',
  teacher_id: '',
  college: '',
  major: '',
  phone: ''
})

const validateUsername = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入用户名'))
    callback(new Error('用户名长度需要3-80个字符'))
  } else {
    callback()
  }
}

const validatePassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入密码'))
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
  username: [{ validator: validateUsername, trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  real_name: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  password: [{ validator: validatePassword, trigger: 'blur' }],
  confirm_password: [{ validator: validateConfirmPassword, trigger: 'blur' }],
  user_type: [{ required: true, message: '请选择身份', trigger: 'change' }],
  college: [{ required: true, message: '请输入学院', trigger: 'blur' }],
  major: [{ required: true, message: '请输入专业', trigger: 'blur' }]
}

const handleRegister = async () => {
  await formRef.value.validate()
  
  loading.value = true
  try {
    const response = await authAPI.register({
      username: form.username,
      email: form.email,
      real_name: form.real_name,
      password: form.password,
      user_type: form.user_type,
      student_id: form.student_id,
      teacher_id: form.teacher_id,
      college: form.college,
      major: form.major,
      phone: form.phone
    })

    if (response.data.code === 201) {
      ElMessage.success('注册成功，请登录')
      router.push('/login')
    } else {
      ElMessage.error(response.data.message || '注册失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '注册失败，请检查网络连接')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;

  .register-card {
    background: white;
    border-radius: 8px;
    padding: 40px;
    width: 100%;
    max-width: 500px;
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

    .footer-text {
      text-align: center;
      color: #666;
      margin-top: 20px;

      a {
        color: #667eea;
        text-decoration: none;
        font-weight: bold;

        &:hover {
          text-decoration: underline;
        }
      }
    }
  }
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}
</style>
