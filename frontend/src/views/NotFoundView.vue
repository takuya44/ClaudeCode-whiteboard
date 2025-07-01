<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center px-4">
    <div class="text-center">
      <h1 class="text-9xl font-bold text-primary-600">
        404
      </h1>
      <h2 class="text-3xl font-semibold text-gray-900 mb-4">
        Page Not Found
      </h2>
      <p class="text-gray-600 mb-8 max-w-md">
        Sorry, we couldn't find the page you're looking for.
      </p>
      <BaseButton @click="$router.push('/')">
        Go Back Home
      </BaseButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { BaseButton } from '@/components/ui'
</script>