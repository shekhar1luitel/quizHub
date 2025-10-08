<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { http } from '../api/http'
import { useAuthStore } from '../stores/auth'

interface QuizSummary {
  id: number
  title: string
  description?: string | null
  question_count: number
}

const loading = ref(true)
const quizzes = ref<QuizSummary[]>([])
const error = ref('')
const auth = useAuthStore()

const features = [
  {
    title: 'Comprehensive Question Bank',
    description: 'Access thousands of carefully curated questions spanning popular LokSewa categories and difficulty levels.',
    icon: '🧠',
  },
  {
    title: 'Mock Tests',
    description: 'Simulate exam scenarios with timed practice sets to build confidence and speed.',
    icon: '⏱️',
  },
  {
    title: 'Performance Tracking',
    description: 'Monitor your progress over time with analytics designed to highlight improvement areas.',
    icon: '📈',
  },
  {
    title: 'Detailed Results',
    description: 'Gain detailed feedback with explanations to understand every answer choice clearly.',
    icon: '🔍',
  },
]

const fetchQuizzes = async () => {
  try {
    const { data } = await http.get<QuizSummary[]>('/quizzes')
    quizzes.value = data
  } catch (err) {
    error.value = 'Unable to load quizzes right now.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const primaryCta = computed(() => {
  if (auth.isAuthenticated) {
    return { label: 'Go to dashboard', to: { name: 'dashboard' }, disabled: false }
  }
  if (quizzes.value.length > 0) {
    return {
      label: 'Start practicing',
      to: { name: 'quiz', params: { id: quizzes.value[0].id } },
      disabled: false,
    }
  }
  return { label: 'Start practicing', to: { name: 'home' }, disabled: true }
})

const secondaryCta = computed(() => {
  if (auth.isAuthenticated) {
    return { label: 'Browse quizzes', to: { name: 'home', hash: '#quizzes' } }
  }
  return { label: 'Login to continue', to: { name: 'login' } }
})

onMounted(fetchQuizzes)
</script>

<template>
  <section class="space-y-16 pb-8">
    <div class="overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-indigo-900 to-blue-800 text-white shadow-xl">
      <div class="relative isolate px-6 py-16 sm:px-12 lg:grid lg:grid-cols-[3fr,2fr] lg:items-center lg:gap-12">
        <div class="space-y-6">
          <p class="inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-xs uppercase tracking-widest text-slate-200">
            <span class="inline-flex h-2 w-2 rounded-full bg-emerald-400"></span>
            Built for competitive success
          </p>
          <h1 class="text-4xl font-semibold leading-tight sm:text-5xl">
            Master your competitive exams
          </h1>
          <p class="max-w-2xl text-base text-slate-200 sm:text-lg">
            Practice with thousands of questions, track your progress, and ace your competitive exams with our comprehensive
            mock test platform.
          </p>
          <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
            <RouterLink
              :to="primaryCta.to"
              class="inline-flex items-center justify-center rounded-full bg-white px-6 py-3 text-sm font-semibold text-slate-900 shadow-lg transition hover:bg-slate-200"
              :class="{ 'pointer-events-none opacity-60': primaryCta.disabled }"
            >
              {{ primaryCta.label }}
            </RouterLink>
            <RouterLink
              :to="secondaryCta.to"
              class="inline-flex items-center justify-center rounded-full border border-white/40 px-6 py-3 text-sm font-semibold text-white transition hover:border-white hover:bg-white/10"
            >
              {{ secondaryCta.label }}
            </RouterLink>
          </div>
        </div>
        <div class="mt-10 lg:mt-0">
          <div class="rounded-2xl border border-white/20 bg-white/10 p-6 backdrop-blur">
            <dl class="grid grid-cols-2 gap-4 text-sm">
              <div class="rounded-xl bg-white/10 p-4 text-center">
                <dt class="text-xs uppercase tracking-widest text-slate-200">Total quizzes</dt>
                <dd class="mt-2 text-3xl font-semibold">{{ quizzes.length || (loading ? '…' : '0') }}</dd>
              </div>
              <div class="rounded-xl bg-white/10 p-4 text-center">
                <dt class="text-xs uppercase tracking-widest text-slate-200">Question bank</dt>
                <dd class="mt-2 text-3xl font-semibold">
                  {{ loading ? '…' : quizzes.reduce((acc, quiz) => acc + quiz.question_count, 0) }}
                </dd>
              </div>
              <div class="rounded-xl bg-white/10 p-4 text-center">
                <dt class="text-xs uppercase tracking-widest text-slate-200">Active users</dt>
                <dd class="mt-2 text-3xl font-semibold">1.2k+</dd>
              </div>
              <div class="rounded-xl bg-white/10 p-4 text-center">
                <dt class="text-xs uppercase tracking-widest text-slate-200">Avg. improvement</dt>
                <dd class="mt-2 text-3xl font-semibold">18%</dd>
              </div>
            </dl>
          </div>
        </div>
      </div>
    </div>

    <section class="space-y-6">
      <header class="space-y-2 text-center">
        <h2 class="text-2xl font-semibold text-slate-900">Why choose QuizMaster?</h2>
        <p class="mx-auto max-w-3xl text-sm text-slate-500">
          Your preparation deserves the best resources. Unlock curated content, adaptive analytics, and a learning experience
          tuned for the LokSewa examination pattern.
        </p>
      </header>
      <div class="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        <article
          v-for="feature in features"
          :key="feature.title"
          class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-lg"
        >
          <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-slate-900/90 text-xl text-white">
            {{ feature.icon }}
          </div>
          <h3 class="text-lg font-semibold text-slate-900">{{ feature.title }}</h3>
          <p class="mt-2 text-sm text-slate-500">{{ feature.description }}</p>
        </article>
      </div>
    </section>

    <section id="quizzes" class="space-y-6">
      <header class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 class="text-2xl font-semibold text-slate-900">Practice categories</h2>
          <p class="text-sm text-slate-500">Select a quiz to begin. New quizzes are added regularly.</p>
        </div>
        <RouterLink
          v-if="auth.isAuthenticated"
          :to="{ name: 'dashboard' }"
          class="inline-flex items-center justify-center rounded-full border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-400 hover:text-slate-900"
        >
          View dashboard
        </RouterLink>
      </header>

      <div v-if="loading" class="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        <div v-for="n in 6" :key="n" class="h-48 animate-pulse rounded-2xl border border-slate-200 bg-white"></div>
      </div>

      <p v-else-if="error" class="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">
        {{ error }}
      </p>

      <div v-else class="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        <article
          v-for="quiz in quizzes"
          :key="quiz.id"
          class="flex h-full flex-col justify-between rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-lg"
        >
          <div class="space-y-3">
            <div class="flex items-center justify-between text-xs uppercase tracking-widest text-slate-400">
              <span>Quiz</span>
              <span>{{ quiz.question_count }} questions</span>
            </div>
            <h3 class="text-xl font-semibold text-slate-900">{{ quiz.title }}</h3>
            <p class="text-sm text-slate-500">{{ quiz.description || 'No description provided yet.' }}</p>
          </div>
          <RouterLink
            :to="{ name: 'quiz', params: { id: quiz.id } }"
            class="mt-6 inline-flex items-center justify-center rounded-full bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-700"
          >
            Start practice
          </RouterLink>
        </article>
        <div
          v-if="quizzes.length === 0"
          class="flex h-full flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-white p-6 text-center text-sm text-slate-500"
        >
          <p>No quizzes yet.</p>
          <p class="mt-1">Ask an admin to create one from the dashboard.</p>
        </div>
      </div>
    </section>
  </section>
</template>
