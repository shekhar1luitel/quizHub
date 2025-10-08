<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { http } from '../../api/http'
import { useAuthStore } from '../../stores/auth'

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

onMounted(() => {
  if (auth.isAuthenticated) {
    router.replace({ name: 'dashboard' })
  }
})

const submit = async () => {
  error.value = ''
  loading.value = true
  try {
    const { data } = await http.post<{ access_token: string }>('/auth/login', {
      email: email.value,
      password: password.value,
    })
    auth.setAccessToken(data.access_token)
    await auth.fetchCurrentUser()
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/dashboard'
    router.push(redirect)
  } catch (err: any) {
    error.value = err?.response?.data?.detail || 'Invalid credentials'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="mx-auto flex w-full max-w-5xl flex-1 flex-col items-center justify-center py-12">
    <div class="mb-8 text-center">
      <RouterLink :to="{ name: 'home' }" class="inline-flex items-center gap-2 text-xl font-semibold text-slate-900">
        <span class="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 via-sky-500 to-emerald-500 text-white shadow">
          <span class="text-lg font-bold">Q</span>
        </span>
        QuizMaster
      </RouterLink>
      <p class="mt-2 text-sm text-slate-500">Sign in to continue your learning journey.</p>
    </div>

    <div class="w-full max-w-md rounded-3xl border border-slate-200 bg-white p-8 shadow-xl">
      <header class="mb-6 space-y-1 text-center">
        <h1 class="text-2xl font-semibold text-slate-900">Welcome back</h1>
        <p class="text-sm text-slate-500">Use your registered email address to access analytics and quizzes.</p>
      </header>
      <form class="space-y-5" @submit.prevent="submit">
        <div class="space-y-2">
          <label class="text-sm font-semibold text-slate-700" for="email">Email</label>
          <input
            id="email"
            v-model="email"
            autocomplete="email"
            class="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200"
            placeholder="you@example.com"
            type="email"
            required
          />
        </div>
        <div class="space-y-2">
          <label class="text-sm font-semibold text-slate-700" for="password">Password</label>
          <input
            id="password"
            v-model="password"
            autocomplete="current-password"
            class="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200"
            placeholder="••••••••"
            type="password"
            required
          />
        </div>
        <button
          class="w-full rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
          :disabled="loading"
          type="submit"
        >
          {{ loading ? 'Signing in…' : 'Sign in' }}
        </button>
        <p v-if="error" class="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">{{ error }}</p>
        <p class="text-center text-xs text-slate-500">
          Don't have an account?
          <RouterLink :to="{ name: 'register' }" class="font-semibold text-slate-700 hover:underline">Create one</RouterLink>
        </p>
      </form>
    </div>
  </section>
</template>
