<template>
  <div class="card overflow-hidden">
    <!-- 标题：点击展开/收起模型参数调节 -->
    <button
      type="button"
      class="flex w-full items-center justify-between px-5 py-4 transition-colors duration-200 hover:bg-black/3 dark:hover:bg-white/5"
      @click="expanded = !expanded"
    >
      <span class="flex items-center gap-2 text-sm font-semibold text-ink dark:text-gray-100">
        <svg viewBox="0 0 24 24" class="h-4.5 w-4.5 text-primary" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9M16.5 3.5a2.12 2.12 0 013 3L7 19l-4 1 1-4z" /></svg>
        模型参数
      </span>
      <span class="flex items-center gap-2 text-xs text-ink-3">
        当前：{{ summary }}
        <svg viewBox="0 0 24 24" class="h-4 w-4 transition-transform duration-200" :class="expanded ? 'rotate-180' : ''" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6" /></svg>
      </span>
    </button>

    <transition name="fade">
      <div v-if="expanded" class="border-t border-gray-100 px-5 pb-5 pt-4 dark:border-dark-border">
        <!-- 模型选择 -->
        <div>
          <label class="mb-1 block text-xs text-ink-2 dark:text-gray-300">模型</label>
          <input
            v-model="local.modelName"
            list="model-options"
            class="input"
            placeholder="默认模型（后端配置）"
            @change="change"
          />
          <datalist id="model-options">
            <option value="deepseek-chat" />
            <option value="deepseek-reasoner" />
            <option value="gpt-4o-mini" />
            <option value="glm-4-flash" />
          </datalist>
        </div>

        <!-- 温度 -->
        <div class="mt-4">
          <label class="mb-1 flex justify-between text-xs text-ink-2 dark:text-gray-300">
            <span>温度 temperature</span><span class="text-ink dark:text-gray-100">{{ local.temperature.toFixed(1) }}</span>
          </label>
          <input
            type="range" min="0" max="2" step="0.1"
            v-model.number="local.temperature"
            class="w-full accent-primary"
            @input="change"
          />
          <p class="mt-0.5 text-[11px] text-ink-3">数值越高回答越有创造性</p>
        </div>

        <!-- 最大生成长度 -->
        <div class="mt-4">
          <label class="mb-1 flex justify-between text-xs text-ink-2 dark:text-gray-300">
            <span>最大生成长度</span>
            <span class="text-ink dark:text-gray-100">{{ local.maxTokens || '不限' }}</span>
          </label>
          <input
            type="range" min="256" max="8192" step="256"
            v-model.number="local.maxTokens"
            class="w-full accent-primary"
            @input="change"
          />
          <p class="mt-0.5 text-[11px] text-ink-3">单次回复 token 上限，拖到最左为不限</p>
        </div>

        <div class="mt-4 flex items-center justify-between">
          <p class="text-[11px] leading-relaxed text-ink-3">
            参数保存在后端会话中，每次对话自动沿用；大模型 API Key 仅存后端，前端不接触密钥。
          </p>
          <button type="button" class="btn-text !py-1 text-xs shrink-0" @click="reset">重置参数</button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Object, default: () => ({ modelName: '', temperature: 0.7, maxTokens: null }) },
  expanded: { type: Boolean, default: true },
})
const emit = defineEmits(['params-change', 'reset'])

const expanded = ref(props.expanded)
const local = reactive({ ...props.modelValue })

// 外部参数变化（如切换会话后加载会话参数）同步到本地
watch(
  () => props.modelValue,
  (v) => {
    local.modelName = v.modelName || ''
    local.temperature = v.temperature ?? 0.7
    local.maxTokens = v.maxTokens ?? null
  },
  { deep: true }
)

const summary = computed(() => {
  const parts = []
  if (local.modelName) parts.push(local.modelName)
  else parts.push('默认模型')
  parts.push(`温度 ${local.temperature.toFixed(1)}`)
  return parts.join(' · ')
})

function change() {
  emit('params-change', { ...local })
}

function reset() {
  local.modelName = ''
  local.temperature = 0.7
  local.maxTokens = null
  emit('params-change', { ...local })
  emit('reset')
}
</script>
