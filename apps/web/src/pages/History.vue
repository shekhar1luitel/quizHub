<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import { http } from '../api/http'

type AttemptType = 'quiz' | 'practice' | 'mock'
type Difficulty = 'Easy' | 'Medium' | 'Hard' | 'Mixed'

interface AttemptHistoryEntryResponse {
  id: number
  quiz_id: number
  quiz_title: string
  submitted_at: string
  total_questions: number
  correct_answers: number
  score: number
  duration_seconds: number
  category_id: number | null
  category_name: string | null
  difficulty: string | null
  type: string
}

interface HistoryEntry {
  id: number
  quizId: number | null
  title: string
  category: string
  categoryId: number | null
  score: number
  totalQuestions: number
  correctAnswers: number
  timeSpent: number
  date: string
  type: AttemptType
  difficulty: Difficulty
}

const searchTerm = ref('')
const selectedCategory = ref('All')
const selectedType = ref<'All' | AttemptType>('All')
const sortBy = ref<'date' | 'score' | 'title'>('date')

const loading = ref(true)
const error = ref('')
const history = ref<HistoryEntry[]>([])

const DEFAULT_CATEGORY = 'General Practice'

const mapType = (value: string | undefined): AttemptType => {
  if (value === 'practice' || value === 'mock') return value
  return 'quiz'
}

const normalizeDifficulty = (value: string | null | undefined): Difficulty => {
  if (!value) return 'Mixed'
  const normalized = value.toLowerCase()
  if (normalized.startsWith('easy')) return 'Easy'
  if (normalized.startsWith('medium')) return 'Medium'
  if (normalized.startsWith('hard')) return 'Hard'
  return 'Mixed'
}

const loadHistory = async () => {
  loading.value = true
  error.value = ''
  try {
    const { data } = await http.get<AttemptHistoryEntryResponse[]>('/attempts/history')
    history.value = data.map((entry) => ({
      id: entry.id,
      quizId: entry.quiz_id ?? null,
      title: entry.quiz_title,
      category: entry.category_name?.trim() || DEFAULT_CATEGORY,
      categoryId: entry.category_id ?? null,
      score: Number(entry.score ?? 0),
      totalQuestions: entry.total_questions,
      correctAnswers: entry.correct_answers,
      timeSpent: entry.duration_seconds ?? 0,
      date: entry.submitted_at,
      type: mapType(entry.type),
      difficulty: normalizeDifficulty(entry.difficulty),
    }))
  } catch (err) {
    console.error(err)
    error.value = 'Unable to load history.'
    history.value = []
  } finally {
    loading.value = false
  }
}

onMounted(loadHistory)

const categories = computed(() => ['All', ...new Set(history.value.map((item) => item.category))])

const filteredHistory = computed(() => {
  const term = searchTerm.value.trim().toLowerCase()
  return history.value
    .filter((item) => {
      const matchesSearch = !term || item.title.toLowerCase().includes(term)
      const matchesCategory = selectedCategory.value === 'All' || item.category === selectedCategory.value
      const matchesType = selectedType.value === 'All' || item.type === selectedType.value
      return matchesSearch && matchesCategory && matchesType
    })
    .sort((a, b) => {
      switch (sortBy.value) {
        case 'score':
          return b.score - a.score
        case 'title':
          return a.title.localeCompare(b.title)
        default:
          return new Date(b.date).getTime() - new Date(a.date).getTime()
      }
    })
})

const totalTests = computed(() => history.value.length)
const averageScore = computed(() =>
  totalTests.value === 0
    ? 0
    : Math.round(history.value.reduce((sum, test) => sum + test.score, 0) / totalTests.value)
)
const totalTimeSpent = computed(() => history.value.reduce((sum, test) => sum + test.timeSpent, 0))
const bestScore = computed(() => (history.value.length ? Math.max(...history.value.map((test) => test.score)) : 0))

