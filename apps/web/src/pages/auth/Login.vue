<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { http } from '../../api/http'
import { useAuthStore } from '../../stores/auth'

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

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
  <section class="mx-auto max-w-md rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
    <header class="mb-6 space-y-1 text-center">
      <h1 class="text-xl font-semibold text-gray-900">Welcome back</h1>
      <p class="text-sm text-gray-500">Log in to continue tracking your progress.</p>
    </header>
    <form class="space-y-4" @submit.prevent="submit">
      <div class="space-y-1">
        <label class="text-sm font-medium text-gray-700" for="email">Email</label>
        <input
          id="email"
          v-model="email"
          autocomplete="email"
          class="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-gray-500 focus:outline-none"
          placeholder="you@example.com"
          type="email"
          required
        />
      </div>
      <div class="space-y-1">
        <label class="text-sm font-medium text-gray-700" for="password">Password</label>
        <input
          id="password"
          v-model="password"
          autocomplete="current-password"
          class="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-gray-500 focus:outline-none"
          placeholder="••••••••"
          type="password"
          required
        />
      </div>
      <button
        class="w-full rounded bg-gray-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-gray-700 disabled:opacity-60"
        :disabled="loading"
        type="submit"
      >
        {{ loading ? 'Signing in…' : 'Sign in' }}
      </button>
      <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
      <p class="text-center text-xs text-gray-500">
        Don’t have an account?
        <router-link :to="{ name: 'register' }" class="font-medium text-gray-700 hover:underline">Register</router-link>
      </p>
    </form>
  </section>
</template>
