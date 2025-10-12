<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import { http } from '../api/http'

type Period = 'week' | 'month' | 'quarter' | 'year'

interface AnalyticsOverallStats {
  total_tests: number
  average_score: number
  total_time_spent_seconds: number
  improvement_rate: number
  streak: number
}

interface AnalyticsSubjectPerformance {
  subject: string
  tests: number
  average_score: number
  best_score: number
  improvement: number
}

interface AnalyticsWeeklyProgressEntry {
  label: string
  tests: number
  average_score: number
}

interface AnalyticsTimeAnalysis {
  average_time_per_question_seconds: number
  fastest_attempt_seconds: number
  slowest_attempt_seconds: number
  recommended_time_per_question_lower: number
  recommended_time_per_question_upper: number
}

interface AnalyticsOverview {
  generated_at: string
  overall_stats: AnalyticsOverallStats
  subject_performance: AnalyticsSubjectPerformance[]
  weekly_progress: AnalyticsWeeklyProgressEntry[]
  time_analysis?: AnalyticsTimeAnalysis | null
  strengths: string[]
  weaknesses: string[]
}

const selectedPeriod = ref<Period>('month')
const loading = ref(true)
const error = ref('')
const analytics = ref<AnalyticsOverview | null>(null)

const formatDuration = (seconds: number) => {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  if (hours > 0) {
    return `${hours}h ${minutes}m`
  }
  return `${minutes}m`
}

const scoreColour = (score: number) => {
  if (score >= 80) return 'text-emerald-600'
  if (score >= 60) return 'text-amber-600'
  return 'text-rose-600'
}

const improvementColour = (value: number) => {
  if (value > 0) return 'text-emerald-600'
  if (value < 0) return 'text-rose-600'
  return 'text-slate-500'
}

const improvementPrefix = (value: number) => (value > 0 ? '+' : value < 0 ? '−' : '')

const loadAnalytics = async () => {
  loading.value = true
  error.value = ''
  try {
    const { data } = await http.get<AnalyticsOverview>('/analytics/overview')
    analytics.value = data
  } catch (err) {
    console.error(err)
    error.value = 'We were unable to load your analytics. Please try again shortly.'
  } finally {
    loading.value = false
  }
}

onMounted(loadAnalytics)

const overallStats = computed(() => analytics.value?.overall_stats)
const hasData = computed(() => Boolean(analytics.value && overallStats.value?.total_tests))

const timePerQuestion = computed(() => {
  const avg = analytics.value?.time_analysis?.average_time_per_question_seconds
  return avg ? `${avg.toFixed(1)}s` : '—'
})

const optimalTimeRange = computed(() => {
  const analysis = analytics.value?.time_analysis
  if (!analysis) return '—'
  return `${analysis.recommended_time_per_question_lower.toFixed(1)}s – ${analysis.recommended_time_per_question_upper.toFixed(1)}s`
})

const periodLabel = computed(() => {
  switch (selectedPeriod.value) {
    case 'week':
      return 'this week'
    case 'quarter':
      return 'this quarter'
    case 'year':
      return 'this year'
    default:
      return 'this month'
  }
})

const filteredWeeklyProgress = computed(() => {
  if (!analytics.value) return []
  const entries = analytics.value.weekly_progress
  if (!entries.length) return []
  const limits: Record<Period, number> = {
    week: 1,
    month: 4,
    quarter: 12,
    year: 52,
  }
  const limit = limits[selectedPeriod.value]
  return entries.slice(-limit)
})

const weeklyAverage = computed(() => {
  if (!filteredWeeklyProgress.value.length) return 0
  const total = filteredWeeklyProgress.value.reduce((sum, entry) => sum + entry.average_score, 0)
  return Math.round(total / filteredWeeklyProgress.value.length)
})

const progressBarWidth = (value: number) => `${Math.min(Math.max(value, 0), 100)}%`
</script>

