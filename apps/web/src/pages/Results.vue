<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { http } from '../api/http'
import { useAuthStore } from '../stores/auth'
import { useBookmarkStore } from '../stores/bookmarks'

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
const bookmarkStore = useBookmarkStore()
const authStore = useAuthStore()
const bookmarkBusy = ref<Record<number, boolean>>({})
const toastVisible = ref(false)
const toastMessage = ref('')
const toastVariant = ref<'success' | 'error'>('success')
let toastTimeout: number | null = null

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

const isBookmarked = (questionId: number) => bookmarkStore.isBookmarked(questionId)

const isBookmarkLoading = (questionId: number) => Boolean(bookmarkBusy.value[questionId])

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

const toggleBookmark = async (questionId: number) => {
  if (!authStore.isAuthenticated) {
    showToast('Login to manage bookmarks', 'error')
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

onMounted(fetchResult)

onUnmounted(() => {
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
          <div class="flex flex-wrap items-center justify-between gap-3">
            <h3 class="text-base font-semibold text-gray-900">{{ answer.prompt }}</h3>
            <div class="flex items-center gap-2">
              <button
                class="inline-flex items-center gap-1 rounded-full border px-3 py-1 text-[11px] font-semibold transition"
                :class="
                  isBookmarked(answer.question_id)
                    ? 'border-blue-500 bg-blue-50 text-blue-700 shadow-sm'
                    : 'border-blue-200 text-blue-600 hover:bg-blue-50'
                "
                type="button"
                :aria-pressed="isBookmarked(answer.question_id)"
                :disabled="isBookmarkLoading(answer.question_id)"
                @click="toggleBookmark(answer.question_id)"
              >
                <svg
                  v-if="!isBookmarkLoading(answer.question_id)"
                  class="h-4 w-4"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                  aria-hidden="true"
                >
                  <path
                    v-if="isBookmarked(answer.question_id)"
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
                  <path d="M10 3.75a6.25 6.25 0 1 1-4.42 10.67" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
                <span>{{ isBookmarked(answer.question_id) ? 'Bookmarked' : 'Bookmark' }}</span>
              </button>
              <span
                class="rounded-full px-3 py-1 text-xs font-semibold"
                :class="answer.is_correct ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'"
              >
                {{ answer.is_correct ? 'Correct' : 'Incorrect' }}
              </span>
            </div>
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
