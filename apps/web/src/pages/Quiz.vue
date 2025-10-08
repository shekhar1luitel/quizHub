<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { http } from '../api/http'
import { useAuthStore } from '../stores/auth'
import { useQuizStore } from '../stores/quiz'

interface QuizQuestionOption {
  id: number
  text: string
}

interface QuizQuestion {
  id: number
  prompt: string
  subject?: string | null
  difficulty?: string | null
  options: QuizQuestionOption[]
}

interface QuizDetail {
  id: number
  title: string
  description?: string | null
  questions: QuizQuestion[]
}

const route = useRoute()
const router = useRouter()
const quizStore = useQuizStore()
const authStore = useAuthStore()

const quiz = ref<QuizDetail | null>(null)
const loading = ref(true)
const error = ref('')
const currentIndex = ref(0)
const submitting = ref(false)
const submissionError = ref('')
const timerSeconds = ref(0)
let interval: number | null = null

const fetchQuiz = async () => {
  loading.value = true
  error.value = ''
  try {
    const id = Number(route.params.id)
    if (Number.isNaN(id)) {
      throw new Error('Invalid quiz id')
    }
    const { data } = await http.get<QuizDetail>(`/quizzes/${id}`)
    quiz.value = data
    quizStore.start(data.id)
    startTimer()
  } catch (err) {
    error.value = 'Unable to load quiz. Please try again later.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const startTimer = () => {
  timerSeconds.value = 0
  if (interval) window.clearInterval(interval)
  interval = window.setInterval(() => {
    timerSeconds.value += 1
    quizStore.recordDuration(timerSeconds.value)
  }, 1000)
}

const stopTimer = () => {
  if (interval) {
    window.clearInterval(interval)
    interval = null
  }
}

const questions = computed(() => quiz.value?.questions ?? [])
const currentQuestion = computed(() => questions.value[currentIndex.value])
const answeredCount = computed(
  () =>
    questions.value.filter((question) =>
      Object.prototype.hasOwnProperty.call(quizStore.answers, question.id)
    ).length
)
const progress = computed(() => {
  if (questions.value.length === 0) return 0
  return Math.round((answeredCount.value / questions.value.length) * 100)
})
const formattedTimer = computed(() => {
  const minutes = Math.floor(timerSeconds.value / 60)
  const seconds = timerSeconds.value % 60
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
})

const selectOption = (questionId: number, optionId: number) => {
  quizStore.selectAnswer(questionId, optionId)
}

const goNext = () => {
  if (currentIndex.value < questions.value.length - 1) {
    currentIndex.value += 1
  }
}

const goPrev = () => {
  if (currentIndex.value > 0) {
    currentIndex.value -= 1
  }
}

const submit = async () => {
  if (!quiz.value) return
  submissionError.value = ''
  if (!authStore.isAuthenticated) {
    router.push({ name: 'login', query: { redirect: route.fullPath } })
    return
  }

  const unanswered = questions.value.filter(
    (question) => !Object.prototype.hasOwnProperty.call(quizStore.answers, question.id)
  )
  if (unanswered.length > 0) {
    submissionError.value = 'Please answer all questions before submitting.'
    return
  }

  submitting.value = true
  try {
    const payload = {
      quiz_id: quiz.value.id,
      duration_seconds: quizStore.durationSeconds,
      answers: questions.value.map((question) => ({
        question_id: question.id,
        selected_option_id: quizStore.answers[question.id] ?? null,
      })),
    }
    const { data } = await http.post<{ id: number }>('/attempts', payload)
    quizStore.reset()
    stopTimer()
    router.push({ name: 'results', params: { id: data.id } })
  } catch (err: any) {
    submissionError.value = err?.response?.data?.detail || 'Submission failed. Please retry.'
    console.error(err)
  } finally {
    submitting.value = false
  }
}

onMounted(fetchQuiz)
onUnmounted(() => {
  stopTimer()
  quizStore.reset()
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold">{{ quiz?.title || 'Quiz' }}</h1>
        <p class="text-sm text-gray-500">Answer every question to submit and view your results.</p>
      </div>
      <div class="rounded-full bg-gray-900 px-4 py-2 text-sm font-semibold text-white">{{ formattedTimer }}</div>
    </div>

    <div v-if="loading" class="space-y-4">
      <div class="h-6 w-2/5 animate-pulse rounded bg-gray-200"></div>
      <div class="h-32 animate-pulse rounded bg-gray-100"></div>
    </div>

    <p v-else-if="error" class="rounded border border-red-200 bg-red-50 p-4 text-sm text-red-700">{{ error }}</p>

    <div v-else-if="currentQuestion" class="space-y-4">
      <div class="flex items-center justify-between text-xs uppercase tracking-wider text-gray-500">
        <span>Question {{ currentIndex + 1 }} of {{ questions.length }}</span>
        <span>{{ progress }}% answered</span>
      </div>

      <article class="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
        <header class="space-y-1">
          <p v-if="currentQuestion.subject" class="text-xs font-semibold uppercase text-gray-400">
            {{ currentQuestion.subject }}
          </p>
          <h2 class="text-lg font-semibold text-gray-900">{{ currentQuestion.prompt }}</h2>
          <p v-if="currentQuestion.difficulty" class="text-xs uppercase tracking-wider text-gray-400">
            Difficulty: {{ currentQuestion.difficulty }}
          </p>
        </header>

        <div class="mt-5 space-y-2">
          <label
            v-for="option in currentQuestion.options"
            :key="option.id"
            class="flex cursor-pointer items-start gap-3 rounded border border-gray-200 bg-gray-50 p-3 text-sm transition hover:border-gray-300"
          >
            <input
              :checked="quizStore.answers[currentQuestion.id] === option.id"
              class="mt-1"
              name="answer"
              type="radio"
              :value="option.id"
              @change="selectOption(currentQuestion.id, option.id)"
            />
            <span>{{ option.text }}</span>
          </label>
        </div>
      </article>

      <div class="flex flex-wrap items-center justify-between gap-3">
        <div class="flex gap-2">
          <button
            class="rounded border border-gray-300 px-3 py-2 text-sm hover:bg-gray-100 disabled:opacity-50"
            :disabled="currentIndex === 0"
            @click="goPrev"
          >
            Previous
          </button>
          <button
            class="rounded border border-gray-300 px-3 py-2 text-sm hover:bg-gray-100 disabled:opacity-50"
            :disabled="currentIndex === questions.length - 1"
            @click="goNext"
          >
            Next
          </button>
        </div>
        <button
          class="rounded bg-emerald-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-500 disabled:opacity-60"
          :disabled="submitting"
          @click="submit"
        >
          {{ submitting ? 'Submitting…' : 'Submit quiz' }}
        </button>
      </div>

      <p v-if="submissionError" class="text-sm text-red-600">{{ submissionError }}</p>
    </div>

    <p v-else class="text-sm text-gray-600">This quiz has no questions yet.</p>
  </div>
</template>
