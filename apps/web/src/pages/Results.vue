<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { http } from '../api/http'

interface AttemptAnswerOption {
  id: number
  text: string
}

interface AttemptAnswerReview {
  question_id: number
  prompt: string
  explanation?: string | null
  selected_option_id?: number | null
  correct_option_id?: number | null
  is_correct: boolean
  options: AttemptAnswerOption[]
}

interface AttemptResult {
  id: number
  quiz_id: number
  quiz_title: string
  submitted_at: string
  total_questions: number
  correct_answers: number
  score: number
  answers: AttemptAnswerReview[]
}

const route = useRoute()
const loading = ref(true)
const error = ref('')
const result = ref<AttemptResult | null>(null)

const fetchResult = async () => {
  try {
    const id = Number(route.params.id)
    if (Number.isNaN(id)) throw new Error('Invalid attempt id')
    const { data } = await http.get<AttemptResult>(`/attempts/${id}`)
    result.value = data
  } catch (err) {
    error.value = 'Unable to load results. Please try again later.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const formatDate = (iso: string) => new Date(iso).toLocaleString()
const resolveOptionLabel = (
  answer: AttemptAnswerReview,
  optionId?: number | null,
  emptyLabel = 'Not answered'
) => {
  if (!optionId) return emptyLabel
  return answer.options.find((option) => option.id === optionId)?.text ?? '—'
}

onMounted(fetchResult)
</script>

<template>
  <div class="space-y-6">
    <header>
      <h1 class="text-2xl font-semibold">Quiz results</h1>
      <p class="text-sm text-gray-500">Review your answers and read the explanations to improve faster.</p>
    </header>

    <div v-if="loading" class="space-y-3">
      <div class="h-5 w-48 animate-pulse rounded bg-gray-200"></div>
      <div class="h-24 animate-pulse rounded bg-gray-100"></div>
    </div>

    <p v-else-if="error" class="rounded border border-red-200 bg-red-50 p-4 text-sm text-red-700">{{ error }}</p>

    <section v-else-if="result" class="space-y-6">
      <div class="grid gap-4 rounded-lg border border-gray-200 bg-white p-6 shadow-sm md:grid-cols-4">
        <div>
          <p class="text-xs uppercase text-gray-500">Quiz</p>
          <p class="text-sm font-semibold text-gray-900">{{ result.quiz_title }}</p>
        </div>
        <div>
          <p class="text-xs uppercase text-gray-500">Score</p>
          <p class="text-2xl font-bold text-emerald-600">{{ result.score.toFixed(2) }}%</p>
        </div>
        <div>
          <p class="text-xs uppercase text-gray-500">Correct</p>
          <p class="text-lg font-semibold text-gray-900">{{ result.correct_answers }} / {{ result.total_questions }}</p>
        </div>
        <div>
          <p class="text-xs uppercase text-gray-500">Submitted</p>
          <p class="text-sm text-gray-700">{{ formatDate(result.submitted_at) }}</p>
        </div>
      </div>

      <div class="space-y-4">
        <h2 class="text-lg font-semibold text-gray-900">Answer review</h2>
        <div v-for="answer in result.answers" :key="answer.question_id" class="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
          <div class="flex items-center justify-between gap-3">
            <h3 class="text-base font-semibold text-gray-900">{{ answer.prompt }}</h3>
            <span
              class="rounded-full px-3 py-1 text-xs font-semibold"
              :class="answer.is_correct ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'"
            >
              {{ answer.is_correct ? 'Correct' : 'Incorrect' }}
            </span>
          </div>
          <ul class="mt-3 list-disc space-y-1 pl-5 text-sm text-gray-700">
            <li v-for="option in answer.options" :key="option.id">{{ option.text }}</li>
          </ul>
          <p class="mt-3 text-sm text-gray-600">
            <span class="font-medium">Your answer:</span>
            <span>{{ resolveOptionLabel(answer, answer.selected_option_id) }}</span>
          </p>
          <p class="text-sm text-gray-600">
            <span class="font-medium">Correct answer:</span>
            <span>{{ resolveOptionLabel(answer, answer.correct_option_id, 'Not shared') }}</span>
          </p>
          <p v-if="answer.explanation" class="mt-3 text-sm text-gray-500">
            {{ answer.explanation }}
          </p>
        </div>
      </div>
    </section>

    <p v-else class="text-sm text-gray-600">Attempt not found.</p>
  </div>
</template>
