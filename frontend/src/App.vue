<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { authAPI } from '@/api/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

onMounted(async () => {
  // 如果有 token 但没有用户信息，尝试获取用户信息
  if (authStore.accessToken && !authStore.user) {
    try {
      const response = await authAPI.getProfile();
      if (response.data.code === 200) {
        authStore.setUser(response.data.data);
      }
    } catch (error) {
      console.error('Failed to restore session:', error);
      // 如果获取失败（例如 token 过期），清除认证信息并跳转登录
      authStore.clearAuth();
      if (router.currentRoute.value.path !== '/login' && router.currentRoute.value.path !== '/register') {
        router.push('/login');
      }
    }
  }
});
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
  width: 100%;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #fafafa;
}
</style>
