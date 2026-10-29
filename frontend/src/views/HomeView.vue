<template>
  <div class="relative flex min-h-full flex-col items-center overflow-hidden px-6 pb-14">
    <!-- 顶部光晕装饰 -->
    <div class="pointer-events-none absolute -top-24 left-1/2 h-72 w-[680px] -translate-x-1/2 rounded-full bg-primary/10 blur-3xl"></div>

    <div class="relative z-10 flex w-full flex-1 flex-col items-center justify-center py-10">
      <!-- 版本更新提示条（可关闭） -->
      <div
        v-if="showNotice"
        class="group inline-flex max-w-full items-center rounded-full border border-primary/20 bg-white/70 py-1.5 pl-4 pr-1.5 text-[13px] text-ink-2 backdrop-blur transition-colors duration-200 hover:border-primary/40 dark:bg-dark-card/70 dark:text-gray-300"
      >
        <button type="button" class="flex min-w-0 items-center gap-1.5" @click="goChat">
          <span class="truncate">轻量AI助手已更新：新增多模型接入与文档解析，更快响应、更低成本</span>
          <svg viewBox="0 0 24 24" class="h-3.5 w-3.5 shrink-0 text-ink-3 transition-transform duration-200 group-hover:translate-x-0.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6" /></svg>
        </button>
        <button
          type="button"
          class="ml-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-ink-3 transition-colors duration-200 hover:bg-black/5 hover:text-ink-2 dark:hover:bg-white/10 dark:hover:text-gray-200"
          title="关闭提示"
          @click="showNotice = false"
        >
          <svg viewBox="0 0 24 24" class="h-3.5 w-3.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18" /></svg>
        </button>
      </div>

      <!-- 大标题 -->
      <h1 class="mt-7 text-center text-4xl font-bold tracking-tight text-ink sm:text-5xl dark:text-gray-100">
        探索无限可能
      </h1>
      <p class="mt-3 text-center text-sm text-ink-2 dark:text-gray-300">
        轻量AI助手 · 面向学生、开发者与办公人群的在线 AI 工作台
      </p>

      <!-- 主输入框 -->
      <div class="mt-9 w-full max-w-2xl">
        <div class="card relative p-2 shadow-soft transition-all duration-200 focus-within:shadow-lg focus-within:ring-2 focus-within:ring-primary/30">
          <textarea
            ref="inputEl"
            v-model="draft"
            rows="1"
            maxlength="20000"
            class="block w-full resize-none bg-transparent px-3 pt-2.5 text-[15px] leading-6 text-ink placeholder:text-ink-3 outline-none dark:text-gray-100 dark:placeholder:text-gray-500"
            placeholder="问点什么，一起探索"
            @input="autosize"
            @keydown.enter.exact.prevent="send"
            @keydown.enter.shift="autosizeNext"
          ></textarea>

          <!-- 输入框左下功能按钮 -->
          <div class="flex items-center gap-1 px-1 pb-1">
            <button
              type="button"
              class="rounded-md px-2.5 py-1 text-[13px] transition-colors duration-200"
              :class="deepThink
                ? 'bg-primary-light/80 font-medium text-primary dark:bg-primary-dark/25 dark:text-primary'
                : 'text-ink-2 hover:bg-black/5 dark:text-gray-300 dark:hover:bg-white/10'"
              title="降低温度，让模型更严谨地深度作答"
              @click="deepThink = !deepThink"
            >
              🧠 深度思考
            </button>
            <button
              type="button"
              class="rounded-md px-2.5 py-1 text-[13px] text-ink-2 transition-colors duration-200 hover:bg-black/5 dark:text-gray-300 dark:hover:bg-white/10"
              title="联网搜索（即将上线）"
              @click="searchSoon"
            >
              🌐 智能搜索
            </button>
          </div>

          <!-- 右下发送按钮 -->
          <button
            type="button"
            class="btn-primary absolute bottom-3 right-3 !rounded-full !p-2.5"
            :disabled="!draft.trim()"
            title="发送"
            @click="send"
          >
            <svg viewBox="0 0 24 24" class="h-4.5 w-4.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4z" /></svg>
          </button>
        </div>
        <p class="mt-2.5 text-center text-[11px] text-ink-3">内容由 AI 生成，请注意甄别 · 登录后会话自动云端保存</p>
      </div>

      <!-- 三个功能入口 -->
      <div class="mt-8 flex flex-wrap items-center justify-center gap-3">
        <RouterLink
          v-for="entry in entries"
          :key="entry.to"
          :to="entry.to"
          class="group flex items-center gap-2 rounded-full border border-gray-200 bg-white/80 px-5 py-2.5 text-sm font-medium text-ink-2 backdrop-blur transition-all duration-200 hover:-translate-y-0.5 hover:border-primary/50 hover:text-primary hover:shadow-soft dark:border-dark-border dark:bg-dark-card/80 dark:text-gray-300 dark:hover:text-primary"
        >
          <span class="flex h-5 w-5 items-center justify-center text-primary">
            <svg viewBox="0 0 24 24" class="h-4.5 w-4.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="entry.icon"></svg>
          </span>
          {{ entry.label }}
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { toast } from '@/utils/toast'

const router = useRouter()
const draft = ref('')
const deepThink = ref(false)
const showNotice = ref(true)
const inputEl = ref(null)

const entries = [
  {
    to: '/chat',
    label: '开始对话',
    icon: '<path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>',
  },
  {
    to: '/draw',
    label: 'AI 生图',
    icon: '<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/>',
  },
  {
    to: '/files',
    label: '文档解析',
    icon: '<path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/>',
  },
]

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
  if (!content) return
  // 跳转对话页，携带问题与深度思考标记；未登录由路由守卫转登录页
  router.push({
    path: '/chat',
    query: { q: content, deep: deepThink.value ? '1' : '' },
  })
}

function goChat() {
  router.push('/chat')
}

function searchSoon() {
  toast('联网搜索即将上线，敬请期待', 'warning')
}
</script>
