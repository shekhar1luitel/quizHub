<script setup lang="ts">
import { ref } from 'vue'
import { http } from '../../api/http'
const email = ref('')
const password = ref('')
const msg = ref('')
const submit = async () => {
  try {
    const { data } = await http.post('/auth/login', { email: email.value, password: password.value })
    msg.value = `Logged in! token: ${data.access_token.substring(0, 12)}...`
  } catch (e: any) {
    msg.value = e?.response?.data?.detail || 'Login failed'
  }
}
</script>
<template>
  <form class="max-w-sm space-y-3" @submit.prevent="submit">
    <input v-model="email" class="w-full border rounded px-3 py-2" placeholder="Email" />
    <input v-model="password" type="password" class="w-full border rounded px-3 py-2" placeholder="Password" />
    <button class="px-4 py-2 bg-black text-white rounded">Login</button>
    <p class="text-sm opacity-75">{{ msg }}</p>
  </form>
</template>
