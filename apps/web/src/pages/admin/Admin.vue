<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { http } from '../../api/http'

interface QuizSummary {
  id: number
  title: string
  question_count: number
}

const quizzes = ref<QuizSummary[]>([])
const loading = ref(true)
const error = ref('')

const totalQuestions = computed(() => quizzes.value.reduce((acc, quiz) => acc + quiz.question_count, 0))

const load = async () => {
  try {
    const { data } = await http.get<QuizSummary[]>('/quizzes')
    quizzes.value = data
  } catch (err) {
    error.value = 'Unable to load quizzes.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <section class="space-y-10">
    <header class="space-y-4">
      <div class="inline-flex items-center gap-2 rounded-full bg-slate-100 px-4 py-1 text-xs font-semibold uppercase tracking-widest text-slate-600">
        Admin Dashboard
      </div>
      <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div class="space-y-2">
          <h1 class="text-3xl font-semibold text-slate-900">QuizMaster control center</h1>
          <p class="max-w-2xl text-sm text-slate-500">
            Oversee the entire quiz library, manage question quality, and keep the platform running smoothly for learners.
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
        </div>
      </div>
    </header>

    <div class="grid gap-5 lg:grid-cols-4">
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Active quizzes</p>
        <p class="mt-3 text-3xl font-semibold text-slate-900">{{ loading ? '…' : quizzes.length }}</p>
        <p class="mt-2 text-xs text-slate-500">Curate balanced coverage across subjects.</p>
      </article>
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Question bank</p>
        <p class="mt-3 text-3xl font-semibold text-slate-900">{{ loading ? '…' : totalQuestions }}</p>
        <p class="mt-2 text-xs text-slate-500">Ensure each quiz has sufficient depth.</p>
      </article>
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">System status</p>
        <p class="mt-3 text-3xl font-semibold text-emerald-600">98%</p>
        <p class="mt-2 text-xs text-slate-500">API uptime for the last 7 days.</p>
      </article>
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Pending reviews</p>
        <p class="mt-3 text-3xl font-semibold text-slate-900">3</p>
        <p class="mt-2 text-xs text-slate-500">Questions awaiting validation.</p>
      </article>
    </div>

    <div class="grid gap-6 xl:grid-cols-[2fr,3fr]">
      <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <header class="flex items-center justify-between">
          <div>
            <h2 class="text-lg font-semibold text-slate-900">Question management</h2>
            <p class="text-xs text-slate-500">Create, edit, and archive questions with detailed explanations.</p>
          </div>
        </header>
        <p class="mt-4 text-sm text-slate-500">
          Maintain high-quality content by regularly reviewing accuracy, difficulty balance, and relevancy to the latest LokSewa syllabus.
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
            <h2 class="text-lg font-semibold text-slate-900">Quiz catalog</h2>
            <p class="text-xs text-slate-500">Monitor quiz availability and coverage.</p>
          </div>
        </header>
        <div class="mt-5 space-y-3 text-sm text-slate-700">
          <p v-if="loading" class="animate-pulse text-slate-400">Loading quizzes…</p>
          <p v-else-if="error" class="text-red-600">{{ error }}</p>
          <ul v-else class="space-y-2">
            <li
              v-for="quiz in quizzes"
              :key="quiz.id"
              class="flex items-center justify-between rounded-2xl border border-slate-200 px-4 py-3"
            >
              <div>
                <p class="font-semibold text-slate-900">{{ quiz.title }}</p>
                <p class="text-xs text-slate-500">{{ quiz.question_count }} questions</p>
              </div>
              <RouterLink
                :to="{ name: 'quiz', params: { id: quiz.id } }"
                class="rounded-full bg-slate-900 px-3 py-1 text-xs font-semibold text-white transition hover:bg-slate-700"
              >
                Preview
              </RouterLink>
            </li>
          </ul>
          <p v-if="!loading && !error && quizzes.length === 0" class="text-xs text-slate-500">
            No quizzes yet. Add questions first, then create quizzes via the API.
          </p>
        </div>
      </section>
    </div>
  </section>
</template>
