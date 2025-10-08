<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const auth = useAuthStore()
const router = useRouter()

const navLinks = computed(() => {
  const links = [{ label: 'Home', to: { name: 'home' } }]
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
  <div class="min-h-screen bg-slate-50 text-slate-900">
    <header class="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur">
      <div class="mx-auto flex max-w-7xl items-center justify-between gap-6 px-6 py-4">
        <RouterLink :to="{ name: 'home' }" class="flex items-center gap-2 text-base font-semibold">
          <span
            class="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 via-sky-500 to-emerald-500 text-white shadow"
            aria-hidden="true"
          >
            <span class="text-lg font-bold">Q</span>
          </span>
          <span class="hidden sm:block">QuizMaster</span>
        </RouterLink>
        <nav class="flex items-center gap-6 text-sm font-medium text-slate-600">
          <RouterLink
            v-for="link in navLinks"
            :key="link.label"
            :to="link.to"
            class="transition hover:text-slate-900"
            active-class="text-slate-900"
          >
            {{ link.label }}
          </RouterLink>
        </nav>
        <div class="flex items-center gap-3 text-sm">
          <span v-if="auth.user" class="hidden text-slate-500 sm:inline">{{ auth.user.email }}</span>
          <RouterLink
            v-if="!auth.isAuthenticated"
            :to="{ name: 'login' }"
            class="rounded-full border border-slate-300 px-4 py-2 font-semibold text-slate-700 transition hover:border-slate-400 hover:text-slate-900"
          >
            Login
          </RouterLink>
          <button
            v-else
            class="rounded-full bg-slate-900 px-4 py-2 font-semibold text-white shadow-sm transition hover:bg-slate-700"
            @click="logout"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
    <main class="mx-auto flex max-w-7xl flex-1 flex-col px-6 pb-16 pt-10">
      <RouterView />
    </main>
    <footer class="border-t border-slate-200 bg-white py-6 text-sm text-slate-500">
      <div class="mx-auto flex max-w-7xl flex-col items-center justify-between gap-3 px-6 sm:flex-row">
        <p>© {{ new Date().getFullYear() }} QuizMaster. Built for competitive exam success.</p>
        <div class="flex items-center gap-4">
          <RouterLink :to="{ name: 'home' }" class="transition hover:text-slate-900">Home</RouterLink>
          <RouterLink v-if="auth.isAuthenticated" :to="{ name: 'dashboard' }" class="transition hover:text-slate-900">
            Dashboard
          </RouterLink>
          <RouterLink v-if="auth.isAdmin" :to="{ name: 'admin' }" class="transition hover:text-slate-900">
            Admin
          </RouterLink>
        </div>
      </div>
    </footer>
  </div>
</template>
