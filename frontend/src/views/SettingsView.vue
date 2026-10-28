<template>
  <div class="mx-auto max-w-2xl px-6 py-8">
    <h1 class="text-xl font-semibold text-ink dark:text-gray-100">设置</h1>
    <p class="mt-1 text-sm text-ink-2 dark:text-gray-300">管理模型服务、模型参数与界面外观</p>

    <!-- ① 大模型设置（横条：管理各类 OpenAI 兼容服务与本地模型） -->
    <section class="card mt-6 overflow-hidden">
      <button
        type="button"
        class="flex w-full items-center justify-between px-5 py-4 transition-colors duration-200 hover:bg-black/3 dark:hover:bg-white/5"
        @click="providerSection = !providerSection"
      >
        <span class="flex items-center gap-2 text-sm font-semibold text-ink dark:text-gray-100">
          <svg viewBox="0 0 24 24" class="h-4.5 w-4.5 text-primary" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2" /><path d="M9 9h6v6H9z" /><path d="M2 2v2m0 18v-2M22 2v2m0 18v-2" /></svg>
          大模型设置
        </span>
        <span class="flex items-center gap-2 text-xs text-ink-3">
          {{ providersStore.providers.length }} 个服务商
          <svg viewBox="0 0 24 24" class="h-4 w-4 transition-transform duration-200" :class="providerSection ? 'rotate-180' : ''" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6" /></svg>
        </span>
      </button>

      <div v-if="providerSection" class="border-t border-gray-100 dark:border-dark-border">
        <p class="px-5 pt-4 text-xs text-ink-3">选择服务商后其「API Key」按钮亮起，点击可添加密钥；添加后即可在对话页选择该模型直接调用。API Key 仅存后端，前端不可见。</p>

        <!-- 服务商列表 -->
        <div class="space-y-2 px-5 py-4">
          <div
            v-for="p in providersStore.providers"
            :key="p.id"
            class="rounded-lg border transition-all duration-200"
            :class="selectedId === p.id
              ? 'border-primary bg-primary/6 shadow-sm dark:bg-primary-dark/10'
              : 'border-gray-200 hover:border-primary/50 dark:border-dark-border'"
          >
            <div class="flex items-center justify-between gap-3 px-4 py-3">
              <button
                type="button"
                class="min-w-0 flex-1 text-left"
                @click="selectedId = selectedId === p.id ? '' : p.id"
              >
                <div class="flex items-center gap-2">
                  <span class="truncate text-sm font-medium text-ink dark:text-gray-100">{{ p.name }}</span>
                  <span v-if="p.is_local" class="chip shrink-0 bg-primary/10 !px-1.5 text-[10px] text-primary">本地</span>
                  <span v-else-if="p.no_auth" class="chip shrink-0 bg-warning/10 !px-1.5 text-[10px] text-warning">免鉴权</span>
                  <span
                    class="shrink-0 text-[10px]"
                    :class="p.api_key_configured ? 'text-success' : 'text-warning'"
                  >
                    {{ p.api_key_configured ? '✓ 已配置 Key' : '未配置 Key' }}
                  </span>
                </div>
                <div class="mt-1 flex items-center gap-2">
                  <span class="truncate text-[11px] text-ink-3">{{ p.base_url }}</span>
                </div>
                <div v-if="(p.models || []).length" class="mt-1.5 flex flex-wrap gap-1.5">
                  <span
                    v-for="m in p.models"
                    :key="m"
                    class="rounded bg-black/4 px-1.5 py-0.5 text-[11px] text-ink-2 dark:bg-white/6 dark:text-gray-300"
                  >{{ m }}</span>
                </div>
              </button>

              <div class="flex shrink-0 items-center gap-1.5">
                <button
                  type="button"
                  class="text-xs transition-all duration-200"
                  :class="selectedId === p.id ? 'btn-primary !px-3' : 'btn-ghost !px-3 text-ink-2 dark:text-gray-300'"
                  :disabled="p.is_local"
                  :title="p.is_local ? '本地模型无需 API Key' : '点击添加 / 更新 API Key'"
                  @click="openApiKey(p)"
                >
                  <svg viewBox="0 0 24 24" class="mr-1 inline h-3.5 w-3.5" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="3" y="11" width="18" height="11" rx="2" /><path d="M7 11V7a5 5 0 0110 0v4" /></svg>
                  API Key
                </button>
                <button
                  type="button"
                  class="btn-ghost !px-2.5 text-xs text-ink-2 hover:text-primary dark:text-gray-300"
                  title="用默认模型测试调用"
                  :disabled="testing === p.id"
                  @click="testProvider(p)"
                >
                  {{ testing === p.id ? '测试中…' : '测试' }}
                </button>
                <button
                  type="button"
                  class="btn-ghost !p-1.5 text-ink-3 hover:text-danger"
                  title="删除服务商"
                  @click="removeProvider(p)"
                >
                  <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 6h18M8 6V4a1 1 0 011-1h6a1 1 0 011 1v2m2 0v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6" /></svg>
                </button>
              </div>
            </div>
            <!-- 测试结果 -->
            <div v-if="testResults[p.id]" class="border-t border-gray-100 px-4 py-2.5 dark:border-dark-border">
              <p class="text-[11px] leading-relaxed" :class="testResults[p.id].ok ? 'text-success' : 'text-danger'">
                {{ testResults[p.id].text }}
              </p>
            </div>
          </div>

          <p v-if="!providersStore.providers.length" class="py-3 text-center text-xs text-ink-3">暂无服务商，请在下方添加</p>

          <!-- 添加服务商（横条展开表单） -->
          <div class="rounded-lg border border-dashed border-gray-300 dark:border-dark-border">
            <button
              type="button"
              class="flex w-full items-center gap-2 px-4 py-3 text-sm text-ink-2 transition-colors duration-200 hover:text-primary dark:text-gray-300"
              @click="adding = !adding"
            >
              <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M12 5v14M5 12h14" /></svg>
              {{ adding ? '收起表单' : '添加服务商' }}
            </button>
            <div v-if="adding" class="space-y-3 border-t border-gray-100 px-4 py-3 dark:border-dark-border">
              <div>
                <label class="mb-1 block text-xs text-ink-2 dark:text-gray-300">名称</label>
                <input v-model="form.name" class="input" placeholder="如：智谱 GLM / 本地 Ollama" />
              </div>
              <div>
                <label class="mb-1 block text-xs text-ink-2 dark:text-gray-300">Base URL（OpenAI 兼容接口地址）</label>
                <input v-model="form.baseUrl" class="input" placeholder="https://api.xxx.com/v1 或 http://127.0.0.1:11434/v1" />
              </div>
              <div>
                <label class="mb-1 block text-xs text-ink-2 dark:text-gray-300">模型列表（逗号分隔）</label>
                <input v-model="form.models" class="input" placeholder="model-a, model-b" />
              </div>
              <div>
                <label class="mb-1 block text-xs text-ink-2 dark:text-gray-300">默认模型（可选）</label>
                <input v-model="form.defaultModel" class="input" placeholder="不填则使用模型列表第一项" />
              </div>
                <div class="flex items-center justify-between pt-1">
                  <label class="flex cursor-pointer items-center gap-2 text-xs text-ink-2 dark:text-gray-300">
                    <input v-model="form.noAuth" type="checkbox" class="h-3.5 w-3.5 accent-primary" />
                    该服务无需 API Key（自部署推理，如魔搭 / 私有 vLLM 等）
                  </label>
                  <button type="button" class="btn-primary !px-4 !py-2 text-xs" :disabled="saving" @click="saveProvider">
                    {{ saving ? '添加中…' : '保存服务商' }}
                  </button>
                </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ② 模型参数（横条：点击展开调节） -->
    <div class="mt-4">
      <ParamPanel
        :model-value="chat.params"
        :expanded="true"
        @params-change="onParamsChange"
        @reset="toast('参数已重置')"
      />
    </div>

    <!-- ③ 外观（横条） -->
    <section class="card mt-4 overflow-hidden">
      <button
        type="button"
        class="flex w-full items-center justify-between px-5 py-4 transition-colors duration-200 hover:bg-black/3 dark:hover:bg-white/5"
        @click="appearSection = !appearSection"
      >
        <span class="flex items-center gap-2 text-sm font-semibold text-ink dark:text-gray-100">
          <svg viewBox="0 0 24 24" class="h-4.5 w-4.5 text-primary" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4" /><path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32l1.41 1.41M2 12h2m16 0h2M4.93 19.07l1.41-1.41m11.32-11.32l1.41-1.41" /></svg>
          外观
        </span>
        <span class="flex items-center gap-2 text-xs text-ink-3">
          {{ theme.dark ? '深色' : '浅色' }}
          <svg viewBox="0 0 24 24" class="h-4 w-4 transition-transform duration-200" :class="appearSection ? 'rotate-180' : ''" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6" /></svg>
        </span>
      </button>
      <div v-if="appearSection" class="grid grid-cols-2 gap-3 border-t border-gray-100 px-5 py-4 dark:border-dark-border">
        <button
          type="button"
          class="rounded border px-4 py-3 text-sm transition-colors duration-200"
          :class="!theme.dark
            ? 'border-primary bg-primary-light/60 font-medium text-primary dark:bg-primary-dark/25 dark:text-primary'
            : 'border-gray-200 text-ink-2 hover:border-primary dark:border-dark-border dark:text-gray-300'"
          @click="theme.setDark(false)"
        >
          <span class="block text-base">☀️</span><span class="mt-1 block">浅色</span>
        </button>
        <button
          type="button"
          class="rounded border px-4 py-3 text-sm transition-colors duration-200"
          :class="theme.dark
            ? 'border-primary bg-primary-light/60 font-medium text-primary dark:bg-primary-dark/25 dark:text-primary'
            : 'border-gray-200 text-ink-2 hover:border-primary dark:border-dark-border dark:text-gray-300'"
          @click="theme.setDark(true)"
        >
          <span class="block text-base">🌙</span><span class="mt-1 block">深色</span>
        </button>
      </div>
    </section>

    <!-- ④ 数据与安全（横条） -->
    <section class="card mt-4 overflow-hidden">
      <button
        type="button"
        class="flex w-full items-center justify-between px-5 py-4 transition-colors duration-200 hover:bg-black/3 dark:hover:bg-white/5"
        @click="safetySection = !safetySection"
      >
        <span class="flex items-center gap-2 text-sm font-semibold text-ink dark:text-gray-100">
          <svg viewBox="0 0 24 24" class="h-4.5 w-4.5 text-primary" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" /><path d="M7 11V7a5 5 0 0110 0v4" /></svg>
          数据与安全
        </span>
        <svg viewBox="0 0 24 24" class="h-4 w-4 transition-transform duration-200 text-ink-3" :class="safetySection ? 'rotate-180' : ''" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6" /></svg>
      </button>
      <ul v-if="safetySection" class="space-y-1.5 border-t border-gray-100 px-5 py-4 text-sm text-ink-2 dark:border-dark-border dark:text-gray-300">
        <li>· 会话与消息实时保存至 MySQL，刷新不丢失、换设备可漫游。</li>
        <li>· 密码使用 bcrypt 哈希存储，登录使用 JWT 鉴权（7 天有效）。</li>
        <li>· 大模型 / 绘图 API Key 仅存后端，前端不接触密钥。</li>
      </ul>
    </section>

    <!-- API Key 弹窗 -->
    <BaseModal
      :show="apiKeyTarget !== null"
      title="配置 API Key"
      confirm-text="保存"
      @close="apiKeyTarget = null"
      @confirm="saveApiKey"
    >
      <p class="mb-3 text-sm text-ink-2 dark:text-gray-300">
        为「{{ apiKeyTarget?.name }}」配置 API Key（仅存后端，不会回显）。
      </p>
      <input
        v-model="apiKeyValue"
        type="password"
        class="input"
        placeholder="粘贴 API Key（留空则清除已存 Key）"
      />
    </BaseModal>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'

