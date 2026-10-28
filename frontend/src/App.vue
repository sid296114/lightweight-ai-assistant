<template>
  <div class="flex h-full flex-col">
    <TopNav />
    <main class="min-h-0 flex-1">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'

import TopNav from '@/components/TopNav.vue'
import { useThemeStore } from '@/stores/theme'

const theme = useThemeStore()
onMounted(() => theme.apply())
</script>
