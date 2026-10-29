<template>
  <div class="flex h-full overflow-hidden">
    <!-- 左侧会话列表 -->
    <SessionSidebar
      :sessions="chat.sessions"
      :current-session-id="chat.currentSessionId"
      :collapsed="chat.sidebarCollapsed"
      :width="sidebarWidth"
      @new-session="newSession"
      @select="selectSession"
      @rename="renameSession"
      @delete="confirmDelete"
    />

    <!-- 左侧栏宽度调节条（可左右拖动） -->
    <div
      v-if="!chat.sidebarCollapsed"
      class="group flex shrink-0 cursor-col-resize items-stretch justify-center"
      style="width: 8px"
      @mousedown="startDrag('sidebar', $event)"
    >
      <div class="w-px bg-gray-200 transition-all duration-200 group-hover:w-[3px] group-hover:bg-primary/60 dark:bg-dark-border"></div>
    </div>

    <!-- 中间对话区 -->
    <div class="flex min-w-0 flex-1 flex-col">
      <!-- 工具条 -->
      <div class="flex h-12 shrink-0 items-center justify-between border-b border-gray-100 px-3 dark:border-dark-border">
        <div class="flex items-center gap-2">
          <button type="button" class="btn-ghost !p-1.5" title="折叠会话列表" @click="chat.sidebarCollapsed = !chat.sidebarCollapsed">
            <svg viewBox="0 0 24 24" class="h-4.5 w-4.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 6h16M4 12h16M4 18h16" /></svg>
          </button>
          <span class="truncate text-sm font-medium text-ink dark:text-gray-100">
            {{ chat.currentSession?.title || '新对话' }}
          </span>
          <span
            v-if="chat.fileName"
            class="chip shrink-0 bg-success/10 text-success"
            title="点击清除文档引用"
          >
            📄 {{ chat.fileName }}
            <button type="button" class="ml-1 text-success hover:text-danger" @click="chat.clearFile()">×</button>
          </span>
        </div>
        <button type="button" class="btn-ghost !p-1.5" title="设置（模型参数等）" @click="router.push('/settings')">
          <svg viewBox="0 0 24 24" class="h-4.5 w-4.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 11-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 11-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 11-2.83-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 110-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 112.83-2.83l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 114 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 112.83 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 110 4h-.09a1.65 1.65 0 00-1.51 1z" /></svg>
        </button>
      </div>

      <!-- 消息区 -->
      <div id="chat-scroll" ref="scrollEl" class="flex-1 overflow-y-auto px-4 py-5 sm:px-8">
        <!-- 空状态 -->
        <div v-if="!chat.messages.length" class="mx-auto mt-10 max-w-xl text-center">
          <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-primary-light/70 text-primary dark:bg-primary-dark/20">
            <svg viewBox="0 0 24 24" class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" /></svg>
          </div>
          <h2 class="mt-4 text-lg font-semibold text-ink dark:text-gray-100">开始新的对话</h2>
          <p class="mt-1.5 text-sm text-ink-2 dark:text-gray-300">支持 Markdown 与代码高亮，可上传文档基于内容提问</p>
          <div class="mt-5 flex flex-wrap justify-center gap-2">
            <button
              v-for="q in suggestions"
              :key="q"
              type="button"
              class="rounded-full border border-gray-200 px-3.5 py-1.5 text-sm text-ink-2 transition-colors duration-200 hover:border-primary hover:text-primary dark:border-dark-border dark:text-gray-300 dark:hover:text-primary"
              @click="quickAsk(q)"
            >
              {{ q }}
            </button>
          </div>
        </div>

        <!-- 消息列表 -->
        <div v-else class="mx-auto max-w-3xl space-y-5">
          <div
            v-for="msg in chat.messages"
            :key="msg.id"
            class="flex gap-3"
            :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
          >
            <div
              v-if="msg.role === 'assistant'"
              class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary text-white"
            >
              <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z" /></svg>
            </div>

            <div
              class="max-w-[85%] rounded px-4 py-2.5 text-sm"
              :class="msg.role === 'user'
                ? 'bg-primary-light/80 text-ink dark:bg-primary-dark/30 dark:text-gray-100'
                : 'card'"
            >
              <div v-if="msg.role === 'user'" class="whitespace-pre-wrap break-words">{{ msg.content }}</div>
              <div v-else class="relative">
                <MarkdownView :content="msg.content" />
                <span v-if="msg.streaming" class="streaming-cursor"></span>
                <div v-if="msg.content && !msg.streaming" class="mt-2 flex justify-end">
                  <button type="button" class="text-xs text-ink-3 hover:text-primary" @click="copyMsg(msg.content)">复制</button>
                </div>
              </div>
            </div>
          </div>

          <!-- 生成中加载状态 -->
          <div v-if="chat.streaming && !chat.messages.length" class="flex items-center gap-2 px-4 text-sm text-ink-3">
            <span class="inline-block h-3.5 w-3.5 animate-spin rounded-full border-2 border-primary border-t-transparent"></span>
            AI 正在思考…
          </div>
        </div>
      </div>

      <!-- 输入区 -->
      <div class="shrink-0 border-t border-gray-100 px-4 py-3 dark:border-dark-border">
        <div class="mx-auto max-w-3xl">
          <!-- 工具切换：AI对话 / AI生图 / 文档解析 -->
          <div class="mb-2 flex items-center gap-1">
            <button
              v-for="t in tools"
              :key="t.to"
              type="button"
              class="rounded-full px-3 py-1 text-sm transition-colors duration-200"
              :class="t.active
                ? 'bg-primary-light/70 font-medium text-primary dark:bg-primary-dark/25 dark:text-primary'
                : 'text-ink-2 hover:bg-black/5 dark:text-gray-300 dark:hover:bg-white/10'"
              @click="goTool(t.to)"
            >
              {{ t.label }}
            </button>
          </div>
          <div class="card flex items-end gap-2 p-2">
            <!-- 模型选择器：未选择显示 +，选中亮蓝色显示模型名 -->
            <ModelPicker />
            <button
              type="button"
              class="btn-ghost !p-2 shrink-0"
              title="上传文档（TXT / Markdown / PDF，≤10MB）"
              @click="fileInput?.click()"
            >
              <svg viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48" /></svg>
            </button>
            <textarea
              ref="inputEl"
              v-model="draft"
              rows="1"
              class="max-h-40 min-h-[40px] flex-1 resize-none bg-transparent px-2 py-2 text-sm text-ink placeholder:text-ink-3 outline-none dark:text-gray-100 dark:placeholder:text-gray-500"
              :placeholder="chat.fileName ? '基于文档提问…' : '输入问题，Enter 发送，Shift+Enter 换行'"
              :maxlength="20000"
              @input="autosize"
              @keydown.enter.exact.prevent="send"
              @keydown.enter.shift="autosizeNext"
            />
            <div class="flex shrink-0 items-center gap-1.5">
              <span v-if="draft.length > 15000" class="text-[11px]" :class="draft.length >= 20000 ? 'text-danger' : 'text-warning'">{{ draft.length }}/20000</span>
              <button
                v-if="chat.streaming"
                type="button"
                class="btn-primary !px-3"
                title="停止生成"
                @click="chat.stopGenerate()"
              >
                <svg viewBox="0 0 24 24" class="h-4 w-4" fill="currentColor"><rect x="6" y="6" width="12" height="12" rx="1.5" /></svg>
                停止
              </button>
              <button
                v-else
                type="button"
                class="btn-primary !p-2"
                :disabled="!draft.trim()"
                title="发送"
                @click="send"
              >
                <svg viewBox="0 0 24 24" class="h-4.5 w-4.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4z" /></svg>
              </button>
            </div>
          </div>
          <p class="mt-1.5 text-center text-[11px] text-ink-3">内容由 AI 生成，请注意甄别 · 登录后会话自动保存</p>
        </div>
      </div>

      <input ref="fileInput" type="file" accept=".txt,.md,.markdown,.pdf" class="hidden" @change="onFileChange" />
    </div>

    <!-- 删除确认 -->
    <BaseModal
      :show="deleteTarget !== null"
      title="删除会话"
      confirm-text="删除"
      @close="deleteTarget = null"
      @confirm="doDelete"
    >
      <p class="text-sm text-ink-2 dark:text-gray-300">
        确定删除会话「{{ deleteTarget?.title }}」吗？会话内全部消息将一并删除，此操作不可恢复。
      </p>
    </BaseModal>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { uploadFile } from '@/api'
