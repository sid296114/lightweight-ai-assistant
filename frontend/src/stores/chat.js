import { defineStore } from 'pinia'

import { request, streamChat } from '@/api'

// 会话本地状态 + 服务端持久化（登录后云端存储）
export const useChatStore = defineStore('chat', {
  state: () => ({
    sessions: [], // 会话列表（按更新时间倒序）
    currentSessionId: null,
    messages: [], // 当前会话消息 [{id, role, content, streaming?}]
    streaming: false, // 是否正在流式生成
    abort: null, // 停止生成的控制器
    fileId: null, // 当前引用的文档 file_id
    fileName: null,
    sidebarCollapsed: false,
    params: {
      providerId: localStorage.getItem('ai_provider_id') || '', // 所选大模型服务商
      modelName: '', // 所选模型名（可为空：未选择）
      temperature: 0.7,
      maxTokens: null,
    },
  }),
  getters: {
    currentSession: (s) => s.sessions.find((x) => x.id === s.currentSessionId) || null,
  },
  actions: {
    // 持久化所选服务商
    setProvider(id) {
      this.params.providerId = id
      localStorage.setItem('ai_provider_id', id || '')
    },
    // ---------- 会话 ----------
    async fetchSessions() {
      this.sessions = await request('/api/chat/sessions')
      return this.sessions
    },
    async createSession() {
      const session = await request('/api/chat/sessions', {
        method: 'POST',
        body: { title: '新对话', temperature: this.params.temperature, model_name: this.params.modelName },
      })
      this.sessions.unshift(session)
      this.currentSessionId = session.id
      this.messages = []
      return session
    },
    async renameSession(id, title) {
      const updated = await request(`/api/chat/sessions/${id}`, {
        method: 'PATCH',
        body: { title },
      })
      const i = this.sessions.findIndex((x) => x.id === id)
      if (i !== -1) this.sessions[i] = updated
    },
    async deleteSession(id) {
      await request(`/api/chat/sessions/${id}`, { method: 'DELETE' })
      this.sessions = this.sessions.filter((x) => x.id !== id)
      if (this.currentSessionId === id) {
        this.currentSessionId = null
        this.messages = []
      }
    },
    async loadMessages(id) {
      this.currentSessionId = id
      this.messages = await request(`/api/chat/sessions/${id}/messages`)
    },

    // ---------- 参数 ----------
    applySessionParams() {
      const s = this.currentSession
      if (s) {
        this.params.modelName = s.model_name || ''
        this.params.temperature = s.temperature ?? 0.7
      }
    },

    // ---------- 对话 ----------
    async sendMessage(content) {
      if (!content.trim() || this.streaming) return

      // 无会话则自动新建（标题由后端取首条内容前 20 字）
      if (!this.currentSessionId) {
        await this.createSession()
        // 新建时标题先置为输入内容，流结束由后端返回 session_id
        const s = this.sessions.find((x) => x.id === this.currentSessionId)
        if (s && s.title === '新对话') {
          s.title = content.trim().slice(0, 20) || '新对话'
        }
      }

      const userMsg = { id: `local-${Date.now()}`, role: 'user', content, streaming: false }
      const assistantMsg = { id: `local-${Date.now() + 1}`, role: 'assistant', content: '', streaming: true }
      this.messages.push(userMsg, assistantMsg)
      this.streaming = true

      const payload = {
        content,
        session_id: this.currentSessionId,
        provider_id: this.params.providerId || null,
        model_name: this.params.modelName || null,
        temperature: this.params.temperature,
        max_tokens: this.params.maxTokens || null,
        file_id: this.fileId || null,
      }

      this.abort = streamChat(payload, {
        onDelta: (chunk) => {
          assistantMsg.content += chunk
          this.scrollToBottom()
        },
        onDone: (evt) => {
          assistantMsg.streaming = false
          assistantMsg.id = evt.message_id
          if (!this.currentSessionId) this.currentSessionId = evt.session_id
          this.streaming = false
          this.abort = null
          // 刷新会话列表（标题/时间变化）
          this.fetchSessions().then(() => {
            this.currentSessionId = evt.session_id
          })
          this.scrollToBottom(true)
        },
        onError: (message) => {
          assistantMsg.streaming = false
          if (!assistantMsg.content) {
            assistantMsg.content = `⚠️ ${message}`
          }
          this.streaming = false
          this.abort = null
        },
      })
      this.scrollToBottom()
    },
    stopGenerate() {
      if (this.abort) {
        this.abort.abort()
        this.abort = null
        this.streaming = false
        // 保留已生成内容，去掉流式标记
        const last = this.messages[this.messages.length - 1]
        if (last && last.streaming) last.streaming = false
      }
    },
    scrollToBottom(force = false) {
      requestAnimationFrame(() => {
        const el = document.getElementById('chat-scroll')
        if (el) el.scrollTop = el.scrollHeight
      })
    },
    setFile(fileId, fileName) {
      this.fileId = fileId
      this.fileName = fileName
    },
    clearFile() {
      this.fileId = null
      this.fileName = null
    },
    reset() {
      this.sessions = []
      this.currentSessionId = null
      this.messages = []
      this.streaming = false
      this.abort = null
      this.fileId = null
      this.fileName = null
    },
  },
})
