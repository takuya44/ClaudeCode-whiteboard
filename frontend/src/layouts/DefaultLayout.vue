<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <AppNavigation />
    <main class="flex-1">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import AppNavigation from '@/components/common/AppNavigation.vue'
</script>