<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import { http } from '../api/http'

interface QuizSummary {
  id: number
  title: string
  description?: string | null
  is_active: boolean
  question_count: number
  organization_id?: number | null
}

interface PracticeCategorySummary {
  id?: number
  slug: string
  name: string
  description?: string | null
  difficulty: string
  total_questions: number
  icon?: string | null
  difficulties?: string[]
  organization_id?: number | null
}

type TimeLimitOption = 10 | 15 | 20

const router = useRouter()

const quizzes = ref<QuizSummary[]>([])
const categories = ref<PracticeCategorySummary[]>([])
const loading = reactive({
  quizzes: false,
  categories: false,
  submitting: false,
})
const error = ref<string | null>(null)
const STORAGE_KEY = 'quizHub::quiz-setup-preferences'

const filters = reactive({
  categorySlug: '' as string,
  difficulty: '' as string,
  quizId: null as number | null,
  timeLimit: 15 as TimeLimitOption,
})

const timeOptions: TimeLimitOption[] = [10, 15, 20]
const difficultyOptions = ['Easy', 'Medium', 'Hard', 'Mixed']
const hasSavedSetup = ref(false)

const selectedQuiz = computed(() => quizzes.value.find((quiz) => quiz.id === filters.quizId) ?? null)
const selectedCategory = computed(() => categories.value.find((cat) => cat.slug === filters.categorySlug) ?? null)
const recommendedQuiz = computed(() => {
  if (!quizzes.value.length) return null
  return quizzes.value.find((quiz) => quiz.is_active) ?? quizzes.value[0]
})
const quickStartBusy = computed(() => loading.quizzes || loading.submitting)
const savedSetupMeta = computed(() => {
  const parts: string[] = []
  if (selectedCategory.value) parts.push(selectedCategory.value.name)
  if (filters.difficulty) parts.push(filters.difficulty)
  parts.push(`${filters.timeLimit} min`)
  return parts.join(' · ')
})
const recommendedMeta = computed(() => {
  const quiz = recommendedQuiz.value
  if (!quiz) return ''
  const parts = [`${quiz.question_count} questions`]
  if (quiz.is_active) {
    parts.push('Live quiz')
  } else {
    parts.push('Draft quiz')
  }
  return parts.join(' · ')
})

const filteredQuizzes = computed(() => {
  const selectedSlug = filters.categorySlug
  return quizzes.value.filter((quiz) => {
    if (!quiz.is_active) return false
    if (!selectedSlug) return true
    const category = categories.value.find((cat) => cat.slug === selectedSlug)
    if (!category) return true
    const normalizedTitle = quiz.title.toLowerCase()
    return (
      normalizedTitle.includes(category.name.toLowerCase()) ||
      (category.description ? normalizedTitle.includes(category.description.toLowerCase()) : false)
    )
  })
})

const canStart = computed(() => Boolean(filters.quizId))

const restoreFilters = () => {
  if (typeof window === 'undefined') return
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (!raw) return
    const saved = JSON.parse(raw) as Partial<typeof filters>
    if (typeof saved.categorySlug === 'string') {
      filters.categorySlug = saved.categorySlug
    }
    if (typeof saved.difficulty === 'string') {
      filters.difficulty = saved.difficulty
    }
    if (typeof saved.quizId === 'number') {
      filters.quizId = saved.quizId
    }
    if (typeof saved.timeLimit === 'number' && (timeOptions as number[]).includes(saved.timeLimit)) {
      filters.timeLimit = saved.timeLimit as TimeLimitOption
    }
    hasSavedSetup.value = Boolean(
      saved.quizId ||
        saved.categorySlug ||
        saved.difficulty ||
        (typeof saved.timeLimit === 'number' && (timeOptions as number[]).includes(saved.timeLimit))
    )
  } catch (restoreError) {
    console.warn('Unable to restore quiz setup preferences', restoreError)
  }
}

