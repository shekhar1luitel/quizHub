<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { http } from '../api/http'
import { useAuthStore } from '../stores/auth'
import { useQuizStore } from '../stores/quiz'
import { useBookmarkStore } from '../stores/bookmarks'

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
const bookmarkStore = useBookmarkStore()

const quiz = ref<QuizDetail | null>(null)
const loading = ref(true)
const error = ref('')
const currentIndex = ref(0)
const submitting = ref(false)
const submissionError = ref('')
const timerSeconds = ref(0)
const flagged = ref<Record<number, boolean>>({})
const bookmarkBusy = ref<Record<number, boolean>>({})
const toastVisible = ref(false)
const toastMessage = ref('')
const toastVariant = ref<'success' | 'error'>('success')
let interval: number | null = null
let toastTimeout: number | null = null

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
    currentIndex.value = 0
    flagged.value = {}
    quizStore.start(data.id)
    startTimer()
    if (authStore.isAuthenticated) {
      void bookmarkStore.ensureQuestionIdsLoaded()
    }
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

const showToast = (message: string, variant: 'success' | 'error') => {
  toastMessage.value = message
  toastVariant.value = variant
  toastVisible.value = true
  if (toastTimeout) {
    window.clearTimeout(toastTimeout)
  }
  toastTimeout = window.setTimeout(() => {
    toastVisible.value = false
    toastMessage.value = ''
  }, 3200)
}

const hideToast = () => {
  if (toastTimeout) {
    window.clearTimeout(toastTimeout)
    toastTimeout = null
  }
  toastVisible.value = false
  toastMessage.value = ''
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
const flaggedCount = computed(() => Object.values(flagged.value).filter(Boolean).length)
const formattedTimer = computed(() => {
  const minutes = Math.floor(timerSeconds.value / 60)
  const seconds = timerSeconds.value % 60
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
})
const questionStatuses = computed(() => {
  const statuses: Record<number, 'flagged' | 'answered' | 'unanswered'> = {}
  for (const question of questions.value) {
    if (flagged.value[question.id]) {
      statuses[question.id] = 'flagged'
    } else if (Object.prototype.hasOwnProperty.call(quizStore.answers, question.id)) {
      statuses[question.id] = 'answered'
    } else {
      statuses[question.id] = 'unanswered'
    }
  }
  return statuses
})
const isFlagged = (questionId: number) => Boolean(flagged.value[questionId])
const toggleFlag = (questionId: number) => {
  const updated = { ...flagged.value }
  if (updated[questionId]) {
    delete updated[questionId]
  } else {
    updated[questionId] = true
  }
  flagged.value = updated
}

const isBookmarked = (questionId: number) => bookmarkStore.isBookmarked(questionId)

const isBookmarkLoading = (questionId: number) => Boolean(bookmarkBusy.value[questionId])

const toggleBookmark = async (questionId: number) => {
  if (!authStore.isAuthenticated) {
    router.push({ name: 'login', query: { redirect: route.fullPath } })
    return
  }
  bookmarkBusy.value = { ...bookmarkBusy.value, [questionId]: true }
  try {
    if (isBookmarked(questionId)) {
      await bookmarkStore.removeBookmark(questionId)
      showToast('Removed from bookmarks', 'success')
    } else {
      await bookmarkStore.addBookmark(questionId)
      showToast('Saved to bookmarks', 'success')
    }
  } catch (err: any) {
    const detail = err?.response?.data?.detail || 'Unable to update bookmark. Please try again.'
    showToast(detail, 'error')
  } finally {
    const updated = { ...bookmarkBusy.value }
    delete updated[questionId]
    bookmarkBusy.value = updated
  }
}
const navigationButtonClass = (questionId: number, index: number) => {
  const status = questionStatuses.value[questionId]
  const classes = [
    'flex h-10 w-10 items-center justify-center rounded-full border text-xs font-semibold transition',
  ]
  if (status === 'answered') {
    classes.push('bg-emerald-50 border-emerald-200 text-emerald-700')
  } else if (status === 'flagged') {
    classes.push('bg-amber-50 border-amber-300 text-amber-700')
  } else {
    classes.push('border-slate-200 text-slate-500 hover:border-slate-300 hover:text-slate-700')
  }
  if (currentIndex.value === index) {
    classes.push('ring-2 ring-slate-900/10')
  }
  return classes.join(' ')
}

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

  if (
    flaggedCount.value > 0 &&
    !window.confirm(
      flaggedCount.value === 1
        ? 'You have 1 flagged question. Submit anyway?'
        : `You have ${flaggedCount.value} flagged questions. Submit anyway?`
    )
  ) {
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
    flagged.value = {}
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
  flagged.value = {}
  hideToast()
})

watch(
  () => authStore.isAuthenticated,
  (isAuthenticated) => {
    if (isAuthenticated) {
      void bookmarkStore.ensureQuestionIdsLoaded(true)
    } else {
      bookmarkStore.reset()
    }
  },
  { immediate: true }
)
</script>

