import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/pages/Register.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Login.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/pages/ForgotPassword.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/reset-password/:token',
    name: 'ResetPassword',
    component: () => import('@/pages/ResetPassword.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/pages/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/files',
    name: 'Files',
    component: () => import('@/pages/Files.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/teacher-management',
    name: 'TeacherManagement',
    component: () => import('@/pages/TeacherManagement.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/student-documents',
    name: 'StudentDocuments',
    component: () => import('@/pages/StudentDocuments.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin-management',
    name: 'AdminManagement',
    component: () => import('@/pages/AdminManagement.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/inbox',
    name: 'Inbox',
    component: () => import('@/pages/Inbox.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/pages/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/review-teacher',
    name: 'ReviewTeacher',
    component: () => import('@/pages/ReviewTeacher.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/review-statistics',
    name: 'ReviewStatistics',
    component: () => import('@/pages/ReviewStatistics.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/teacher-ratings-display',
    name: 'TeacherRatingsDisplay',
    component: () => import('@/pages/TeacherRatingsDisplay.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/debug',
    name: 'SystemDebug',
    component: () => import('@/pages/SystemDebug.vue')
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/pages/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 导航守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const isLoggedIn = authStore.isLoggedIn()
  
  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/login')
  } else if (to.meta.requiresGuest && isLoggedIn) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
