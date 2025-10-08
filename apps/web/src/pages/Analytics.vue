<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'

type Period = 'week' | 'month' | 'quarter' | 'year'

type CategoryPerformance = {
  category: string
  tests: number
  averageScore: number
  bestScore: number
  improvement: number
}

const selectedPeriod = ref<Period>('month')

const analytics = {
  overallStats: {
    totalTests: 25,
    averageScore: 78,
    totalTimeSpent: 15_600,
    improvementRate: 12,
    streak: 7,
  },
  categoryPerformance: [
    { category: 'General Knowledge', tests: 8, averageScore: 82, bestScore: 95, improvement: 15 },
    { category: 'Aptitude', tests: 6, averageScore: 75, bestScore: 88, improvement: 8 },
    { category: 'Reasoning', tests: 5, averageScore: 85, bestScore: 92, improvement: 18 },
    { category: 'English', tests: 3, averageScore: 68, bestScore: 78, improvement: -5 },
    { category: 'Mathematics', tests: 3, averageScore: 72, bestScore: 85, improvement: 22 },
  ],
  weeklyProgress: [
    { week: 'Week 1', tests: 3, averageScore: 65 },
    { week: 'Week 2', tests: 5, averageScore: 72 },
    { week: 'Week 3', tests: 4, averageScore: 78 },
    { week: 'Week 4', tests: 6, averageScore: 82 },
    { week: 'Week 5', tests: 7, averageScore: 85 },
  ],
  timeAnalysis: {
    averageTimePerQuestion: 45,
    fastestTest: 1200,
    slowestTest: 2400,
    optimalTimeRange: [30, 60],
  },
  strengths: ['Pattern Recognition', 'Logical Reasoning', 'World Geography'],
  weaknesses: ['Grammar Rules', 'Mathematical Calculations', 'Current Events'],
}

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

const timePerQuestion = computed(() => `${analytics.timeAnalysis.averageTimePerQuestion}s`)
const optimalTimeRange = computed(
  () => `${analytics.timeAnalysis.optimalTimeRange[0]}s – ${analytics.timeAnalysis.optimalTimeRange[1]}s`
)

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

const progressBarWidth = (value: number) => `${Math.min(Math.max(value, 0), 100)}%`

