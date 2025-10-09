<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import { http } from '../../api/http'

interface QuizSummary {
  id: number
  title: string
  description?: string | null
  is_active: boolean
  question_count: number
}

interface QuizQuestionDetail {
  id: number
  prompt: string
  subject?: string | null
  difficulty?: string | null
}

interface QuizDetail {
  id: number
  title: string
  description?: string | null
  is_active: boolean
  questions: QuizQuestionDetail[]
}

interface QuestionSummary {
  id: number
  prompt: string
  subject?: string | null
  difficulty?: string | null
  is_active: boolean
  option_count: number
  category_id: number
  category_name: string
}

const quizzes = ref<QuizSummary[]>([])
const quizzesLoading = ref(false)
const quizzesError = ref('')

const questions = ref<QuestionSummary[]>([])
const questionsLoading = ref(false)
const questionsError = ref('')

const editingId = ref<number | null>(null)
const success = ref('')
const error = ref('')
const questionSearch = ref('')

const form = reactive({
  title: '',
  description: '',
  is_active: true,
  question_ids: [] as number[],
})

const filteredQuestions = computed(() => {
  const term = questionSearch.value.trim().toLowerCase()
  if (!term) return questions.value
  return questions.value.filter((question) => {
    const haystacks = [
      question.prompt,
      question.category_name,
      question.subject || '',
      question.difficulty || '',
    ]
    return haystacks.some((value) => value.toLowerCase().includes(term))
  })
})

const selectedQuestions = computed(() =>
  form.question_ids
    .map((id) => questions.value.find((question) => question.id === id))
    .filter((question): question is QuestionSummary => Boolean(question))
)

const totalActiveQuizzes = computed(() => quizzes.value.filter((quiz) => quiz.is_active).length)
const totalQuestionsSelected = computed(() => form.question_ids.length)
const RECENT_LIMIT = 5
const recentQuizzes = computed(() => quizzes.value.slice(0, RECENT_LIMIT))
const hasMoreQuizzes = computed(() => quizzes.value.length > recentQuizzes.value.length)

const route = useRoute()
const router = useRouter()

const resetForm = () => {
  form.title = ''
  form.description = ''
  form.is_active = true
  form.question_ids = []
  editingId.value = null
  success.value = ''
  error.value = ''
}

const loadQuizzes = async () => {
  quizzesLoading.value = true
  quizzesError.value = ''
  try {
    const { data } = await http.get<QuizSummary[]>('/quizzes')
    quizzes.value = data
  } catch (err) {
    quizzesError.value = 'Unable to load quizzes.'
    console.error(err)
  } finally {
    quizzesLoading.value = false
  }
}

const loadQuestions = async () => {
  questionsLoading.value = true
  questionsError.value = ''
  try {
    const { data } = await http.get<QuestionSummary[]>('/questions')
    questions.value = data
  } catch (err) {
    questionsError.value = 'Unable to load questions.'
    console.error(err)
  } finally {
    questionsLoading.value = false
  }
}

const addQuestion = (questionId: number) => {
  if (!form.question_ids.includes(questionId)) {
    form.question_ids = [...form.question_ids, questionId]
  }
}

const removeQuestion = (questionId: number) => {
  form.question_ids = form.question_ids.filter((id) => id !== questionId)
}

const moveQuestion = (questionId: number, direction: 'up' | 'down') => {
  const index = form.question_ids.indexOf(questionId)
  if (index === -1) return
  const swapWith = direction === 'up' ? index - 1 : index + 1
  if (swapWith < 0 || swapWith >= form.question_ids.length) return
  const next = [...form.question_ids]
  ;[next[index], next[swapWith]] = [next[swapWith], next[index]]
  form.question_ids = next
}

