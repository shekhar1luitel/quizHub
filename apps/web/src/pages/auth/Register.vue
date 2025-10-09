<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { http } from '../../api/http'
import { useAuthStore } from '../../stores/auth'

const mode = ref<'register' | 'verify'>('register')
const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const verifying = ref(false)
const resending = ref(false)
const error = ref('')
const info = ref('')
const resendInfo = ref('')
const otp = ref('')
const enrollToken = ref('')

const router = useRouter()
const auth = useAuthStore()

onMounted(() => {
  if (auth.isAuthenticated) {
    router.replace({ name: 'dashboard' })
  }
})

const submitRegistration = async () => {
  error.value = ''
  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match.'
    return
  }

  if (!username.value.trim()) {
    error.value = 'Username is required.'
    return
  }

  loading.value = true
  try {
    const payload: Record<string, string> = {
      username: username.value.toLowerCase().trim(),
      email: email.value,
      password: password.value,
    }
    if (enrollToken.value.trim()) {
      payload.enroll_token = enrollToken.value.trim()
    }
    await http.post('/auth/register', payload)
    mode.value = 'verify'
    info.value = `We sent a 6-digit verification code to ${email.value}. Enter it below to activate your account.`
    resendInfo.value = ''
    otp.value = ''
  } catch (err: any) {
    error.value = err?.response?.data?.detail || 'Registration failed'
  } finally {
    loading.value = false
  }
}

const submitVerification = async () => {
  error.value = ''
  if (!otp.value.trim()) {
    error.value = 'Enter the verification code from your email.'
    return
  }
  verifying.value = true
  try {
    await http.post('/auth/verify-email', {
      username: username.value.toLowerCase().trim(),
      code: otp.value.trim(),
    })
    const { data } = await http.post<{ access_token: string }>('/auth/login', {
      username: username.value.toLowerCase().trim(),
      password: password.value,
    })
    auth.setAccessToken(data.access_token)
    await auth.fetchCurrentUser()
    router.push({ name: 'dashboard' })
  } catch (err: any) {
    error.value = err?.response?.data?.detail || 'Verification failed'
  } finally {
    verifying.value = false
  }
}

const resendVerification = async () => {
  error.value = ''
  resendInfo.value = ''
  resending.value = true
  try {
    await http.post('/auth/resend-verification', {
      username: username.value.toLowerCase().trim(),
      email: email.value,
    })
    resendInfo.value = 'Verification code resent. Please check your inbox.'
  } catch (err: any) {
    error.value = err?.response?.data?.detail || 'Unable to resend verification code'
  } finally {
    resending.value = false
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
      <p class="mt-2 text-sm text-slate-500">Join thousands of students preparing for success.</p>
    </div>

    <div class="w-full max-w-md rounded-3xl border border-slate-200 bg-white p-8 shadow-xl">
      <header class="mb-6 space-y-1 text-center" v-if="mode === 'register'">
        <h1 class="text-2xl font-semibold text-slate-900">Create account</h1>
        <p class="text-sm text-slate-500">Sign up to save your quiz history, track analytics, and unlock personalized insights.</p>
      </header>
      <header class="mb-6 space-y-1 text-center" v-else>
        <h1 class="text-2xl font-semibold text-slate-900">Verify your email</h1>
        <p class="text-sm text-slate-500">Enter the verification code we sent to activate your account.</p>
      </header>

      <form v-if="mode === 'register'" class="space-y-5" @submit.prevent="submitRegistration">
        <div class="space-y-2">
          <label class="text-sm font-semibold text-slate-700" for="reg-username">Username</label>
          <input
            id="reg-username"
            v-model="username"
            autocomplete="username"
            class="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200"
            placeholder="choose a unique username"
            type="text"
            minlength="3"
            maxlength="150"
            required
          />
        </div>
        <div class="space-y-2">
          <label class="text-sm font-semibold text-slate-700" for="reg-email">Email</label>
          <input
            id="reg-email"
            v-model="email"
            autocomplete="email"
            class="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200"
            placeholder="you@example.com"
            type="email"
            required
          />
        </div>
        <div class="space-y-2">
          <label class="text-sm font-semibold text-slate-700" for="reg-password">Password</label>
          <input
            id="reg-password"
            v-model="password"
            autocomplete="new-password"
            class="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200"
            placeholder="At least 8 characters"
            type="password"
            minlength="8"
            maxlength="72"
            required
          />
        </div>
        <div class="space-y-2">
          <label class="text-sm font-semibold text-slate-700" for="confirm-password">Confirm password</label>
          <input
            id="confirm-password"
            v-model="confirmPassword"
            autocomplete="new-password"
            class="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200"
            placeholder="Re-enter your password"
            type="password"
            minlength="8"
            maxlength="72"
            required
          />
        </div>
        <div class="space-y-2">
          <label class="text-sm font-semibold text-slate-700" for="enroll-token">Enrollment token (optional)</label>
          <input
            id="enroll-token"
            v-model="enrollToken"
            class="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200"
            placeholder="Paste your organization token"
            type="text"
            maxlength="255"
          />
          <p class="text-xs text-slate-400">
            Provide the token shared by your institution to join their private workspace instantly.
          </p>
        </div>
        <button
          class="w-full rounded-2xl bg-emerald-500 px-4 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-60"
          :disabled="loading"
          type="submit"
        >
          {{ loading ? 'Creating account…' : 'Create account' }}
        </button>
      </form>

      <form v-else class="space-y-5" @submit.prevent="submitVerification">
        <p class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">{{ info }}</p>
        <div class="space-y-2">
          <label class="text-sm font-semibold text-slate-700" for="reg-otp">Verification code</label>
          <input
            id="reg-otp"
            v-model="otp"
            inputmode="numeric"
            maxlength="6"
            minlength="6"
            class="w-full rounded-2xl border border-slate-300 px-4 py-3 text-center text-lg tracking-widest focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200"
            placeholder="• • • • • •"
            required
          />
        </div>
        <button
          class="w-full rounded-2xl bg-slate-900 px-4 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
          :disabled="verifying"
          type="submit"
        >
          {{ verifying ? 'Verifying…' : 'Verify & Sign in' }}
        </button>
        <button
          class="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm font-semibold text-slate-700 transition hover:border-slate-400 disabled:cursor-not-allowed disabled:opacity-60"
          :disabled="resending"
          type="button"
          @click="resendVerification"
        >
          {{ resending ? 'Sending…' : 'Resend code' }}
        </button>
        <p v-if="resendInfo" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">{{ resendInfo }}</p>
      </form>

      <p v-if="error" class="mt-4 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">{{ error }}</p>
      <p v-if="mode === 'register'" class="mt-4 text-center text-xs text-slate-500">
        Already have an account?
        <RouterLink :to="{ name: 'login' }" class="font-semibold text-slate-700 hover:underline">Sign in</RouterLink>
      </p>
      <p v-else class="mt-4 text-center text-xs text-slate-500">
        Enter the code emailed to <span class="font-semibold">{{ email }}</span>. Need to change email?
        <button class="font-semibold text-slate-700 hover:underline" type="button" @click="mode = 'register'">Edit details</button>
      </p>
    </div>
  </section>
</template>
