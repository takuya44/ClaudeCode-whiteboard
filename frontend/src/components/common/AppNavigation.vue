<template>
  <nav class="bg-white shadow-sm border-b border-gray-200">
    <div class="container mx-auto px-4">
      <div class="flex justify-between items-center h-16">
        <div class="flex items-center space-x-8">
          <router-link
            to="/"
            class="flex items-center space-x-2"
          >
            <div class="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <svg
                class="w-5 h-5 text-white"
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
            <span class="text-xl font-bold text-gray-900">Whiteboard</span>
          </router-link>

          <div
            v-if="isAuthenticated"
            class="hidden md:flex space-x-6"
          >
            <router-link
              to="/app/dashboard"
              class="text-gray-600 hover:text-primary-600 px-3 py-2 text-sm font-medium transition-colors"
              :class="{ 'text-primary-600': $route.name === 'Dashboard' }"
            >
              ダッシュボード
            </router-link>
            <router-link
              to="/app/search"
              class="text-gray-600 hover:text-primary-600 px-3 py-2 text-sm font-medium transition-colors"
              :class="{ 'text-primary-600': $route.name === 'Search' }"
            >
              検索
            </router-link>
          </div>
        </div>

        <div class="flex items-center space-x-4">
          <template v-if="isAuthenticated">
            <!-- User Menu Dropdown -->
            <div
              ref="userMenuRef"
              class="relative"
            >
              <button
                class="flex items-center space-x-2 text-gray-600 hover:text-gray-900 p-2 rounded-md transition-colors"
                @click="toggleUserMenu"
              >
                <div class="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                  <span class="text-primary-600 font-medium text-sm">
                    {{ userInitials }}
                  </span>
                </div>
                <svg
                  class="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </button>

              <Transition
                enter-active-class="transition duration-200 ease-out"
                enter-from-class="transform scale-95 opacity-0"
                enter-to-class="transform scale-100 opacity-100"
                leave-active-class="transition duration-75 ease-in"
                leave-from-class="transform scale-100 opacity-100"
                leave-to-class="transform scale-95 opacity-0"
              >
                <div
                  v-if="showUserMenu"
                  class="absolute right-0 mt-2 w-56 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none z-50"
                >
                  <div class="px-4 py-3 border-b border-gray-100">
                    <p class="text-sm font-medium text-gray-900">
                      {{ user?.name }}
                    </p>
                    <p class="text-sm text-gray-500">
                      {{ user?.email }}
                    </p>
                  </div>
                  <div class="py-1">
                    <router-link
                      to="/app/profile"
                      class="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                      @click="showUserMenu = false"
                    >
                      <svg
                        class="w-4 h-4 mr-3"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                        />
                      </svg>
                      プロフィール設定
                    </router-link>
                    <button
                      class="flex w-full items-center px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                      @click="handleLogout"
                    >
                      <svg
                        class="w-4 h-4 mr-3"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                        />
                      </svg>
                      ログアウト
                    </button>
                  </div>
                </div>
              </Transition>
            </div>
          </template>

          <template v-else>
            <router-link
              to="/login"
              class="text-gray-600 hover:text-primary-600 px-3 py-2 text-sm font-medium transition-colors"
            >
              ログイン
            </router-link>
            <BaseButton
              size="sm"
              @click="$router.push('/register')"
            >
              はじめる
            </BaseButton>
          </template>

          <!-- Mobile Menu Button -->
          <button
            v-if="isAuthenticated"
            class="md:hidden p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors"
            @click="toggleMobileMenu"
          >
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>
        </div>
      </div>

      <!-- Mobile Menu -->
      <Transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="transform opacity-0 -translate-y-2"
        enter-to-class="transform opacity-100 translate-y-0"
        leave-active-class="transition duration-75 ease-in"
        leave-from-class="transform opacity-100 translate-y-0"
        leave-to-class="transform opacity-0 -translate-y-2"
      >
        <div
          v-if="showMobileMenu && isAuthenticated"
          class="md:hidden border-t border-gray-200 py-4"
        >
          <div class="space-y-2">
            <router-link
              to="/app/dashboard"
              class="block px-3 py-2 text-gray-600 hover:text-primary-600 font-medium transition-colors"
              @click="showMobileMenu = false"
            >
              ダッシュボード
            </router-link>
            <router-link
              to="/app/search"
              class="block px-3 py-2 text-gray-600 hover:text-primary-600 font-medium transition-colors"
              @click="showMobileMenu = false"
            >
              検索
            </router-link>
            <router-link
              to="/app/profile"
              class="block px-3 py-2 text-gray-600 hover:text-primary-600 font-medium transition-colors"
              @click="showMobileMenu = false"
            >
              プロフィール
            </router-link>
            <button
              class="w-full text-left px-3 py-2 text-red-600 hover:text-red-700 font-medium transition-colors"
              @click="handleLogout"
            >
              ログアウト
            </button>
          </div>
        </div>
      </Transition>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { BaseButton } from '@/components/ui'

const router = useRouter()
const authStore = useAuthStore()

const showUserMenu = ref(false)
const showMobileMenu = ref(false)
const userMenuRef = ref<HTMLElement>()

const isAuthenticated = computed(() => authStore.isAuthenticated)
const user = computed(() => authStore.user)

const userInitials = computed(() => {
  if (!user.value?.name) return 'U'
  return user.value.name
    .split(' ')
    .map(name => name.charAt(0))
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
  showMobileMenu.value = false
}

const toggleMobileMenu = () => {
  showMobileMenu.value = !showMobileMenu.value
  showUserMenu.value = false
}

const handleLogout = () => {
  authStore.logout()
  showUserMenu.value = false
  showMobileMenu.value = false
  router.push('/')
}

const handleClickOutside = (event: MouseEvent) => {
  if (userMenuRef.value && !userMenuRef.value.contains(event.target as Node)) {
    showUserMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>