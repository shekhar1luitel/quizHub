<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import { http } from '../api/http'

type Difficulty = 'Easy' | 'Medium' | 'Hard' | 'Mixed'
type DifficultyFilter = 'All' | Difficulty

interface PracticeCategorySummary {
  slug: string
  name: string
  total_questions: number
  difficulty: string
  difficulties: string[]
}

interface CategoryReference {
  icon: string
  description: string
  difficulty?: Difficulty
  subcategories: string[]
  quizId?: number
}

interface DisplayCategory {
  slug: string
  name: string
  icon: string
  totalQuestions: number
  completed: number
  description: string
  difficulty: Difficulty
  subcategories: string[]
  quizId: number | null
}

const categoryReference: Record<string, CategoryReference> = {
  'general-knowledge': {
    icon: '🌍',
    description: 'World geography, history, science, and current events',
    difficulty: 'Mixed',
    subcategories: ['World Geography', 'History', 'Science', 'Sports'],
    quizId: 1,
  },
  aptitude: {
    icon: '🧮',
    description: 'Numerical reasoning, logical thinking, and problem solving',
    difficulty: 'Medium',
    subcategories: ['Numerical', 'Logical', 'Verbal', 'Abstract'],
    quizId: 2,
  },
  reasoning: {
    icon: '🧠',
    description: 'Logical reasoning, pattern recognition, and analytical thinking',
    difficulty: 'Hard',
    subcategories: ['Logical', 'Analytical', 'Critical', 'Spatial'],
    quizId: 3,
  },
  english: {
    icon: '📚',
    description: 'Grammar, vocabulary, comprehension, and writing skills',
    difficulty: 'Easy',
    subcategories: ['Grammar', 'Vocabulary', 'Reading', 'Writing'],
    quizId: 4,
  },
  'current-affairs': {
    icon: '📰',
    description: 'Recent events, politics, economics, and social issues',
    difficulty: 'Mixed',
    subcategories: ['Politics', 'Economics', 'Technology', 'Sports'],
    quizId: 5,
  },
  mathematics: {
    icon: '📊',
    description: 'Algebra, geometry, statistics, and advanced mathematics',
    difficulty: 'Hard',
    subcategories: ['Algebra', 'Geometry', 'Statistics', 'Calculus'],
    quizId: 6,
  },
}

const searchTerm = ref('')
const selectedDifficulty = ref<DifficultyFilter>('All')
const loading = ref(true)
const error = ref('')
const categories = ref<PracticeCategorySummary[]>([])

const defaultReference: CategoryReference = {
  icon: '📝',
  description: 'Practice this subject to strengthen your mastery.',
  subcategories: [],
}

const decoratedCategories = computed<DisplayCategory[]>(() =>
  categories.value.map((category) => {
    const reference = categoryReference[category.slug] ?? defaultReference
    const difficulty = (reference.difficulty ?? category.difficulty ?? 'Mixed') as Difficulty
    return {
      slug: category.slug,
      name: category.name,
      icon: reference.icon,
      totalQuestions: category.total_questions,
      completed: 0,
      description: reference.description,
      difficulty,
      subcategories: reference.subcategories,
      quizId: reference.quizId ?? null,
    }
  })
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

const progressFor = (category: DisplayCategory) => {
  if (category.totalQuestions === 0) return 0
  return Math.round((category.completed / category.totalQuestions) * 100)
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
                  {{ category.completed }} / {{ category.totalQuestions }} completed
                </span>
              </div>
            </div>
          </div>
        </header>

        <p class="text-sm leading-6 text-slate-600">{{ category.description }}</p>

        <div class="space-y-3">
          <div class="h-2 rounded-full bg-slate-100">
            <div
              class="h-full rounded-full bg-gradient-to-r from-indigo-500 via-sky-500 to-emerald-500"
              :style="{ width: `${progressFor(category)}%` }"
            />
          </div>
          <p class="text-xs font-medium text-slate-500">{{ progressFor(category) }}% mastery</p>
        </div>

        <div>
          <h3 class="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Subcategories</h3>
          <ul class="mt-3 flex flex-wrap gap-2 text-xs text-slate-600">
            <li
              v-for="sub in category.subcategories"
              :key="sub"
              class="rounded-full border border-slate-200 px-3 py-1"
            >
              {{ sub }}
            </li>
          </ul>
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
            :to="{ name: 'practice', params: { slug: category.slug } }"
            class="flex-1 rounded-full border border-slate-200 px-4 py-2 text-center text-slate-700 transition hover:border-slate-300 hover:text-slate-900"
          >
            Practice
          </RouterLink>
        </div>
      </article>
    </div>
  </section>
</template>
