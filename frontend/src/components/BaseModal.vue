<template>
  <transition name="fade">
    <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-black/30 p-4" @click.self="$emit('close')">
      <div class="card w-full max-w-sm p-5">
        <h3 class="mb-4 text-base font-semibold text-ink dark:text-gray-100">{{ title }}</h3>
        <slot />
        <div class="mt-5 flex justify-end gap-2">
          <button type="button" class="btn-ghost" @click="$emit('close')">取消</button>
          <button type="button" class="btn-primary" @click="$emit('confirm')">{{ confirmText }}</button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
defineProps({
  show: { type: Boolean, default: false },
  title: { type: String, default: '提示' },
  confirmText: { type: String, default: '确定' },
})
defineEmits(['close', 'confirm'])
</script>
