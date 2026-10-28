import { defineStore } from 'pinia'

import { request, tokenStore } from '@/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: tokenStore.user, // { id, username, email, created_at }
  }),
  getters: {
    isLoggedIn: (s) => !!s.user && !!tokenStore.token,
  },
  actions: {
    async login(email, password) {
      const { access_token } = await request('/api/auth/login', {
        method: 'POST',
        body: { email, password },
      })
      tokenStore.token = access_token
      await this.fetchMe()
    },
    async register(username, email, password) {
      const { access_token } = await request('/api/auth/register', {
        method: 'POST',
        body: { username, email, password },
      })
      tokenStore.token = access_token
      await this.fetchMe()
    },
    async fetchMe() {
      const user = await request('/api/auth/me')
      this.user = user
      tokenStore.user = user
      return user
    },
    async changePassword(oldPassword, newPassword) {
      return request('/api/auth/change-password', {
        method: 'POST',
        body: { old_password: oldPassword, new_password: newPassword },
      })
    },
    logout() {
      tokenStore.clear()
      this.user = null
    },
  },
})
