<template>
  <div class="mx-auto max-w-3xl px-6 py-10">
    <h1 class="text-xl font-semibold text-ink dark:text-gray-100">关于</h1>
    <p class="mt-1 text-sm text-ink-2 dark:text-gray-300">产品简介、技术栈与版本信息</p>

    <section class="card mt-6 p-6">
      <h2 class="text-sm font-semibold text-ink dark:text-gray-100">产品简介</h2>
      <p class="mt-2 text-sm leading-relaxed text-ink-2 dark:text-gray-300">
        轻量AI助手是一款面向学生、开发者与办公人群的轻量化在线 AI 工作台。以对话为核心，提供流式 AI 对话、
        代码高亮、文档解析与 AI 生图能力，界面采用低饱和冷色系设计，追求干净、安静、舒适的长期使用体验。
      </p>
    </section>

    <section class="card mt-5 p-6">
      <h2 class="text-sm font-semibold text-ink dark:text-gray-100">技术栈</h2>
      <div class="mt-3 grid gap-3 text-sm sm:grid-cols-2">
        <div v-for="t in stack" :key="t.name" class="flex items-center justify-between rounded bg-black/3 px-3 py-2.5 dark:bg-white/5">
          <span class="text-ink-2 dark:text-gray-300">{{ t.name }}</span>
          <span class="font-medium text-ink dark:text-gray-100">{{ t.value }}</span>
        </div>
      </div>
      <p class="mt-4 rounded bg-primary-light/40 px-3 py-2 text-xs leading-relaxed text-ink-2 dark:bg-primary-dark/10 dark:text-gray-300">
        前端 Vue3 + TailwindCSS + Pinia，后端 Python FastAPI，数据库 MySQL 8.0。
        大模型 / 绘图 API 调用统一经后端转发，密钥不暴露于前端；流式输出基于 SSE 协议。
      </p>
    </section>

    <section class="card mt-5 p-6">
      <h2 class="text-sm font-semibold text-ink dark:text-gray-100">版本信息</h2>
      <div class="mt-2 flex items-center justify-between text-sm">
        <span class="text-ink-2 dark:text-gray-300">当前版本</span>
        <span class="chip bg-primary-light/60 text-primary dark:bg-primary-dark/20">v1.0.0</span>
      </div>
    </section>

    <section class="card mt-5 p-6">
      <h2 class="text-sm font-semibold text-ink dark:text-gray-100">免责提示</h2>
      <p class="mt-2 text-sm leading-relaxed text-ink-2 dark:text-gray-300">
        AI 生成内容可能存在偏差或错误，仅供参考，请勿直接用于重大决策。文档解析结果仅做文本提取，
        不保证内容的完整性与准确性。使用本产品即表示你同意上述说明。
      </p>
    </section>
  </div>
</template>

<script setup>
const stack = [
  { name: '前端框架', value: 'Vue3 + TailwindCSS' },
  { name: '状态管理', value: 'Pinia' },
  { name: '后端框架', value: 'Python FastAPI' },
  { name: '数据库', value: 'MySQL 8.0' },
  { name: '鉴权方案', value: 'JWT + bcrypt' },
  { name: 'AI 能力', value: '大模型 API / SSE 流式' },
]
</script>