import { streamChat } from '@/api'
import BaseModal from '@/components/BaseModal.vue'
import ParamPanel from '@/components/ParamPanel.vue'
import { useChatStore } from '@/stores/chat'
import { useProvidersStore } from '@/stores/providers'
import { useThemeStore } from '@/stores/theme'
import { toast } from '@/utils/toast'

const chat = useChatStore()
const theme = useThemeStore()
const providersStore = useProvidersStore()

// 各横条展开状态
const providerSection = ref(true)
const appearSection = ref(false)
const safetySection = ref(false)

// 大模型设置
const selectedId = ref('')
const adding = ref(false)
const saving = ref(false)
const testing = ref('')
const testResults = reactive({})
const apiKeyTarget = ref(null)
const apiKeyValue = ref('')

const form = reactive({ name: '', baseUrl: '', models: '', defaultModel: '', noAuth: false })

async function saveProvider() {
  const name = form.name.trim()
  const baseUrl = form.baseUrl.trim()
  if (!name || !baseUrl) {
    toast('请填写名称与 Base URL', 'error')
    return
  }
  saving.value = true
  try {
    await providersStore.add({
      name,
      base_url: baseUrl,
      models: form.models.split(',').map((s) => s.trim()).filter(Boolean),
      default_model: form.defaultModel.trim(),
      no_auth: form.noAuth,
    })
    form.name = ''
    form.baseUrl = ''
    form.models = ''
    form.defaultModel = ''
    form.noAuth = false
    adding.value = false
    toast('服务商已添加')
  } catch (e) {
    toast(e.message, 'error')
  } finally {
    saving.value = false
  }
}

