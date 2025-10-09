<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

import { useAuthStore } from '../stores/auth'
import type { OrgMembershipSummary } from '../stores/auth'

const auth = useAuthStore()

const user = computed(() => auth.user)
const profile = computed(() => auth.user?.profile ?? null)
const organization = computed(() => auth.user?.organization ?? null)
const membershipList = computed(() => auth.activeMemberships)

const displayName = computed(() => profile.value?.name || user.value?.username || 'Learner')
const avatarUrl = computed(() => profile.value?.avatar_url || null)
const avatarFallback = computed(() => (displayName.value.charAt(0) || 'U').toUpperCase())

const roleLabel = computed(() => {
  switch (user.value?.role) {
    case 'superuser':
      return 'Superuser'
    case 'admin':
      return 'Admin'
    case 'org_admin':
      return 'Institution admin'
    default:
      return 'Learner'
  }
})

const accountTypeLabel = computed(() => {
  const accountType = user.value?.account_type ?? 'individual'
  return accountType.replace(/_/g, ' ')
})

const enrollmentStatus = computed(() => {
  if (!organization.value) return 'No active institution'
  return `Enrolled with ${organization.value.name}`
})

const primaryOrgId = computed(() => user.value?.learner_account?.primary_org_id ?? null)
const organizationAccountOrgId = computed(() => user.value?.organization_account?.organization_id ?? null)
const platformCreatedAt = computed(() => user.value?.platform_account?.created_at ?? null)

const membershipBadgeLabel = (membership: OrgMembershipSummary) => {
  const type = membership.organization.type?.toLowerCase().trim() ?? ''
  if (type.includes('free')) return 'Free offer'
  if (type.includes('paid') || type.includes('premium') || type.includes('pro')) return 'Paid program'
  if (type.includes('ielts')) return 'IELTS focus'
  if (type.includes('rbb')) return 'RBB Level 4'
  if (type) {
    return type
      .split(/[-_]/)
      .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
      .join(' ')
  }
  if (membership.org_role === 'org_admin') return 'Org admin'
  if (membership.org_role === 'instructor') return 'Instructor'
  return 'Member access'
}
</script>

