<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { http } from '../api/http'

interface AttemptSummary {
  id: number
  quiz_id: number
  quiz_title: string
  score: number
  submitted_at: string
}

interface SubjectAccuracy {
  subject_id: number | null
  subject_name: string
  attempts: number
  average_score: number
}

interface WeeklyActivityEntry {
  label: string
  attempts: number
}

interface DashboardSummary {
  total_attempts: number
  average_score: number
  total_correct_answers: number
  total_questions_answered: number
  recent_attempts: AttemptSummary[]
  streak: number
  subject_accuracy: SubjectAccuracy[]
  weekly_activity: WeeklyActivityEntry[]
}

const loading = ref(true)
const error = ref('')
const summary = ref<DashboardSummary | null>(null)

const loadDashboard = async () => {
  try {
    const { data } = await http.get<DashboardSummary>('/dashboard/summary')
    summary.value = data
  } catch (err) {
    error.value = 'Unable to load dashboard data.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const formatDate = (iso: string) => new Date(iso).toLocaleString()

const attemptAccuracy = computed(() => {
  if (!summary.value || summary.value.total_questions_answered === 0) return 0
  return Math.round((summary.value.total_correct_answers / summary.value.total_questions_answered) * 100)
})

const streakLabel = computed(() => {
  if (!summary.value) return '0 days'
  const value = summary.value.streak
  if (value === 1) return '1 day'
  return `${value} days`
})

const topSubjects = computed(() => {
  if (!summary.value) return []
  return summary.value.subject_accuracy.slice(0, 5)
})

const weeklyActivity = computed(() => summary.value?.weekly_activity ?? [])
const hasWeeklyActivity = computed(() => weeklyActivity.value.length > 0)
const hasSubjectData = computed(() => topSubjects.value.length > 0)

const scoreClass = (score: number) => {
  if (score >= 80) return 'text-emerald-600'
  if (score >= 60) return 'text-amber-600'
  return 'text-rose-600'
}

const progressWidth = (score: number) => `${Math.min(Math.max(score, 0), 100)}%`

const improvementHint = computed(() => {
  if (!summary.value) return 'Complete quizzes to unlock insights.'
  if (summary.value.average_score >= 85) {
    return 'Outstanding performance! Maintain consistency to stay ahead.'
  }
  if (summary.value.average_score >= 60) {
    return 'Great job. Focus on revising weaker sections to boost your score.'
  }
  return 'Start with foundational quizzes and build momentum with regular practice.'
})

onMounted(loadDashboard)
</script>

<template>
  <section class="space-y-8">
    <header class="space-y-3">
      <p class="text-sm font-medium uppercase tracking-widest text-slate-400">Dashboard</p>
      <div class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h1 class="text-3xl font-semibold text-slate-900">Welcome back</h1>
          <p class="text-sm text-slate-500">Ready to dive back into your preparation? Track your progress and pick up where you left off.</p>
        </div>
        <RouterLink
          :to="{ name: 'home', hash: '#quizzes' }"
          class="inline-flex items-center justify-center rounded-full bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-700"
        >
          Start a new quiz
        </RouterLink>
      </div>
    </header>

    <div v-if="loading" class="grid gap-5 lg:grid-cols-4">
      <div v-for="n in 4" :key="n" class="h-32 animate-pulse rounded-3xl bg-white/60"></div>
    </div>

    <p v-else-if="error" class="rounded-3xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">{{ error }}</p>

    <div v-else-if="summary" class="space-y-8">
      <div class="grid gap-5 lg:grid-cols-4">
        <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Total progress</p>
          <p class="mt-3 text-3xl font-semibold text-slate-900">{{ summary.total_attempts }}<span class="text-base font-normal text-slate-400"> attempts</span></p>
          <p class="mt-2 text-xs text-slate-500">Consistent practice builds confidence.</p>
        </article>
        <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Average score</p>
          <p class="mt-3 text-3xl font-semibold text-slate-900">{{ summary.average_score.toFixed(1) }}%</p>
          <p class="mt-2 text-xs text-emerald-600">{{ improvementHint }}</p>
        </article>
        <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Questions solved</p>
          <p class="mt-3 text-3xl font-semibold text-slate-900">{{ summary.total_questions_answered }}</p>
          <p class="mt-2 text-xs text-slate-500">
            {{ attemptAccuracy }}% accuracy · {{ summary.total_correct_answers }} correct
          </p>
        </article>
        <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Current streak</p>
          <p class="mt-3 text-3xl font-semibold text-slate-900">{{ streakLabel }}</p>
          <p class="mt-2 text-xs text-slate-500">Keep the habit going every day.</p>
        </article>
      </div>

      <div class="grid gap-6 lg:grid-cols-[3fr,2fr]">
        <div class="space-y-6">
          <section class="rounded-3xl border border-slate-200 bg-white shadow-sm">
            <header class="flex items-center justify-between border-b border-slate-200 px-6 py-4">
              <div>
                <h2 class="text-base font-semibold text-slate-900">Recent attempts</h2>
                <p class="text-xs text-slate-500">Review how you performed in your last sessions.</p>
              </div>
            </header>
            <div v-if="summary.recent_attempts.length === 0" class="p-6 text-sm text-slate-500">
              You haven’t completed any quizzes yet. Start one from the home page.
            </div>
            <ul v-else class="divide-y divide-slate-200 text-sm">
              <li
                v-for="attempt in summary.recent_attempts"
                :key="attempt.id"
                class="flex items-center justify-between gap-4 px-6 py-4"
              >
                <div>
                  <p class="font-semibold text-slate-900">{{ attempt.quiz_title || 'Untitled quiz' }}</p>
                  <p class="text-xs text-slate-500">{{ formatDate(attempt.submitted_at) }}</p>
                </div>
                <span class="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-600">
                  {{ attempt.score.toFixed(1) }}%
                </span>
              </li>
            </ul>
          </section>

          <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <header class="flex items-center justify-between">
              <div>
                <h2 class="text-base font-semibold text-slate-900">Subject performance</h2>
                <p class="text-xs text-slate-500">Spot your strongest and weakest areas.</p>
              </div>
            </header>
            <p v-if="!hasSubjectData" class="mt-4 text-sm text-slate-500">
              Attempt a few quizzes to unlock subject-level insights.
            </p>
            <ul v-else class="mt-4 space-y-3 text-sm">
              <li
                v-for="subject in topSubjects"
                :key="`${subject.subject_id ?? 'general'}-${subject.subject_name}`"
                class="rounded-2xl border border-slate-200 p-4"
              >
                <div class="flex items-center justify-between">
                  <div>
                    <p class="font-semibold text-slate-900">{{ subject.subject_name }}</p>
                    <p class="text-xs text-slate-500">{{ subject.attempts }} sessions</p>
                  </div>
                  <span :class="['text-sm font-semibold', scoreClass(subject.average_score)]">
                    {{ subject.average_score.toFixed(1) }}%
                  </span>
                </div>
                <div class="mt-3 h-2 rounded-full bg-slate-100">
                  <div
                    class="h-full rounded-full bg-gradient-to-r from-indigo-500 via-sky-500 to-emerald-500"
                    :style="{ width: progressWidth(subject.average_score) }"
                  />
                </div>
              </li>
            </ul>
          </section>

          <section v-if="hasWeeklyActivity" class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <header class="flex items-center justify-between">
              <div>
                <h2 class="text-base font-semibold text-slate-900">Weekly activity</h2>
                <p class="text-xs text-slate-500">Stay consistent with your study rhythm.</p>
              </div>
            </header>
            <ul class="mt-4 space-y-3 text-sm">
              <li
                v-for="entry in weeklyActivity"
                :key="entry.label"
                class="flex items-center justify-between rounded-2xl border border-slate-200 px-4 py-3"
              >
                <span class="font-semibold text-slate-900">{{ entry.label }}</span>
                <span class="text-xs text-slate-500">{{ entry.attempts }} {{ entry.attempts === 1 ? 'session' : 'sessions' }}</span>
              </li>
            </ul>
          </section>
        </div>

        <aside class="space-y-6">
          <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 class="text-base font-semibold text-slate-900">Quick actions</h2>
            <ul class="mt-4 space-y-3 text-sm">
              <li>
                <RouterLink
                  :to="{ name: 'home', hash: '#quizzes' }"
                  class="flex items-center justify-between rounded-2xl border border-slate-200 px-4 py-3 transition hover:border-slate-300"
                >
                  <span>Take a new mock test</span>
                  <span aria-hidden="true">→</span>
                </RouterLink>
              </li>
              <li>
                <RouterLink
                  :to="summary.recent_attempts.length
                    ? { name: 'results', params: { id: summary.recent_attempts[0].id } }
                    : { name: 'dashboard' }"
                  class="flex items-center justify-between rounded-2xl border border-slate-200 px-4 py-3 transition hover:border-slate-300"
                  :class="{ 'pointer-events-none opacity-50': summary.recent_attempts.length === 0 }"
                >
                  <span>Review latest results</span>
                  <span aria-hidden="true">→</span>
                </RouterLink>
              </li>
              <li>
                <RouterLink
                  :to="{ name: 'bookmarks' }"
                  class="flex items-center justify-between rounded-2xl border border-slate-200 px-4 py-3 transition hover:border-slate-300"
                >
                  <span>Revise bookmarked questions</span>
                  <span aria-hidden="true">→</span>
                </RouterLink>
              </li>
              <li>
                <RouterLink
                  :to="{ name: 'home' }"
                  class="flex items-center justify-between rounded-2xl border border-slate-200 px-4 py-3 transition hover:border-slate-300"
                >
                  <span>Explore all quizzes</span>
                  <span aria-hidden="true">→</span>
                </RouterLink>
              </li>
            </ul>
          </section>

          <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 class="text-base font-semibold text-slate-900">Study insight</h2>
            <p class="mt-2 text-sm text-slate-500">
              {{ improvementHint }}
            </p>
            <p class="mt-4 text-xs text-slate-400">Tip: dedicate 15 minutes after each quiz to review explanations for incorrect answers.</p>
          </section>
        </aside>
      </div>
    </div>

    <p v-else class="text-sm text-slate-500">No dashboard data available yet.</p>
  </section>
</template>
