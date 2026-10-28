<template>
  <div class="md-body" @click="onClick" v-html="rendered"></div>
</template>

<script setup>
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'
// 按需引入 highlight.js 常用语言集合，减小打包体积
import hljs from 'highlight.js/lib/common'

import { copyText } from '@/utils/toast'

const props = defineProps({
  content: { type: String, default: '' },
})

// Markdown 渲染：标题/列表/引用/表格 + 代码高亮 + 一键复制（html 禁用以防注入）
const md = new MarkdownIt({
  html: false, // 禁用原始 HTML，避免 XSS
  linkify: true,
  breaks: true,
})

// 代码块：深色背景 + 语言标识 + 复制按钮
md.renderer.rules.fence = (tokens, idx) => {
  const token = tokens[idx]
  const lang = (token.info || '').trim().split(/\s+/)[0] || ''
  const code = token.content
  let highlighted
  if (lang && hljs.getLanguage(lang)) {
    try {
      highlighted = hljs.highlight(code, { language: lang, ignoreIllegals: true }).value
    } catch {
      highlighted = md.utils.escapeHtml(code)
    }
  } else {
    highlighted = md.utils.escapeHtml(code)
  }
  return (
    `<div class="code-block">` +
    `<div class="code-header"><span class="code-lang">${md.utils.escapeHtml(lang || 'text')}</span>` +
    `<button type="button" class="code-copy" data-role="copy">复制</button></div>` +
    `<pre><code class="hljs language-${md.utils.escapeHtml(lang || 'plaintext')}">${highlighted}</code></pre></div>`
  )
}

// 链接新窗口打开
const defaultLinkOpen =
  md.renderer.rules.link_open || ((tokens, idx, options, env, self) => self.renderToken(tokens, idx, options))
md.renderer.rules.link_open = (tokens, idx, options, env, self) => {
  tokens[idx].attrSet('target', '_blank')
  tokens[idx].attrSet('rel', 'noopener noreferrer')
  return defaultLinkOpen(tokens, idx, options, env, self)
}

const rendered = computed(() => md.render(props.content))

function onClick(e) {
  const btn = e.target.closest('[data-role="copy"]')
  if (!btn) return
  const block = btn.closest('.code-block')
  if (!block) return
  const code = block.querySelector('pre code')
  if (code) copyText(code.textContent, '代码已复制')
}
</script>
