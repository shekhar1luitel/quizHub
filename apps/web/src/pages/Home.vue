<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import { http } from '../api/http'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()

const isAuthenticated = computed(() => auth.isAuthenticated)

const primaryCta = computed(() =>
  isAuthenticated.value
    ? { label: 'Go to Dashboard', to: { name: 'dashboard' as const } }
    : { label: 'Start Practicing', to: { name: 'register' as const } },
)

const secondaryCta = computed(() =>
  isAuthenticated.value
    ? { label: 'Browse Quizzes', to: { name: 'dashboard' as const } }
    : { label: 'Login to Continue', to: { name: 'login' as const } },
)

type PracticeCategorySummary = {
  slug: string
  name: string
  description?: string | null
  icon?: string | null
  total_questions: number
  difficulty: string
}

type QuizSummary = {
  id: number
  title: string
  description?: string | null
  is_active: boolean
  question_count: number
}

const loading = ref(true)
const error = ref('')

const stats = ref({
  categories: 0,
  questions: 0,
  quizzes: 0,
})

const topCategories = ref<PracticeCategorySummary[]>([])
const featuredQuizzes = ref<QuizSummary[]>([])

const loadHomeData = async () => {
  loading.value = true
  error.value = ''
  try {
    const [categoriesResponse, quizzesResponse] = await Promise.all([
      http.get<PracticeCategorySummary[]>('/practice/categories'),
      http.get<QuizSummary[]>('/quizzes'),
    ])

    const categories = categoriesResponse.data
    const quizzes = quizzesResponse.data.filter((quiz) => quiz.is_active)

    stats.value = {
      categories: categories.length,
      questions: categories.reduce((total, item) => total + item.total_questions, 0),
      quizzes: quizzes.length,
    }

    topCategories.value = [...categories]
      .sort((a, b) => b.total_questions - a.total_questions)
      .slice(0, 4)

    featuredQuizzes.value = [...quizzes]
      .sort((a, b) => b.question_count - a.question_count)
      .slice(0, 3)
  } catch (err) {
    console.error(err)
    error.value = 'We could not load the latest practice data. Please try again soon.'
  } finally {
    loading.value = false
  }
}

onMounted(loadHomeData)

const fallbackDescription = 'Sharpen your understanding with focused practice and clear explanations.'
</script>

