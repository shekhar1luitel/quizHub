<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import type { AxiosError } from 'axios'

import { http } from '../api/http'
import { useAuthStore } from '../stores/auth'

interface HeroQuizSummary {
  id: number
  title: string
  description?: string | null
  question_count: number
  is_active: boolean
  organization_id?: number | null
}

interface PracticeCategorySummary {
  slug: string
  name: string
  description?: string | null
  icon?: string | null
  total_questions: number
  difficulty: string
  difficulties?: string[]
  organization_id?: number | null
}

interface DashboardAttemptSummary {
  id: number
  quiz_id: number
  quiz_title: string
  score: number
  submitted_at: string
}

interface DashboardCategoryAccuracy {
  category_id: number | null
  category_name: string
  attempts: number
  average_score: number
}

interface DashboardWeeklyActivity {
  label: string
  attempts: number
}

interface DashboardSummary {
  total_attempts: number
  average_score: number
  total_correct_answers: number
  total_questions_answered: number
  recent_attempts: DashboardAttemptSummary[]
  streak: number
  category_accuracy: DashboardCategoryAccuracy[]
  weekly_activity: DashboardWeeklyActivity[]
}

const auth = useAuthStore()

const loading = ref(true)
const error = ref<string | null>(null)
const featuredQuizzes = ref<HeroQuizSummary[]>([])
const topCategories = ref<PracticeCategorySummary[]>([])
const dashboardSummary = ref<DashboardSummary | null>(null)
const quizMetrics = ref({ total: 0, active: 0 })
const categoryMetrics = ref({ total: 0, questions: 0 })

const primaryCtaLabel = computed(() => {
  if (!auth.isAuthenticated) return 'Start Practicing'
  if (auth.isLearner) return 'Go to Dashboard'
  if (auth.isSuperuser) return 'Open platform controls'
  if (auth.isAdmin) return 'Open admin console'
  return 'View profile'
})

const primaryCtaRoute = computed(() => {
  if (!auth.isAuthenticated) return { name: 'register' }
  if (auth.isLearner) return { name: 'dashboard' }
  if (auth.isSuperuser) return { name: 'admin-organizations' }
  if (auth.isAdmin) return { name: 'admin' }
  return { name: 'profile' }
})

const secondaryCtaLabel = computed(() => {
  if (!auth.isAuthenticated) return 'Login'
  if (auth.isLearner) return 'Browse categories'
  if (auth.isSuperuser) return 'Manage users'
  if (auth.isAdmin) return 'Manage quizzes'
  return 'Account settings'
})

const secondaryCtaRoute = computed(() => {
  if (!auth.isAuthenticated) return { name: 'login' }
  if (auth.isLearner) return { name: 'categories' }
  if (auth.isSuperuser) return { name: 'admin-users' }
  if (auth.isAdmin) return { name: 'admin-quizzes' }
  return { name: 'settings' }
})

const heroHeading = computed(() => {
  if (dashboardSummary.value) {
    return 'Welcome back — here’s your snapshot'
  }
  if (auth.isAdmin) {
    return 'Monitor platform activity at a glance'
  }
  return 'Practice Lok Sewa–style quizzes with instant feedback'
})

const heroDescription = computed(() => {
  if (dashboardSummary.value) {
    return 'Review today’s numbers, revisit analytics, and jump straight into your next quiz.'
  }
  if (auth.isAdmin) {
    return 'Review active content, ensure categories stay fresh, and keep the learning experience running smoothly.'
  }
  return 'Build confidence with curated question banks, timed mock tests, and rich explanations. Track progress on your personal dashboard and tackle weak areas faster.'
})

const scoreColour = (value: number) => {
  if (value >= 80) return 'text-emerald-600'
  if (value >= 60) return 'text-amber-600'
  return 'text-rose-600'
}

const summaryAccuracy = computed(() => {
  if (!dashboardSummary.value || dashboardSummary.value.total_questions_answered === 0) return 0
  return Math.round(
    (dashboardSummary.value.total_correct_answers / dashboardSummary.value.total_questions_answered) * 100
  )
})

