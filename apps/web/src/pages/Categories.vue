<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'

interface Category {
  id: number
  name: string
  icon: string
  totalQuestions: number
  completed: number
  description: string
  difficulty: 'Easy' | 'Medium' | 'Hard' | 'Mixed'
  subcategories: string[]
}

const searchTerm = ref('')
const selectedDifficulty = ref<'All' | Category['difficulty']>('All')

const categories = ref<Category[]>([
  {
    id: 1,
    name: 'General Knowledge',
    icon: '🌍',
    totalQuestions: 500,
    completed: 45,
    description: 'World geography, history, science, and current events',
    difficulty: 'Mixed',
    subcategories: ['World Geography', 'History', 'Science', 'Sports'],
  },
  {
    id: 2,
    name: 'Aptitude',
    icon: '🧮',
    totalQuestions: 300,
    completed: 23,
    description: 'Numerical reasoning, logical thinking, and problem solving',
    difficulty: 'Medium',
    subcategories: ['Numerical', 'Logical', 'Verbal', 'Abstract'],
  },
  {
    id: 3,
    name: 'Reasoning',
    icon: '🧠',
    totalQuestions: 400,
    completed: 67,
    description: 'Logical reasoning, pattern recognition, and analytical thinking',
    difficulty: 'Hard',
    subcategories: ['Logical', 'Analytical', 'Critical', 'Spatial'],
  },
  {
    id: 4,
    name: 'English',
    icon: '📚',
    totalQuestions: 250,
    completed: 12,
    description: 'Grammar, vocabulary, comprehension, and writing skills',
    difficulty: 'Easy',
    subcategories: ['Grammar', 'Vocabulary', 'Reading', 'Writing'],
  },
  {
    id: 5,
    name: 'Current Affairs',
    icon: '📰',
    totalQuestions: 200,
    completed: 8,
    description: 'Recent events, politics, economics, and social issues',
    difficulty: 'Mixed',
    subcategories: ['Politics', 'Economics', 'Technology', 'Sports'],
  },
  {
    id: 6,
    name: 'Mathematics',
    icon: '📊',
    totalQuestions: 350,
    completed: 34,
    description: 'Algebra, geometry, statistics, and advanced mathematics',
    difficulty: 'Hard',
    subcategories: ['Algebra', 'Geometry', 'Statistics', 'Calculus'],
  },
])

const filteredCategories = computed(() => {
  const term = searchTerm.value.trim().toLowerCase()
  return categories.value.filter((category) => {
    const matchesSearch =
      !term ||
      category.name.toLowerCase().includes(term) ||
      category.description.toLowerCase().includes(term)
    const matchesDifficulty =
      selectedDifficulty.value === 'All' || category.difficulty === selectedDifficulty.value
    return matchesSearch && matchesDifficulty
  })
})

const difficultyClasses = (difficulty: Category['difficulty']) => {
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

const progressFor = (category: Category) => {
  if (category.totalQuestions === 0) return 0
  return Math.round((category.completed / category.totalQuestions) * 100)
}
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

    <div
      v-if="filteredCategories.length === 0"
      class="rounded-3xl border border-slate-200 bg-white p-10 text-center text-sm text-slate-500"
    >
      No categories match your filters yet. Try a different search term.
    </div>

    <div class="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
      <article
        v-for="category in filteredCategories"
        :key="category.id"
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
            :to="{ name: 'quiz', params: { id: category.id } }"
            class="flex-1 rounded-full bg-slate-900 px-4 py-2 text-center text-white transition hover:bg-slate-700"
          >
            Start quiz
          </RouterLink>
          <RouterLink
            :to="{ name: 'practice', params: { id: category.id } }"
            class="flex-1 rounded-full border border-slate-200 px-4 py-2 text-center text-slate-700 transition hover:border-slate-300 hover:text-slate-900"
          >
            Practice
          </RouterLink>
        </div>
      </article>
    </div>
  </section>
</template>
