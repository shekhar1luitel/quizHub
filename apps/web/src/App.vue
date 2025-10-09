<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const auth = useAuthStore()
const router = useRouter()

const navLinks = computed(() => {
  const links = [
    { label: 'Home', to: { name: 'home' } },
    { label: 'Categories', to: { name: 'categories' } },
  ]
  if (auth.isAuthenticated) {
    links.push({ label: 'Dashboard', to: { name: 'dashboard' } })
    links.push({ label: 'History', to: { name: 'history' } })
    links.push({ label: 'Analytics', to: { name: 'analytics' } })
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
    <header class="sticky top-0 z-40 border-b border-white/30 bg-gradient-to-r from-white/90 via-white/80 to-white/90 backdrop-blur">
      <div class="mx-auto flex w-full max-w-6xl items-center justify-between gap-4 px-6 py-4">
        <RouterLink :to="{ name: 'home' }" class="flex items-center gap-3 text-base font-semibold text-slate-800 transition hover:text-brand-600">
          <span
            class="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-500 via-sky-400 to-emerald-400 text-white shadow-lg shadow-brand-900/20"
            aria-hidden="true"
          >
            <span class="text-lg font-bold">Q</span>
          </span>
          <div class="hidden sm:flex flex-col leading-tight">
            <span class="text-xs font-semibold uppercase tracking-[0.35em] text-slate-400">QuizMaster</span>
            <span class="text-xs font-medium text-slate-500">Exam readiness suite</span>
          </div>
        </RouterLink>
        <nav class="hidden items-center gap-2 rounded-full border border-slate-200/70 bg-white/80 px-2 py-1 text-sm font-medium text-slate-600 shadow-sm backdrop-blur md:flex">
          <RouterLink
            v-for="link in navLinks"
            :key="link.label"
            :to="link.to"
            class="inline-flex items-center rounded-full px-4 py-2 transition hover:text-brand-600"
            active-class="bg-brand-50 text-brand-600 shadow-inner"
          >
            {{ link.label }}
          </RouterLink>
        </nav>
        <div class="flex items-center gap-2 text-sm">
          <span
            v-if="auth.user"
            class="hidden items-center gap-2 rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-500 sm:inline-flex"
          >
            <span class="inline-flex h-2 w-2 rounded-full bg-emerald-400"></span>
            {{ auth.user.email }}
          </span>
          <RouterLink
            v-if="!auth.isAuthenticated"
            :to="{ name: 'login' }"
            class="inline-flex items-center justify-center gap-2 rounded-full bg-slate-900 px-4 py-2 font-semibold text-white shadow-lg shadow-slate-900/25 transition hover:bg-slate-700"
          >
            <svg class="h-4 w-4" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="M11 4h-1.5a3.5 3.5 0 0 0 0 7H11m0 0-2-2m2 2-2 2m4-9h1a3 3 0 0 1 3 3v6a3 3 0 0 1-3 3h-1" />
            </svg>
            Login
          </RouterLink>
          <button
            v-else
            class="inline-flex items-center gap-2 rounded-full bg-slate-900 px-4 py-2 font-semibold text-white shadow-lg shadow-slate-900/25 transition hover:bg-slate-700"
            @click="logout"
          >
            <svg class="h-4 w-4" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="M11 4h-1.5a3.5 3.5 0 0 0 0 7H11m0 0-2-2m2 2-2 2m4-9h1a3 3 0 0 1 3 3v6a3 3 0 0 1-3 3h-1" />
            </svg>
            Logout
          </button>
        </div>
      </div>
    </header>
    <main class="mx-auto flex w-full max-w-6xl flex-1 flex-col px-6 pb-16 pt-10 md:pt-12">
      <RouterView />
    </main>
    <footer class="border-t border-slate-200/70 bg-white/80 py-6 text-sm text-slate-500 backdrop-blur">
      <div class="mx-auto flex w-full max-w-6xl flex-col items-center justify-between gap-4 px-6 text-xs font-semibold uppercase tracking-[0.3em] sm:flex-row sm:text-[11px]">
        <p class="text-[11px] font-medium normal-case tracking-normal text-slate-400">
          © {{ new Date().getFullYear() }} QuizMaster · Crafted for exam success.
        </p>
        <div class="flex items-center gap-3 text-slate-400">
          <RouterLink :to="{ name: 'home' }" class="transition hover:text-brand-600">Home</RouterLink>
          <RouterLink v-if="auth.isAuthenticated" :to="{ name: 'dashboard' }" class="transition hover:text-brand-600">
            Dashboard
          </RouterLink>
          <RouterLink v-if="auth.isAdmin" :to="{ name: 'admin' }" class="transition hover:text-brand-600">
            Admin
          </RouterLink>
        </div>
      </div>
    </footer>
  </div>
</template>
