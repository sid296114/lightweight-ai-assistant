// 轻量 toast：复制成功、上传成功等轻提示，无强打扰弹窗
let container = null

function ensureContainer() {
  if (!container) {
    container = document.createElement('div')
    container.className =
      'fixed top-16 left-1/2 -translate-x-1/2 z-[999] flex flex-col items-center gap-2 pointer-events-none'
    document.body.appendChild(container)
  }
  return container
}

export function toast(message, type = 'success') {
  const wrap = ensureContainer()
  const el = document.createElement('div')
  const color = type === 'error' ? 'text-danger' : type === 'warning' ? 'text-warning' : 'text-success'
  el.className =
    'card px-4 py-2 text-sm font-medium flex items-center gap-2 animate-fadeIn ' + color
  el.textContent = message
  wrap.appendChild(el)
  setTimeout(() => {
    el.classList.add('opacity-0', 'transition-opacity', 'duration-200')
    setTimeout(() => el.remove(), 220)
  }, 1800)
}

export async function copyText(text, successMsg = '复制成功') {
  try {
    await navigator.clipboard.writeText(text)
    toast(successMsg)
  } catch {
    toast('复制失败，请手动复制', 'error')
  }
}
