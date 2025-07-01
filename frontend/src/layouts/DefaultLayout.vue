<template>
  <div class="min-h-screen bg-gray-50">
    <AppNavigation />
    <main>
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import AppNavigation from '@/components/common/AppNavigation.vue'
</script>