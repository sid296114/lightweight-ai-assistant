<template>
  <div class="flex min-h-full items-center justify-center px-4 py-12">
    <div class="card w-full max-w-md p-7">
      <h1 class="text-xl font-semibold text-ink dark:text-gray-100">登录</h1>
      <p class="mt-1 text-sm text-ink-2 dark:text-gray-300">使用邮箱与密码登录，继续你的会话</p>

      <form class="mt-6 space-y-4" @submit.prevent="submit">
        <div>
          <label class="mb-1 block text-xs text-ink-2 dark:text-gray-300">邮箱</label>
          <input v-model.trim="form.email" type="email" class="input" placeholder="you@example.com" required autocomplete="email" />
        </div>
        <div>
          <label class="mb-1 block text-xs text-ink-2 dark:text-gray-300">密码</label>
          <input v-model="form.password" type="password" class="input" placeholder="至少 6 位" required autocomplete="current-password" />
        </div>
        <p v-if="error" class="rounded bg-danger/10 px-3 py-2 text-xs text-danger">{{ error }}</p>
        <button type="submit" class="btn-primary w-full" :disabled="loading">
          {{ loading ? '登录中…' : '登录' }}
        </button>
      </form>

      <p class="mt-5 text-center text-sm text-ink-2 dark:text-gray-300">
        还没有账号？
        <RouterLink to="/register" class="text-primary hover:underline">立即注册</RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import { toast } from '@/utils/toast'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const form = reactive({ email: '', password: '' })
const loading = ref(false)
const error = ref('')

async function submit() {
  if (loading.value) return
  loading.value = true
  error.value = ''
  try {
    await auth.login(form.email, form.password)
    toast('登录成功')
    router.push(route.query.redirect || '/chat')
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>
