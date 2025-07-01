<template>
  <div class="h-screen bg-white">
    <!-- Whiteboard Editor -->
    <WhiteboardEditor :whiteboard-id="whiteboardId" />
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import WhiteboardEditor from '@/components/whiteboard/WhiteboardEditor.vue'

const route = useRoute()
const whiteboardId = route.params.id as string
</script>