<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, RouterLink } from 'vue-router'

import { http } from '../api/http'

type Difficulty = 'Easy' | 'Medium' | 'Hard' | 'Mixed'

interface PracticeQuestionOption {
  id: number
  text: string
  is_correct: boolean
}

interface PracticeQuestionResponse {
  id: number
  prompt: string
  explanation?: string | null
  difficulty?: string | null
  options: PracticeQuestionOption[]
}

interface PracticeCategoryDetail {
  slug: string
  name: string
  description?: string | null
  icon?: string | null
  total_questions: number
  difficulty: string
  questions: PracticeQuestionResponse[]
}

interface PracticeQuestionView {
  id: number
  prompt: string
  options: string[]
  correctAnswer: number
  explanation: string
  difficulty: Difficulty
}

const route = useRoute()
const categorySlug = computed(() => String(route.params.slug || ''))

const category = ref<PracticeCategoryDetail | null>(null)
const questions = ref<PracticeQuestionView[]>([])
const loading = ref(false)
const error = ref('')

const currentIndex = ref(0)
const selectedAnswer = ref<number | null>(null)
const showResult = ref(false)
const showExplanation = ref(false)

const fallbackIcon = '📝'

const fallbackDescription = 'Sharpen your understanding with targeted practice questions.'

const fallbackExplanation =
  'Review the concept behind this question and try again for better mastery.'

const normalizeDifficulty = (value?: string | null): Difficulty => {
  if (!value) return 'Mixed'
  const normalized = value.toLowerCase()
  if (normalized.startsWith('easy')) return 'Easy'
  if (normalized.startsWith('medium')) return 'Medium'
  if (normalized.startsWith('hard')) return 'Hard'
  return 'Mixed'
}

const transformQuestion = (question: PracticeQuestionResponse): PracticeQuestionView => {
  const correctIndex = question.options.findIndex((option) => option.is_correct)
  return {
    id: question.id,
    prompt: question.prompt,
    options: question.options.map((option) => option.text),
    correctAnswer: correctIndex >= 0 ? correctIndex : -1,
    explanation: question.explanation?.trim() || fallbackExplanation,
    difficulty: normalizeDifficulty(question.difficulty),
  }
}

const currentQuestion = computed(() => questions.value[currentIndex.value])

const categoryIcon = computed(() => category.value?.icon?.trim() || fallbackIcon)

const selectAnswer = (optionIndex: number) => {
  if (showResult.value) return
  selectedAnswer.value = optionIndex
}

const submitAnswer = () => {
  if (selectedAnswer.value === null) return
  showResult.value = true
  showExplanation.value = true
}

const goNext = () => {
  if (currentIndex.value < questions.value.length - 1) {
    currentIndex.value += 1
    resetState(false)
  }
}

const goPrev = () => {
  if (currentIndex.value > 0) {
    currentIndex.value -= 1
    resetState(false)
  }
}

const retryQuestion = () => {
  resetState(false)
}

const resetState = (resetIndex = true) => {
  selectedAnswer.value = null
  showResult.value = false
  showExplanation.value = false
  if (resetIndex) {
    currentIndex.value = 0
  }
}

const isCorrect = computed(
  () => selectedAnswer.value !== null && selectedAnswer.value === currentQuestion.value?.correctAnswer
)

