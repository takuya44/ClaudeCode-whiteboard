<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100">
    <div class="container mx-auto px-4 py-16">
      <div class="text-center mb-16">
        <h1 class="text-5xl font-bold text-gray-900 mb-6">
          コラボレーション ホワイトボード
        </h1>
        <p class="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          強力なホワイトボードアプリケーションで、リアルタイムにアイデアを作成、共有、コラボレーションしましょう。
        </p>
        <div class="space-x-4">
          <BaseButton
            v-if="!isAuthenticated"
            size="lg"
            @click="$router.push('/register')"
          >
            はじめる
          </BaseButton>
          <BaseButton
            v-else
            size="lg"
            @click="$router.push('/app/dashboard')"
          >
            ダッシュボードへ
          </BaseButton>
          <BaseButton
            v-if="!isAuthenticated"
            variant="outline"
            size="lg"
            @click="$router.push('/login')"
          >
            ログイン
          </BaseButton>
        </div>
      </div>
      
      <div class="grid md:grid-cols-3 gap-8 mb-16">
        <div class="text-center p-6 bg-white rounded-lg shadow-soft">
          <div class="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
            <svg
              class="w-6 h-6 text-primary-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
              />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">
            描画・作成
          </h3>
          <p class="text-gray-600">
            強力な描画ツールを使用して、図表、スケッチ、ビジュアルアイデアを作成しましょう。
          </p>
        </div>
        
        <div class="text-center p-6 bg-white rounded-lg shadow-soft">
          <div class="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
            <svg
              class="w-6 h-6 text-primary-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"
              />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">
            コラボレーション
          </h3>
          <p class="text-gray-600">
            チームメンバーや友人とリアルタイムで一緒に作業しましょう。
          </p>
        </div>
        
        <div class="text-center p-6 bg-white rounded-lg shadow-soft">
          <div class="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
            <svg
              class="w-6 h-6 text-primary-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z"
              />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">
            共有
          </h3>
          <p class="text-gray-600">
            ホワイトボードを共有し、いつでもどこでも誰とでもコラボレーションできます。
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { BaseButton } from '@/components/ui'

const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)
</script>