<template>
  <section class="space-y-10">
    <header class="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
      <div class="flex items-start gap-4">
        <RouterLink
          :to="{ name: 'dashboard' }"
          class="inline-flex items-center gap-2 rounded-full border border-slate-200 px-4 py-2 text-xs font-semibold uppercase tracking-widest text-slate-600 transition hover:border-slate-300 hover:text-slate-900"
        >
          <span aria-hidden="true">←</span>
          Back to dashboard
        </RouterLink>
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">Insights</p>
          <h1 class="mt-2 text-3xl font-semibold text-slate-900">Performance analytics</h1>
          <p class="mt-2 max-w-xl text-sm text-slate-500">
            Track how your preparation evolves across weeks, subjects, and practice types.
          </p>
        </div>
      </div>
      <label class="flex items-center gap-3 text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
        Period
        <select
          v-model="selectedPeriod"
          class="rounded-2xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 focus:border-slate-400 focus:outline-none"
        >
          <option value="week">This week</option>
          <option value="month">This month</option>
          <option value="quarter">This quarter</option>
          <option value="year">This year</option>
        </select>
      </label>
    </header>

    <div v-if="loading" class="grid gap-6 lg:grid-cols-5">
      <div v-for="n in 5" :key="n" class="h-32 animate-pulse rounded-3xl bg-white/70"></div>
    </div>

    <p v-else-if="error" class="rounded-3xl border border-amber-200 bg-amber-50 p-5 text-sm text-amber-800">{{ error }}</p>

    <div v-else-if="analytics && hasData" class="grid gap-6 lg:grid-cols-5">
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-[0.25em] text-slate-400">Total tests</p>
        <p class="mt-3 text-3xl font-semibold text-slate-900">{{ overallStats?.total_tests }}</p>
        <p class="text-xs text-slate-500">Completed in {{ periodLabel }}</p>
      </article>
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-[0.25em] text-slate-400">Average score</p>
        <p :class="['mt-3 text-3xl font-semibold', scoreColour(overallStats?.average_score || 0)]">
          {{ overallStats?.average_score.toFixed(1) }}%
        </p>
        <div class="mt-3 h-2 rounded-full bg-slate-100">
          <div
            class="h-full rounded-full bg-gradient-to-r from-indigo-500 via-sky-500 to-emerald-500"
            :style="{ width: progressBarWidth(overallStats?.average_score || 0) }"
          />
        </div>
      </article>
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-[0.25em] text-slate-400">Study time</p>
        <p class="mt-3 text-3xl font-semibold text-slate-900">{{ formatDuration(overallStats?.total_time_spent_seconds || 0) }}</p>
        <p class="text-xs text-slate-500">Across quizzes and practice</p>
      </article>
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-[0.25em] text-slate-400">Improvement</p>
        <p :class="['mt-3 text-3xl font-semibold', improvementColour(overallStats?.improvement_rate || 0)]">
          {{ improvementPrefix(overallStats?.improvement_rate || 0) }}{{ (overallStats?.improvement_rate || 0).toFixed(1) }}%
        </p>
        <p class="text-xs text-slate-500">Compared with the previous period</p>
      </article>
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-[0.25em] text-slate-400">Streak</p>
        <p class="mt-3 text-3xl font-semibold text-slate-900">{{ overallStats?.streak }} days</p>
        <p class="text-xs text-slate-500">Keep the momentum going</p>
      </article>
    </div>

    <div v-else class="rounded-3xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-500">
      Complete a quiz to unlock your personal analytics.
    </div>

    <section v-if="analytics && hasData" class="grid gap-6 lg:grid-cols-[2fr,3fr]">
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <header class="flex items-center justify-between">
          <div>
            <h2 class="text-lg font-semibold text-slate-900">Subject performance</h2>
            <p class="text-xs text-slate-500">Understand how you’re performing across subjects.</p>
          </div>
        </header>
        <p v-if="analytics.subject_performance.length === 0" class="mt-6 text-sm text-slate-500">
          We need a bit more activity before we can surface subject insights.
        </p>
        <ul v-else class="mt-6 space-y-4 text-sm">
          <li
            v-for="entry in analytics.subject_performance"
            :key="entry.subject"
            class="rounded-2xl border border-slate-200 p-4"
          >
            <div class="flex items-center justify-between">
              <div>
                <p class="font-semibold text-slate-900">{{ entry.subject }}</p>
                <p class="text-xs text-slate-500">{{ entry.tests }} assessments</p>
              </div>
              <p :class="['text-lg font-semibold', scoreColour(entry.average_score)]">{{ entry.average_score.toFixed(1) }}%</p>
            </div>
            <div class="mt-3 grid gap-3 text-xs text-slate-500 md:grid-cols-3">
              <div>
                <p class="font-semibold text-slate-600">Best score</p>
                <p>{{ entry.best_score.toFixed(1) }}%</p>
              </div>
              <div>
                <p class="font-semibold text-slate-600">Average</p>
                <p>{{ entry.average_score.toFixed(1) }}%</p>
              </div>
              <div>
                <p class="font-semibold text-slate-600">Trend</p>
                <p :class="improvementColour(entry.improvement)">
                  {{ improvementPrefix(entry.improvement) }}{{ Math.abs(entry.improvement).toFixed(1) }}%
                </p>
              </div>
            </div>
          </li>
        </ul>
      </article>

      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <header class="flex items-center justify-between">
          <div>
            <h2 class="text-lg font-semibold text-slate-900">Weekly progress</h2>
            <p class="text-xs text-slate-500">Average score {{ periodLabel }}: {{ weeklyAverage }}%</p>
          </div>
        </header>
        <p v-if="filteredWeeklyProgress.length === 0" class="mt-6 text-sm text-slate-500">
          Complete a few more quizzes to unlock week-by-week tracking.
        </p>
        <ul v-else class="mt-6 space-y-3 text-sm">
          <li
            v-for="entry in filteredWeeklyProgress"
            :key="entry.label"
            class="rounded-2xl border border-slate-200 px-4 py-3"
          >
            <div class="flex items-center justify-between">
              <p class="font-semibold text-slate-900">{{ entry.label }}</p>
              <span :class="['text-sm font-semibold', scoreColour(entry.average_score)]">
                {{ entry.average_score.toFixed(1) }}%
              </span>
            </div>
            <p class="text-xs text-slate-500">{{ entry.tests }} quizzes</p>
          </li>
        </ul>
      </article>
    </section>

    <section v-if="analytics && hasData" class="grid gap-6 lg:grid-cols-[2fr,3fr]">
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <header class="flex items-center justify-between">
          <div>
            <h2 class="text-lg font-semibold text-slate-900">Time analysis</h2>
            <p class="text-xs text-slate-500">Find your ideal pace across different quizzes.</p>
          </div>
        </header>
        <div v-if="!analytics.time_analysis" class="mt-6 text-sm text-slate-500">
          Keep attempting quizzes to unlock timing insights.
        </div>
        <dl v-else class="mt-6 grid gap-4 text-sm md:grid-cols-2">
          <div class="rounded-2xl border border-slate-200 p-4">
            <dt class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Average time per question</dt>
            <dd class="mt-2 text-lg font-semibold text-slate-900">{{ timePerQuestion }}</dd>
            <dd class="text-xs text-slate-500">Sweet spot {{ optimalTimeRange }}</dd>
          </div>
          <div class="rounded-2xl border border-slate-200 p-4">
            <dt class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Fastest completion</dt>
            <dd class="mt-2 text-lg font-semibold text-slate-900">
              {{ formatDuration(analytics.time_analysis.fastest_attempt_seconds) }}
            </dd>
            <dd class="text-xs text-slate-500">Recorded on your quickest quiz</dd>
          </div>
          <div class="rounded-2xl border border-slate-200 p-4">
            <dt class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Slowest completion</dt>
            <dd class="mt-2 text-lg font-semibold text-slate-900">
              {{ formatDuration(analytics.time_analysis.slowest_attempt_seconds) }}
            </dd>
            <dd class="text-xs text-slate-500">Take time to review explanations</dd>
          </div>
          <div class="rounded-2xl border border-slate-200 p-4">
            <dt class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">Recommended pace</dt>
            <dd class="mt-2 text-lg font-semibold text-slate-900">{{ optimalTimeRange }}</dd>
            <dd class="text-xs text-slate-500">Target range for consistent accuracy</dd>
          </div>
        </dl>
      </article>

      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <header class="flex items-center justify-between">
          <div>
            <h2 class="text-lg font-semibold text-slate-900">Skill insights</h2>
            <p class="text-xs text-slate-500">Celebrate strengths and plan your next revision session.</p>
          </div>
        </header>
        <div class="mt-6 grid gap-4 md:grid-cols-2">
          <section class="rounded-2xl border border-emerald-200 bg-emerald-50 p-4">
            <h3 class="text-xs font-semibold uppercase tracking-[0.25em] text-emerald-500">Strengths</h3>
            <p v-if="analytics.strengths.length === 0" class="mt-3 text-sm text-emerald-700">
              Keep practicing to discover your strongest topics.
            </p>
            <ul v-else class="mt-3 space-y-2 text-sm text-emerald-800">
              <li v-for="skill in analytics.strengths" :key="`strength-${skill}`" class="rounded-xl bg-white/70 px-3 py-2">
                {{ skill }}
              </li>
            </ul>
          </section>
          <section class="rounded-2xl border border-amber-200 bg-amber-50 p-4">
            <h3 class="text-xs font-semibold uppercase tracking-[0.25em] text-amber-500">Opportunities</h3>
            <p v-if="analytics.weaknesses.length === 0" class="mt-3 text-sm text-amber-700">
              No gaps detected yet. Attempt more quizzes to find areas to improve.
            </p>
            <ul v-else class="mt-3 space-y-2 text-sm text-amber-800">
              <li v-for="skill in analytics.weaknesses" :key="`weakness-${skill}`" class="rounded-xl bg-white/70 px-3 py-2">
                {{ skill }}
              </li>
            </ul>
          </section>
        </div>
      </article>
    </section>
  </section>
</template>