import BaseModal from '@/components/BaseModal.vue'
import MarkdownView from '@/components/MarkdownView.vue'
import ModelPicker from '@/components/ModelPicker.vue'
import SessionSidebar from '@/components/SessionSidebar.vue'
import { useChatStore } from '@/stores/chat'
import { copyText, toast } from '@/utils/toast'

const chat = useChatStore()
const route = useRoute()
const router = useRouter()

const draft = ref('')
const inputEl = ref(null)
const fileInput = ref(null)
const scrollEl = ref(null)
const deleteTarget = ref(null)

// 左侧栏宽度（px，可拖拽调节，本地持久化）
const sidebarWidth = ref(parseInt(localStorage.getItem('ai_sidebar_width') || '240', 10))

const clamp = (v, min, max) => Math.min(max, Math.max(min, v))

function startDrag(side, e) {
  e.preventDefault()
  document.body.classList.add('resizing')
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
  const startX = e.clientX
  const startW = sidebarWidth.value

  const onMove = (ev) => {
    const dx = ev.clientX - startX
    // 左栏：向右拖变宽，向左拖变窄
    sidebarWidth.value = clamp(startW + dx, 180, 440)
  }
  const onUp = () => {
    document.body.classList.remove('resizing')
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
    document.removeEventListener('mousemove', onMove)
    document.removeEventListener('mouseup', onUp)
    localStorage.setItem('ai_sidebar_width', String(sidebarWidth.value))
  }
  document.addEventListener('mousemove', onMove)
  document.addEventListener('mouseup', onUp)
}