const submit = async () => {
  error.value = ''
  success.value = ''

  if (form.title.trim().length === 0) {
    error.value = 'Provide a title for the quiz.'
    return
  }
  if (form.question_ids.length === 0) {
    error.value = 'Select at least one question.'
    return
  }

  const payload = {
    title: form.title,
    description: form.description || null,
    is_active: form.is_active,
    question_ids: form.question_ids,
  }

  try {
    if (editingId.value) {
      await http.put(`/quizzes/${editingId.value}`, payload)
      success.value = 'Quiz updated.'
    } else {
      await http.post('/quizzes', payload)
      success.value = 'Quiz created.'
    }
    await loadQuizzes()
    resetForm()
  } catch (err: any) {
    error.value = err?.response?.data?.detail || 'Save failed.'
  }
}

const editQuiz = async (id: number) => {
  error.value = ''
  success.value = ''
  try {
    const { data } = await http.get<QuizDetail>(`/quizzes/${id}`)
    editingId.value = data.id
    form.title = data.title
    form.description = data.description || ''
    form.is_active = data.is_active
    form.question_ids = data.questions.map((question) => question.id)
  } catch (err) {
    error.value = 'Unable to load quiz.'
  }
}

const deleteQuiz = async (id: number) => {
  if (!window.confirm('Delete this quiz?')) return
  try {
    await http.delete(`/quizzes/${id}`)
    if (editingId.value === id) {
      resetForm()
    }
    await loadQuizzes()
  } catch (err) {
    error.value = 'Delete failed.'
  }
}

loadQuestions().finally(() => {
  loadQuizzes()
})

const clearEditQuery = () => {
  if (!('edit' in route.query)) return
  const { edit, ...rest } = route.query
  router.replace({
    name: (route.name as string | undefined) ?? 'admin-quizzes',
    params: route.params,
    query: rest,
  })
}

watch(
  () => route.query.edit,
  (value) => {
    if (!value) return
    const id = Number(value)
    if (Number.isNaN(id)) return
    editQuiz(id).finally(() => {
      clearEditQuery()
    })
  },
  { immediate: true }
)
</script>

