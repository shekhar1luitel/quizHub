<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'

import { http } from '../../api/http'

interface MailConfig {
  host: string | null
  port: number | null
  username: string | null
  password: string | null
  tls_ssl: boolean
  from_name: string | null
  from_email: string | null
  is_configured: boolean
}

interface DispatchResult {
  processed: number
  sent: number
  failed: number
  errors: string[]
}

const config = reactive<MailConfig>({
  host: null,
  port: null,
  username: null,
  password: null,
  tls_ssl: true,
  from_name: null,
  from_email: null,
  is_configured: false,
})

const loading = ref(false)
const saving = ref(false)
const error = ref('')
const success = ref('')
const dispatchSummary = ref<DispatchResult | null>(null)

const loadConfig = async () => {
  loading.value = true
  error.value = ''
  try {
    const { data } = await http.get<MailConfig>('/admin/config/mail')
    Object.assign(config, data)
  } catch (err) {
    console.error(err)
    error.value = 'Unable to load mail configuration.'
  } finally {
    loading.value = false
  }
}

const saveConfig = async () => {
  saving.value = true
  error.value = ''
  success.value = ''
  try {
    const portValue = typeof config.port === 'number' && !Number.isNaN(config.port) ? config.port : null
    const payload = {
      host: config.host,
      port: portValue,
      username: config.username,
      password: config.password,
      tls_ssl: config.tls_ssl,
      from_name: config.from_name,
      from_email: config.from_email,
    }
    const { data } = await http.put<MailConfig>('/admin/config/mail', payload)
    Object.assign(config, data)
    success.value = 'Mail configuration saved.'
  } catch (err) {
    console.error(err)
    error.value = 'Unable to save mail configuration.'
  } finally {
    saving.value = false
  }
}

const dispatchEmails = async () => {
  dispatchSummary.value = null
  error.value = ''
  success.value = ''
  try {
    const { data } = await http.post<DispatchResult>('/admin/email/dispatch')
    dispatchSummary.value = data
    if (data.processed === 0) {
      success.value = 'No queued emails to send.'
    } else {
      success.value = `Processed ${data.processed} emails.`
    }
  } catch (err: any) {
    console.error(err)
    error.value = err?.response?.data?.detail || 'Unable to dispatch emails.'
  }
}

onMounted(() => {
  void loadConfig()
})
</script>

<template>
  <section class="space-y-8">
    <header class="space-y-2">
      <div class="inline-flex items-center gap-2 rounded-full bg-slate-100 px-4 py-1 text-xs font-semibold uppercase tracking-widest text-slate-600">
        Delivery infrastructure
      </div>
      <div class="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 class="text-3xl font-semibold text-slate-900">Mail configuration</h1>
          <p class="text-sm text-slate-500">
            Connect QuizMaster to your SMTP provider to send verification codes, admin invites, and transactional messages.
          </p>
        </div>
        <span
          class="inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold"
          :class="config.is_configured ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'"
        >
          {{ config.is_configured ? 'Ready for sending' : 'Configuration incomplete' }}
        </span>
      </div>
    </header>

    <p v-if="error" class="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">{{ error }}</p>
    <p v-if="success" class="rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">{{ success }}</p>

    <form class="grid gap-6 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm lg:grid-cols-2" @submit.prevent="saveConfig">
      <label class="flex flex-col gap-1 text-sm text-slate-600">
        SMTP host
        <input v-model="config.host" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="smtp.example.com" type="text" />
      </label>
      <label class="flex flex-col gap-1 text-sm text-slate-600">
        Port
        <input v-model.number="config.port" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="587" type="number" min="1" max="65535" />
      </label>
      <label class="flex flex-col gap-1 text-sm text-slate-600">
        Username
        <input v-model="config.username" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Optional" type="text" />
      </label>
      <label class="flex flex-col gap-1 text-sm text-slate-600">
        Password
        <input v-model="config.password" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Optional" type="password" />
      </label>
      <label class="flex flex-col gap-1 text-sm text-slate-600">
        From name
        <input v-model="config.from_name" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="QuizMaster" type="text" />
      </label>
      <label class="flex flex-col gap-1 text-sm text-slate-600">
        From email
        <input v-model="config.from_email" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="noreply@example.com" type="email" />
      </label>
      <label class="flex items-center gap-2 text-xs text-slate-600">
        <input v-model="config.tls_ssl" type="checkbox" class="h-4 w-4 rounded border-slate-200 text-brand-600" />
        Use STARTTLS
      </label>

      <div class="flex items-center gap-4">
        <button
          class="inline-flex items-center justify-center rounded-full bg-slate-900 px-5 py-2 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:opacity-50"
          type="submit"
          :disabled="saving"
        >
          {{ saving ? 'Saving…' : 'Save configuration' }}
        </button>
        <button
          class="inline-flex items-center justify-center rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:text-slate-900"
          type="button"
          @click="dispatchEmails"
        >
          Dispatch queued mail
        </button>
      </div>
    </form>

    <section v-if="dispatchSummary" class="rounded-3xl border border-slate-200 bg-white p-6 text-sm text-slate-600">
      <h2 class="text-lg font-semibold text-slate-900">Dispatch summary</h2>
      <ul class="mt-3 list-disc space-y-1 pl-5 text-sm">
        <li>Processed: {{ dispatchSummary.processed }}</li>
        <li>Sent: {{ dispatchSummary.sent }}</li>
        <li>Failed: {{ dispatchSummary.failed }}</li>
      </ul>
      <div v-if="dispatchSummary.errors.length" class="mt-3 space-y-1 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-xs text-amber-700">
        <p class="font-semibold uppercase tracking-[0.2em]">Errors</p>
        <ul class="list-disc space-y-1 pl-5">
          <li v-for="message in dispatchSummary.errors" :key="message">{{ message }}</li>
        </ul>
      </div>
    </section>

    <p v-if="loading" class="text-xs text-slate-400">Loading configuration…</p>
  </section>
</template>