<template>
  <div class="space-y-6">
    <div
      v-if="toastVisible"
      class="flex items-center justify-between gap-3 rounded-full border px-4 py-2 text-sm font-semibold shadow-sm"
      :class="
        toastVariant === 'success'
          ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
          : 'border-red-200 bg-red-50 text-red-700'
      "
      role="status"
    >
      <span>{{ toastMessage }}</span>
      <button
        class="text-xs font-semibold uppercase tracking-wide text-current/70 transition hover:text-current"
        type="button"
        @click="hideToast"
      >
        Dismiss
      </button>
    </div>
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h1 class="text-2xl font-semibold">{{ quiz?.title || 'Quiz' }}</h1>
        <p class="text-sm text-gray-500">Answer every question and use the navigator to review flagged items.</p>
      </div>
      <div class="flex items-center gap-3">
        <button
          v-if="currentQuestion"
          class="inline-flex items-center gap-2 rounded-full border px-4 py-2 text-xs font-semibold transition"
          :class="
            isBookmarked(currentQuestion.id)
              ? 'border-blue-500 bg-blue-50 text-blue-700 shadow-sm'
              : 'border-blue-200 text-blue-600 hover:bg-blue-50'
          "
          type="button"
          :aria-pressed="isBookmarked(currentQuestion.id)"
          :disabled="isBookmarkLoading(currentQuestion.id)"
          @click="toggleBookmark(currentQuestion.id)"
        >
          <svg
            v-if="!isBookmarkLoading(currentQuestion.id)"
            class="h-4 w-4"
            viewBox="0 0 20 20"
            fill="currentColor"
            aria-hidden="true"
          >
            <path
              v-if="isBookmarked(currentQuestion.id)"
              d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118l-2.8-2.034c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
            />
            <path
              v-else
              fill-rule="evenodd"
              d="M10 3.22l-.97 2.988a1 1 0 01-.95.69H5.02l2.492 1.811a1 1 0 01.364 1.118l-.95 2.927L10 10.916l3.073 2.838-.95-2.927a1 1 0 01.364-1.118l2.492-1.81h-3.06a1 1 0 01-.951-.69L10 3.22z"
              clip-rule="evenodd"
            />
          </svg>
          <svg
            v-else
            class="h-4 w-4 animate-spin text-blue-600"
            viewBox="0 0 20 20"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
            aria-hidden="true"
          >
            <path
              d="M10 3.75a6.25 6.25 0 1 1-4.42 10.67"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
          <span>{{ isBookmarked(currentQuestion.id) ? 'Bookmarked' : 'Bookmark' }}</span>
        </button>
        <button
          v-if="currentQuestion"
          class="inline-flex items-center gap-2 rounded-full border border-amber-300 px-4 py-2 text-xs font-semibold text-amber-700 transition hover:bg-amber-50"
          type="button"
          @click="toggleFlag(currentQuestion.id)"
        >
          <span class="inline-flex h-2 w-2 rounded-full" :class="isFlagged(currentQuestion.id) ? 'bg-amber-500' : 'bg-amber-300'" />
          {{ isFlagged(currentQuestion.id) ? 'Flagged for review' : 'Flag question' }}
        </button>
        <div class="rounded-full bg-gray-900 px-4 py-2 text-sm font-semibold text-white">{{ formattedTimer }}</div>
      </div>
    </div>

    <div v-if="loading" class="space-y-4">
      <div class="h-6 w-2/5 animate-pulse rounded bg-gray-200"></div>
      <div class="h-32 animate-pulse rounded bg-gray-100"></div>
    </div>

    <p v-else-if="error" class="rounded border border-red-200 bg-red-50 p-4 text-sm text-red-700">{{ error }}</p>

    <div v-else-if="currentQuestion" class="grid gap-6 lg:grid-cols-[minmax(0,1fr),260px]">
      <section class="space-y-4">
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
      </section>

      <aside class="space-y-4">
        <div class="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
          <div class="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-gray-500">
            <span>Progress</span>
            <span class="text-gray-700">{{ progress }}%</span>
          </div>
          <div class="mt-3 h-2 w-full overflow-hidden rounded-full bg-gray-200">
            <div class="h-full rounded-full bg-emerald-500 transition-all" :style="{ width: `${progress}%` }"></div>
          </div>
          <p class="mt-3 text-xs text-gray-500">
            {{ answeredCount }} of {{ questions.length }} answered
            <span v-if="flaggedCount"> • {{ flaggedCount }} flagged</span>
          </p>
        </div>

        <div class="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
          <h2 class="text-sm font-semibold text-gray-900">Question navigator</h2>
          <div class="mt-4 grid grid-cols-5 gap-2">
            <button
              v-for="(question, index) in questions"
              :key="question.id"
              type="button"
              :class="navigationButtonClass(question.id, index)"
              @click="currentIndex = index"
            >
              {{ index + 1 }}
            </button>
          </div>
          <div class="mt-4 flex flex-wrap gap-3 text-[11px] text-gray-500">
            <span class="inline-flex items-center gap-1">
              <span class="h-2 w-2 rounded-full bg-emerald-500"></span>
              Answered
            </span>
            <span class="inline-flex items-center gap-1">
              <span class="h-2 w-2 rounded-full bg-amber-500"></span>
              Flagged
            </span>
            <span class="inline-flex items-center gap-1">
              <span class="h-2 w-2 rounded-full bg-gray-400"></span>
              Unanswered
            </span>
          </div>
        </div>
      </aside>
    </div>

    <p v-else class="text-sm text-gray-600">This quiz has no questions yet.</p>
  </div>
</template>
