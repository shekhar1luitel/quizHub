<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import QrcodeVue from 'qrcode.vue'

import { http } from '../api/http'
import { useAuthStore } from '../stores/auth'
import type { AuthUser } from '../stores/auth'

interface EnrollmentTokenResponse {
  token: string
  enroll_url: string
  expires_at: string
}

const auth = useAuthStore()

const form = reactive({
  username: '',
  email: '',
  name: '',
  phone: '',
  avatarUrl: '',
  currentPassword: '',
  newPassword: '',
})

const saving = ref(false)
const savingError = ref<string | null>(null)
const savingMessage = ref<string | null>(null)

const enrollmentLink = ref<string | null>(null)
const enrollmentExpiresAt = ref<string | null>(null)
const enrollmentLoading = ref(false)
const enrollmentError = ref<string | null>(null)

const canManageEnrollment = computed(() => auth.isOrgManager && Boolean(auth.user?.organization))
const organizationName = computed(() => auth.user?.organization?.name ?? 'your organization')

const shareLink = computed(() => enrollmentLink.value ?? auth.user?.profile?.qr_code_uri ?? null)

const studentId = computed(() => auth.user?.profile?.student_id ?? null)

const avatarPreview = computed(() => form.avatarUrl.trim() || auth.user?.profile?.avatar_url || '')
const avatarFallback = computed(() => {
  const base = auth.user?.profile?.name || auth.user?.username || 'U'
  return base.charAt(0).toUpperCase()
})

const syncForm = (user: AuthUser | null) => {
  form.username = user?.username ?? ''
  form.email = user?.email ?? ''
  form.name = user?.profile?.name ?? ''
  form.phone = user?.profile?.phone ?? ''
  form.avatarUrl = user?.profile?.avatar_url ?? ''
  form.currentPassword = ''
  form.newPassword = ''
  if (!enrollmentLink.value && user?.profile?.qr_code_uri) {
    enrollmentLink.value = user.profile.qr_code_uri
  }
}

watch(
  () => auth.user,
  (user) => syncForm(user),
  { immediate: true }
)

const buildUpdatePayload = () => {
  const payload: Record<string, unknown> = {}
  if (form.username && form.username !== auth.user?.username) {
    payload.username = form.username
  }
  if (form.email && form.email !== auth.user?.email) {
    payload.email = form.email
  }
  payload.name = form.name ? form.name : null
  payload.phone = form.phone ? form.phone : null
  const currentAvatar = auth.user?.profile?.avatar_url ?? ''
  if (form.avatarUrl.trim() !== currentAvatar) {
    payload.avatar_url = form.avatarUrl.trim() ? form.avatarUrl.trim() : null
  }
  if (form.newPassword) {
    payload.current_password = form.currentPassword
    payload.new_password = form.newPassword
  }
  return payload
}

const saveProfile = async () => {
  saving.value = true
  savingError.value = null
  savingMessage.value = null
  try {
    if (form.newPassword && !form.currentPassword) {
      savingError.value = 'Add your current password to confirm this change.'
      return
    }
    const payload = buildUpdatePayload()
    if (!Object.keys(payload).length) {
      savingMessage.value = 'Nothing to update — you already look good!'
      return
    }
    const { data } = await http.patch<AuthUser>('/users/me', payload)
    auth.setUser(data)
    savingMessage.value = 'Profile updated successfully.'
    form.currentPassword = ''
    form.newPassword = ''
  } catch (error) {
    if (error instanceof Error) {
      savingError.value = error.message
    } else {
      savingError.value = 'Unable to save changes. Please try again.'
    }
  } finally {
    saving.value = false
  }
}

const generateEnrollmentLink = async () => {
  if (!auth.user?.organization) return
  enrollmentLoading.value = true
  enrollmentError.value = null
  try {
    const { data } = await http.post<EnrollmentTokenResponse>(
      `/organizations/${auth.user.organization.id}/enroll-tokens`,
      {}
    )
    enrollmentLink.value = data.enroll_url
    enrollmentExpiresAt.value = data.expires_at
    await auth.fetchCurrentUser()
    savingMessage.value = 'Enrollment invite refreshed.'
  } catch (error) {
    if (error instanceof Error) {
      enrollmentError.value = error.message
    } else {
      enrollmentError.value = 'Failed to create enrollment link.'
    }
  } finally {
    enrollmentLoading.value = false
  }
}

