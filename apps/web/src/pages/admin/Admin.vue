<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import { http } from '../../api/http'
import { useAuthStore } from '../../stores/auth'

interface AdminTotals {
  total_quizzes: number
  active_quizzes: number
  total_questions: number
  inactive_questions: number
  total_categories: number
  total_users: number
}

interface AdminRecentQuiz {
  id: number
  title: string
  question_count: number
  is_active: boolean
  created_at: string
}

interface AdminCategorySnapshot {
  id: number
  name: string
  question_count: number
}

interface AdminOverview {
  totals: AdminTotals
  recent_quizzes: AdminRecentQuiz[]
  top_categories: AdminCategorySnapshot[]
}

const loading = ref(true)
const error = ref('')
const overview = ref<AdminOverview | null>(null)

const auth = useAuthStore()
const isSuperuser = computed(() => auth.isSuperuser)
const platformTitle = computed(() => (isSuperuser.value ? 'Platform Dashboard' : 'Admin Dashboard'))
const platformSubtitle = computed(() =>
  isSuperuser.value
    ? 'Monitor tenant health, mail delivery, and configuration across the entire platform.'
    : 'Oversee quiz quality, question coverage, and category balance in one place.'
)

const totals = computed(() => overview.value?.totals)

const loadOverview = async () => {
  loading.value = true
  error.value = ''
  try {
    const { data } = await http.get<AdminOverview>('/admin/overview')
    overview.value = data
  } catch (err) {
    console.error(err)
    error.value = 'Unable to load the admin overview. Please try again.'
  } finally {
    loading.value = false
  }
}

onMounted(loadOverview)

const quizHealth = computed(() => {
  if (!totals.value) return 0
  if (totals.value.total_quizzes === 0) return 0
  return Math.round((totals.value.active_quizzes / totals.value.total_quizzes) * 100)
})
</script>

<template>
  <section class="space-y-10">
    <header class="space-y-4">
      <div class="inline-flex items-center gap-2 rounded-full bg-slate-100 px-4 py-1 text-xs font-semibold uppercase tracking-widest text-slate-600">
        {{ platformTitle }}
      </div>
      <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div class="space-y-2">
          <h1 class="text-3xl font-semibold text-slate-900">QuizMaster control center</h1>
          <p class="max-w-2xl text-sm text-slate-500">
            {{ platformSubtitle }}
          </p>
        </div>
        <div class="flex flex-col gap-3 sm:flex-row">
          <RouterLink
            :to="{ name: 'admin-categories' }"
            class="inline-flex items-center justify-center rounded-full border border-slate-200 px-6 py-2.5 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:text-slate-900"
          >
            Manage categories
          </RouterLink>
          <RouterLink
            :to="{ name: 'admin-questions' }"
            class="inline-flex items-center justify-center rounded-full bg-slate-900 px-6 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-700"
          >
            Add question
          </RouterLink>
          <RouterLink
            :to="{ name: 'admin-quizzes' }"
            class="inline-flex items-center justify-center rounded-full border border-slate-200 px-6 py-2.5 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:text-slate-900"
          >
            Build quiz
          </RouterLink>
        </div>
      </div>
    </header>

    <div v-if="loading" class="grid gap-5 lg:grid-cols-4">
      <div v-for="n in 4" :key="n" class="h-32 animate-pulse rounded-3xl bg-white/70"></div>
    </div>

    <p v-else-if="error" class="rounded-3xl border border-amber-200 bg-amber-50 p-5 text-sm text-amber-800">{{ error }}</p>

    <div v-else-if="overview" class="grid gap-5 lg:grid-cols-4">
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Active quizzes</p>
        <p class="mt-3 text-3xl font-semibold text-slate-900">{{ totals?.active_quizzes }}</p>
        <p class="text-xs text-slate-500">Out of {{ totals?.total_quizzes }} published quizzes</p>
      </article>
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Question bank</p>
        <p class="mt-3 text-3xl font-semibold text-slate-900">{{ totals?.total_questions }}</p>
        <p class="text-xs text-slate-500">{{ totals?.inactive_questions }} awaiting review</p>
      </article>
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Category coverage</p>
        <p class="mt-3 text-3xl font-semibold text-slate-900">{{ totals?.total_categories }}</p>
        <p class="text-xs text-slate-500">Categories currently available to learners</p>
      </article>
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Quiz health</p>
        <p class="mt-3 text-3xl font-semibold text-slate-900">{{ quizHealth }}%</p>
        <p class="text-xs text-slate-500">Share of active quizzes ready to launch</p>
      </article>
    </div>

    <div v-if="overview" class="grid gap-6 xl:grid-cols-[2fr,3fr]">
      <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <header class="flex items-center justify-between">
          <div>
            <h2 class="text-lg font-semibold text-slate-900">Question management</h2>
            <p class="text-xs text-slate-500">Create, edit, and archive questions with detailed explanations.</p>
          </div>
        </header>
        <p class="mt-4 text-sm text-slate-500">
          Keep your library fresh by reviewing inactive questions and balancing difficulty across categories.
        </p>
        <RouterLink
          :to="{ name: 'admin-questions' }"
          class="mt-6 inline-flex items-center justify-center rounded-full border border-slate-200 px-5 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:text-slate-900"
        >
          Manage questions
        </RouterLink>
      </section>

      <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <header class="flex items-center justify-between">
          <div>
            <h2 class="text-lg font-semibold text-slate-900">Latest quizzes</h2>
            <p class="text-xs text-slate-500">Monitor coverage and activate new content.</p>
          </div>
        </header>
        <div class="mt-5 space-y-3 text-sm">
          <p v-if="overview.recent_quizzes.length === 0" class="text-slate-500">
            No quizzes yet.
            <RouterLink :to="{ name: 'admin-quizzes' }" class="text-brand-600 hover:underline">Build your first quiz.</RouterLink>
          </p>
          <ul v-else class="space-y-2">
            <li
              v-for="quiz in overview.recent_quizzes"
              :key="quiz.id"
              class="flex items-center justify-between rounded-2xl border border-slate-200 px-4 py-3"
            >
              <div>
                <p class="font-semibold text-slate-900">{{ quiz.title }}</p>
                <p class="text-xs text-slate-500">{{ quiz.question_count }} questions · {{ quiz.is_active ? 'Active' : 'Inactive' }}</p>
              </div>
              <RouterLink
                :to="{ name: 'quiz', params: { id: quiz.id } }"
                class="rounded-full bg-slate-900 px-3 py-1 text-xs font-semibold text-white transition hover:bg-slate-700"
              >
                Preview
              </RouterLink>
            </li>
          </ul>
        </div>
      </section>
    </div>

    <section v-if="overview" class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <header class="flex items-center justify-between">
        <div>
          <h2 class="text-lg font-semibold text-slate-900">Top categories</h2>
          <p class="text-xs text-slate-500">Where learners spend most of their time.</p>
        </div>
      </header>
      <div class="mt-6">
        <p v-if="overview.top_categories.length === 0" class="text-sm text-slate-500">No categories yet. Create one to begin.</p>
        <div v-else class="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
          <article
            v-for="category in overview.top_categories"
            :key="category.id"
            class="rounded-2xl border border-slate-200 bg-slate-50 p-4"
          >
            <p class="text-sm font-semibold text-slate-900">{{ category.name }}</p>
            <p class="text-xs text-slate-500">{{ category.question_count }} questions available</p>
          </article>
        </div>
      </div>
    </section>
  </section>
</template>
