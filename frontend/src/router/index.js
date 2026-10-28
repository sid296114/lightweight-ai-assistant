import { createRouter, createWebHistory } from 'vue-router'

import { tokenStore } from '@/api'

const routes = [
  { path: '/', name: 'home', component: () => import('@/views/HomeView.vue'), meta: { title: '首页' } },
  { path: '/chat', name: 'chat', component: () => import('@/views/ChatView.vue'), meta: { title: 'AI对话', requiresAuth: true } },
  { path: '/draw', name: 'draw', component: () => import('@/views/DrawView.vue'), meta: { title: 'AI生图', requiresAuth: true } },
  { path: '/files', name: 'files', component: () => import('@/views/FilesView.vue'), meta: { title: '文档解析', requiresAuth: true } },
  { path: '/about', name: 'about', component: () => import('@/views/AboutView.vue'), meta: { title: '关于' } },
  { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue'), meta: { title: '登录' } },
  { path: '/register', name: 'register', component: () => import('@/views/RegisterView.vue'), meta: { title: '注册' } },
  { path: '/profile', name: 'profile', component: () => import('@/views/ProfileView.vue'), meta: { title: '用户中心', requiresAuth: true } },
  { path: '/settings', name: 'settings', component: () => import('@/views/SettingsView.vue'), meta: { title: '设置', requiresAuth: true } },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  document.title = `${to.meta.title || '轻量AI助手'} · 轻量AI助手`
  if (to.meta.requiresAuth && !tokenStore.token) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if ((to.name === 'login' || to.name === 'register') && tokenStore.token) {
    return { name: 'chat' }
  }
  return true
})

export default router