const summaryCards = computed(() => {
  if (!dashboardSummary.value) return []
  const summary = dashboardSummary.value
  return [
    {
      label: 'Total sessions',
      value: summary.total_attempts.toString(),
      caption: 'Completed quizzes and practice sets.',
      valueClass: 'text-slate-900',
    },
    {
      label: 'Average score',
      value: `${summary.average_score.toFixed(1)}%`,
      caption: 'Across all attempts.',
      valueClass: scoreColour(summary.average_score),
    },
    {
      label: 'Questions solved',
      value: summary.total_questions_answered.toString(),
      caption: `${summaryAccuracy.value}% accuracy · ${summary.total_correct_answers} correct`,
      valueClass: 'text-slate-900',
    },
    {
      label: 'Current streak',
      value: summary.streak === 1 ? '1 day' : `${summary.streak} days`,
      caption: 'Keep practising daily to grow this number.',
      valueClass: 'text-indigo-600',
    },
  ]
})

const adminCards = computed(() => {
  if (!auth.isAdmin) return []
  const active = quizMetrics.value.active
  const totalQuizzes = quizMetrics.value.total
  const totalCategories = categoryMetrics.value.total
  const totalQuestions = categoryMetrics.value.questions
  return [
    {
      label: 'Active quizzes',
      value: totalQuizzes ? `${active}/${totalQuizzes}` : `${active}`,
      caption: totalQuizzes
        ? 'Live quizzes vs total created.'
        : 'Live quizzes ready for learners.',
      valueClass: 'text-slate-900',
    },
    {
      label: 'Practice categories',
      value: totalCategories.toString(),
      caption: 'Subjects currently published.',
      valueClass: 'text-slate-900',
    },
    {
      label: 'Question coverage',
      value: totalQuestions.toString(),
      caption: 'Active questions powering quizzes.',
      valueClass: 'text-indigo-600',
    },
  ]
})

const loadHomeData = async () => {
  loading.value = true
  error.value = null
  dashboardSummary.value = null
  try {
    await auth.initialize()
  } catch (err) {
    console.error(err)
  }

  const fetchQuizzes = async () => {
    try {
      const { data } = await http.get<HeroQuizSummary[]>('/quizzes')
      quizMetrics.value = {
        total: data.length,
        active: data.filter((quiz) => quiz.is_active).length,
      }
      featuredQuizzes.value = data.filter((quiz) => quiz.is_active).slice(0, 3)
    } catch (err) {
      console.error(err)
      featuredQuizzes.value = []
      quizMetrics.value = { total: 0, active: 0 }
    }
  }

  const fetchCategories = async () => {
    try {
      const { data } = await http.get<PracticeCategorySummary[]>('/practice/categories')
      categoryMetrics.value = {
        total: data.length,
        questions: data.reduce((sum, item) => sum + (item.total_questions ?? 0), 0),
      }
      topCategories.value = data.slice(0, 4)
    } catch (err) {
      console.error(err)
      const status = (err as AxiosError).response?.status
      if (status === 401 || status === 403) {
        topCategories.value = []
        error.value = null
      } else {
        error.value = 'We could not load the latest practice data. Please try again soon.'
      }
      categoryMetrics.value = { total: 0, questions: 0 }
    }
  }

  const fetchSummary = async () => {
    if (!auth.isLearner) {
      dashboardSummary.value = null
      return
    }
    try {
      const { data } = await http.get<DashboardSummary>('/dashboard/summary')
      dashboardSummary.value = data
    } catch (err) {
      console.error(err)
      dashboardSummary.value = null
    }
  }

  try {
    await Promise.all([fetchQuizzes(), fetchCategories(), fetchSummary()])
  } finally {
    loading.value = false
  }
}

onMounted(loadHomeData)
</script>

