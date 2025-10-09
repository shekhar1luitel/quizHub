<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import { http } from '../api/http'
import { useAuthStore } from '../stores/auth'
import type { OrgMembershipSummary } from '../stores/auth'

interface InstitutionQuizSummary {
  id: number
  title: string
  description?: string | null
  question_count: number
  is_active: boolean
}

const props = defineProps<{ slug: string }>()

const auth = useAuthStore()
const router = useRouter()

const loading = ref(false)
const error = ref<string | null>(null)
const quizzes = ref<InstitutionQuizSummary[]>([])

const activeMemberships = computed(() => auth.activeMemberships as OrgMembershipSummary[])

const membership = computed<OrgMembershipSummary | null>(() => {
  return activeMemberships.value.find((item) => item.organization.slug === props.slug) ?? null
})

const organizationName = computed(() => {
  if (membership.value) return membership.value.organization.name
  return props.slug
    .split('-')
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(' ')
})

const membershipBadgeLabel = computed(() => {
  const current = membership.value
  if (!current) return 'Institution access'
  const type = current.organization.type?.toLowerCase().trim() ?? ''
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
  if (current.org_role === 'org_admin') return 'Org admin'
  if (current.org_role === 'instructor') return 'Instructor'
  return 'Member access'
})

const membershipRoleDescription = computed(() => {
  const role = membership.value?.org_role
  if (role === 'org_admin') return 'You help manage this institution’s enrollment.'
  if (role === 'instructor') return 'Instructor access with the ability to guide learners.'
  return 'Learner access with institution curated practice.'
})

const membershipStatusLabel = computed(() => {
  const status = membership.value?.status ?? 'unknown'
  if (status === 'active') return 'Active access'
  if (status === 'invited') return 'Pending acceptance'
  return status.charAt(0).toUpperCase() + status.slice(1)
})

const describeInstitution = computed(() => {
  const current = membership.value
  if (!current) {
    return 'Scan your institution QR code from Settings to unlock institution-specific practice menus.'
  }
  const type = current.organization.type?.toLowerCase().trim() ?? ''
  if (type.includes('ielts')) {
    return 'Focused IELTS mock tests, speaking simulations, and band score insights tailored by your institution.'
  }
  if (type.includes('rbb')) {
    return 'Specialised RBB Level 4 preparation with exclusive mock exams and banking aptitude drills.'
  }
  if (type.includes('free')) {
    return `${current.organization.name} shares complimentary practice tests and revision packs for enrolled learners.`
  }
  if (type.includes('paid') || type.includes('premium') || type.includes('pro')) {
    return `${current.organization.name} runs a paid preparation track with premium mocks and analytics.`
  }
  if (type) {
    return `${current.organization.name} offers a ${type} program with curated quizzes and study guidance.`
  }
  return `${current.organization.name} curates practice experiences for its learners inside QuizMaster.`
})

const organizationLogo = computed(() => membership.value?.organization.logo_url ?? null)

const loadQuizzes = async (organizationId: number) => {
  loading.value = true
  error.value = null
  quizzes.value = []
  try {
    const { data } = await http.get<InstitutionQuizSummary[]>('/quizzes', {
      params: { organization_id: organizationId },
    })
    quizzes.value = data.filter((quiz) => quiz.is_active)
  } catch (err) {
    console.error(err)
    error.value = 'Unable to load institution quizzes right now.'
  } finally {
    loading.value = false
  }
}

watch(
  () => membership.value?.organization.id,
  (organizationId) => {
    if (typeof document !== 'undefined') {
      const title = organizationId ? `${organizationName.value} · Institution Hub · QuizMaster` : 'Institution Hub · QuizMaster'
      document.title = title
    }
    if (organizationId) {
      if (membership.value?.status === 'active') {
        void loadQuizzes(organizationId)
      } else {
        quizzes.value = []
        if (membership.value?.status === 'invited') {
          error.value = 'Your invitation is pending approval from the institution.'
        } else if (membership.value?.status) {
          error.value = `Access is currently ${membership.value.status}. Contact your institution for assistance.`
        } else {
          error.value = 'Access to this institution is not active yet.'
        }
      }
    } else {
      quizzes.value = []
      error.value = null
    }
  },
  { immediate: true }
)

const goBack = () => {
  router.push({ name: 'dashboard' })
}
</script>

