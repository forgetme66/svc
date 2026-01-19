<script setup>
import { ref, onMounted } from 'vue'

const systemInfo = ref({
  frontendUrl: window.location.href,
  backendUrl: '',
  isDevMode: import.meta.env.DEV,
  apiBaseUrl: '',
  backendStatus: 'checking...',
  apiBaseUrlStatus: 'checking...'
})

onMounted(async () => {
  // 计算API基础URL
  const protocol = window.location.protocol
  const hostname = window.location.hostname
  const port = 5000
  systemInfo.value.backendUrl = `${protocol}//${hostname}:${port}`
  systemInfo.value.apiBaseUrl = import.meta.env.DEV ? '/api' : `${protocol}//${hostname}:${port}/api`
  
  // 检查后端健康状态
  try {
    const response = await fetch(`${systemInfo.value.backendUrl}/api/health`)
    if (response.ok) {
      systemInfo.value.backendStatus = '✓ 正常运行'
    } else {
      systemInfo.value.backendStatus = '✗ 返回错误'
    }
  } catch (error) {
    systemInfo.value.backendStatus = '✗ 无法连接'
  }
  
  // 检查API基础URL
  try {
    const response = await fetch(`${systemInfo.value.apiBaseUrl}/health`)
    if (response.ok) {
      systemInfo.value.apiBaseUrlStatus = '✓ 正常工作'
    } else {
      systemInfo.value.apiBaseUrlStatus = '✗ 返回错误'
    }
  } catch (error) {
    systemInfo.value.apiBaseUrlStatus = '✗ 无法连接'
  }
})
</script>

<template>
  <div style="font-family: monospace; padding: 20px; background: #f5f5f5;">
    <h2>系统环境检查</h2>
    
    <div style="margin: 20px 0; padding: 10px; background: white; border-radius: 4px;">
      <div><strong>前端访问URL:</strong> {{ systemInfo.frontendUrl }}</div>
      <div><strong>开发模式:</strong> {{ systemInfo.isDevMode ? '✓ 是' : '✗ 否' }}</div>
      <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #ddd;">
        <strong>后端连接地址:</strong> {{ systemInfo.backendUrl }}
        <span :style="{ color: systemInfo.backendStatus.includes('✓') ? 'green' : 'red' }">
          {{ systemInfo.backendStatus }}
        </span>
      </div>
      <div style="margin-top: 10px;">
        <strong>API基础URL:</strong> {{ systemInfo.apiBaseUrl }}
        <span :style="{ color: systemInfo.apiBaseUrlStatus.includes('✓') ? 'green' : 'red' }">
          {{ systemInfo.apiBaseUrlStatus }}
        </span>
      </div>
    </div>
    
    <div style="margin-top: 20px; padding: 10px; background: #fff3cd; border-radius: 4px;">
      <strong>故障排查:</strong>
      <ul>
        <li v-if="!systemInfo.backendStatus.includes('✓')">
          ❌ 后端未运行或无法连接，请在 <code>backend</code> 目录运行：<code>python app.py</code>
        </li>
        <li v-if="!systemInfo.apiBaseUrlStatus.includes('✓')">
          ❌ API调用失败，检查：
          <ul>
            <li>后端是否正确启动</li>
            <li>端口5000是否被占用</li>
            <li>CORS配置是否正确</li>
            <li>前端dev server是否需要重启</li>
          </ul>
        </li>
        <li v-if="systemInfo.backendStatus.includes('✓') && systemInfo.apiBaseUrlStatus.includes('✓')">
          ✓ 系统连接正常，可以进行文件上传操作
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
code {
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 12px;
}
</style>