const copyLink = async () => {
  if (!shareLink.value) return
  try {
    await navigator.clipboard.writeText(shareLink.value)
    savingMessage.value = 'Invite link copied to clipboard.'
  } catch {
    savingError.value = 'Clipboard unavailable. Copy the URL manually.'
  }
}
</script>

<template>
  <div class="mx-auto flex max-w-5xl flex-col gap-12">
    <section class="rounded-2xl border border-slate-200/80 bg-white/90 shadow-sm shadow-slate-200/50 backdrop-blur">
      <header class="border-b border-slate-200/80 px-6 py-5 sm:px-8">
        <h2 class="text-lg font-semibold text-slate-900">Profile & preferences</h2>
        <p class="mt-1 text-sm text-slate-500">
          Keep your account details current so teammates recognize you in leaderboards and analytics.
        </p>
      </header>
      <form class="space-y-8 px-6 py-6 sm:px-8" @submit.prevent="saveProfile">
        <div class="flex flex-col gap-3 rounded-2xl border border-slate-200/70 bg-slate-50/70 p-4 sm:flex-row sm:items-center sm:justify-between">
          <div class="flex items-center gap-4">
            <div class="flex h-16 w-16 items-center justify-center overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
              <img v-if="avatarPreview" :src="avatarPreview" alt="Avatar preview" class="h-full w-full object-cover" />
              <span v-else class="text-xl font-semibold text-slate-500">{{ avatarFallback }}</span>
            </div>
            <label class="flex flex-col gap-1 text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
              Avatar URL
              <input
                v-model="form.avatarUrl"
                type="url"
                placeholder="https://cdn.example.com/avatars/you.png"
                class="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition focus:border-brand-300 focus:outline-none focus:ring-2 focus:ring-brand-200"
              />
            </label>
          </div>
          <p class="text-xs text-slate-500">
            Add a publicly accessible image URL. We recommend a square image at least 240×240 pixels.
          </p>
        </div>

        <div class="grid gap-6 md:grid-cols-2">
          <label class="flex flex-col gap-2">
            <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Username</span>
            <input
              v-model="form.username"
              type="text"
              class="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-700 shadow-sm transition focus:border-brand-300 focus:outline-none focus:ring-2 focus:ring-brand-200"
              autocomplete="username"
              required
            />
          </label>
          <label class="flex flex-col gap-2">
            <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Email</span>
            <input
              v-model="form.email"
              type="email"
              class="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-700 shadow-sm transition focus:border-brand-300 focus:outline-none focus:ring-2 focus:ring-brand-200"
              autocomplete="email"
              required
            />
          </label>
          <label class="flex flex-col gap-2">
            <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Display name</span>
            <input
              v-model="form.name"
              type="text"
              placeholder="Your full name"
              class="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-700 shadow-sm transition focus:border-brand-300 focus:outline-none focus:ring-2 focus:ring-brand-200"
              autocomplete="name"
            />
          </label>
          <label class="flex flex-col gap-2">
            <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Contact number</span>
            <input
              v-model="form.phone"
              type="tel"
              placeholder="+977 ..."
              class="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-700 shadow-sm transition focus:border-brand-300 focus:outline-none focus:ring-2 focus:ring-brand-200"
              autocomplete="tel"
            />
          </label>
        </div>

        <div class="grid gap-6 md:grid-cols-2">
          <label class="flex flex-col gap-2">
            <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Current password</span>
            <input
              v-model="form.currentPassword"
              type="password"
              placeholder="Required if setting a new password"
              class="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-700 shadow-sm transition focus:border-brand-300 focus:outline-none focus:ring-2 focus:ring-brand-200"
              autocomplete="current-password"
            />
          </label>
          <label class="flex flex-col gap-2">
            <span class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">New password</span>
            <input
              v-model="form.newPassword"
              type="password"
              placeholder="Leave blank to keep existing password"
              class="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-medium text-slate-700 shadow-sm transition focus:border-brand-300 focus:outline-none focus:ring-2 focus:ring-brand-200"
              autocomplete="new-password"
              minlength="8"
            />
          </label>
        </div>

        <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">
            {{ studentId ? `Student ID: ${studentId}` : 'No student ID yet' }}
          </div>
          <div class="flex items-center gap-3">
            <button
              type="button"
              class="inline-flex items-center gap-2 rounded-full border border-slate-200 px-4 py-2 text-xs font-semibold uppercase tracking-[0.25em] text-slate-500 transition hover:border-slate-300 hover:text-slate-700"
              @click="syncForm(auth.user)"
            >
              Reset
            </button>
            <button
              type="submit"
              :disabled="saving"
              class="inline-flex items-center gap-2 rounded-full bg-slate-900 px-5 py-2 text-xs font-semibold uppercase tracking-[0.25em] text-white shadow-lg shadow-slate-900/20 transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-400"
            >
              <span v-if="saving" class="h-2 w-2 animate-pulse rounded-full bg-white/80"></span>
              Save changes
            </button>
          </div>
        </div>

        <div v-if="savingMessage" class="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
          {{ savingMessage }}
        </div>
        <div v-if="savingError" class="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-600">
          {{ savingError }}
        </div>
      </form>
    </section>

    <section
      v-if="canManageEnrollment"
      class="rounded-2xl border border-slate-200/80 bg-gradient-to-br from-slate-900 via-slate-900 to-slate-800 text-white shadow-xl shadow-slate-900/10"
    >
      <div class="space-y-6 px-6 py-8 sm:px-10">
        <div class="flex flex-col gap-2">
          <h2 class="text-lg font-semibold">Enrollment QR code</h2>
          <p class="text-sm text-slate-300">
            Share this QR code with learners to instantly enroll them into {{ organizationName }} — they will gain access to syllabus,
            quizzes, and resource packs once they scan and sign in.
          </p>
        </div>

        <div
          class="flex flex-col items-start justify-between gap-8 rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur sm:flex-row sm:items-center"
        >
          <div class="space-y-4">
            <p class="text-sm text-slate-200">
              Generate a fresh invite whenever you need to rotate access. Tokens automatically expire to keep your community secure.
            </p>
            <div class="flex flex-wrap items-center gap-3">
              <button
                type="button"
                :disabled="enrollmentLoading"
                class="inline-flex items-center gap-2 rounded-full bg-emerald-500 px-5 py-2 text-xs font-semibold uppercase tracking-[0.25em] text-emerald-950 shadow-lg shadow-emerald-500/30 transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:bg-emerald-700"
                @click="generateEnrollmentLink"
              >
                <span v-if="enrollmentLoading" class="h-2 w-2 animate-pulse rounded-full bg-emerald-900/60"></span>
                Refresh invite
              </button>
              <button
                v-if="shareLink"
                type="button"
                class="inline-flex items-center gap-2 rounded-full border border-white/30 px-4 py-2 text-xs font-semibold uppercase tracking-[0.25em] text-white/80 transition hover:border-white hover:text-white"
                @click="copyLink"
              >
                Copy link
              </button>
            </div>
            <p v-if="enrollmentExpiresAt" class="text-xs font-semibold uppercase tracking-[0.25em] text-emerald-200/70">
              Expires {{ new Date(enrollmentExpiresAt).toLocaleString() }}
            </p>
          </div>

          <div class="flex w-full flex-col items-center gap-3 text-center sm:w-auto">
            <div
              class="rounded-3xl border border-white/20 bg-white/90 p-5 shadow-lg shadow-slate-900/20"
            >
              <QrcodeVue v-if="shareLink" :value="shareLink" :size="192" level="M" render-as="svg" />
              <div v-else class="flex h-48 w-48 items-center justify-center text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">
                Generate invite
              </div>
            </div>
            <p v-if="shareLink" class="max-w-xs text-[11px] text-slate-200">
              Learners can also visit:
              <br />
              <span class="break-all font-semibold text-white">{{ shareLink }}</span>
            </p>
          </div>
        </div>

        <div v-if="enrollmentError" class="rounded-xl border border-rose-400 bg-rose-500/20 px-4 py-3 text-sm text-rose-100">
          {{ enrollmentError }}
        </div>
      </div>
    </section>
  </div>
</template>
