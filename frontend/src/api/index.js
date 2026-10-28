// 前端 API 封装：统一携带 JWT、统一错误处理、SSE 流式解析。
// 开发环境经 Vite 代理 /api → http://127.0.0.1:8000

const TOKEN_KEY = 'ai_assistant_token'
const USER_KEY = 'ai_assistant_user'

export const tokenStore = {
  get token() {
    return localStorage.getItem(TOKEN_KEY) || ''
  },
  set token(v) {
    if (v) localStorage.setItem(TOKEN_KEY, v)
    else localStorage.removeItem(TOKEN_KEY)
  },
  get user() {
    try {
      return JSON.parse(localStorage.getItem(USER_KEY) || 'null')
    } catch {
      return null
    }
  },
  set user(v) {
    if (v) localStorage.setItem(USER_KEY, JSON.stringify(v))
    else localStorage.removeItem(USER_KEY)
  },
  clear() {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  },
}

function extractDetail(payload) {
  if (typeof payload === 'string') return payload
  if (payload && typeof payload.detail === 'string') return payload.detail
  if (payload && Array.isArray(payload.detail)) {
    return payload.detail.map((d) => d.msg || d.loc?.join('.') || '').filter(Boolean).join('；')
  }
  return '请求失败'
}

export class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.status = status
  }
}

/** 通用 JSON 请求 */
export async function request(path, { method = 'GET', body, headers = {} } = {}) {
  const resp = await fetch(path, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(tokenStore.token ? { Authorization: `Bearer ${tokenStore.token}` } : {}),
      ...headers,
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  })

  if (resp.status === 204) return null

  let data = null
  try {
    data = await resp.json()
  } catch {
    data = null
  }

  if (!resp.ok) {
    if (resp.status === 401) {
      tokenStore.clear()
      if (!location.pathname.startsWith('/login')) {
        location.href = '/login'
      }
    }
    throw new ApiError(extractDetail(data), resp.status)
  }
  return data
}

/** 上传文件（FormData） */
export async function uploadFile(file) {
  const form = new FormData()
  form.append('file', file)
  const resp = await fetch('/api/files/upload', {
    method: 'POST',
    headers: tokenStore.token ? { Authorization: `Bearer ${tokenStore.token}` } : {},
    body: form,
  })
  let data = null
  try {
    data = await resp.json()
  } catch {
    data = null
  }
  if (!resp.ok) {
    if (resp.status === 401) {
      tokenStore.clear()
      location.href = '/login'
    }
    throw new ApiError(extractDetail(data), resp.status)
  }
  return data
}

/**
 * SSE 流式对话。
 * onDelta(chunk)、onDone({session_id, message_id})、onError(message)。
 * 返回 AbortController，供“停止生成”使用。
 */
export function streamChat(payload, { onDelta, onDone, onError }) {  const controller = new AbortController()

  ;(async () => {
    try {
      const resp = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(tokenStore.token ? { Authorization: `Bearer ${tokenStore.token}` } : {}),
        },
        body: JSON.stringify(payload),
        signal: controller.signal,
      })

      if (!resp.ok) {
        let data = null
        try {
          data = await resp.json()
        } catch {
          data = null
        }
        throw new ApiError(extractDetail(data), resp.status)
      }

      if (!resp.body) {
        throw new ApiError('浏览器不支持流式读取', 0)
      }

      const reader = resp.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })

        let idx
        while ((idx = buffer.indexOf('\n\n')) !== -1) {
          const raw = buffer.slice(0, idx)
          buffer = buffer.slice(idx + 2)
          const line = raw.split('\n').find((l) => l.startsWith('data: '))
          if (!line) continue
          try {
            const evt = JSON.parse(line.slice(6))
            if (evt.type === 'delta') onDelta?.(evt.content)
            else if (evt.type === 'done') onDone?.(evt)
            else if (evt.type === 'error') onError?.(evt.message || '生成失败')
          } catch {
            // 忽略无法解析的帧
          }
        }
      }
    } catch (err) {
      if (err.name === 'AbortError') return // 用户主动停止，静默结束
      onError?.(err instanceof ApiError ? err.message : '网络异常，请稍后重试')
    }
  })()

  return controller
}

/** 大模型服务商：列表（含 api_key_configured，不含明文 Key） */
export function listProviders() {
  return request('/api/providers')
}

/** 新增服务商（name / base_url / models / default_model） */
export function createProvider(payload) {
  return request('/api/providers', { method: 'POST', body: payload })
}

/** 更新服务商 */
export function updateProvider(id, payload) {
  return request(`/api/providers/${id}`, { method: 'PATCH', body: payload })
}

/** 删除服务商 */
export function deleteProvider(id) {
  return request(`/api/providers/${id}`, { method: 'DELETE' })
}

/** 设置/清除 API Key（空串清除；仅存后端，不返回明文） */
export function setProviderApiKey(id, apiKey) {
  return request(`/api/providers/${id}/api-key`, { method: 'POST', body: { api_key: apiKey } })
}