function openApiKey(p) {
  apiKeyTarget.value = p
  apiKeyValue.value = ''
}

async function saveApiKey() {
  const p = apiKeyTarget.value
  apiKeyTarget.value = null
  if (!p) return
  try {
    await providersStore.saveApiKey(p.id, apiKeyValue.value.trim())
    toast(apiKeyValue.value.trim() ? 'API Key 已保存' : 'API Key 已清除')
  } catch (e) {
    toast(e.message, 'error')
  }
}

async function removeProvider(p) {
  try {
    await providersStore.remove(p.id)
    if (selectedId.value === p.id) selectedId.value = ''
    toast(`已删除「${p.name}」`)
  } catch (e) {
    toast(e.message, 'error')
  }
}

// 测试调用：用该服务商默认模型发一条真实流式请求
function testProvider(p) {
  testing.value = p.id
  testResults[p.id] = null
  const model = p.default_model || p.models?.[0] || ''
  streamChat(
    { content: '你好，请回复“连接成功”', provider_id: p.id, model_name: model || null, temperature: 0.7 },
    {
      onDelta: (chunk) => {
        testResults[p.id] = { ok: true, text: '✓ 调用成功：' + (testResults[p.id]?.text ? testResults[p.id].text : '') + chunk }
      },
      onDone: () => {
        if (!testResults[p.id]) testResults[p.id] = { ok: true, text: '✓ 调用成功（无内容返回）' }
        testing.value = ''
      },
      onError: (message) => {
        testResults[p.id] = { ok: false, text: '✗ ' + message }
        testing.value = ''
      },
    }
  )
}

function onParamsChange(params) {
  chat.params = { ...chat.params, ...params }
}

onMounted(() => {
  providersStore.ensure().catch(() => {})
  // 若当前对话选了服务商，默认选中对应行
  if (chat.params.providerId) selectedId.value = chat.params.providerId
})
</script>
