import { defineStore } from 'pinia'

import { createProvider, deleteProvider, listProviders, setProviderApiKey, updateProvider } from '@/api'

// 大模型服务商（各类 OpenAI 兼容接口 + 本地大模型）
export const useProvidersStore = defineStore('providers', {
  state: () => ({
    providers: [],
    loaded: false,
  }),
  actions: {
    async fetch() {
      this.providers = await listProviders()
      this.loaded = true
      return this.providers
    },
    async ensure() {
      if (!this.loaded) return this.fetch()
      return this.providers
    },
    getById(id) {
      return this.providers.find((p) => p.id === id) || null
    },
    async add(payload) {
      const p = await createProvider(payload)
      this.providers.push(p)
      return p
    },
    async update(id, payload) {
      const p = await updateProvider(id, payload)
      const i = this.providers.findIndex((x) => x.id === id)
      if (i !== -1) this.providers[i] = p
      return p
    },
    async remove(id) {
      await deleteProvider(id)
      this.providers = this.providers.filter((x) => x.id !== id)
    },
    async saveApiKey(id, apiKey) {
      const p = await setProviderApiKey(id, apiKey)
      const i = this.providers.findIndex((x) => x.id === id)
      if (i !== -1) this.providers[i] = p
      return p
    },
  },
})
