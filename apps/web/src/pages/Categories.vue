<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import { http } from '../api/http'

type Difficulty = 'Easy' | 'Medium' | 'Hard' | 'Mixed'
type DifficultyFilter = 'All' | Difficulty

interface PracticeCategorySummary {
  slug: string
  name: string
  description?: string | null
  icon?: string | null
  total_questions: number
  difficulty: string
  difficulties: string[]
  quiz_id?: number | null
}

interface DisplayCategory {
  slug: string
  name: string
  icon: string
  totalQuestions: number
  description: string
  difficulty: Difficulty
  difficulties: string[]
  quizId: number | null
}

const fallbackDescription = 'Practice this subject to strengthen your mastery.'
const fallbackIcon = '📝'

const searchTerm = ref('')
const selectedDifficulty = ref<DifficultyFilter>('All')
const loading = ref(true)
const error = ref('')
const categories = ref<PracticeCategorySummary[]>([])

const normalizeDifficulty = (value: string | null | undefined): Difficulty => {
  if (!value) return 'Mixed'
  const normalized = value.toLowerCase()
  if (normalized.startsWith('easy')) return 'Easy'
  if (normalized.startsWith('medium')) return 'Medium'
  if (normalized.startsWith('hard')) return 'Hard'
  return 'Mixed'
}

const decoratedCategories = computed<DisplayCategory[]>(() =>
  categories.value.map((category) => ({
    slug: category.slug,
    name: category.name,
    icon: category.icon?.trim() || fallbackIcon,
    totalQuestions: category.total_questions,
    description: category.description?.trim() || fallbackDescription,
    difficulty: normalizeDifficulty(category.difficulty),
    difficulties: category.difficulties,
    quizId: category.quiz_id ?? null,
  }))
)

const filteredCategories = computed(() => {
  const term = searchTerm.value.trim().toLowerCase()
  return decoratedCategories.value.filter((category) => {
    const matchesSearch =
      !term ||
      category.name.toLowerCase().includes(term) ||
      category.description.toLowerCase().includes(term)
    const matchesDifficulty =
      selectedDifficulty.value === 'All' || category.difficulty === selectedDifficulty.value
    return matchesSearch && matchesDifficulty
  })
})

const difficultyClasses = (difficulty: Difficulty) => {
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

const loadCategories = async () => {
  loading.value = true
  error.value = ''
  try {
    const { data } = await http.get<PracticeCategorySummary[]>('/practice/categories')
    categories.value = data
  } catch (err) {
    error.value = 'Unable to load categories.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(loadCategories)
</script>

<template>
  <section class="space-y-10">
    <header class="space-y-6">
      <div class="flex items-center gap-4">
        <RouterLink
          :to="{ name: 'dashboard' }"
          class="inline-flex items-center gap-2 rounded-full border border-slate-200 px-4 py-2 text-xs font-semibold uppercase tracking-widest text-slate-600 transition hover:border-slate-300 hover:text-slate-900"
        >
          <span aria-hidden="true">←</span>
          Back to dashboard
        </RouterLink>
        <div class="flex items-center gap-3 text-slate-900">
          <span class="flex h-10 w-10 items-center justify-center rounded-full bg-slate-900/10 text-lg">📚</span>
          <div>
            <h1 class="text-3xl font-semibold">Practice categories</h1>
            <p class="text-sm text-slate-500">Find a subject to focus your next practice session.</p>
          </div>
        </div>
      </div>
      <div class="flex flex-col gap-4 lg:flex-row lg:items-center">
        <div class="relative flex-1">
          <input
            v-model="searchTerm"
            type="search"
            placeholder="Search categories or descriptions..."
            class="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200"
          />
          <span class="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-xs text-slate-400">Search</span>
        </div>
        <label class="flex items-center gap-3 text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
          Difficulty
          <select
            v-model="selectedDifficulty"
            class="rounded-2xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 focus:border-slate-400 focus:outline-none"
          >
            <option value="All">All</option>
            <option value="Easy">Easy</option>
            <option value="Medium">Medium</option>
            <option value="Hard">Hard</option>
            <option value="Mixed">Mixed</option>
          </select>
        </label>
      </div>
    </header>

    <div v-if="loading" class="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
      <div v-for="n in 6" :key="n" class="h-64 animate-pulse rounded-3xl bg-white/60"></div>
    </div>

    <p
      v-else-if="error"
      class="rounded-3xl border border-red-200 bg-red-50 p-10 text-center text-sm text-red-600"
    >
      {{ error }}
    </p>

    <div
      v-else-if="filteredCategories.length === 0"
      class="rounded-3xl border border-slate-200 bg-white p-10 text-center text-sm text-slate-500"
    >
      No categories match your filters yet. Try a different search term.
    </div>

    <div v-else class="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
      <article
        v-for="category in filteredCategories"
        :key="category.slug"
        class="flex flex-col gap-5 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg"
      >
        <header class="flex items-start justify-between gap-3">
          <div class="flex items-center gap-3">
            <span class="text-3xl">{{ category.icon }}</span>
            <div>
              <h2 class="text-xl font-semibold text-slate-900">{{ category.name }}</h2>
              <div class="mt-1 flex items-center gap-2 text-xs text-slate-500">
                <span :class="['inline-flex items-center gap-1 rounded-full px-3 py-1 font-semibold', difficultyClasses(category.difficulty)]">
                  {{ category.difficulty }}
                </span>
                <span>
                  {{ category.totalQuestions }} questions available
                </span>
              </div>
            </div>
          </div>
        </header>

        <p class="text-sm leading-6 text-slate-600">{{ category.description }}</p>

        <div>
          <h3 class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Difficulty coverage</h3>
          <ul v-if="category.difficulties.length" class="mt-3 flex flex-wrap gap-2 text-xs text-slate-600">
            <li
              v-for="level in category.difficulties"
              :key="`${category.slug}-${level}`"
              class="rounded-full border border-slate-200 px-3 py-1"
            >
              {{ level }}
            </li>
          </ul>
          <p v-else class="mt-3 text-xs text-slate-500">Mixed practice levels.</p>
        </div>

        <div class="mt-auto flex gap-3 text-sm font-semibold">
          <RouterLink
            v-if="category.quizId !== null"
            :to="{ name: 'quiz', params: { id: category.quizId } }"
            class="flex-1 rounded-full bg-slate-900 px-4 py-2 text-center text-white transition hover:bg-slate-700"
          >
            Start quiz
          </RouterLink>
          <button
            v-else
            class="flex-1 rounded-full border border-slate-200 px-4 py-2 text-center text-slate-400"
            type="button"
            disabled
          >
            Quiz coming soon
          </button>
          <RouterLink
            v-if="category.totalQuestions > 0"
            :to="{ name: 'practice', params: { slug: category.slug } }"
            class="flex-1 rounded-full border border-slate-200 px-4 py-2 text-center text-slate-700 transition hover:border-slate-300 hover:text-slate-900"
          >
            Practice
          </RouterLink>
          <button
            v-else
            class="flex-1 rounded-full border border-slate-200 px-4 py-2 text-center text-slate-400"
            type="button"
            disabled
          >
            Practice coming soon
          </button>
        </div>
      </article>
    </div>
  </section>
</template>
