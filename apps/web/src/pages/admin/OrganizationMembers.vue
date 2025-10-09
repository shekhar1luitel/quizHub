<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { http } from '../../api/http'

interface OrganizationItem {
  id: number
  name: string
  slug: string
  status: string
  logo_url: string | null
}

interface OrgMember {
  user_id: number
  username: string
  email: string
  role: string
  account_type: string
  org_role: string
  status: string
}

interface OrgMemberResponse {
  items: OrgMember[]
  total: number
}

interface EnrollTokenResponse {
  token: string
  expires_at: string
}

const route = useRoute()
const organizationId = ref<number>(Number(route.params.id))

watch(
  () => route.params.id,
  (value) => {
    organizationId.value = Number(value)
    void loadMembers()
    void loadOrganization()
  },
)

const organization = ref<OrganizationItem | null>(null)
const members = ref<OrgMember[]>([])
const totalMembers = ref(0)
const loading = ref(false)
const error = ref('')
const tokenSuccess = ref('')
const generatedToken = ref<EnrollTokenResponse | null>(null)
const isOrganizationDisabled = computed(() => organization.value?.status === 'inactive')
const organizationLogo = computed(() => organization.value?.logo_url ?? null)

const tokenForm = reactive({ expires_in_minutes: 1440 })

const loadOrganization = async () => {
  error.value = ''
  try {
    const { data } = await http.get<OrganizationItem[]>('/organizations', {
      params: { limit: 200 },
    })
    organization.value = data.find((org) => org.id === organizationId.value) || null
  } catch (err) {
    console.error(err)
  }
}

const loadMembers = async () => {
  loading.value = true
  error.value = ''
  try {
    const { data } = await http.get<OrgMemberResponse>(`/organizations/${organizationId.value}/members`, {
      params: { limit: 100 },
    })
    members.value = data.items
    totalMembers.value = data.total
  } catch (err) {
    console.error(err)
    error.value = 'Unable to load members.'
  } finally {
    loading.value = false
  }
}

const generateToken = async () => {
  tokenSuccess.value = ''
  generatedToken.value = null
  if (isOrganizationDisabled.value) {
    error.value = 'This organization is disabled. Enable it before issuing new enrollment tokens.'
    return
  }
  try {
    const { data } = await http.post<EnrollTokenResponse>(
      `/organizations/${organizationId.value}/enroll-tokens`,
      { expires_in_minutes: tokenForm.expires_in_minutes },
    )
    generatedToken.value = data
    tokenSuccess.value = 'Enrollment token generated successfully.'
  } catch (err) {
    console.error(err)
    error.value = 'Unable to generate enrollment token.'
  }
}

const formatDateTime = (value: string) => new Date(value).toLocaleString()

onMounted(() => {
  void loadOrganization()
  void loadMembers()
})
</script>

<template>
  <section class="space-y-8">
    <header class="space-y-2">
      <div class="inline-flex items-center gap-2 rounded-full bg-slate-100 px-4 py-1 text-xs font-semibold uppercase tracking-widest text-slate-600">
        Organization directory
      </div>
      <div class="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div class="flex items-start gap-3">
          <div v-if="organizationLogo" class="h-12 w-12 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
            <img :src="organizationLogo" :alt="`${organization?.name ?? `Organization #${organizationId}`} logo`" class="h-full w-full object-contain p-1.5" />
          </div>
          <div>
            <h1 class="text-3xl font-semibold text-slate-900">
              {{ organization?.name || `Organization #${organizationId}` }}
            </h1>
            <p class="text-sm text-slate-500">
              Monitor members, invite learners, and keep records up to date for institutional customers.
            </p>
          </div>
        </div>
        <div class="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-xs text-slate-500">
          <span class="font-semibold text-slate-900">{{ totalMembers }}</span>
          members
        </div>
      </div>
    </header>

    <p
      v-if="isOrganizationDisabled"
      class="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800"
    >
      This organization is currently disabled. Learners cannot access its quizzes or attempts until it is enabled again.
    </p>

    <p v-if="error" class="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">{{ error }}</p>
    <p v-if="tokenSuccess" class="rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">{{ tokenSuccess }}</p>

    <section class="grid gap-6 lg:grid-cols-[2fr,3fr]">
      <form class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm" @submit.prevent="generateToken">
        <h2 class="text-lg font-semibold text-slate-900">Generate enrollment token</h2>
        <p class="mt-1 text-xs text-slate-500">
          Share tokens with institution coordinators so they can onboard learners via QR scan or manual entry.
        </p>
        <label class="mt-4 flex flex-col gap-1 text-sm text-slate-600">
          Expiration (minutes)
          <input
            v-model.number="tokenForm.expires_in_minutes"
            class="rounded-xl border border-slate-200 px-3 py-2 text-sm disabled:bg-slate-100 disabled:text-slate-400"
            min="15"
            max="43200"
            type="number"
            :disabled="isOrganizationDisabled"
          />
        </label>
        <button
          class="mt-4 inline-flex items-center justify-center rounded-full bg-slate-900 px-5 py-2 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-400"
          type="submit"
          :disabled="isOrganizationDisabled"
        >
          Generate token
        </button>

        <div v-if="generatedToken" class="mt-6 space-y-2 rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
          <p class="text-xs font-semibold uppercase tracking-[0.35em] text-slate-400">Token</p>
          <p class="font-mono text-base text-slate-900">{{ generatedToken.token }}</p>
          <p class="text-xs text-slate-500">Expires {{ formatDateTime(generatedToken.expires_at) }}</p>
        </div>
      </form>

      <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold text-slate-900">Active members</h2>
          <button
            class="inline-flex items-center justify-center rounded-full border border-slate-200 px-4 py-2 text-xs font-semibold text-slate-700 transition hover:border-slate-300 hover:text-slate-900"
            type="button"
            @click="loadMembers"
          >
            Refresh list
          </button>
        </div>
        <div class="mt-4 overflow-x-auto">
          <table class="min-w-full text-left text-sm">
            <thead class="text-xs uppercase tracking-wider text-slate-400">
              <tr>
                <th class="pb-2 pr-4">Member</th>
                <th class="pb-2 pr-4">Account</th>
                <th class="pb-2 pr-4">Org role</th>
                <th class="pb-2">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="member in members" :key="member.user_id">
                <td class="py-3 pr-4">
                  <div class="font-semibold text-slate-900">{{ member.username }}</div>
                  <div class="text-xs text-slate-500">{{ member.email }}</div>
                </td>
                <td class="py-3 pr-4 text-xs uppercase tracking-[0.25em]">{{ member.account_type }}</td>
                <td class="py-3 pr-4 text-xs uppercase tracking-[0.25em]">{{ member.org_role }}</td>
                <td class="py-3 text-xs">
                  <span
                    class="rounded-full px-3 py-1 font-semibold"
                    :class="member.status === 'active' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-600'"
                  >
                    {{ member.status }}
                  </span>
                </td>
              </tr>
              <tr v-if="!loading && members.length === 0">
                <td colspan="4" class="py-6 text-center text-sm text-slate-500">No members found.</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-if="loading" class="mt-3 text-xs text-slate-400">Loading members…</p>
      </div>
    </section>
  </section>
</template>