<template>
  <section class="space-y-10">
    <div class="relative overflow-hidden rounded-3xl border border-slate-200 bg-white text-slate-900 shadow-glow">
      <div class="absolute -top-16 right-10 h-44 w-44 rounded-full bg-brand-200/50 blur-3xl"></div>
      <div class="absolute -bottom-24 left-12 h-48 w-48 rounded-full bg-indigo-200/40 blur-3xl"></div>
      <div class="relative flex flex-col gap-6 px-8 py-10 lg:flex-row lg:items-center lg:justify-between">
        <div class="max-w-2xl space-y-4">
          <span class="inline-flex items-center gap-2 rounded-full bg-brand-50 px-4 py-1 text-xs font-semibold uppercase tracking-[0.35em] text-brand-600">
            Quiz studio
          </span>
          <div class="space-y-3">
            <h1 class="text-3xl font-semibold leading-snug md:text-4xl">Launch polished mock tests</h1>
            <p class="text-sm text-slate-600">
              Combine curated questions into full-length quizzes that appear on the homepage and dashboard.
            </p>
          </div>
        </div>
        <div class="flex flex-wrap items-center gap-3">
          <RouterLink
            :to="{ name: 'admin-questions' }"
            class="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-5 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-brand-300 hover:text-brand-600"
          >
            Manage questions
          </RouterLink>
          <button
            class="inline-flex items-center gap-2 rounded-full bg-brand-600 px-5 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-500"
            type="button"
            @click="resetForm"
          >
            {{ editingId ? 'Cancel editing' : 'Reset form' }}
          </button>
        </div>
      </div>
    </div>

    <div class="grid gap-5 md:grid-cols-3">
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-[0.35em] text-slate-400">Total quizzes</p>
        <p class="mt-3 text-3xl font-semibold text-slate-900">{{ quizzes.length }}</p>
        <p class="text-xs text-slate-500">Across all categories and subjects.</p>
      </article>
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-[0.35em] text-slate-400">Active quizzes</p>
        <p class="mt-3 text-3xl font-semibold text-slate-900">{{ totalActiveQuizzes }}</p>
        <p class="text-xs text-slate-500">Visible to learners on the homepage.</p>
      </article>
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-[0.35em] text-slate-400">Questions selected</p>
        <p class="mt-3 text-3xl font-semibold text-slate-900">{{ totalQuestionsSelected }}</p>
        <p class="text-xs text-slate-500">In the quiz currently being edited.</p>
      </article>
    </div>

    <div class="grid gap-6 xl:grid-cols-[1.45fr,1fr] 2xl:grid-cols-[1.6fr,1fr]">
      <form class="space-y-6 rounded-3xl border border-slate-200/80 bg-white/95 p-6 shadow-xl shadow-brand-900/5 backdrop-blur md:p-8" @submit.prevent="submit">
        <header class="space-y-1">
          <p class="text-xs font-semibold uppercase tracking-[0.35em] text-slate-400">{{ editingId ? 'Update quiz' : 'New quiz' }}</p>
          <h2 class="text-xl font-semibold text-slate-900">{{ editingId ? 'Edit quiz' : 'Create quiz' }}</h2>
          <p class="text-xs text-slate-500">
            Pick a set of vetted questions, control visibility, and describe what learners can expect.
          </p>
        </header>

        <div class="space-y-2">
          <label class="text-sm font-semibold text-slate-700" for="quiz-title">Title</label>
          <input
            id="quiz-title"
            v-model="form.title"
            class="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm focus:border-brand-400 focus:outline-none focus:ring-4 focus:ring-brand-100"
            placeholder="Loksewa General Knowledge Mock Test"
            required
          />
        </div>

        <div class="space-y-2">
          <label class="text-sm font-semibold text-slate-700" for="quiz-description">Description</label>
          <textarea
            id="quiz-description"
            v-model="form.description"
            class="min-h-[120px] w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm focus:border-brand-400 focus:outline-none focus:ring-4 focus:ring-brand-100"
            placeholder="Outline the focus, timing, or key takeaways."
          ></textarea>
        </div>

        <div class="space-y-2">
          <label class="text-sm font-semibold text-slate-700">Selected questions</label>
          <div
            v-if="selectedQuestions.length === 0"
            class="rounded-2xl border border-dashed border-slate-200 bg-slate-50 px-4 py-6 text-center text-xs text-slate-500"
          >
            Pick questions from the bank below to build this quiz.
          </div>
          <ol v-else class="space-y-3">
            <li
              v-for="(question, index) in selectedQuestions"
              :key="question.id"
              class="flex flex-col gap-3 rounded-2xl border border-slate-200 p-4 shadow-sm md:flex-row md:items-start md:justify-between"
            >
              <div class="space-y-2">
                <p class="inline-flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.35em] text-slate-500">
                  <span class="flex h-6 w-6 items-center justify-center rounded-full bg-slate-900/90 text-[11px] text-white">
                    {{ index + 1 }}
                  </span>
                  {{ question.category_name }}
                </p>
                <p class="text-sm font-semibold text-slate-900">{{ question.prompt }}</p>
                <div class="flex flex-wrap items-center gap-2 text-[11px] font-medium uppercase tracking-[0.25em] text-slate-400">
                  <span>{{ question.subject || 'General' }}</span>
                  <span>•</span>
                  <span>{{ question.difficulty || 'Mixed' }}</span>
                </div>
              </div>
              <div class="flex items-center gap-2 self-end md:self-start">
                <button
                  class="inline-flex items-center gap-2 rounded-full border border-slate-200 px-3 py-1 text-xs font-semibold text-slate-700 transition hover:border-brand-300 hover:text-brand-600"
                  type="button"
                  :disabled="index === 0"
                  @click="moveQuestion(question.id, 'up')"
                >
                  ↑
                  <span class="sr-only">Move up</span>
                </button>
                <button
                  class="inline-flex items-center gap-2 rounded-full border border-slate-200 px-3 py-1 text-xs font-semibold text-slate-700 transition hover:border-brand-300 hover:text-brand-600"
                  type="button"
                  :disabled="index === selectedQuestions.length - 1"
                  @click="moveQuestion(question.id, 'down')"
                >
                  ↓
                  <span class="sr-only">Move down</span>
                </button>
                <button
                  class="inline-flex items-center gap-2 rounded-full border border-rose-200 px-3 py-1 text-xs font-semibold text-rose-500 transition hover:bg-rose-50"
                  type="button"
                  @click="removeQuestion(question.id)"
                >
                  Remove
                </button>
              </div>
            </li>
          </ol>
        </div>

        <div class="space-y-3 rounded-3xl border border-slate-200 bg-slate-50/80 p-4">
          <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
            <label class="text-sm font-semibold text-slate-700">Question bank</label>
            <input
              v-model="questionSearch"
              class="w-full rounded-2xl border border-slate-200 px-4 py-2 text-sm focus:border-brand-400 focus:outline-none focus:ring-4 focus:ring-brand-100 sm:w-72"
              placeholder="Search by prompt, category, or subject"
              type="search"
            />
          </div>
          <p v-if="questionsLoading" class="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-xs text-slate-500">Loading questions…</p>
          <p v-else-if="questionsError" class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-xs text-rose-600">
            {{ questionsError }}
          </p>
          <div v-else class="space-y-3">
            <article
              v-for="question in filteredQuestions"
              :key="question.id"
              class="flex flex-col gap-3 rounded-2xl border border-slate-200 bg-white p-4 text-sm shadow-sm transition hover:border-brand-200"
            >
              <div class="flex items-start justify-between gap-3">
                <div class="space-y-1">
                  <div class="flex flex-wrap items-center gap-2 text-[11px] font-semibold uppercase tracking-[0.3em] text-slate-400">
                    <span>{{ question.category_name }}</span>
                    <span>•</span>
                    <span>{{ question.subject || 'General' }}</span>
                    <span>•</span>
                    <span>{{ question.difficulty || 'Mixed' }}</span>
                  </div>
                  <p class="font-semibold text-slate-900">{{ question.prompt }}</p>
                </div>
                <span
                  class="inline-flex items-center gap-2 rounded-full px-3 py-1 text-[11px] font-semibold"
                  :class="question.is_active ? 'bg-emerald-50 text-emerald-600' : 'bg-slate-100 text-slate-500'"
                >
                  {{ question.is_active ? 'Active' : 'Inactive' }}
                </span>
              </div>
              <div class="flex items-center justify-between text-xs text-slate-500">
                <span>{{ question.option_count }} options</span>
                <div class="flex items-center gap-2">
                  <button
                    v-if="!form.question_ids.includes(question.id)"
                    class="inline-flex items-center gap-2 rounded-full bg-brand-50 px-3 py-1 text-xs font-semibold text-brand-600 transition hover:bg-brand-100"
                    type="button"
                    @click="addQuestion(question.id)"
                  >
                    Add
                  </button>
                  <button
                    v-else
                    class="inline-flex items-center gap-2 rounded-full border border-rose-200 px-3 py-1 text-xs font-semibold text-rose-500 transition hover:bg-rose-50"
                    type="button"
                    @click="removeQuestion(question.id)"
                  >
                    Remove
                  </button>
                </div>
              </div>
            </article>
            <p v-if="filteredQuestions.length === 0" class="rounded-2xl border border-slate-200 bg-white px-4 py-3 text-xs text-slate-500">
              Nothing matches your search.
            </p>
          </div>
        </div>

        <label class="flex items-center gap-3 rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-600">
          <input id="quiz-active" v-model="form.is_active" type="checkbox" class="h-4 w-4 rounded border-slate-300 text-brand-600 focus:ring-brand-200" />
          Quiz is active and visible to learners
        </label>

        <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
          <button
            class="inline-flex w-full items-center justify-center gap-2 rounded-full bg-brand-600 px-6 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-500 sm:w-auto"
            type="submit"
          >
            {{ editingId ? 'Save changes' : 'Create quiz' }}
          </button>
          <button
            class="inline-flex w-full items-center justify-center gap-2 rounded-full border border-slate-200 px-6 py-2 text-sm font-semibold text-slate-700 transition hover:border-brand-300 hover:text-brand-600 sm:w-auto"
            type="button"
            @click="resetForm"
          >
            Clear form
          </button>
        </div>

        <p v-if="success" class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-xs text-emerald-600">
          {{ success }}
        </p>
        <p v-else-if="error" class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-xs text-rose-600">
          {{ error }}
        </p>
      </form>

      <div class="space-y-4 rounded-3xl border border-slate-200 bg-white/95 p-6 shadow-xl shadow-brand-900/5">
        <header class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.35em] text-slate-400">Quiz activity</p>
            <h2 class="text-lg font-semibold text-slate-900">Recent quizzes</h2>
            <p class="text-xs text-slate-500">
              <span v-if="quizzes.length === 0">No quizzes created yet.</span>
              <span v-else>Showing {{ recentQuizzes.length }} of {{ quizzes.length }} quizzes</span>
            </p>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <RouterLink
              :to="{ name: 'admin-quiz-library' }"
              class="inline-flex items-center gap-2 rounded-full border border-slate-200 px-4 py-2 text-xs font-semibold text-slate-700 transition hover:border-brand-300 hover:text-brand-600"
            >
              View all quizzes
              <span aria-hidden="true">→</span>
            </RouterLink>
            <RouterLink
              :to="{ name: 'home', hash: '#quizzes' }"
              class="inline-flex items-center gap-2 rounded-full border border-slate-200 px-4 py-2 text-xs font-semibold text-slate-700 transition hover:border-brand-300 hover:text-brand-600"
            >
              Preview section
            </RouterLink>
          </div>
        </header>

        <p v-if="quizzesLoading" class="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-500">Loading quizzes…</p>
        <p v-else-if="quizzesError" class="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-600">{{ quizzesError }}</p>
        <p
          v-else-if="recentQuizzes.length === 0"
          class="rounded-2xl border border-slate-200 bg-slate-50 p-6 text-center text-sm text-slate-500"
        >
          No quizzes yet. Assemble one on the left to get started.
        </p>
        <ul v-else class="space-y-3">
          <li
            v-for="quiz in recentQuizzes"
            :key="quiz.id"
            class="rounded-2xl border border-slate-200 p-4 shadow-sm transition hover:-translate-y-0.5 hover:border-brand-200 hover:shadow-lg"
          >
            <div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
              <div class="space-y-2">
                <div class="flex flex-wrap items-center gap-2 text-xs">
                  <span class="inline-flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1 font-semibold text-slate-600">
                    {{ quiz.question_count }} questions
                  </span>
                </div>
                <p class="text-base font-semibold text-slate-900">{{ quiz.title }}</p>
                <p class="text-xs text-slate-500">
                  {{ quiz.description || 'No description provided yet.' }}
                </p>
              </div>
              <div class="flex items-center gap-2 self-end md:self-start">
                <span
                  class="inline-flex items-center gap-2 rounded-full px-3 py-1 text-[11px] font-semibold"
                  :class="quiz.is_active ? 'bg-emerald-50 text-emerald-600' : 'bg-slate-100 text-slate-500'"
                >
                  {{ quiz.is_active ? 'Active' : 'Inactive' }}
                </span>
                <button
                  class="inline-flex items-center gap-2 rounded-full border border-slate-200 px-4 py-2 text-xs font-semibold text-slate-700 transition hover:border-brand-300 hover:text-brand-600"
                  type="button"
                  @click="editQuiz(quiz.id)"
                >
                  Edit
                </button>
                <button
                  class="inline-flex items-center gap-2 rounded-full border border-rose-200 px-4 py-2 text-xs font-semibold text-rose-500 transition hover:bg-rose-50"
                  type="button"
                  @click="deleteQuiz(quiz.id)"
                >
                  Delete
                </button>
              </div>
            </div>
          </li>
        </ul>

        <p
          v-if="hasMoreQuizzes && !quizzesLoading"
          class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-xs text-slate-500"
        >
          Showing the latest {{ recentQuizzes.length }} quizzes. Visit the
          <RouterLink :to="{ name: 'admin-quiz-library' }" class="font-semibold text-brand-600 hover:text-brand-500">
            full quiz library
          </RouterLink>
          to manage the entire catalogue.
        </p>
      </div>
    </div>
  </section>
</template>