<template>
  <div class="space-y-16">
    <section class="relative overflow-hidden rounded-4xl border border-slate-200 bg-white text-slate-900 shadow-glow">
      <div class="absolute -right-28 top-0 h-56 w-56 rounded-full bg-brand-200/35 blur-3xl"></div>
      <div class="absolute -left-16 bottom-0 h-52 w-52 rounded-full bg-emerald-200/30 blur-3xl"></div>
      <div class="relative mx-auto grid max-w-6xl gap-12 px-6 py-16 md:px-10 lg:grid-cols-[3fr,2fr]">
        <div class="space-y-6">
          <p class="inline-flex items-center gap-2 rounded-full bg-brand-50 px-4 py-1 text-xs font-semibold uppercase tracking-[0.4em] text-brand-600">
            Nepal Loksewa prep
          </p>
          <h1 class="text-4xl font-semibold leading-tight text-slate-900 md:text-5xl">
            Master your competitive exams with confidence
          </h1>
          <p class="max-w-xl text-sm text-slate-600 md:text-base">
            Access curated question banks, full-length mock tests, and personalised insights so you can focus on the topics that matter most.
          </p>
          <div class="flex flex-col gap-3 sm:flex-row">
            <RouterLink
              :to="primaryCta.to"
              class="inline-flex items-center justify-center gap-2 rounded-full bg-brand-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-brand-900/25 transition hover:bg-brand-500"
            >
              {{ primaryCta.label }}
              <span aria-hidden="true">→</span>
            </RouterLink>
            <RouterLink
              :to="secondaryCta.to"
              class="inline-flex items-center justify-center gap-2 rounded-full border border-slate-200 bg-white px-6 py-3 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-brand-300 hover:text-brand-600"
            >
              {{ secondaryCta.label }}
            </RouterLink>
          </div>
          <div class="grid gap-3 sm:grid-cols-3">
            <article
              v-for="stat in [
                { label: 'Practice categories', value: stats.categories },
                { label: 'Active quizzes', value: stats.quizzes },
                { label: 'Questions to explore', value: stats.questions },
              ]"
              :key="stat.label"
              class="rounded-2xl border border-slate-200 bg-white/80 p-4 text-left shadow-sm backdrop-blur"
            >
              <p class="text-xs font-semibold uppercase tracking-[0.4em] text-slate-400">{{ stat.label }}</p>
              <p class="mt-2 text-2xl font-semibold text-slate-900">{{ loading ? '…' : stat.value }}</p>
            </article>
          </div>
        </div>

        <div class="space-y-4">
          <div v-if="loading" class="h-64 animate-pulse rounded-3xl border border-slate-200 bg-slate-100/60"></div>
          <div v-else-if="error" class="rounded-3xl border border-amber-200 bg-amber-50 p-6 text-sm text-amber-800">
            {{ error }}
          </div>
          <div v-else class="space-y-4">
            <article class="rounded-3xl border border-slate-200 bg-white p-6 text-slate-900 shadow-sm">
              <h2 class="text-base font-semibold">Latest highlights</h2>
              <p class="mt-2 text-sm text-slate-500">
                Stay on track with fresh practice sets and quizzes sourced from the Loksewa curriculum.
              </p>
              <ul class="mt-4 space-y-2 text-sm text-slate-600">
                <li>• {{ stats.categories }} categories curated for daily prep</li>
                <li>• {{ stats.questions }} questions with detailed explanations</li>
                <li>• {{ stats.quizzes }} mock tests ready to launch anytime</li>
              </ul>
            </article>
            <article class="rounded-3xl border border-slate-200 bg-white p-6 text-slate-900 shadow-sm">
              <h2 class="text-base font-semibold">Quick start</h2>
              <ul class="mt-3 space-y-2 text-sm text-slate-600">
                <li>
                  <RouterLink :to="{ name: 'categories' }" class="text-brand-600 underline-offset-4 hover:underline">Browse categories</RouterLink>
                  to target specific topics
                </li>
                <li>
                  <RouterLink :to="{ name: 'dashboard' }" class="text-brand-600 underline-offset-4 hover:underline">Visit your dashboard</RouterLink>
                  for personalised insights
                </li>
                <li>
                  <RouterLink :to="{ name: 'home', hash: '#quizzes' }" class="text-brand-600 underline-offset-4 hover:underline">Launch a mock test</RouterLink>
                  and track your progress instantly
                </li>
              </ul>
            </article>
          </div>
        </div>
      </div>
    </section>

    <section v-if="!loading" class="space-y-10">
      <div class="mx-auto max-w-6xl px-6">
        <header class="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.4em] text-slate-400">Plan your practice</p>
            <h2 class="text-3xl font-semibold text-slate-900">Top categories right now</h2>
            <p class="mt-2 text-sm text-slate-500">
              Choose a subject to unlock targeted practice sessions tailored to your goals.
            </p>
          </div>
          <RouterLink
            :to="{ name: 'categories' }"
            class="inline-flex items-center justify-center gap-2 rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-brand-300 hover:text-brand-600"
          >
            View all categories
            <span aria-hidden="true">→</span>
          </RouterLink>
        </header>

        <div v-if="topCategories.length === 0" class="mt-10 rounded-3xl border border-slate-200 bg-white/80 p-10 text-center text-sm text-slate-500">
          Categories will appear here once they are created.
        </div>
        <div v-else class="mt-10 grid gap-6 md:grid-cols-2 xl:grid-cols-4">
          <article
            v-for="category in topCategories"
            :key="category.slug"
            class="flex h-full flex-col gap-4 rounded-3xl border border-slate-200 bg-white/90 p-6 shadow-lg shadow-brand-900/5 transition hover:-translate-y-1 hover:shadow-xl"
          >
            <div class="space-y-2">
              <p class="text-xs font-semibold uppercase tracking-[0.35em] text-brand-500">{{ category.difficulty }}</p>
              <h3 class="text-xl font-semibold text-slate-900">{{ category.name }}</h3>
            </div>
            <p class="text-sm leading-6 text-slate-600">
              {{ category.description?.trim() || fallbackDescription }}
            </p>
            <div class="mt-auto flex items-center justify-between text-sm text-slate-500">
              <span>{{ category.total_questions }} questions</span>
              <RouterLink
                :to="{ name: 'practice', params: { slug: category.slug } }"
                class="inline-flex items-center gap-1 text-brand-600 hover:underline"
              >
                Practice
                <span aria-hidden="true">→</span>
              </RouterLink>
            </div>
          </article>
        </div>
      </div>
    </section>

    <section id="quizzes" class="rounded-4xl border border-slate-200 bg-white/90 p-8 shadow-xl shadow-brand-900/5 md:p-10">
      <div class="mx-auto max-w-6xl space-y-10">
        <header class="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.4em] text-slate-400">Mock tests</p>
            <h2 class="text-3xl font-semibold text-slate-900">Featured quizzes</h2>
            <p class="mt-2 text-sm text-slate-500">
              Tackle full-length practice tests designed to mirror the Loksewa experience.
            </p>
          </div>
          <RouterLink
            :to="{ name: isAuthenticated ? 'dashboard' : 'register' }"
            class="inline-flex items-center justify-center gap-2 rounded-full bg-brand-600 px-4 py-2 text-sm font-semibold text-white shadow-glow transition hover:bg-brand-500"
          >
            {{ isAuthenticated ? 'Open dashboard' : 'Create free account' }}
          </RouterLink>
        </header>

        <div v-if="loading" class="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          <div v-for="n in 3" :key="`quiz-skeleton-${n}`" class="h-48 animate-pulse rounded-3xl bg-slate-100"></div>
        </div>
        <div v-else-if="featuredQuizzes.length === 0" class="rounded-3xl border border-slate-200 bg-slate-50 p-10 text-center text-sm text-slate-500">
          Publish your first quiz to see it featured here.
        </div>
        <div v-else class="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          <article
            v-for="quiz in featuredQuizzes"
            :key="quiz.id"
            class="flex flex-col gap-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-lg shadow-brand-900/5 transition hover:-translate-y-1 hover:shadow-xl"
          >
            <h3 class="text-xl font-semibold text-slate-900">{{ quiz.title }}</h3>
            <p class="text-sm text-slate-500">{{ quiz.description || 'Challenge yourself with a timed mock test.' }}</p>
            <div class="mt-auto flex items-center justify-between text-sm text-slate-500">
              <span>{{ quiz.question_count }} questions</span>
              <RouterLink :to="{ name: 'quiz', params: { id: quiz.id } }" class="inline-flex items-center gap-1 text-brand-600 hover:underline">
                Start
                <span aria-hidden="true">→</span>
              </RouterLink>
            </div>
          </article>
        </div>
      </div>
    </section>

    <section class="rounded-4xl border border-slate-200 bg-white/90 p-10 text-center shadow-xl shadow-brand-900/5 md:p-14">
      <div class="mx-auto max-w-4xl space-y-4">
        <h2 class="text-3xl font-semibold text-slate-900 md:text-4xl">Ready to accelerate your preparation?</h2>
        <p class="text-sm text-slate-500">
          Join thousands of aspirants who rely on QuizMaster for structured practice, real-time analytics, and exam-ready confidence.
        </p>
        <div class="mt-6 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <RouterLink
            :to="primaryCta.to"
            class="inline-flex items-center justify-center gap-2 rounded-full bg-brand-600 px-5 py-2.5 text-sm font-semibold text-white shadow-glow transition hover:bg-brand-500"
          >
            {{ primaryCta.label }}
          </RouterLink>
          <RouterLink
            :to="secondaryCta.to"
            class="inline-flex items-center justify-center gap-2 rounded-full border border-slate-200 px-5 py-2.5 text-sm font-semibold text-slate-700 transition hover:border-brand-300 hover:text-brand-600"
          >
            {{ secondaryCta.label }}
          </RouterLink>
        </div>
      </div>
    </section>
  </div>
</template>
