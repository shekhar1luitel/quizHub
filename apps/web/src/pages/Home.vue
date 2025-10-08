<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { http } from '../api/http'

interface QuizSummary {
  id: number
  title: string
  description?: string | null
  question_count: number
}

const loading = ref(true)
const quizzes = ref<QuizSummary[]>([])
const error = ref('')

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

onMounted(fetchQuizzes)
</script>

<template>
  <section class="space-y-6">
    <header class="space-y-2">
      <h1 class="text-3xl font-semibold tracking-tight">Sharpen your Loksewa preparation</h1>
      <p class="max-w-2xl text-gray-600">
        Attempt curated quizzes that mirror Lok Sewa examinations, track your performance, and focus on
        improvement areas using detailed analytics.
      </p>
    </header>

    <div v-if="loading" class="grid gap-4 md:grid-cols-2">
      <div v-for="n in 4" :key="n" class="animate-pulse rounded-lg border border-gray-200 bg-white p-4">
        <div class="h-4 w-32 rounded bg-gray-200"></div>
        <div class="mt-3 h-3 w-full rounded bg-gray-100"></div>
        <div class="mt-2 h-3 w-3/4 rounded bg-gray-100"></div>
        <div class="mt-4 h-9 w-24 rounded bg-gray-200"></div>
      </div>
    </div>

    <p v-else-if="error" class="rounded border border-red-200 bg-red-50 p-4 text-sm text-red-700">
      {{ error }}
    </p>

    <div v-else class="grid gap-4 md:grid-cols-2">
      <article
        v-for="quiz in quizzes"
        :key="quiz.id"
        class="flex h-full flex-col justify-between rounded-lg border border-gray-200 bg-white p-5 shadow-sm"
      >
        <div class="space-y-2">
          <h2 class="text-xl font-semibold">{{ quiz.title }}</h2>
          <p class="text-sm text-gray-600">{{ quiz.description || 'No description provided yet.' }}</p>
          <p class="text-xs uppercase tracking-wide text-gray-400">
            {{ quiz.question_count }} questions
          </p>
        </div>
        <RouterLink
          :to="{ name: 'quiz', params: { id: quiz.id } }"
          class="mt-4 inline-flex items-center justify-center rounded bg-gray-900 px-3 py-2 text-sm font-semibold text-white transition hover:bg-gray-700"
        >
          Start quiz
        </RouterLink>
      </article>
      <div v-if="quizzes.length === 0" class="rounded-lg border border-dashed border-gray-300 p-6 text-sm text-gray-600">
        No quizzes yet. Ask an admin to create one from the dashboard.
      </div>
    </div>
  </section>
</template>