const persistFilters = () => {
  if (typeof window === 'undefined') return
  try {
    const payload = {
      categorySlug: filters.categorySlug,
      difficulty: filters.difficulty,
      quizId: filters.quizId,
      timeLimit: filters.timeLimit,
    }
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(payload))
    hasSavedSetup.value = Boolean(payload.quizId || payload.categorySlug || payload.difficulty || payload.timeLimit)
  } catch (persistError) {
    console.warn('Unable to persist quiz setup preferences', persistError)
  }
}

const loadQuizzes = async () => {
  loading.quizzes = true
  try {
    const { data } = await http.get<QuizSummary[]>('/quizzes')
    quizzes.value = data
    const current = filters.quizId ? data.find((quiz) => quiz.id === filters.quizId && quiz.is_active) ?? null : null
    if (!current && data.length > 0) {
      const active = data.find((quiz) => quiz.is_active)
      filters.quizId = active?.id ?? data[0]?.id ?? null
    }
  } catch (err) {
    console.error(err)
    error.value = 'Unable to load quizzes. Please try again.'
  } finally {
    loading.quizzes = false
  }
}

const loadCategories = async () => {
  loading.categories = true
  try {
    const { data } = await http.get<PracticeCategorySummary[]>('/practice/categories')
    categories.value = data
  } catch (err) {
    console.error(err)
  } finally {
    loading.categories = false
  }
}

const startQuiz = () => {
  if (!filters.quizId) return
  loading.submitting = true
  router
    .push({ name: 'quiz', params: { id: filters.quizId }, query: { tl: filters.timeLimit } })
    .finally(() => {
      loading.submitting = false
    })
}

const goToCategories = (slug: string) => {
  router.push({ name: 'practice', params: { slug } })
}

const resumeSavedSetup = () => {
  if (!canStart.value || quickStartBusy.value) return
  startQuiz()
}

const startRecommendedQuiz = () => {
  if (quickStartBusy.value) return
  const nextQuiz = recommendedQuiz.value
  if (!nextQuiz) return
  filters.quizId = nextQuiz.id
  if (!(timeOptions as number[]).includes(filters.timeLimit)) {
    filters.timeLimit = 15
  }
  startQuiz()
}

onMounted(() => {
  restoreFilters()
  loadQuizzes()
  loadCategories()
})

watch(
  () => [filters.categorySlug, filters.difficulty, filters.quizId, filters.timeLimit],
  () => {
    persistFilters()
  }
)
</script>

