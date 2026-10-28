<template>
  <div class="mx-auto max-w-3xl px-6 py-8">
    <h1 class="text-xl font-semibold text-ink dark:text-gray-100">文档解析</h1>
    <p class="mt-1 text-sm text-ink-2 dark:text-gray-300">上传文档，AI 将读取内容并支持基于文档问答、总结与要点提取</p>

    <!-- 上传区 -->
    <div
      class="card mt-6 cursor-pointer border-2 border-dashed border-gray-200 p-10 text-center transition-colors duration-200 hover:border-primary dark:border-dark-border"
      :class="{ 'border-primary bg-primary-light/40 dark:bg-primary-dark/10': dragging }"
      @click="fileInput?.click()"
      @dragover.prevent="dragging = true"
      @dragleave.prevent="dragging = false"
      @drop.prevent="onDrop"
    >
      <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-primary-light/70 text-primary dark:bg-primary-dark/20">
        <svg viewBox="0 0 24 24" class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12" /></svg>
      </div>
      <p class="mt-3 text-sm font-medium text-ink dark:text-gray-100">点击选择文件，或将文件拖拽到此处</p>
      <p class="mt-1 text-xs text-ink-3">支持 TXT / Markdown / PDF · 单文件 ≤ 10MB · PDF ≤ 50 页</p>
      <input ref="fileInput" type="file" accept=".txt,.md,.markdown,.pdf" class="hidden" @change="onPick" />
    </div>

    <!-- 解析结果 -->
    <section v-if="result" class="card mt-5 p-6">
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div class="flex items-center gap-3">
          <span class="flex h-10 w-10 items-center justify-center rounded-lg bg-success/10 text-success">
            <svg viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5" /></svg>
          </span>
          <div>
            <div class="text-sm font-medium text-ink dark:text-gray-100">{{ result.filename }}</div>
            <div class="mt-0.5 text-xs text-ink-3">
              {{ formatSize(result.size_bytes) }}
              <template v-if="result.pages"> · {{ result.pages }} 页</template>
              · 解析出 {{ result.chars }} 字符
            </div>
          </div>
        </div>
        <RouterLink to="/chat" class="btn-primary" @click="askWithDoc">基于此文档提问</RouterLink>
      </div>

      <div v-if="result.truncated" class="mt-4 rounded bg-warning/10 px-3 py-2 text-xs text-warning">
        文档较长，已截断至 20 万字符，超长部分未进入上下文。
      </div>

      <div class="mt-4">
        <h3 class="text-xs font-medium text-ink-2 dark:text-gray-300">内容预览</h3>
        <pre class="mt-2 max-h-52 overflow-y-auto whitespace-pre-wrap rounded bg-black/3 p-3 text-xs leading-relaxed text-ink-2 dark:bg-white/5 dark:text-gray-300">{{ result.preview }}</pre>
      </div>
    </section>

    <!-- 说明 -->
    <section class="card mt-5 p-5">
      <h2 class="text-sm font-semibold text-ink dark:text-gray-100">解析说明</h2>
      <ul class="mt-2 space-y-1.5 text-sm text-ink-2 dark:text-gray-300">
        <li>· TXT / Markdown 直接读取原文；PDF 使用 PyMuPDF 提取文本。</li>
        <li>· 短文档全文进入上下文，超长自动截断；不构建 RAG 索引。</li>
        <li>· 首期不支持扫描件（图片型 PDF），上传时会提示。</li>
        <li>· 解析后的文档可在 AI 对话中输入区上传，或点击上方按钮直接提问。</li>
      </ul>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'

import { uploadFile } from '@/api'
import { useChatStore } from '@/stores/chat'
import { toast } from '@/utils/toast'

const chat = useChatStore()
const fileInput = ref(null)
const dragging = ref(false)
const result = ref(null)

function formatSize(bytes) {
  if (bytes >= 1024 * 1024) return (bytes / 1024 / 1024).toFixed(1) + ' MB'
  return Math.max(1, Math.round(bytes / 1024)) + ' KB'
}

async function handleFile(file) {
  if (!file) return
  dragging.value = false
  try {
    result.value = await uploadFile(file)
    toast(`解析成功：${result.value.filename}`)
  } catch (e) {
    toast(e.message, 'error')
  }
}

function onPick(e) {
  handleFile(e.target.files?.[0])
  e.target.value = ''
}

function onDrop(e) {
  handleFile(e.dataTransfer?.files?.[0])
}

function askWithDoc() {
  if (result.value) {
    chat.setFile(result.value.file_id, result.value.filename)
  }
}
</script>
