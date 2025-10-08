<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const auth = useAuthStore()
const router = useRouter()

const navLinks = computed(() => {
  const links = [{ label: 'Quizzes', to: { name: 'home' } }]
  if (auth.isAuthenticated) {
    links.push({ label: 'Dashboard', to: { name: 'dashboard' } })
  }
  if (auth.isAdmin) {
    links.push({ label: 'Admin', to: { name: 'admin' } })
  }
  return links
})

const logout = () => {
  auth.logout()
  router.push({ name: 'home' })
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 text-gray-900">
    <header class="px-6 py-4 shadow bg-white">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <nav class="flex items-center gap-4">
          <RouterLink :to="{ name: 'home' }" class="text-lg font-semibold">Loksewa Quiz Hub</RouterLink>
          <RouterLink
            v-for="link in navLinks"
            :key="link.label"
            :to="link.to"
            class="text-sm font-medium text-gray-600 hover:text-gray-900"
          >
            {{ link.label }}
          </RouterLink>
        </nav>
        <div class="flex items-center gap-3 text-sm">
          <span v-if="auth.user" class="text-gray-600">{{ auth.user.email }}</span>
          <RouterLink v-if="!auth.isAuthenticated" :to="{ name: 'login' }" class="btn-secondary">
            Login
          </RouterLink>
          <button
            v-else
            class="rounded bg-gray-900 px-3 py-1.5 text-white shadow-sm hover:bg-gray-700"
            @click="logout"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
    <main class="mx-auto max-w-6xl px-6 py-8">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.btn-secondary {
  @apply rounded border border-gray-300 px-3 py-1.5 text-gray-700 hover:bg-gray-100;
}
</style>
