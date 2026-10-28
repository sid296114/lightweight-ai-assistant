<template>
  <div class="flex min-h-full items-center justify-center px-4 py-12">
    <div class="card w-full max-w-md p-7">
      <h1 class="text-xl font-semibold text-ink dark:text-gray-100">注册</h1>
      <p class="mt-1 text-sm text-ink-2 dark:text-gray-300">创建账号，会话将云端持久化保存</p>

      <form class="mt-6 space-y-4" @submit.prevent="submit">
        <div>
          <label class="mb-1 block text-xs text-ink-2 dark:text-gray-300">用户名</label>
          <input v-model.trim="form.username" class="input" placeholder="2-50 个字符" minlength="2" maxlength="50" required autocomplete="username" />
        </div>
        <div>
          <label class="mb-1 block text-xs text-ink-2 dark:text-gray-300">邮箱</label>
          <input v-model.trim="form.email" type="email" class="input" placeholder="you@example.com" required autocomplete="email" />
        </div>
        <div>
          <label class="mb-1 block text-xs text-ink-2 dark:text-gray-300">密码</label>
          <input v-model="form.password" type="password" class="input" placeholder="至少 6 位" minlength="6" maxlength="64" required autocomplete="new-password" />
          <p v-if="form.password && form.password.length < 6" class="mt-1 text-[11px] text-warning">密码长度至少 6 位</p>
        </div>
        <div>
          <label class="mb-1 block text-xs text-ink-2 dark:text-gray-300">确认密码</label>
          <input v-model="confirm" type="password" class="input" placeholder="再次输入密码" required autocomplete="new-password" />
        </div>
        <p v-if="error" class="rounded bg-danger/10 px-3 py-2 text-xs text-danger">{{ error }}</p>
        <button type="submit" class="btn-primary w-full" :disabled="loading">
          {{ loading ? '注册中…' : '注册并登录' }}
        </button>
      </form>

      <p class="mt-5 text-center text-sm text-ink-2 dark:text-gray-300">
        已有账号？
        <RouterLink to="/login" class="text-primary hover:underline">去登录</RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import { toast } from '@/utils/toast'

const auth = useAuthStore()
const router = useRouter()

const form = reactive({ username: '', email: '', password: '' })
const confirm = ref('')
const loading = ref(false)
const error = ref('')

async function submit() {
  if (loading.value) return
  error.value = ''
  if (form.password !== confirm.value) {
    error.value = '两次输入的密码不一致'
    return
  }
  loading.value = true
  try {
    await auth.register(form.username, form.email, form.password)
    toast('注册成功，已自动登录')
    router.push('/chat')
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>
