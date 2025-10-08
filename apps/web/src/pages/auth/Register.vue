<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { http } from '../../api/http'
import { useAuthStore } from '../../stores/auth'

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const router = useRouter()
const auth = useAuthStore()

const submit = async () => {
  error.value = ''
  loading.value = true
  try {
    await http.post('/auth/register', { email: email.value, password: password.value })
    const { data } = await http.post<{ access_token: string }>('/auth/login', {
      email: email.value,
      password: password.value,
    })
    auth.setAccessToken(data.access_token)
    await auth.fetchCurrentUser()
    router.push({ name: 'dashboard' })
  } catch (err: any) {
    error.value = err?.response?.data?.detail || 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="mx-auto max-w-md rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
    <header class="mb-6 space-y-1 text-center">
      <h1 class="text-xl font-semibold text-gray-900">Create an account</h1>
      <p class="text-sm text-gray-500">Register to save your quiz history and analytics.</p>
    </header>
    <form class="space-y-4" @submit.prevent="submit">
      <div class="space-y-1">
        <label class="text-sm font-medium text-gray-700" for="reg-email">Email</label>
        <input
          id="reg-email"
          v-model="email"
          autocomplete="email"
          class="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-gray-500 focus:outline-none"
          placeholder="you@example.com"
          type="email"
          required
        />
      </div>
      <div class="space-y-1">
        <label class="text-sm font-medium text-gray-700" for="reg-password">Password</label>
        <input
          id="reg-password"
          v-model="password"
          autocomplete="new-password"
          class="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-gray-500 focus:outline-none"
          placeholder="At least 8 characters"
          type="password"
          minlength="8"
          maxlength="72"
          required
        />
        <p class="text-xs text-gray-500">Use 8–72 characters to meet security requirements.</p>
      </div>
      <button
        class="w-full rounded bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-500 disabled:opacity-60"
        :disabled="loading"
        type="submit"
      >
        {{ loading ? 'Creating account…' : 'Create account' }}
      </button>
      <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
      <p class="text-center text-xs text-gray-500">
        Already have an account?
        <router-link :to="{ name: 'login' }" class="font-medium text-gray-700 hover:underline">Sign in</router-link>
      </p>
    </form>
  </section>
</template>
