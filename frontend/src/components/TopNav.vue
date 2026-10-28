<template>
  <header class="sticky top-0 z-40 flex h-14 items-center justify-between border-b border-gray-100 bg-white/80 px-4 backdrop-blur dark:border-dark-border dark:bg-dark-bg/80">
    <div class="flex items-center gap-6">
      <!-- Logo -->
      <RouterLink to="/" class="flex items-center gap-2 shrink-0">
        <span class="flex h-7 w-7 items-center justify-center rounded-lg bg-primary text-white">
          <svg viewBox="0 0 24 24" class="h-4.5 w-4.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z" />
          </svg>
        </span>
        <span class="text-[15px] font-semibold text-ink dark:text-gray-100">轻量AI助手</span>
      </RouterLink>

      <!-- 导航菜单（按路由控制：对话页隐藏全部；首页只保留"首页"；其余页显示全部） -->
      <nav v-if="visibleMenus.length" class="hidden items-center gap-1 md:flex">
        <RouterLink
          v-for="item in visibleMenus"
          :key="item.to"
          :to="item.to"
          class="rounded px-3 py-1.5 text-sm transition-colors duration-200"
          :class="isActive(item.to)
            ? 'bg-primary-light/60 text-primary font-medium dark:bg-primary-dark/20 dark:text-primary'
            : 'text-ink-2 hover:bg-black/5 dark:text-gray-300 dark:hover:bg-white/10'"
        >
          {{ item.label }}
        </RouterLink>
      </nav>
    </div>

    <div class="flex items-center gap-2">
      <!-- 主题切换 -->
      <button type="button" class="btn-ghost !p-2" title="切换深浅色模式" @click="theme.toggle()">
        <svg v-if="!theme.dark" viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" />
        </svg>
        <svg v-else viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="4" />
          <path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32l1.41 1.41M2 12h2m16 0h2M4.93 19.07l1.41-1.41m11.32-11.32l1.41-1.41" />
        </svg>
      </button>

      <!-- 登录态：对话页头像移至左侧栏顶部，此处不再重复显示 -->
      <template v-if="!isChat">
        <template v-if="auth.isLoggedIn">
          <div class="relative" ref="menuRef">
            <button
              type="button"
              class="btn-ghost gap-1.5"
              @click="open = !open"
            >
              <span class="flex h-6 w-6 items-center justify-center rounded-full bg-primary text-xs text-white">
                {{ (auth.user?.username || 'U').slice(0, 1).toUpperCase() }}
              </span>
              <span class="max-w-[90px] truncate hidden sm:inline">{{ auth.user?.username }}</span>
              <svg viewBox="0 0 24 24" class="h-3.5 w-3.5" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6" /></svg>
            </button>
            <div
              v-if="open"
              class="card absolute right-0 top-full mt-1.5 w-40 overflow-hidden p-1 text-sm"
            >
              <RouterLink to="/profile" class="block rounded px-3 py-2 text-ink-2 hover:bg-black/5 dark:text-gray-300 dark:hover:bg-white/10" @click="open = false">
                用户中心
              </RouterLink>
              <button
                type="button"
                class="block w-full rounded px-3 py-2 text-left text-danger hover:bg-danger/10"
                @click="handleLogout"
              >
                退出登录
              </button>
            </div>
          </div>
        </template>
        <template v-else>
          <RouterLink to="/login" class="btn-text">登录</RouterLink>
          <RouterLink to="/register" class="btn-primary !py-1.5">注册</RouterLink>
        </template>
      </template>
    </div>
  </header>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const theme = useThemeStore()

const menus = [
  { label: '首页', to: '/' },
  { label: 'AI对话', to: '/chat' },
  { label: 'AI生图', to: '/draw' },
  { label: '文档解析', to: '/files' },
  { label: '关于', to: '/about' },
]

// 对话页：沉浸式顶栏（隐藏导航菜单，首页/关于入口在左侧栏头像下拉）
const isChat = computed(() => route.path === '/chat')

// 首页：顶栏只保留"首页"一项；其余页面显示全部菜单
const visibleMenus = computed(() => {
  if (route.path === '/chat') return []
  if (route.path === '/') return menus.filter((m) => m.to === '/')
  return menus
})

function isActive(to) {
  return route.path === to
}

const open = ref(false)
const menuRef = ref(null)

function onClickOutside(e) {
  if (menuRef.value && !menuRef.value.contains(e.target)) open.value = false
}

onMounted(() => document.addEventListener('click', onClickOutside))
onBeforeUnmount(() => document.removeEventListener('click', onClickOutside))

function handleLogout() {
  auth.logout()
  open.value = false
  router.push('/')
}
</script>
