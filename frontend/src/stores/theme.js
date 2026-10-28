import { defineStore } from 'pinia'

const KEY = 'ai_theme'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    dark: localStorage.getItem(KEY) === 'dark',
  }),
  actions: {
    setDark(dark) {
      this.dark = dark
      localStorage.setItem(KEY, dark ? 'dark' : 'light')
      this.apply()
    },
    toggle() {
      this.dark = !this.dark
      localStorage.setItem(KEY, this.dark ? 'dark' : 'light')
      this.apply()
    },
    apply() {
      document.documentElement.classList.toggle('dark', this.dark)
    },
  },
})
