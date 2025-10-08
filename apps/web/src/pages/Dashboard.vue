<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { http } from '../api/http'

interface AttemptSummary {
  id: number
  quiz_id: number
  quiz_title: string
  score: number
  submitted_at: string
}

interface DashboardSummary {
  total_attempts: number
  average_score: number
  total_correct_answers: number
  total_questions_answered: number
  recent_attempts: AttemptSummary[]
}

const loading = ref(true)
const error = ref('')
const summary = ref<DashboardSummary | null>(null)

const loadDashboard = async () => {
  try {
    const { data } = await http.get<DashboardSummary>('/dashboard/summary')
    summary.value = data
  } catch (err) {
    error.value = 'Unable to load dashboard data.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const formatDate = (iso: string) => new Date(iso).toLocaleString()

onMounted(loadDashboard)
</script>

<template>
  <section class="space-y-6">
    <header>
      <h1 class="text-2xl font-semibold">Your learning snapshot</h1>
      <p class="text-sm text-gray-500">Track quiz performance and revisit recent attempts.</p>
    </header>

    <div v-if="loading" class="grid gap-4 md:grid-cols-4">
      <div v-for="n in 4" :key="n" class="h-24 animate-pulse rounded-lg bg-gray-100"></div>
    </div>

    <p v-else-if="error" class="rounded border border-red-200 bg-red-50 p-4 text-sm text-red-700">{{ error }}</p>

    <div v-else-if="summary" class="space-y-6">
      <div class="grid gap-4 md:grid-cols-4">
        <article class="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
          <p class="text-xs uppercase text-gray-500">Attempts</p>
          <p class="text-2xl font-semibold text-gray-900">{{ summary.total_attempts }}</p>
        </article>
        <article class="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
          <p class="text-xs uppercase text-gray-500">Average score</p>
          <p class="text-2xl font-semibold text-gray-900">{{ summary.average_score.toFixed(1) }}%</p>
        </article>
        <article class="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
          <p class="text-xs uppercase text-gray-500">Correct answers</p>
          <p class="text-2xl font-semibold text-gray-900">{{ summary.total_correct_answers }}</p>
        </article>
        <article class="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
          <p class="text-xs uppercase text-gray-500">Questions practiced</p>
          <p class="text-2xl font-semibold text-gray-900">{{ summary.total_questions_answered }}</p>
        </article>
      </div>

      <div class="rounded-lg border border-gray-200 bg-white shadow-sm">
        <header class="flex items-center justify-between border-b border-gray-200 px-5 py-3">
          <h2 class="text-sm font-semibold text-gray-700">Recent attempts</h2>
        </header>
        <div v-if="summary.recent_attempts.length === 0" class="p-5 text-sm text-gray-600">
          You haven’t completed any quizzes yet. Start one from the home page.
        </div>
        <ul v-else class="divide-y divide-gray-200 text-sm">
          <li v-for="attempt in summary.recent_attempts" :key="attempt.id" class="flex items-center justify-between px-5 py-3">
            <div>
              <p class="font-medium text-gray-900">{{ attempt.quiz_title || 'Untitled quiz' }}</p>
              <p class="text-xs text-gray-500">{{ formatDate(attempt.submitted_at) }}</p>
            </div>
            <span class="text-sm font-semibold text-emerald-600">{{ attempt.score.toFixed(1) }}%</span>
          </li>
        </ul>
      </div>
    </div>

    <p v-else class="text-sm text-gray-600">No dashboard data available yet.</p>
  </section>
</template>
