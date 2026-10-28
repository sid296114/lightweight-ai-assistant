<template>
  <div class="mx-auto max-w-lg px-6 py-10">
    <h1 class="text-xl font-semibold text-ink dark:text-gray-100">用户中心</h1>
    <p class="mt-1 text-sm text-ink-2 dark:text-gray-300">管理你的账号信息</p>

    <!-- 账号信息 -->
    <section class="card mt-6 p-6">
      <div class="flex items-center gap-4">
        <span class="flex h-12 w-12 items-center justify-center rounded-full bg-primary text-lg text-white">
          {{ (auth.user?.username || 'U').slice(0, 1).toUpperCase() }}
        </span>
        <div>
          <div class="text-base font-medium text-ink dark:text-gray-100">{{ auth.user?.username }}</div>
          <div class="text-sm text-ink-2 dark:text-gray-300">{{ auth.user?.email }}</div>
        </div>
      </div>
      <dl class="mt-5 grid grid-cols-2 gap-3 text-sm">
        <div class="rounded bg-black/3 px-3 py-2 dark:bg-white/5">
          <dt class="text-xs text-ink-3">注册时间</dt>
          <dd class="mt-0.5 text-ink dark:text-gray-100">{{ formatDate(auth.user?.created_at) }}</dd>
        </div>
        <div class="rounded bg-black/3 px-3 py-2 dark:bg-white/5">
          <dt class="text-xs text-ink-3">账号状态</dt>
          <dd class="mt-0.5 text-success">正常</dd>
        </div>
      </dl>
    </section>

    <!-- 修改密码 -->
    <section class="card mt-5 p-6">
      <h2 class="text-sm font-semibold text-ink dark:text-gray-100">修改密码</h2>
      <form class="mt-4 space-y-3" @submit.prevent="changePwd">
        <input v-model="pwd.old" type="password" class="input" placeholder="旧密码" required autocomplete="current-password" />
        <input v-model="pwd.new1" type="password" class="input" placeholder="新密码（至少 6 位）" minlength="6" required autocomplete="new-password" />
        <input v-model="pwd.new2" type="password" class="input" placeholder="确认新密码" required autocomplete="new-password" />
        <p v-if="pwdError" class="rounded bg-danger/10 px-3 py-2 text-xs text-danger">{{ pwdError }}</p>
        <p v-if="pwdOk" class="rounded bg-success/10 px-3 py-2 text-xs text-success">{{ pwdOk }}</p>
        <button type="submit" class="btn-primary" :disabled="pwdLoading">修改密码</button>
      </form>
    </section>

    <!-- 退出 -->
    <button type="button" class="btn-danger-text mt-5" @click="logout">退出登录</button>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import { toast } from '@/utils/toast'

const auth = useAuthStore()
const router = useRouter()

const pwd = reactive({ old: '', new1: '', new2: '' })
const pwdLoading = ref(false)
const pwdError = ref('')
const pwdOk = ref('')

function formatDate(v) {
  if (!v) return ''
  return new Date(v).toLocaleString('zh-CN', { dateStyle: 'medium', timeStyle: 'short' })
}

async function changePwd() {
  pwdError.value = ''
  pwdOk.value = ''
  if (pwd.new1 !== pwd.new2) {
    pwdError.value = '两次输入的新密码不一致'
    return
  }
  pwdLoading.value = true
  try {
    await auth.changePassword(pwd.old, pwd.new1)
    pwdOk.value = '密码修改成功'
    pwd.old = pwd.new1 = pwd.new2 = ''
    toast('密码修改成功')
  } catch (e) {
    pwdError.value = e.message
  } finally {
    pwdLoading.value = false
  }
}

function logout() {
  auth.logout()
  toast('已退出登录')
  router.push('/')
}
</script>
