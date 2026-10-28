<template>
  <aside
    class="flex h-full shrink-0 flex-col border-r border-gray-100 bg-white transition-[width] duration-200 dark:border-dark-border dark:bg-dark-card"
    :class="{ '!w-0 border-r-0 overflow-hidden': collapsed }"
    :style="{ width: collapsed ? '0px' : width + 'px' }"
  >
    <div class="px-3 pt-3">
      <!-- 头像：点击弹出向下导航（首页 / 关于 / 用户中心 / 退出） -->
      <div class="relative" ref="avatarRef">
        <button
          type="button"
          class="flex w-full items-center gap-2.5 rounded px-2 py-1.5 transition-colors duration-200 hover:bg-black/5 dark:hover:bg-white/10"
          @click="open = !open"
        >
          <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary text-sm font-medium text-white">
            {{ initial }}
          </span>
          <span class="min-w-0 flex-1 text-left">
            <span class="block truncate text-sm text-ink dark:text-gray-100">{{ username }}</span>
            <span class="block truncate text-[11px] text-ink-3">{{ email }}</span>
          </span>
          <svg viewBox="0 0 24 24" class="h-4 w-4 shrink-0 text-ink-3 transition-transform duration-200" :class="open ? 'rotate-180' : ''" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6" /></svg>
        </button>

        <!-- 向下展开的导航菜单 -->
        <div
          v-if="open"
          class="card absolute left-2 right-2 top-full z-20 mt-1.5 overflow-hidden p-1 text-sm"
        >
          <RouterLink v-for="item in navItems" :key="item.to" :to="item.to" class="flex items-center gap-2 rounded px-3 py-2 text-ink-2 transition-colors duration-200 hover:bg-black/5 dark:text-gray-300 dark:hover:bg-white/10" @click="open = false">
            <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="item.icon"></svg>
            {{ item.label }}
          </RouterLink>
          <button type="button" class="flex w-full items-center gap-2 rounded px-3 py-2 text-left text-danger transition-colors duration-200 hover:bg-danger/10" @click="logout">
            <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9" /></svg>
            退出登录
          </button>
        </div>
      </div>
    </div>

    <div class="flex items-center justify-between px-3 pt-2">
      <button type="button" class="btn-primary !px-3 !py-1.5 w-full" @click="$emit('new-session')">
        <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M12 5v14M5 12h14" /></svg>
        新建会话
      </button>
    </div>

    <!-- 会话列表 -->
    <div class="mt-2 flex-1 overflow-y-auto px-2 pb-2">
      <div
        v-for="s in sessions"
        :key="s.id"
        class="group relative mb-1 cursor-pointer rounded px-3 py-2.5 transition-colors duration-200"
        :class="s.id === currentSessionId
          ? 'bg-primary-light/70 dark:bg-primary-dark/25'
          : 'hover:bg-black/5 dark:hover:bg-white/10'"
        @click="$emit('select', s.id)"
      >
        <div v-if="editingId === s.id" class="flex items-center gap-1" @click.stop>
          <input
            v-model="editTitle"
            class="input !px-2 !py-1 text-[13px]"
            maxlength="100"
            @keydown.enter="saveRename(s)"
            @keydown.esc="editingId = null"
          />
        </div>
        <template v-else>
          <div class="flex items-center justify-between gap-1">
            <span class="truncate text-[13px] text-ink dark:text-gray-100">{{ s.title || '新对话' }}</span>
            <span class="flex shrink-0 gap-0.5 opacity-0 transition-opacity duration-200 group-hover:opacity-100">
              <button type="button" class="rounded p-1 text-ink-3 hover:bg-black/10 hover:text-ink dark:hover:bg-white/15" title="重命名" @click.stop="startRename(s)">
                <svg viewBox="0 0 24 24" class="h-3.5 w-3.5" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 3a2.85 2.83 0 114 4L7.5 20.5 2 22l1.5-5.5z" /></svg>
              </button>
              <button type="button" class="rounded p-1 text-ink-3 hover:bg-danger/10 hover:text-danger" title="删除" @click.stop="$emit('delete', s)">
                <svg viewBox="0 0 24 24" class="h-3.5 w-3.5" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2m3 0v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6" /></svg>
              </button>
            </span>
          </div>
          <div class="mt-0.5 text-[11px] text-ink-3">{{ formatTime(s.updated_at) }}</div>
        </template>
      </div>

      <div v-if="!sessions.length" class="mt-6 text-center text-xs text-ink-3">
        暂无会话，点击上方按钮开始对话
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import { toast } from '@/utils/toast'

const props = defineProps({
  sessions: { type: Array, default: () => [] },
  currentSessionId: { type: Number, default: null },
  collapsed: { type: Boolean, default: false },
  // 侧栏宽度（px，可通过拖拽调节）
  width: { type: Number, default: 240 },
})
const emit = defineEmits(['new-session', 'select', 'rename', 'delete'])

const auth = useAuthStore()
const router = useRouter()

const editingId = ref(null)
const editTitle = ref('')
const open = ref(false)
const avatarRef = ref(null)

const username = computed(() => auth.user?.username || '')
const email = computed(() => auth.user?.email || '')
const initial = computed(() => (username.value || 'U').slice(0, 1).toUpperCase())

const navItems = [
  { label: '首页', to: '/', icon: '<path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><path d="M9 22V12h6v10"/>' },
  { label: '设置', to: '/settings', icon: '<path d="M12 20h9M16.5 3.5a2.12 2.12 0 013 3L7 19l-4 1 1-4z"/>' },
  { label: '关于', to: '/about', icon: '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>' },
  { label: '用户中心', to: '/profile', icon: '<path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/>' },
]

function onClickOutside(e) {
  if (avatarRef.value && !avatarRef.value.contains(e.target)) open.value = false
}

onMounted(() => document.addEventListener('click', onClickOutside))
onBeforeUnmount(() => document.removeEventListener('click', onClickOutside))

function logout() {
  open.value = false
  auth.logout()
  toast('已退出登录')
  router.push('/')
}

function formatTime(v) {
  if (!v) return ''
  const d = new Date(v)
  const now = new Date()
  const sameDay = d.toDateString() === now.toDateString()
  if (sameDay) return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  return d.toLocaleDateString('zh-CN', { month: 'numeric', day: 'numeric' })
}

function startRename(s) {
  editingId.value = s.id
  editTitle.value = s.title || ''
}
function saveRename(s) {
  const title = editTitle.value.trim()
  editingId.value = null
  if (title && title !== s.title) emit('rename', { id: s.id, title })
}
</script>