<template>
  <section class="mx-auto max-w-4xl space-y-8">
    <header class="rounded-3xl border border-slate-200 bg-white/95 p-6 text-slate-900 shadow-lg shadow-brand-900/10">
      <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div class="space-y-2">
          <p class="text-[11px] font-semibold uppercase tracking-[0.35em] text-slate-400">Quiz setup</p>
          <h1 class="text-2xl font-semibold leading-tight md:text-3xl">Configure your practice session</h1>
          <p class="text-sm text-slate-500">
            Choose a quiz, adjust difficulty, and set a comfortable timer. You can revisit your selections anytime.
          </p>
        </div>
        <div class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-xs text-slate-500">
          <p class="font-semibold uppercase tracking-[0.3em] text-slate-400">Quick tip</p>
          <p>Not sure where to begin? Select a category below and start with the recommended mock test.</p>
        </div>
      </div>
    </header>

    <div v-if="hasSavedSetup || recommendedQuiz" class="grid gap-4 md:grid-cols-2">
      <button
        v-if="hasSavedSetup && canStart"
        class="group flex h-full flex-col gap-3 rounded-3xl border border-slate-900 bg-slate-900 p-5 text-left text-white shadow-lg shadow-slate-900/20 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
        type="button"
        :disabled="quickStartBusy || !canStart"
        @click="resumeSavedSetup"
      >
        <span class="text-[11px] font-semibold uppercase tracking-[0.35em] text-white/70">
          Resume in one click
        </span>
        <div class="space-y-1">
          <p class="text-lg font-semibold leading-tight">{{ selectedQuiz?.title || 'Saved mock test' }}</p>
          <p class="text-sm text-white/80">
            {{ savedSetupMeta }}
          </p>
        </div>
        <span class="inline-flex items-center gap-1 text-xs font-semibold uppercase tracking-[0.3em] text-white/80">
          Start now
          <span aria-hidden="true">→</span>
        </span>
      </button>

      <button
        v-if="recommendedQuiz"
        class="group flex h-full flex-col gap-3 rounded-3xl border border-slate-200 bg-white p-5 text-left text-slate-900 shadow-sm transition hover:-translate-y-0.5 hover:border-brand-200 hover:shadow-lg disabled:cursor-not-allowed disabled:opacity-60"
        type="button"
        :disabled="quickStartBusy"
        @click="startRecommendedQuiz"
      >
        <span class="text-[11px] font-semibold uppercase tracking-[0.35em] text-slate-400">
          Quick mock test
        </span>
        <div class="space-y-1">
          <p class="text-lg font-semibold leading-tight">
            {{ recommendedQuiz.title }}
          </p>
          <p class="text-sm text-slate-500">
            {{ recommendedMeta }}
          </p>
        </div>
        <span class="inline-flex items-center gap-1 text-xs font-semibold uppercase tracking-[0.3em] text-brand-600 group-hover:text-brand-500">
          Launch quiz
          <span aria-hidden="true">→</span>
        </span>
      </button>
    </div>

    <div class="grid gap-6 lg:grid-cols-[1.1fr,0.9fr]">
      <section class="space-y-6 rounded-3xl border border-slate-200 bg-white/95 p-6 shadow-xl shadow-brand-900/10">
        <div class="space-y-4">
          <h2 class="text-lg font-semibold text-slate-900">1. Filter your practice</h2>
          <div class="space-y-2">
            <label class="text-sm font-semibold text-slate-700">Subject focus</label>
            <div class="flex flex-wrap gap-2">
              <button
                class="inline-flex items-center gap-2 rounded-full border px-4 py-2 text-xs font-semibold transition"
                :class="filters.categorySlug === '' ? 'border-slate-900 bg-slate-900 text-white' : 'border-slate-200 text-slate-600 hover:border-slate-300 hover:text-slate-900'"
                type="button"
                @click="filters.categorySlug = ''"
              >
                All subjects
              </button>
              <button
                v-for="category in categories"
                :key="category.slug"
                class="inline-flex items-center gap-2 rounded-full border px-4 py-2 text-xs font-semibold transition"
                :class="filters.categorySlug === category.slug ? 'border-slate-900 bg-slate-900 text-white' : 'border-slate-200 text-slate-600 hover:border-slate-300 hover:text-slate-900'"
                type="button"
                @click="filters.categorySlug = category.slug"
              >
                {{ category.name }}
              </button>
            </div>
          </div>

          <div class="grid gap-4 md:grid-cols-2">
            <div class="space-y-2">
              <label class="text-sm font-semibold text-slate-700" for="difficulty">Difficulty</label>
              <select
                id="difficulty"
                v-model="filters.difficulty"
                class="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm focus:border-brand-400 focus:outline-none focus:ring-4 focus:ring-brand-100"
              >
                <option value="">All levels</option>
                <option v-for="difficulty in difficultyOptions" :key="difficulty" :value="difficulty">
                  {{ difficulty }}
                </option>
              </select>
            </div>
            <div class="space-y-2">
              <label class="text-sm font-semibold text-slate-700" for="time-limit">Time limit</label>
              <div id="time-limit" class="flex items-center gap-2">
                <button
                  v-for="option in timeOptions"
                  :key="option"
                  class="inline-flex flex-1 items-center justify-center rounded-full border px-3 py-2 text-xs font-semibold transition"
                  :class="filters.timeLimit === option ? 'border-slate-900 bg-slate-900 text-white' : 'border-slate-200 text-slate-600 hover:border-slate-300 hover:text-slate-900'"
                  type="button"
                  @click="filters.timeLimit = option"
                >
                  {{ option }} min
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <h2 class="text-lg font-semibold text-slate-900">2. Pick a mock test</h2>
            <span class="text-xs text-slate-500">
              {{ loading.quizzes ? 'Loading…' : `${filteredQuizzes.length} available` }}
            </span>
          </div>
          <div
            v-if="error"
            class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-600"
          >
            {{ error }}
          </div>
          <div
            v-else-if="filteredQuizzes.length === 0 && !loading.quizzes"
            class="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-600"
          >
            No mock tests match these filters yet. Try adjusting the subject or difficulty.
          </div>
          <div
            v-else
            class="space-y-3"
          >
            <label
              v-for="quiz in filteredQuizzes"
              :key="quiz.id"
              class="flex cursor-pointer flex-col gap-2 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm shadow-sm transition hover:border-brand-200"
            >
              <div class="flex items-center justify-between gap-3">
                <div class="space-y-1">
                  <div class="flex items-center gap-2">
                    <input
                      :checked="filters.quizId === quiz.id"
                      class="h-4 w-4 border-slate-300 text-brand-600 focus:ring-brand-200"
                      name="quiz-selection"
                      type="radio"
                      @change="filters.quizId = quiz.id"
                    />
                    <span class="font-semibold text-slate-900">{{ quiz.title }}</span>
                  </div>
                  <p class="text-xs text-slate-500">{{ quiz.description || 'Sharpen your knowledge with curated questions and instant feedback.' }}</p>
                </div>
                <span class="inline-flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1 text-[11px] font-semibold text-slate-600">
                  {{ quiz.question_count }} questions
                </span>
              </div>
            </label>
          </div>
        </div>

        <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
          <button
            class="inline-flex w-full items-center justify-center gap-2 rounded-full bg-slate-900 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-slate-900/20 transition hover:bg-slate-700 sm:w-auto"
            :class="{ 'cursor-not-allowed opacity-60': !canStart || loading.submitting }"
            :disabled="!canStart || loading.submitting"
            type="button"
            @click="startQuiz"
          >
            <svg class="h-4 w-4" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 4l10 6-10 6V4z" />
            </svg>
            {{ loading.submitting ? 'Launching…' : 'Start quiz' }}
          </button>
          <RouterLink
            :to="{ name: 'dashboard' }"
            class="inline-flex w-full items-center justify-center gap-2 rounded-full border border-slate-200 px-6 py-3 text-sm font-semibold text-slate-700 transition hover:border-brand-300 hover:text-brand-600 sm:w-auto"
          >
            View dashboard
          </RouterLink>
        </div>
      </section>

      <aside class="space-y-5 rounded-3xl border border-slate-200 bg-white/95 p-6 shadow-xl shadow-brand-900/10">
        <header class="space-y-2">
          <p class="text-[11px] font-semibold uppercase tracking-[0.35em] text-slate-400">Recommended focus</p>
          <h2 class="text-lg font-semibold text-slate-900">Popular categories</h2>
          <p class="text-xs text-slate-500">Jump into areas learners practice most often.</p>
        </header>
        <div class="space-y-3">
          <article
            v-for="category in categories.slice(0, 4)"
            :key="category.slug"
            class="rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-sm"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="space-y-1">
                <p class="text-sm font-semibold text-slate-900">{{ category.name }}</p>
                <p class="text-xs text-slate-500">{{ category.description || 'Sharpen your fundamentals with targeted questions.' }}</p>
              </div>
              <span class="inline-flex items-center gap-1 rounded-full bg-slate-100 px-3 py-1 text-[11px] font-semibold text-slate-600">
                {{ category.total_questions }} qns
              </span>
            </div>
            <div class="mt-3 flex items-center justify-between text-xs text-slate-500">
              <span>
                {{ category.difficulty }}
              </span>
              <button
                class="inline-flex items-center gap-1 text-xs font-semibold text-brand-600 transition hover:text-brand-500"
                type="button"
                @click="goToCategories(category.slug)"
              >
                Practice
                <span aria-hidden="true">→</span>
              </button>
            </div>
          </article>
        </div>
      </aside>
    </div>
  </section>
</template>