<template>
  <section v-if="user" class="space-y-8">
    <header class="rounded-4xl border border-slate-200 bg-white/95 p-6 sm:p-10 shadow-xl shadow-slate-900/10">
      <div class="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
        <div class="flex items-start gap-5">
          <div class="relative inline-flex h-20 w-20 items-center justify-center overflow-hidden rounded-3xl border border-slate-200 bg-slate-100 shadow-sm md:h-24 md:w-24">
            <img v-if="avatarUrl" :src="avatarUrl" alt="Profile avatar" class="h-full w-full object-cover" />
            <span v-else class="text-3xl font-semibold text-slate-500">{{ avatarFallback }}</span>
          </div>
          <div class="space-y-2">
            <span class="inline-flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.35em] text-slate-500">
              {{ roleLabel }}
            </span>
            <h1 class="text-3xl font-semibold text-slate-900 sm:text-4xl">
              {{ displayName }}
            </h1>
            <p class="text-sm text-slate-500">
              {{ enrollmentStatus }}
            </p>
          </div>
        </div>
        <RouterLink
          :to="{ name: 'settings' }"
          class="inline-flex items-center gap-2 rounded-full bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-slate-900/20 transition hover:bg-slate-700"
        >
          Edit details
        </RouterLink>
      </div>
    </header>

    <div class="grid gap-6 lg:grid-cols-[2fr,3fr]">
      <section class="space-y-5 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <header class="space-y-1">
          <h2 class="text-base font-semibold text-slate-900">Account overview</h2>
          <p class="text-sm text-slate-500">Quick snapshot of your QuizMaster identity and access.</p>
        </header>
        <dl class="grid gap-4 text-sm text-slate-600">
          <div>
            <dt class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">Username</dt>
            <dd class="mt-1 text-slate-800">{{ user.username }}</dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">Email</dt>
            <dd class="mt-1 text-slate-800">{{ user.email }}</dd>
          </div>
          <div v-if="profile?.phone">
            <dt class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">Phone</dt>
            <dd class="mt-1 text-slate-800">{{ profile.phone }}</dd>
          </div>
          <div v-if="profile?.student_id">
            <dt class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">Student ID</dt>
            <dd class="mt-1 text-slate-800">{{ profile.student_id }}</dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">Account type</dt>
            <dd class="mt-1 text-slate-800 capitalize">{{ accountTypeLabel }}</dd>
          </div>
          <div v-if="platformCreatedAt">
            <dt class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">Platform access since</dt>
            <dd class="mt-1 text-slate-800">{{ new Date(platformCreatedAt).toLocaleString() }}</dd>
          </div>
          <div v-if="organizationAccountOrgId !== null">
            <dt class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">Assigned institution</dt>
            <dd class="mt-1 text-slate-800">Org #{{ organizationAccountOrgId }}</dd>
          </div>
          <div v-if="primaryOrgId !== null">
            <dt class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">Primary organization</dt>
            <dd class="mt-1 text-slate-800">Org #{{ primaryOrgId }}</dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">Status</dt>
            <dd class="mt-1 text-slate-800">{{ user.status === 'active' ? 'Active' : 'Pending verification' }}</dd>
          </div>
        </dl>
      </section>

      <section class="space-y-5 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <header class="space-y-1">
          <h2 class="text-base font-semibold text-slate-900">Institution access</h2>
          <p class="text-sm text-slate-500">
            Track the institutions you’re connected with and jump into their practice hubs.
          </p>
        </header>

        <div v-if="membershipList.length === 0" class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-6 text-sm text-slate-500">
          No institutions yet. Join using a QR code or enrollment link shared by your academy.
        </div>

        <ul v-else class="space-y-4">
          <li
            v-for="membership in membershipList"
            :key="membership.id"
            class="flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm sm:flex-row sm:items-center sm:justify-between"
          >
            <div class="flex items-start gap-3">
              <div class="mt-1 h-12 w-12 overflow-hidden rounded-xl border border-slate-200 bg-slate-50">
                <img
                  v-if="membership.organization.logo_url"
                  :src="membership.organization.logo_url"
                  :alt="`${membership.organization.name} logo`"
                  class="h-full w-full object-contain p-1.5"
                />
                <div v-else class="flex h-full w-full items-center justify-center text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">
                  {{ membership.organization.name.charAt(0) }}
                </div>
              </div>
              <div>
                <p class="text-sm font-semibold text-slate-900">{{ membership.organization.name }}</p>
                <p class="text-xs uppercase tracking-[0.3em] text-brand-500">{{ membershipBadgeLabel(membership) }}</p>
                <p class="mt-1 text-xs text-slate-500 capitalize">Role: {{ membership.org_role.replace('_', ' ') }}</p>
              </div>
            </div>
            <RouterLink
              :to="{ name: 'institution', params: { slug: membership.organization.slug } }"
              class="inline-flex items-center gap-2 rounded-full bg-slate-900 px-4 py-2 text-xs font-semibold uppercase tracking-[0.25em] text-white shadow-lg shadow-slate-900/20 transition hover:bg-slate-700"
            >
              Visit hub
              <span aria-hidden="true">→</span>
            </RouterLink>
          </li>
        </ul>
      </section>
    </div>

    <section class="rounded-3xl border border-slate-200 bg-slate-900 p-6 text-white shadow-lg shadow-slate-900/20">
      <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div class="space-y-2">
          <h2 class="text-base font-semibold">Keep your profile current</h2>
          <p class="text-sm text-slate-200">
            Update your name, phone number, avatar, and enrollment links from the settings page so mentors can recognise you instantly.
          </p>
        </div>
        <RouterLink
          :to="{ name: 'settings' }"
          class="inline-flex items-center gap-2 rounded-full border border-white/30 px-4 py-2 text-xs font-semibold uppercase tracking-[0.25em] text-white transition hover:border-white"
        >
          Manage settings
        </RouterLink>
      </div>
    </section>
  </section>
</template>
