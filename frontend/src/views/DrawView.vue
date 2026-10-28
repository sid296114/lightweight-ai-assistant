<template>
  <div class="mx-auto max-w-5xl px-6 py-8">
    <h1 class="text-xl font-semibold text-ink dark:text-gray-100">AI 生图</h1>
    <p class="mt-1 text-sm text-ink-2 dark:text-gray-300">输入提示词，生成你的专属图片</p>

    <!-- 未配置提示 -->
    <div class="card mt-5 p-5">
      <div class="flex items-start gap-3">
        <span class="chip shrink-0 bg-warning/10 text-warning">预留</span>
        <p class="text-sm leading-relaxed text-ink-2 dark:text-gray-300">
          当前版本绘图模型 API 选型待定，生图接口已预留（<code class="rounded bg-black/5 px-1 dark:bg-white/10">POST /api/draw/generate</code>）。
          在 <code class="rounded bg-black/5 px-1 dark:bg-white/10">backend/.env</code> 中配置
          <code class="rounded bg-black/5 px-1 dark:bg-white/10">DRAW_API_KEY</code> 后即可启用真实生成。
        </p>
      </div>
    </div>

    <div class="mt-5 grid gap-5 lg:grid-cols-[1fr_320px]">
      <!-- 参数表单 -->
      <section class="card p-6">
        <div>
          <label class="mb-1.5 block text-sm text-ink-2 dark:text-gray-300">正向提示词</label>
          <textarea
            v-model="form.prompt"
            rows="5"
            class="input resize-none"
            placeholder="描述你想要的画面，例如：一只戴着宇航员头盔的橘猫，漂浮在星空中，未来感插画风格，柔和冷色调"
            maxlength="2000"
          ></textarea>
        </div>
        <div class="mt-4">
          <label class="mb-1.5 block text-sm text-ink-2 dark:text-gray-300">反向提示词（不希望出现的内容）</label>
          <input v-model="form.negativePrompt" class="input" placeholder="例如：模糊、低质量、多余肢体" maxlength="1000" />
        </div>

        <div class="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-3">
          <div>
            <label class="mb-1.5 block text-sm text-ink-2 dark:text-gray-300">图片尺寸</label>
            <select v-model="form.size" class="input">
              <option value="1024x1024">方形 1024×1024</option>
              <option value="768x768">方形 768×768</option>
              <option value="512x512">方形 512×512</option>
              <option value="1344x768">横版 16:9</option>
              <option value="768x1344">竖版 9:16</option>
            </select>
          </div>
          <div>
            <label class="mb-1.5 block text-sm text-ink-2 dark:text-gray-300">生成数量</label>
            <select v-model.number="form.n" class="input">
              <option v-for="i in [1, 2, 3, 4]" :key="i" :value="i">生成 {{ i }} 张</option>
            </select>
          </div>
        </div>

        <button type="button" class="btn-primary mt-5" :disabled="!form.prompt.trim() || loading" @click="generate">
          {{ loading ? '生成中…' : '开始生成' }}
        </button>
        <p v-if="error" class="mt-3 rounded bg-danger/10 px-3 py-2 text-xs text-danger">{{ error }}</p>
      </section>

      <!-- 生成记录 -->
      <section class="card p-5">
        <h2 class="text-sm font-semibold text-ink dark:text-gray-100">生成记录</h2>
        <p v-if="!history.length" class="mt-3 text-sm text-ink-3">暂无记录，生成后自动保存在本地</p>
        <ul v-else class="mt-3 space-y-2">
          <li
            v-for="(h, i) in history"
            :key="i"
            class="flex items-start justify-between gap-2 rounded bg-black/3 px-3 py-2.5 text-sm dark:bg-white/5"
          >
            <div class="min-w-0">
              <div class="truncate text-ink dark:text-gray-100">{{ h.prompt }}</div>
              <div class="mt-0.5 text-xs text-ink-3">{{ h.size }} · {{ h.time }}</div>
            </div>
            <span class="chip shrink-0" :class="h.ok ? 'bg-success/10 text-success' : 'bg-danger/10 text-danger'">
              {{ h.ok ? '已提交' : '未生成' }}
            </span>
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'

import { request } from '@/api'
import { toast } from '@/utils/toast'

const form = reactive({ prompt: '', negativePrompt: '', size: '1024x1024', n: 1 })
const loading = ref(false)
const error = ref('')
const history = ref([])

const HISTORY_KEY = 'ai_draw_history'

onMounted(() => {
  try {
    history.value = JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]')
  } catch {
    history.value = []
  }
})

function pushHistory(ok) {
  history.value.unshift({
    prompt: form.prompt.trim().slice(0, 60),
    size: form.size,
    time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
    ok,
  })
  history.value = history.value.slice(0, 20)
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history.value))
}

async function generate() {
  error.value = ''
  loading.value = true
  try {
    const res = await request('/api/draw/generate', {
      method: 'POST',
      body: {
        prompt: form.prompt,
        negative_prompt: form.negativePrompt,
        size: form.size,
        n: form.n,
      },
    })
    pushHistory(true)
    toast('图片生成成功（服务接入后可见）')
  } catch (e) {
    pushHistory(false)
    error.value = e.message
    toast('生图失败', 'error')
  } finally {
    loading.value = false
  }
}
</script>