const formatDate = (iso: string) =>
  new Date(iso).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })

const formatDuration = (seconds: number) => {
  const minutes = Math.floor(seconds / 60)
  const remainder = seconds % 60
  return `${minutes}m ${remainder}s`
}

const scoreColour = (score: number) => {
  if (score >= 80) return 'text-emerald-600'
  if (score >= 60) return 'text-amber-600'
  return 'text-rose-600'
}

const difficultyBadge = (difficulty: HistoryEntry['difficulty']) => {
  switch (difficulty) {
    case 'Easy':
      return 'bg-emerald-100 text-emerald-800'
    case 'Medium':
      return 'bg-amber-100 text-amber-800'
    case 'Hard':
      return 'bg-rose-100 text-rose-800'
    default:
      return 'bg-sky-100 text-sky-800'
  }
}

const typeBadge = (type: AttemptType) => {
  switch (type) {
    case 'practice':
      return 'bg-emerald-50 text-emerald-700 border-emerald-100'
    case 'mock':
      return 'bg-purple-50 text-purple-700 border-purple-100'
    default:
      return 'bg-sky-50 text-sky-700 border-sky-100'
  }
}
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
          <p class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">History</p>
          <h1 class="mt-2 text-3xl font-semibold text-slate-900">Quiz history</h1>
          <p class="mt-2 max-w-xl text-sm text-slate-500">Review how you performed, when you practised, and where to focus next.</p>
        </div>
      </div>
      <RouterLink
        :to="{ name: 'analytics' }"
        class="inline-flex items-center justify-center rounded-full bg-slate-900 px-5 py-2 text-sm font-semibold text-white transition hover:bg-slate-700"
      >
        View analytics
      </RouterLink>
    </header>

    <div v-if="loading" class="grid gap-6 md:grid-cols-4">
      <div v-for="n in 4" :key="`history-skeleton-${n}`" class="h-32 animate-pulse rounded-3xl bg-white/70"></div>
    </div>
    <p v-else-if="error" class="rounded-3xl border border-amber-200 bg-amber-50 p-6 text-sm text-amber-700">
      {{ error }}
    </p>
    <div
      v-else-if="history.length === 0"
      class="rounded-3xl border border-slate-200 bg-white p-8 text-center text-sm text-slate-500"
    >
      Complete your first quiz to start building a history of attempts. Your session insights will appear here.
    </div>
    <div v-else class="grid gap-6 md:grid-cols-4">
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-[0.25em] text-slate-400">Total sessions</p>
        <p class="mt-3 text-3xl font-semibold text-slate-900">{{ totalTests }}</p>
        <p class="text-xs text-slate-500">Across all practice types</p>
      </article>
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-[0.25em] text-slate-400">Average score</p>
        <p :class="['mt-3 text-3xl font-semibold', scoreColour(averageScore)]">{{ averageScore }}%</p>
        <p class="text-xs text-slate-500">Consistency matters more than perfection</p>
      </article>
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-[0.25em] text-slate-400">Best score</p>
        <p class="mt-3 text-3xl font-semibold text-indigo-600">{{ bestScore }}%</p>
        <p class="text-xs text-slate-500">Reach this benchmark again this week</p>
      </article>
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-[0.25em] text-slate-400">Time invested</p>
        <p class="mt-3 text-3xl font-semibold text-slate-900">{{ formatDuration(totalTimeSpent) }}</p>
        <p class="text-xs text-slate-500">Keep reviewing explanations to learn faster</p>
      </article>
    </div>

    <section v-if="!error" class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <header class="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <h2 class="text-lg font-semibold text-slate-900">Sessions</h2>
          <p class="text-xs text-slate-500">Filter and review your recent activity.</p>
        </div>
        <div class="grid gap-3 md:grid-cols-4">
          <input
            v-model="searchTerm"
            type="search"
            placeholder="Search session title..."
            class="w-full rounded-2xl border border-slate-200 px-4 py-2 text-sm focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200"
          />
          <select
            v-model="selectedCategory"
            class="w-full rounded-2xl border border-slate-200 px-4 py-2 text-sm text-slate-700 focus:border-slate-400 focus:outline-none"
          >
            <option v-for="category in categories" :key="category" :value="category">{{ category }}</option>
          </select>
          <select
            v-model="selectedType"
            class="w-full rounded-2xl border border-slate-200 px-4 py-2 text-sm text-slate-700 focus:border-slate-400 focus:outline-none"
          >
            <option value="All">All types</option>
            <option value="quiz">Quiz</option>
            <option value="practice">Practice</option>
            <option value="mock">Mock</option>
          </select>
          <select
            v-model="sortBy"
            class="w-full rounded-2xl border border-slate-200 px-4 py-2 text-sm text-slate-700 focus:border-slate-400 focus:outline-none"
          >
            <option value="date">Newest first</option>
            <option value="score">Highest score</option>
            <option value="title">Alphabetical</option>
          </select>
        </div>
      </header>

      <div v-if="loading" class="mt-6 space-y-3">
        <div v-for="n in 3" :key="`history-row-${n}`" class="h-20 animate-pulse rounded-3xl bg-slate-100/60"></div>
      </div>
      <div v-else-if="filteredHistory.length === 0" class="mt-6 rounded-2xl bg-slate-50 p-6 text-sm text-slate-500">
        No sessions yet with these filters. Try removing a filter or practise a quiz.
      </div>

      <ul v-else class="mt-6 space-y-4">
        <li
          v-for="entry in filteredHistory"
          :key="entry.id"
          class="rounded-3xl border border-slate-200 p-5 transition hover:border-slate-300 hover:shadow-md"
        >
          <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div class="space-y-1">
              <h3 class="text-lg font-semibold text-slate-900">{{ entry.title }}</h3>
              <p class="text-xs text-slate-500">{{ formatDate(entry.date) }} · {{ entry.totalQuestions }} questions</p>
              <div class="flex flex-wrap gap-2 text-xs">
                <span class="rounded-full border border-slate-200 px-3 py-1 text-slate-600">{{ entry.category }}</span>
                <span :class="['rounded-full border px-3 py-1', typeBadge(entry.type)]">
                  {{ entry.type === 'mock' ? 'Mock test' : entry.type === 'practice' ? 'Practice set' : 'Quiz' }}
                </span>
                <span :class="['rounded-full px-3 py-1 text-xs font-semibold', difficultyBadge(entry.difficulty)]">
                  {{ entry.difficulty }}
                </span>
              </div>
            </div>
            <div class="space-y-2 text-right text-sm">
              <p :class="['text-2xl font-semibold', scoreColour(entry.score)]">{{ entry.score }}%</p>
              <p class="text-xs text-slate-500">{{ entry.correctAnswers }} correct</p>
              <p class="text-xs text-slate-500">{{ formatDuration(entry.timeSpent) }} spent</p>
              <div class="flex items-center justify-end gap-3 text-xs font-semibold text-slate-600">
                <RouterLink
                  :to="{ name: 'results', params: { id: entry.id } }"
                  class="rounded-full border border-slate-200 px-3 py-1 transition hover:border-slate-300 hover:text-slate-900"
                >
                  View breakdown
                </RouterLink>
                <RouterLink
                  v-if="entry.quizId"
                  :to="{ name: 'quiz', params: { id: entry.quizId } }"
                  class="rounded-full bg-slate-900 px-3 py-1 text-white transition hover:bg-slate-700"
                >
                  Retake
                </RouterLink>
                <button
                  v-else
                  class="rounded-full border border-slate-200 px-3 py-1 text-slate-400"
                  type="button"
                  disabled
                >
                  Retake
                </button>
              </div>
            </div>
          </div>
        </li>
      </ul>
    </section>
  </section>
</template>
