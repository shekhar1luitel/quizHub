<script setup lang="ts">
import { onMounted, ref } from 'vue'
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
  <section class="space-y-6">
    <header>
      <h1 class="text-2xl font-semibold text-gray-900">Admin workspace</h1>
      <p class="text-sm text-gray-500">Manage the quiz catalog and build new practice sets.</p>
    </header>

    <div class="grid gap-4 md:grid-cols-2">
      <article class="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
        <h2 class="text-lg font-semibold text-gray-900">Questions</h2>
        <p class="mt-1 text-sm text-gray-600">
          Create, edit, and retire question items. Support explanations and marking the correct option.
        </p>
        <RouterLink
          :to="{ name: 'admin-questions' }"
          class="mt-4 inline-flex items-center justify-center rounded bg-gray-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-gray-700"
        >
          Manage questions
        </RouterLink>
      </article>
      <article class="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
        <h2 class="text-lg font-semibold text-gray-900">Quizzes</h2>
        <p class="mt-1 text-sm text-gray-600">
          Review available quizzes and confirm each has enough questions before publishing to learners.
        </p>
        <div class="mt-4 space-y-2 text-sm text-gray-700">
          <p v-if="loading" class="animate-pulse text-gray-400">Loading quizzes…</p>
          <p v-else-if="error" class="text-red-600">{{ error }}</p>
          <ul v-else class="space-y-1">
            <li v-for="quiz in quizzes" :key="quiz.id" class="flex items-center justify-between">
              <span>{{ quiz.title }}</span>
              <span class="text-xs text-gray-500">{{ quiz.question_count }} questions</span>
            </li>
          </ul>
          <p v-if="!loading && !error && quizzes.length === 0" class="text-xs text-gray-500">
            No quizzes yet. Add questions first, then create quizzes via the API.
          </p>
        </div>
      </article>
    </div>
  </section>
</template>