<template>
  <div class="space-y-12">
    <section class="rounded-4xl border border-slate-200 bg-white/95 p-6 shadow-xl shadow-brand-900/10 sm:p-10">
      <div class="mx-auto grid max-w-6xl gap-8 lg:grid-cols-[3fr,2fr] lg:items-center">
        <div class="space-y-6">
          <span class="inline-flex items-center gap-2 rounded-full bg-brand-50 px-4 py-1 text-xs font-semibold uppercase tracking-[0.35em] text-brand-600">
            Lok Sewa prep made simple
          </span>
          <div class="space-y-4">
            <h1 class="text-3xl font-semibold leading-tight text-slate-900 sm:text-4xl">
              {{ heroHeading }}
            </h1>
            <p class="text-sm text-slate-600 sm:text-base">
              {{ heroDescription }}
            </p>
          </div>
          <div class="flex flex-col gap-3 sm:flex-row">
            <RouterLink
              :to="primaryCtaRoute"
              class="inline-flex items-center justify-center gap-2 rounded-full bg-slate-900 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-slate-900/20 transition hover:bg-slate-700"
            >
              {{ primaryCtaLabel }}
              <span aria-hidden="true">→</span>
            </RouterLink>
            <RouterLink
              :to="secondaryCtaRoute"
              class="inline-flex items-center justify-center gap-2 rounded-full border border-slate-200 px-6 py-3 text-sm font-semibold text-slate-700 transition hover:border-brand-300 hover:text-brand-600"
            >
              {{ secondaryCtaLabel }}
            </RouterLink>
          </div>
          <dl v-if="dashboardSummary" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div
              v-for="card in summaryCards"
              :key="card.label"
              class="rounded-2xl border border-slate-200 bg-white/70 p-4 text-left shadow-sm"
            >
              <dt class="text-xs font-semibold uppercase tracking-[0.35em] text-slate-400">{{ card.label }}</dt>
              <dd class="mt-2">
                <p :class="['text-2xl font-semibold', card.valueClass]">{{ card.value }}</p>
                <p class="mt-1 text-xs text-slate-500">{{ card.caption }}</p>
              </dd>
            </div>
          </dl>
          <dl v-else-if="adminCards.length" class="grid gap-4 sm:grid-cols-3">
            <div
              v-for="card in adminCards"
              :key="card.label"
              class="rounded-2xl border border-slate-200 bg-white/70 p-4 text-left shadow-sm"
            >
              <dt class="text-xs font-semibold uppercase tracking-[0.35em] text-slate-400">{{ card.label }}</dt>
              <dd class="mt-2">
                <p :class="['text-2xl font-semibold', card.valueClass]">{{ card.value }}</p>
                <p class="mt-1 text-xs text-slate-500">{{ card.caption }}</p>
              </dd>
            </div>
          </dl>
          <dl v-else class="grid gap-4 sm:grid-cols-3">
            <div class="rounded-2xl border border-slate-200 bg-white/70 p-4 text-left shadow-sm">
              <dt class="text-xs font-semibold uppercase tracking-[0.35em] text-slate-400">Instant results</dt>
              <dd class="mt-2 text-base font-semibold text-slate-900">See correct answers and explanations right away.</dd>
            </div>
            <div class="rounded-2xl border border-slate-200 bg-white/70 p-4 text-left shadow-sm">
              <dt class="text-xs font-semibold uppercase tracking-[0.35em] text-slate-400">Smart dashboard</dt>
              <dd class="mt-2 text-base font-semibold text-slate-900">Track accuracy by subject and maintain streaks.</dd>
            </div>
            <div class="rounded-2xl border border-slate-200 bg-white/70 p-4 text-left shadow-sm">
              <dt class="text-xs font-semibold uppercase tracking-[0.35em] text-slate-400">Flexible practice</dt>
              <dd class="mt-2 text-base font-semibold text-slate-900">Filter by difficulty, bookmark questions, and retry.</dd>
            </div>
          </dl>
        </div>

        <div class="space-y-4 rounded-3xl border border-slate-200 bg-slate-900 p-6 text-white shadow-lg shadow-brand-900/40">
          <p class="text-xs font-semibold uppercase tracking-[0.35em] text-white/60">Featured quizzes</p>
          <div v-if="loading" class="space-y-3">
            <div v-for="n in 3" :key="n" class="h-20 animate-pulse rounded-2xl bg-white/10"></div>
          </div>
          <p v-else-if="error" class="rounded-2xl border border-amber-300/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-100">
            {{ error }}
          </p>
          <template v-else>
            <div v-if="featuredQuizzes.length === 0" class="rounded-2xl border border-white/10 bg-white/5 px-4 py-6 text-sm text-white/80">
              Quizzes coming soon. Admins can activate a quiz from the Quiz Studio to showcase it here.
            </div>
            <article
              v-for="quiz in featuredQuizzes"
              :key="quiz.id"
              class="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur transition hover:border-white/20"
            >
              <p class="text-sm font-semibold">{{ quiz.title }}</p>
              <p class="mt-2 text-xs text-white/70">
                {{ quiz.description || 'Timed mock test with curated explanations.' }}
              </p>
              <div class="mt-3 flex items-center justify-between text-xs text-white/60">
                <span>{{ quiz.question_count }} questions</span>
                <RouterLink
                  :to="{ name: 'quiz', params: { id: quiz.id } }"
                  class="inline-flex items-center gap-1 text-xs font-semibold text-white transition hover:text-blue-200"
                >
                  Start
                  <span aria-hidden="true">→</span>
                </RouterLink>
              </div>
            </article>
          </template>
        </div>
      </div>
    </section>

    <section class="mx-auto max-w-6xl space-y-6 px-2">
      <header class="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.35em] text-slate-400">Choose a focus</p>
          <h2 class="text-2xl font-semibold text-slate-900">Top practice categories</h2>
          <p class="text-sm text-slate-500">Dive into popular subjects or keep exploring to find your next challenge.</p>
        </div>
        <RouterLink
          :to="{ name: 'categories' }"
          class="inline-flex items-center justify-center gap-2 rounded-full border border-slate-200 px-4 py-2 text-xs font-semibold text-slate-700 transition hover:border-brand-300 hover:text-brand-600"
        >
          View all categories
          <span aria-hidden="true">→</span>
        </RouterLink>
      </header>

      <div v-if="loading" class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div v-for="n in 4" :key="`category-skeleton-${n}`" class="h-40 animate-pulse rounded-3xl border border-slate-200 bg-slate-100"></div>
      </div>
      <div v-else-if="topCategories.length === 0" class="rounded-3xl border border-slate-200 bg-white/80 p-10 text-center text-sm text-slate-500">
        Categories will appear here once they are created in the admin panel.
      </div>
      <div v-else class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <article
          v-for="category in topCategories"
          :key="category.slug"
          class="flex h-full flex-col gap-3 rounded-3xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg"
        >
          <div class="space-y-1">
            <p class="text-xs font-semibold uppercase tracking-[0.3em] text-brand-500">{{ category.difficulty }}</p>
            <h3 class="text-lg font-semibold text-slate-900">{{ category.name }}</h3>
            <p class="text-xs text-slate-500">
              {{ category.description || 'Sharpen your fundamentals with curated question sets.' }}
            </p>
          </div>
          <div class="mt-auto flex items-center justify-between text-xs text-slate-500">
            <span>{{ category.total_questions }} questions</span>
            <RouterLink
              :to="{ name: 'practice', params: { slug: category.slug } }"
              class="inline-flex items-center gap-1 text-brand-600 transition hover:text-brand-500"
            >
              Practice
              <span aria-hidden="true">→</span>
            </RouterLink>
          </div>
        </article>
      </div>
    </section>

    <section class="mx-auto max-w-6xl rounded-4xl border border-slate-200 bg-white/95 p-8 shadow-xl shadow-brand-900/10">
      <div class="grid gap-6 lg:grid-cols-2">
        <div class="space-y-3">
          <p class="text-xs font-semibold uppercase tracking-[0.35em] text-slate-400">Why QuizMaster</p>
          <h2 class="text-2xl font-semibold text-slate-900">Everything you need for Phase 1 prep</h2>
          <p class="text-sm text-slate-500">
            Carefully structured content, analytics, and admin controls make QuizMaster the central hub for Lok Sewa
            practice.
          </p>
          <ul class="space-y-3 text-sm text-slate-600">
            <li class="flex items-start gap-2">
              <span class="mt-1 h-2 w-2 rounded-full bg-brand-500"></span>
              Track streaks, accuracy, and category performance on a single dashboard.
            </li>
            <li class="flex items-start gap-2">
              <span class="mt-1 h-2 w-2 rounded-full bg-brand-500"></span>
              Admins can import questions, manage user access, and monitor platform health.
            </li>
            <li class="flex items-start gap-2">
              <span class="mt-1 h-2 w-2 rounded-full bg-brand-500"></span>
              Bookmark tricky questions and build targeted revision sets.
            </li>
          </ul>
        </div>
        <div class="space-y-4 rounded-3xl border border-slate-200 bg-slate-50 p-6">
          <h3 class="text-sm font-semibold text-slate-900">Upcoming features</h3>
          <p class="text-sm text-slate-600">
            CSV import, user management, and in-depth analytics are part of Phase 1. Payments and certification will
            follow in later milestones.
          </p>
          <RouterLink
            :to="{ name: 'quiz-setup' }"
            class="inline-flex items-center justify-center gap-2 rounded-full bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-700"
          >
            Explore quiz setup
            <span aria-hidden="true">→</span>
          </RouterLink>
        </div>
      </div>
    </section>
  </div>
</template>
