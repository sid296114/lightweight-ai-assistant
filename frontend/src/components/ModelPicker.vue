<template>
  <div class="relative shrink-0">
    <!-- 触发按钮：未选择显示 +，已选择亮蓝色显示模型名 -->
    <button
      type="button"
      class="flex h-9 items-center gap-1.5 rounded-lg border px-3 text-sm transition-all duration-200"
      :class="selected
        ? 'border-primary bg-primary/15 font-medium text-primary dark:bg-primary-dark/30'
        : 'border-gray-200 text-ink-2 hover:border-primary hover:text-primary dark:border-dark-border dark:text-gray-300'"
      :title="selected ? `当前模型：${selectedModel}（${selectedProvider?.name || '未知服务'}）` : '选择大模型'"
      @click="toggle"
    >
      <template v-if="selected">
        <span class="max-w-[140px] truncate">{{ selectedModel }}</span>
        <svg viewBox="0 0 24 24" class="h-3.5 w-3.5 shrink-0" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M6 9l6 6 6-6" /></svg>
      </template>
      <template v-else>
        <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M12 5v14M5 12h14" /></svg>
      </template>
    </button>

    <!-- 选择面板：向上弹出 -->
    <transition name="fade">
      <div
        v-if="open"
        class="card absolute bottom-full left-0 z-50 mb-2 w-80 max-h-[340px] overflow-y-auto p-1 shadow-xl"
      >
        <p class="px-2 py-1.5 text-xs font-semibold text-ink dark:text-gray-100">选择大模型（支持各类 OpenAI 兼容服务与本地模型）</p>

        <template v-if="providers.length">
          <!-- 清除选择 -->
          <button
            type="button"
            class="mb-1 flex w-full items-center gap-2 rounded-lg px-2 py-2 text-left text-xs text-ink-2 transition-colors duration-200 hover:bg-black/4 dark:text-gray-300 dark:hover:bg-white/6"
            @click="clear"
          >
            <svg viewBox="0 0 24 24" class="h-4 w-4 text-ink-3" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6L6 18M6 6l12 12" /></svg>
            清除选择（使用默认模型）
          </button>

          <div
            v-for="p in providers"
            :key="p.id"
            class="rounded-lg px-2 py-2 transition-colors duration-200"
            :class="p.id === chat.params.providerId ? 'bg-primary/8' : 'hover:bg-black/3 dark:hover:bg-white/5'"
          >
            <div class="flex items-center justify-between gap-2">
              <span class="truncate text-sm font-medium text-ink dark:text-gray-100">
                {{ p.name }}
                <span v-if="p.is_local" class="ml-1 rounded bg-primary/10 px-1 py-0.5 text-[10px] text-primary">本地</span>
              </span>
              <span class="shrink-0 text-[10px]" :class="p.api_key_configured ? 'text-success' : 'text-ink-3'">
                {{ p.api_key_configured ? '🔑 已配置' : '未配置 Key' }}
              </span>
            </div>
            <div class="mt-1.5 flex flex-wrap gap-1.5">
              <button
                v-if="p.default_model"
                type="button"
                class="rounded-full border px-2.5 py-1 text-xs transition-all duration-200"
                :class="selectedProvider === p.id && selectedModel === p.default_model
                  ? 'border-primary bg-primary/15 font-medium text-primary'
                  : 'border-gray-200 text-ink-2 hover:border-primary hover:text-primary dark:border-dark-border dark:text-gray-300'"
                @click="pick(p, p.default_model)"
              >
                {{ p.default_model }}
              </button>
              <button
                v-for="m in p.models"
                :key="m"
                type="button"
                class="rounded-full border px-2.5 py-1 text-xs transition-all duration-200"
                :class="selectedProvider === p.id && selectedModel === m
                  ? 'border-primary bg-primary/15 font-medium text-primary'
                  : 'border-gray-200 text-ink-2 hover:border-primary hover:text-primary dark:border-dark-border dark:text-gray-300'"
                @click="pick(p, m)"
              >
                {{ m }}
              </button>
            </div>
          </div>

          <a href="/settings" class="mt-1 block rounded-lg px-2 py-1.5 text-xs text-primary hover:bg-primary/8" @click.stop>管理服务商与 API Key →</a>
        </template>
        <div v-else class="px-2 py-4 text-center text-xs text-ink-3">暂无服务商，请到设置中添加</div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

import { useChatStore } from '@/stores/chat'
import { useProvidersStore } from '@/stores/providers'

const chat = useChatStore()
const providersStore = useProvidersStore()

const open = ref(false)

const providers = computed(() => providersStore.providers)
const selected = computed(() => !!(chat.params.providerId && chat.params.modelName))
const selectedProvider = computed(() => chat.params.providerId)
const selectedModel = computed(() => chat.params.modelName)

function toggle() {
  open.value = !open.value
  if (open.value) {
    providersStore.ensure().catch(() => {})
  }
}

function pick(p, model) {
  chat.setProvider(p.id)
  chat.params.modelName = model
  open.value = false
}

function clear() {
  chat.setProvider('')
  chat.params.modelName = ''
  open.value = false
}
</script>