const weeklyAverage = computed(() =>
  Math.round(
    analytics.weeklyProgress.reduce((sum, entry) => sum + entry.averageScore, 0) /
      analytics.weeklyProgress.length
  )
)
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

    <div class="grid gap-6 lg:grid-cols-5">
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-[0.25em] text-slate-400">Total tests</p>
        <p class="mt-3 text-3xl font-semibold text-slate-900">{{ analytics.overallStats.totalTests }}</p>
        <p class="text-xs text-slate-500">Completed in {{ periodLabel }}</p>
      </article>
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-[0.25em] text-slate-400">Average score</p>
        <p :class="['mt-3 text-3xl font-semibold', scoreColour(analytics.overallStats.averageScore)]">
          {{ analytics.overallStats.averageScore }}%
        </p>
        <div class="mt-3 h-2 rounded-full bg-slate-100">
          <div
            class="h-full rounded-full bg-gradient-to-r from-indigo-500 via-sky-500 to-emerald-500"
            :style="{ width: progressBarWidth(analytics.overallStats.averageScore) }"
          />
        </div>
      </article>
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-[0.25em] text-slate-400">Study time</p>
        <p class="mt-3 text-3xl font-semibold text-slate-900">{{ formatDuration(analytics.overallStats.totalTimeSpent) }}</p>
        <p class="text-xs text-slate-500">Across quizzes and practice</p>
      </article>
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-[0.25em] text-slate-400">Improvement</p>
        <p :class="['mt-3 text-3xl font-semibold', improvementColour(analytics.overallStats.improvementRate)]">
          +{{ analytics.overallStats.improvementRate }}%
        </p>
        <p class="text-xs text-slate-500">Compared to last {{ periodLabel }}</p>
      </article>
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-[0.25em] text-slate-400">Study streak</p>
        <p class="mt-3 text-3xl font-semibold text-indigo-600">{{ analytics.overallStats.streak }}</p>
        <p class="text-xs text-slate-500">Days in a row</p>
      </article>
    </div>

    <div class="grid gap-6 xl:grid-cols-[1.5fr,1fr]">
      <section class="space-y-6 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <header class="flex items-center justify-between">
          <div>
            <h2 class="text-lg font-semibold text-slate-900">Category performance</h2>
            <p class="text-xs text-slate-500">Your strongest and weakest subjects</p>
          </div>
        </header>
        <ul class="space-y-5 text-sm">
          <li
            v-for="category in analytics.categoryPerformance"
            :key="category.category"
            class="space-y-3"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <span class="font-semibold text-slate-800">{{ category.category }}</span>
                <span class="rounded-full border border-slate-200 px-3 py-1 text-xs text-slate-500">
                  {{ category.tests }} tests
                </span>
              </div>
              <div class="flex items-center gap-3">
                <span :class="['font-semibold', scoreColour(category.averageScore)]">
                  {{ category.averageScore }}%
                </span>
                <span :class="['text-xs font-semibold', improvementColour(category.improvement)]">
                  {{ improvementPrefix(category.improvement) }}{{ Math.abs(category.improvement) }}%
                </span>
              </div>
            </div>
            <div class="h-2 rounded-full bg-slate-100">
              <div
                class="h-full rounded-full bg-gradient-to-r from-indigo-500 via-sky-500 to-emerald-500"
                :style="{ width: progressBarWidth(category.averageScore) }"
              />
            </div>
            <div class="flex justify-between text-xs text-slate-500">
              <span>Avg {{ category.averageScore }}%</span>
              <span>Best {{ category.bestScore }}%</span>
            </div>
          </li>
        </ul>
      </section>

      <aside class="space-y-6">
        <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 class="text-lg font-semibold text-slate-900">Time analysis</h2>
          <dl class="mt-4 space-y-3 text-sm text-slate-600">
            <div class="flex items-center justify-between">
              <dt class="text-slate-500">Average per question</dt>
              <dd class="font-semibold text-slate-900">{{ timePerQuestion }}</dd>
            </div>
            <div class="flex items-center justify-between">
              <dt class="text-slate-500">Fastest test</dt>
              <dd class="font-semibold text-slate-900">{{ formatDuration(analytics.timeAnalysis.fastestTest) }}</dd>
            </div>
            <div class="flex items-center justify-between">
              <dt class="text-slate-500">Slowest test</dt>
              <dd class="font-semibold text-slate-900">{{ formatDuration(analytics.timeAnalysis.slowestTest) }}</dd>
            </div>
            <div class="flex items-center justify-between">
              <dt class="text-slate-500">Optimal range</dt>
              <dd class="font-semibold text-slate-900">{{ optimalTimeRange }}</dd>
            </div>
          </dl>
        </section>

        <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 class="text-lg font-semibold text-slate-900">Focus areas</h2>
          <div class="mt-4 grid gap-4 text-sm text-slate-600">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-600">Strengths</p>
              <ul class="mt-2 space-y-2">
                <li
                  v-for="item in analytics.strengths"
                  :key="item"
                  class="rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-2 text-emerald-700"
                >
                  {{ item }}
                </li>
              </ul>
            </div>
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.2em] text-rose-600">Weaknesses</p>
              <ul class="mt-2 space-y-2">
                <li
                  v-for="item in analytics.weaknesses"
                  :key="item"
                  class="rounded-2xl border border-rose-100 bg-rose-50 px-4 py-2 text-rose-700"
                >
                  {{ item }}
                </li>
              </ul>
            </div>
          </div>
        </section>
      </aside>
    </div>

    <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <header class="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 class="text-lg font-semibold text-slate-900">Weekly progress</h2>
          <p class="text-xs text-slate-500">Average score trend across recent weeks</p>
        </div>
        <p class="text-xs font-semibold uppercase tracking-[0.2em] text-indigo-600">
          Weekly average {{ weeklyAverage }}%
        </p>
      </header>
      <div class="mt-6 grid gap-4 md:grid-cols-5">
        <div
          v-for="entry in analytics.weeklyProgress"
          :key="entry.week"
          class="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm"
        >
          <p class="text-xs font-semibold uppercase tracking-[0.25em] text-slate-500">{{ entry.week }}</p>
          <p class="mt-3 text-2xl font-semibold text-slate-900">{{ entry.averageScore }}%</p>
          <p class="text-xs text-slate-500">{{ entry.tests }} tests</p>
        </div>
      </div>
    </section>
  </section>
</template>
