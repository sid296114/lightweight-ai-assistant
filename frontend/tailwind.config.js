/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // 冷色系设计令牌（对齐 PRD 3.1）
        primary: {
          DEFAULT: '#6495ED', // 低饱和冷冰蓝（主色）
          hover: '#4A7FE0',
          light: '#EAF1FD', // 浅冷蓝（用户消息气泡等）
          dark: '#3B6CC4',
        },
        ink: '#1D2129', // 主文字
        'ink-2': '#4E5969', // 次要文字
        'ink-3': '#86909C', // 占位/辅助文字
        'app-bg': '#FAFBFD', // 页面背景（浅色默认）
        card: '#FFFFFF',
        'dark-bg': '#111827', // 深色模式底色
        'dark-card': '#1F2937',
        'dark-border': '#374151',
        success: '#52C41A',
        warning: '#FF7D00',
        danger: '#F53F3F',
      },
      borderRadius: {
        DEFAULT: '8px', // 全局统一圆角 8px
      },
      boxShadow: {
        soft: '0 2px 12px rgba(0,0,0,0.06)', // 轻薄柔和阴影
      },
      fontFamily: {
        sans: ['Inter', '"PingFang SC"', '"Microsoft YaHei"', '"Noto Sans CJK SC"', 'sans-serif'],
      },
      transitionDuration: {
        DEFAULT: '200ms',
      },
      keyframes: {
        fadeIn: {
          from: { opacity: '0', transform: 'translateY(4px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        fadeIn: 'fadeIn 200ms ease-out',
      },
    },
  },
  plugins: [],
}
