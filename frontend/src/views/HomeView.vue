<template>
  <div class="mx-auto max-w-5xl px-6 pt-14 pb-10">
    <!-- Hero -->
    <section class="text-center">
      <div class="mx-auto mb-6 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary-light/70 text-primary dark:bg-primary-dark/20">
        <svg viewBox="0 0 24 24" class="h-8 w-8" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z" />
        </svg>
      </div>
      <h1 class="text-3xl font-bold tracking-tight text-ink dark:text-gray-100">
        轻量AI助手 · 在线AI工作台
      </h1>
      <p class="mx-auto mt-3 max-w-xl text-ink-2 dark:text-gray-300">
        面向学生、开发者与办公人群的轻量化 AI 工作台。流畅的流式对话、代码高亮、文档解析与 AI 生图，界面干净清爽。
      </p>

      <div class="mt-7 flex items-center justify-center gap-3">
        <RouterLink v-if="!auth.isLoggedIn" to="/register" class="btn-primary">免费注册</RouterLink>
        <RouterLink v-else to="/chat" class="btn-primary">开始对话</RouterLink>
        <RouterLink to="/about" class="btn-ghost">了解产品</RouterLink>
      </div>
    </section>

    <!-- 功能入口 -->
    <section class="mt-12 grid gap-4 sm:grid-cols-3">
      <RouterLink
        v-for="card in cards"
        :key="card.to"
        :to="card.to"
        class="card group p-5 transition-shadow duration-200 hover:shadow-md"
      >
        <span class="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-light/70 text-primary group-hover:bg-primary group-hover:text-white transition-colors duration-200 dark:bg-primary-dark/20">
          <svg viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" v-html="card.icon"></svg>
        </span>
        <h3 class="mt-4 text-base font-semibold text-ink dark:text-gray-100">{{ card.title }}</h3>
        <p class="mt-1.5 text-sm text-ink-2 dark:text-gray-300">{{ card.desc }}</p>
      </RouterLink>
    </section>

    <!-- 特性 -->
    <section class="mt-12 grid gap-4 sm:grid-cols-2">
      <div v-for="f in features" :key="f.title" class="flex items-start gap-3 rounded bg-white/60 p-4 dark:bg-dark-card/60">
        <span class="chip mt-0.5 shrink-0 bg-success/10 text-success">{{ f.tag }}</span>
        <div>
          <h4 class="text-sm font-medium text-ink dark:text-gray-100">{{ f.title }}</h4>
          <p class="mt-0.5 text-sm text-ink-2 dark:text-gray-300">{{ f.desc }}</p>
        </div>
      </div>
    </section>

    <!-- 登录提示 -->
    <section v-if="!auth.isLoggedIn" class="mt-12 card flex items-center justify-between p-5">
      <div>
        <h3 class="text-sm font-semibold text-ink dark:text-gray-100">登录后体验完整功能</h3>
        <p class="mt-0.5 text-sm text-ink-2 dark:text-gray-300">会话云端持久化，切换设备不丢失；支持文件解析与 AI 生图。</p>
      </div>
      <RouterLink to="/login" class="btn-primary shrink-0">登录</RouterLink>
    </section>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const cards = [
  {
    to: '/chat',
    title: 'AI对话',
    desc: '流式打字输出、Markdown 渲染、代码高亮一键复制，模型参数自由调节。',
    icon: '<path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/>',
  },
  {
    to: '/draw',
    title: 'AI生图',
    desc: '正向/反向提示词、尺寸与数量参数，生成记录可下载。',
    icon: '<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/>',
  },
  {
    to: '/files',
    title: '文档解析',
    desc: '上传 TXT / Markdown / PDF，基于文档内容问答、总结、提取要点。',
    icon: '<path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/>',
  },
]

const features = [
  { tag: '流式', title: 'SSE 流式输出', desc: 'AI 回复逐字渲染，随时可停止生成。' },
  { tag: '安全', title: '账号与数据安全', desc: 'bcrypt 密码哈希、JWT 鉴权、API Key 仅存后端。' },
  { tag: '持久化', title: '会话云端保存', desc: '会话与消息入库 MySQL，刷新不丢失、换设备可漫游。' },
  { tag: '双主题', title: '浅色 / 深色模式', desc: '低饱和冷色系，长时间使用舒适不疲劳。' },
]
</script>