const suggestions = ['用 Python 写一个快速排序', '总结一下 TCP 三次握手', '帮我拟定一份周报提纲', '解释一下 Vue 的响应式原理']

// 输入框上方的工具切换（AI对话为当前页）
const tools = [
  { label: 'AI对话', to: '/chat', active: true },
  { label: 'AI生图', to: '/draw', active: false },
  { label: '文档解析', to: '/files', active: false },
]

function goTool(to) {
  if (to === '/chat') return
  router.push(to)
}

function autosize() {
  const el = inputEl.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 160) + 'px'
}
function autosizeNext() {
  requestAnimationFrame(autosize)
}

function send() {
  const content = draft.value.trim()
  if (!content || chat.streaming) return
  draft.value = ''
  if (inputEl.value) {
    inputEl.value.style.height = 'auto'
  }
  chat.sendMessage(content)
}

function quickAsk(q) {
  chat.sendMessage(q)
}

async function newSession() {
  try {
    await chat.createSession()
  } catch (e) {
    toast(e.message, 'error')
  }
}

async function selectSession(id) {
  if (id === chat.currentSessionId) return
  try {
    await chat.loadMessages(id)
    chat.applySessionParams()
  } catch (e) {
    toast(e.message, 'error')
  }
}

async function renameSession({ id, title }) {
  try {
    await chat.renameSession(id, title)
    toast('已重命名')
  } catch (e) {
    toast(e.message, 'error')
  }
}

function confirmDelete(s) {
  deleteTarget.value = s
}
async function doDelete() {
  const id = deleteTarget.value?.id
  deleteTarget.value = null
  if (!id) return
  try {
    await chat.deleteSession(id)
    toast('会话已删除')
  } catch (e) {
    toast(e.message, 'error')
  }
}

async function onFileChange(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file) return
  try {
    const res = await uploadFile(file)
    chat.setFile(res.file_id, res.filename)
    toast(`文档已加载：${res.filename}（${res.chars} 字符）`)
    if (res.truncated) toast('文档较长，已截断为 20 万字符，超长部分未进入上下文', 'warning')
  } catch (err) {
    toast(err.message, 'error')
  }
}

function copyMsg(content) {
  copyText(content, '消息已复制')
}

onMounted(() => {
  chat.fetchSessions().catch(() => {})
  chat.scrollToBottom()

  // 支持首页输入框带问题跳转：/chat?q=xxx&deep=1
  const q = route.query.q
  if (q) {
    if (route.query.deep === '1') {
      chat.params.temperature = 0.3
      toast('深度思考模式已开启（温度 0.3）')
    }
    chat.sendMessage(String(q))
    // 清理 query，避免刷新页面重复发送
    router.replace({ query: {} })
  }
})
</script>