<template>
  <div class="space-y-8">
    <section
      v-if="!membership"
      class="rounded-3xl border border-amber-200 bg-amber-50/70 p-8 text-amber-900 shadow-sm shadow-amber-200/50"
    >
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div class="space-y-2">
          <h1 class="text-2xl font-semibold">Access unavailable</h1>
          <p class="text-sm">
            You are not currently enrolled in <span class="font-semibold">{{ organizationName }}</span>. Scan the QR code
            shared by your institution or redeem a fresh enrollment invite from Settings to unlock their practice hub.
          </p>
        </div>
        <button
          class="inline-flex items-center gap-2 rounded-full bg-slate-900 px-5 py-2 text-sm font-semibold text-white shadow-lg shadow-slate-900/20 transition hover:bg-slate-700"
          type="button"
          @click="goBack"
        >
          Go to dashboard
        </button>
      </div>
    </section>

    <template v-else>
      <section class="rounded-4xl border border-slate-200 bg-white/95 p-8 shadow-xl shadow-slate-900/10">
        <div class="space-y-6">
          <div class="flex flex-wrap items-center gap-3 text-xs font-semibold uppercase tracking-[0.35em] text-slate-400">
            <span class="inline-flex items-center gap-2 rounded-full bg-brand-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.35em] text-brand-600">
              {{ membershipBadgeLabel }}
            </span>
            <span>{{ membershipStatusLabel }}</span>
          </div>
          <div v-if="organizationLogo" class="h-14 w-14 overflow-hidden rounded-2xl border border-slate-200 bg-white/80 shadow-sm shadow-slate-900/10">
            <img :src="organizationLogo" :alt="`${organizationName} logo`" class="h-full w-full object-contain p-1.5" />
          </div>
          <div class="space-y-3">
            <h1 class="text-3xl font-semibold text-slate-900 sm:text-4xl">
              {{ organizationName }}
            </h1>
            <p class="text-sm text-slate-500 sm:text-base">
              {{ describeInstitution }}
            </p>
          </div>
          <div class="grid gap-4 sm:grid-cols-3">
            <div class="rounded-2xl border border-slate-200 bg-white/80 p-4 shadow-sm">
              <p class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">Your role</p>
              <p class="mt-2 text-sm font-semibold text-slate-900">{{ membership.org_role.replace('_', ' ') }}</p>
              <p class="mt-1 text-xs text-slate-500">{{ membershipRoleDescription }}</p>
            </div>
            <div class="rounded-2xl border border-slate-200 bg-white/80 p-4 shadow-sm">
              <p class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">Access status</p>
              <p class="mt-2 text-sm font-semibold text-slate-900">{{ membershipStatusLabel }}</p>
              <p class="mt-1 text-xs text-slate-500">
                Active enrollment keeps quizzes, analytics, and announcements unlocked for this institution.
              </p>
            </div>
            <div class="rounded-2xl border border-slate-200 bg-white/80 p-4 shadow-sm">
              <p class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">How to share access</p>
              <p class="mt-2 text-sm font-semibold text-slate-900">Use enrollment QR or invite token</p>
              <p class="mt-1 text-xs text-slate-500">
                Learners join by scanning the QR code from Settings or via an invite token provided by the institution.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section class="rounded-4xl border border-slate-200 bg-white p-6 shadow-sm">
        <header class="flex flex-col gap-2 border-b border-slate-200 pb-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h2 class="text-lg font-semibold text-slate-900">Available quizzes</h2>
            <p class="text-sm text-slate-500">
              Explore the latest mock tests and practice sets published by {{ organizationName }}.
            </p>
          </div>
          <RouterLink
            :to="{ name: 'home', hash: '#quizzes' }"
            class="inline-flex items-center gap-2 rounded-full border border-slate-200 px-4 py-2 text-xs font-semibold uppercase tracking-[0.25em] text-slate-600 transition hover:border-brand-200 hover:text-brand-600"
          >
            View marketplace
          </RouterLink>
        </header>

        <div v-if="loading" class="mt-6 grid gap-4 lg:grid-cols-3">
          <div v-for="n in 3" :key="`institution-quiz-skeleton-${n}`" class="h-32 animate-pulse rounded-2xl bg-slate-100"></div>
        </div>

        <p v-else-if="error" class="mt-6 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-700">
          {{ error }}
        </p>

        <p
          v-else-if="quizzes.length === 0"
          class="mt-6 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-6 text-sm text-slate-500"
        >
          {{ organizationName }} has not published any quizzes yet. You’ll see mock tests and practice sets here as soon as they go live.
        </p>

        <div v-else class="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <article
            v-for="quiz in quizzes"
            :key="quiz.id"
            class="flex h-full flex-col justify-between gap-4 rounded-3xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg"
          >
            <div class="space-y-2">
              <p class="text-xs font-semibold uppercase tracking-[0.3em] text-brand-500">
                {{ membershipBadgeLabel }}
              </p>
              <h3 class="text-lg font-semibold text-slate-900">{{ quiz.title }}</h3>
              <p class="text-xs text-slate-500">
                {{ quiz.description || 'Curated by your institution to match the exact test pattern.' }}
              </p>
            </div>
            <div class="flex items-center justify-between text-xs text-slate-500">
              <span>{{ quiz.question_count }} questions</span>
              <RouterLink
                :to="{ name: 'quiz', params: { id: quiz.id } }"
                class="inline-flex items-center gap-1 rounded-full bg-slate-900 px-3 py-1 text-xs font-semibold text-white shadow-sm transition hover:bg-slate-700"
              >
                Start quiz
                <span aria-hidden="true">→</span>
              </RouterLink>
            </div>
          </article>
        </div>
      </section>

      <section class="grid gap-4 lg:grid-cols-[2fr,3fr]">
        <article class="rounded-3xl border border-slate-200 bg-slate-900 p-6 text-white shadow-lg shadow-slate-900/20">
          <h2 class="text-base font-semibold">Stay synced with {{ organizationName }}</h2>
          <p class="mt-3 text-sm text-slate-200">
            Notifications about new tests, batch announcements, and resource drops arrive in your Notifications tab. Keep
            an eye out for fresh mock tests or limited-time offers from your institution.
          </p>
          <RouterLink
            :to="{ name: 'notifications' }"
            class="mt-5 inline-flex items-center gap-2 rounded-full bg-white/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.25em] text-white transition hover:bg-white/20"
          >
            View notifications
          </RouterLink>
        </article>
        <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 class="text-base font-semibold text-slate-900">How pricing works</h2>
          <p class="mt-2 text-sm text-slate-500">
            {{ membershipBadgeLabel }}. Institutions that mark programmes as paid may share coupon codes or payment links
            directly with you. Free programmes unlock instantly once you enroll.
          </p>
          <ul class="mt-4 space-y-2 text-sm text-slate-600">
            <li>— Free offers unlock quizzes without payment once you scan the enrollment QR code.</li>
            <li>— Paid programmes may bundle premium content, mentorship, and analytics dashboards.</li>
            <li>— Check notifications or contact your institution mentor for billing or upgrade support.</li>
          </ul>
        </article>
      </section>
    </template>
  </div>
</template>