const difficultyBadge = (difficulty: Difficulty) => {
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

const loadPracticeSet = async () => {
  if (!categorySlug.value) return
  loading.value = true
  error.value = ''
  try {
    const { data } = await http.get<PracticeCategoryDetail>(`/practice/categories/${categorySlug.value}`)
    category.value = data
    questions.value = data.questions.map(transformQuestion)
    resetState()
  } catch (err) {
    console.error(err)
    error.value = 'Unable to load practice questions.'
    category.value = null
    questions.value = []
  } finally {
    loading.value = false
  }
}

watch(categorySlug, () => {
  loadPracticeSet()
})

loadPracticeSet()
</script>

<template>
  <section class="space-y-8">
    <header class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
      <RouterLink
        :to="{ name: 'categories' }"
        class="inline-flex items-center gap-2 rounded-full border border-slate-200 px-4 py-2 text-xs font-semibold uppercase tracking-widest text-slate-600 transition hover:border-slate-300 hover:text-slate-900"
      >
        <span aria-hidden="true">←</span>
        Back to categories
      </RouterLink>
      <div class="flex flex-1 items-start gap-4">
        <span class="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-900/10 text-2xl">
          {{ categoryIcon }}
        </span>
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">Practice</p>
          <h1 class="mt-2 text-3xl font-semibold text-slate-900">{{ category?.name || 'Reinforcement mode' }}</h1>
          <p class="mt-2 text-sm text-slate-500">
            {{ category?.description?.trim() || fallbackDescription }}
          </p>
          <p class="mt-2 text-xs font-medium uppercase tracking-[0.3em] text-slate-400">
            {{ category?.difficulty || 'Mixed' }} focus · {{ category?.total_questions ?? questions.length }} questions ·
            Question {{ questions.length ? currentIndex + 1 : 0 }} of {{ questions.length }}
          </p>
        </div>
      </div>
    </header>

    <article v-if="loading" class="space-y-6 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <div class="h-4 w-1/4 animate-pulse rounded bg-slate-200"></div>
      <div class="h-6 w-3/4 animate-pulse rounded bg-slate-200"></div>
      <div class="space-y-3">
        <div v-for="n in 4" :key="n" class="h-12 animate-pulse rounded-2xl bg-slate-100"></div>
      </div>
    </article>

    <p
      v-else-if="error"
      class="rounded-3xl border border-red-200 bg-red-50 p-6 text-sm text-red-600"
    >
      {{ error }}
    </p>

    <p
      v-else-if="questions.length === 0"
      class="rounded-3xl border border-slate-200 bg-white p-6 text-sm text-slate-500"
    >
      No practice questions are available for this category yet. Add new questions from the admin panel to get started.
    </p>

    <article v-else class="space-y-6 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <header class="flex items-start justify-between gap-3">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">Question {{ currentIndex + 1 }}</p>
          <h2 class="mt-2 text-xl font-semibold text-slate-900">{{ currentQuestion.prompt }}</h2>
        </div>
        <span :class="['rounded-full px-3 py-1 text-xs font-semibold', difficultyBadge(currentQuestion.difficulty)]">
          {{ currentQuestion.difficulty }}
        </span>
      </header>

      <div class="space-y-3">
        <button
          v-for="(option, index) in currentQuestion.options"
          :key="`${currentQuestion.id}-${index}`"
          class="w-full rounded-2xl border px-5 py-3 text-left text-sm transition"
          :class="[
            !showResult
              ? selectedAnswer === index
                ? 'border-slate-900 bg-slate-900/5 text-slate-900'
                : 'border-slate-200 hover:border-slate-300 hover:bg-slate-100'
              : index === currentQuestion.correctAnswer
                ? 'border-emerald-400 bg-emerald-50 text-emerald-700'
                : selectedAnswer === index
                  ? 'border-rose-400 bg-rose-50 text-rose-700'
                  : 'border-slate-200 text-slate-600'
          ]"
          :disabled="showResult"
          @click="selectAnswer(index)"
        >
          <span class="flex items-center gap-3">
            <span class="text-xs font-semibold text-slate-400">{{ String.fromCharCode(65 + index) }}.</span>
            <span class="flex-1">{{ option }}</span>
          </span>
        </button>
      </div>

      <div
        v-if="showResult"
        class="rounded-2xl border px-5 py-4"
        :class="isCorrect ? 'border-emerald-200 bg-emerald-50 text-emerald-700' : 'border-rose-200 bg-rose-50 text-rose-700'"
      >
        <p class="text-sm font-semibold">{{ isCorrect ? 'Great job! That was correct.' : 'Not quite right this time.' }}</p>
      </div>

      <div v-if="showExplanation" class="rounded-2xl border border-slate-200 bg-slate-50 px-5 py-4 text-sm text-slate-600">
        <p class="font-semibold text-slate-900">Explanation</p>
        <p class="mt-2 leading-6">{{ currentQuestion.explanation }}</p>
      </div>

      <footer class="flex flex-col gap-3 border-t border-slate-200 pt-4 text-sm md:flex-row md:items-center md:justify-between">
        <div class="flex items-center gap-3">
          <button
            class="rounded-full border border-slate-200 px-4 py-2 font-semibold text-slate-600 transition hover:border-slate-300 hover:text-slate-900"
            :disabled="currentIndex === 0"
            @click="goPrev"
          >
            Previous
          </button>
          <button
            class="rounded-full border border-slate-200 px-4 py-2 font-semibold text-slate-600 transition hover:border-slate-300 hover:text-slate-900"
            :disabled="currentIndex >= questions.length - 1"
            @click="goNext"
          >
            Next
          </button>
        </div>
        <div class="flex items-center gap-3">
          <button
            v-if="showResult"
            class="rounded-full border border-slate-200 px-4 py-2 font-semibold text-slate-600 transition hover:border-slate-300 hover:text-slate-900"
            @click="retryQuestion"
          >
            Try again
          </button>
          <button
            v-else
            class="rounded-full bg-slate-900 px-5 py-2 font-semibold text-white transition hover:bg-slate-700 disabled:opacity-50"
            :disabled="selectedAnswer === null"
            @click="submitAnswer"
          >
            Check answer
          </button>
        </div>
      </footer>
    </article>
  </section>
</template>
