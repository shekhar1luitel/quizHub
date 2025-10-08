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
  <div class="min-h-screen bg-background text-foreground">
    <header class="border-b border-border bg-card">
      <div class="container mx-auto flex items-center justify-between px-4 py-4">
        <div class="flex items-center gap-2">
          <span class="inline-flex h-10 w-10 items-center justify-center rounded-md bg-secondary/20 text-secondary">
            <svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M3 5a2 2 0 0 1 2-2h6v16H5a2 2 0 0 0-2 2Z" />
              <path d="M21 5a2 2 0 0 0-2-2h-6v16h6a2 2 0 0 1 2 2Z" />
              <path d="M12 4v16" />
            </svg>
          </span>
          <RouterLink :to="{ name: 'home' }" class="text-2xl font-bold">
            QuizMaster
          </RouterLink>
        </div>
        <div class="flex gap-2">
          <RouterLink
            :to="{ name: isAuthenticated ? 'dashboard' : 'login' }"
            class="inline-flex items-center justify-center rounded-md border border-border px-4 py-2 text-sm font-medium transition hover:bg-muted"
          >
            {{ isAuthenticated ? 'Dashboard' : 'Login' }}
          </RouterLink>
          <RouterLink
            v-if="!isAuthenticated"
            :to="{ name: 'register' }"
            class="inline-flex items-center justify-center rounded-md bg-secondary px-4 py-2 text-sm font-medium text-secondary-foreground transition hover:bg-secondary/90"
          >
            Sign Up
          </RouterLink>
        </div>
      </div>
    </header>

    <main>
      <section class="bg-card py-20 px-4">
        <div class="container mx-auto grid max-w-6xl gap-12 lg:grid-cols-[3fr,2fr]">
          <div class="space-y-6 text-center lg:text-left">
            <p class="text-xs font-semibold uppercase tracking-[0.3em] text-muted-foreground">Nepal Loksewa prep</p>
            <h1 class="text-4xl font-bold leading-tight md:text-6xl">
              Master your competitive exams with confidence
            </h1>
            <p class="text-lg text-muted-foreground">
              Access curated question banks, full-length mock tests, and personalised insights so you can focus on the topics that matter most.
            </p>
            <div class="flex flex-col items-center justify-center gap-4 sm:flex-row lg:justify-start">
              <RouterLink
                :to="primaryCta.to"
                class="inline-flex items-center justify-center rounded-md bg-secondary px-6 py-3 text-sm font-semibold text-secondary-foreground shadow-sm transition hover:bg-secondary/90"
              >
                {{ primaryCta.label }}
              </RouterLink>
              <RouterLink
                :to="secondaryCta.to"
                class="inline-flex items-center justify-center rounded-md border border-border px-6 py-3 text-sm font-semibold transition hover:bg-muted"
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
                class="rounded-lg border border-border bg-background/80 p-5 text-left shadow-sm backdrop-blur"
              >
                <p class="text-xs font-semibold uppercase tracking-[0.3em] text-muted-foreground">{{ stat.label }}</p>
                <p class="mt-2 text-2xl font-bold">{{ loading ? '…' : stat.value }}</p>
              </article>
            </div>
          </div>

          <div class="space-y-4">
            <div v-if="loading" class="h-64 animate-pulse rounded-2xl bg-muted"></div>
            <div v-else-if="error" class="rounded-2xl border border-amber-200 bg-amber-50 p-6 text-sm text-amber-800">
              {{ error }}
            </div>
            <div v-else class="space-y-4">
              <article class="rounded-2xl border border-border bg-background p-6 shadow-sm">
                <h2 class="text-base font-semibold">Latest highlights</h2>
                <p class="mt-2 text-sm text-muted-foreground">
                  Stay on track with fresh practice sets and quizzes sourced from the Loksewa curriculum.
                </p>
                <ul class="mt-4 space-y-3 text-sm text-muted-foreground">
                  <li>• {{ stats.categories }} categories curated for daily prep</li>
                  <li>• {{ stats.questions }} questions with detailed explanations</li>
                  <li>• {{ stats.quizzes }} mock tests ready to launch anytime</li>
                </ul>
              </article>
              <article class="rounded-2xl border border-border bg-background p-6 shadow-sm">
                <h2 class="text-base font-semibold">Quick start</h2>
                <ul class="mt-3 space-y-2 text-sm text-muted-foreground">
                  <li>
                    <RouterLink :to="{ name: 'categories' }" class="text-secondary hover:underline">Browse categories</RouterLink>
                    to target specific topics
                  </li>
                  <li>
                    <RouterLink :to="{ name: 'dashboard' }" class="text-secondary hover:underline">Visit your dashboard</RouterLink>
                    for personalised insights
                  </li>
                  <li>
                    <RouterLink :to="{ name: 'home', hash: '#quizzes' }" class="text-secondary hover:underline">Launch a mock test</RouterLink>
                    and track your progress instantly
                  </li>
                </ul>
              </article>
            </div>
          </div>
        </div>
      </section>

      <section v-if="!loading" class="py-16 px-4">
        <div class="container mx-auto max-w-6xl">
          <header class="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.3em] text-muted-foreground">Plan your practice</p>
              <h2 class="text-3xl font-bold">Top categories right now</h2>
              <p class="mt-2 text-sm text-muted-foreground">
                Choose a subject to unlock targeted practice sessions tailored to your goals.
              </p>
            </div>
            <RouterLink
              :to="{ name: 'categories' }"
              class="inline-flex items-center justify-center rounded-md border border-border px-4 py-2 text-sm font-semibold transition hover:bg-muted"
            >
              View all categories
            </RouterLink>
          </header>

          <div v-if="topCategories.length === 0" class="mt-10 rounded-2xl border border-border bg-background p-8 text-center text-sm text-muted-foreground">
            Categories will appear here once they are created.
          </div>
          <div v-else class="mt-10 grid gap-6 md:grid-cols-2 xl:grid-cols-4">
            <article
              v-for="category in topCategories"
              :key="category.slug"
              class="flex flex-col gap-4 rounded-2xl border border-border bg-card p-6 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg"
            >
              <div class="space-y-1">
                <p class="text-sm font-semibold uppercase tracking-[0.3em] text-muted-foreground">{{ category.difficulty }}</p>
                <h3 class="text-xl font-semibold">{{ category.name }}</h3>
              </div>
              <p class="text-sm leading-6 text-muted-foreground">
                {{ category.description?.trim() || fallbackDescription }}
              </p>
              <div class="mt-auto flex items-center justify-between text-sm">
                <span class="text-muted-foreground">{{ category.total_questions }} questions</span>
                <RouterLink
                  :to="{ name: 'practice', params: { slug: category.slug } }"
                  class="inline-flex items-center gap-1 text-secondary hover:underline"
                >
                  Practice
                  <span aria-hidden="true">→</span>
                </RouterLink>
              </div>
            </article>
          </div>
        </div>
      </section>

      <section id="quizzes" class="bg-muted/40 py-16 px-4">
        <div class="container mx-auto max-w-6xl">
          <header class="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.3em] text-muted-foreground">Mock tests</p>
              <h2 class="text-3xl font-bold">Featured quizzes</h2>
              <p class="mt-2 text-sm text-muted-foreground">
                Tackle full-length practice tests designed to mirror the Loksewa experience.
              </p>
            </div>
            <RouterLink
              :to="{ name: isAuthenticated ? 'dashboard' : 'register' }"
              class="inline-flex items-center justify-center rounded-md bg-secondary px-4 py-2 text-sm font-semibold text-secondary-foreground shadow-sm transition hover:bg-secondary/90"
            >
              {{ isAuthenticated ? 'Open dashboard' : 'Create free account' }}
            </RouterLink>
          </header>

          <div v-if="loading" class="mt-10 grid gap-6 md:grid-cols-2 xl:grid-cols-3">
            <div v-for="n in 3" :key="`quiz-skeleton-${n}`" class="h-48 animate-pulse rounded-2xl bg-card"></div>
          </div>
          <div v-else-if="featuredQuizzes.length === 0" class="mt-10 rounded-2xl border border-border bg-background p-8 text-center text-sm text-muted-foreground">
            Publish your first quiz to see it featured here.
          </div>
          <div v-else class="mt-10 grid gap-6 md:grid-cols-2 xl:grid-cols-3">
            <article
              v-for="quiz in featuredQuizzes"
              :key="quiz.id"
              class="flex flex-col gap-4 rounded-2xl border border-border bg-card p-6 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg"
            >
              <h3 class="text-xl font-semibold text-foreground">{{ quiz.title }}</h3>
              <p class="text-sm text-muted-foreground">{{ quiz.description || 'Challenge yourself with a timed mock test.' }}</p>
              <div class="mt-auto flex items-center justify-between text-sm text-muted-foreground">
                <span>{{ quiz.question_count }} questions</span>
                <RouterLink :to="{ name: 'quiz', params: { id: quiz.id } }" class="inline-flex items-center gap-1 text-secondary hover:underline">
                  Start
                  <span aria-hidden="true">→</span>
                </RouterLink>
              </div>
            </article>
          </div>
        </div>
      </section>

      <section class="py-16 px-4">
        <div class="container mx-auto max-w-4xl rounded-3xl border border-border bg-card p-10 text-center shadow-sm">
          <h2 class="text-3xl font-bold text-foreground">Ready to accelerate your preparation?</h2>
          <p class="mt-4 text-sm text-muted-foreground">
            Join thousands of aspirants who rely on QuizMaster for structured practice, real-time analytics, and exam-ready confidence.
          </p>
          <div class="mt-6 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <RouterLink
              :to="primaryCta.to"
              class="inline-flex items-center justify-center rounded-md bg-secondary px-5 py-2.5 text-sm font-semibold text-secondary-foreground shadow-sm transition hover:bg-secondary/90"
            >
              {{ primaryCta.label }}
            </RouterLink>
            <RouterLink
              :to="secondaryCta.to"
              class="inline-flex items-center justify-center rounded-md border border-border px-5 py-2.5 text-sm font-semibold transition hover:bg-muted"
            >
              {{ secondaryCta.label }}
            </RouterLink>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>
