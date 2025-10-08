<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { http } from '../../api/http'

interface QuestionSummary {
  id: number
  prompt: string
  subject?: string | null
  difficulty?: string | null
  is_active: boolean
  option_count: number
}

interface QuestionFormOption {
  id?: number
  text: string
  is_correct: boolean
}

interface QuestionDetail {
  id: number
  prompt: string
  explanation?: string | null
  subject?: string | null
  difficulty?: string | null
  is_active: boolean
  options: QuestionFormOption[]
}

const questions = ref<QuestionSummary[]>([])
const loading = ref(false)
const error = ref('')
const success = ref('')
const editingId = ref<number | null>(null)

const totalQuestions = computed(() => questions.value.length)
const activeQuestions = computed(() => questions.value.filter((question) => question.is_active).length)
const averageOptions = computed(() => {
  if (questions.value.length === 0) return 0
  const totalOptions = questions.value.reduce((acc, question) => acc + question.option_count, 0)
  return Math.round((totalOptions / questions.value.length) * 10) / 10
})

const form = reactive({
  prompt: '',
  explanation: '',
  subject: '',
  difficulty: '',
  is_active: true,
  options: [
    { text: '', is_correct: false },
    { text: '', is_correct: false },
  ] as QuestionFormOption[],
})

const resetForm = () => {
  form.prompt = ''
  form.explanation = ''
  form.subject = ''
  form.difficulty = ''
  form.is_active = true
  form.options = [
    { text: '', is_correct: false },
    { text: '', is_correct: false },
  ]
  editingId.value = null
  success.value = ''
  error.value = ''
}

const loadQuestions = async () => {
  loading.value = true
  error.value = ''
  try {
    const { data } = await http.get<QuestionSummary[]>('/questions')
    questions.value = data
  } catch (err) {
    error.value = 'Unable to load questions.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const ensureOptionCount = () => {
  if (form.options.length < 2) {
    form.options.push({ text: '', is_correct: false })
  }
}

const addOption = () => {
  form.options.push({ text: '', is_correct: false })
}

const removeOption = (index: number) => {
  form.options.splice(index, 1)
  ensureOptionCount()
}

const markCorrect = (index: number) => {
  form.options = form.options.map((option, i) => ({ ...option, is_correct: i === index }))
}

const submit = async () => {
  error.value = ''
  success.value = ''

  const trimmedOptions = form.options.filter((option) => option.text.trim().length > 0)
  if (trimmedOptions.length < 2) {
    error.value = 'Provide at least two options.'
    return
  }
  if (!trimmedOptions.some((option) => option.is_correct)) {
    error.value = 'Mark one option as the correct answer.'
    return
  }

  const payload = {
    prompt: form.prompt,
    explanation: form.explanation || null,
    subject: form.subject || null,
    difficulty: form.difficulty || null,
    is_active: form.is_active,
    options: trimmedOptions,
  }

  try {
    let message = 'Question created.'
    if (editingId.value) {
      await http.put(`/questions/${editingId.value}`, payload)
      message = 'Question updated.'
    } else {
      await http.post('/questions', payload)
    }
    await loadQuestions()
    resetForm()
    success.value = message
  } catch (err: any) {
    error.value = err?.response?.data?.detail || 'Save failed.'
  }
}

const editQuestion = async (id: number) => {
  error.value = ''
  success.value = ''
  try {
    const { data } = await http.get<QuestionDetail>(`/questions/${id}`)
    editingId.value = data.id
    form.prompt = data.prompt
    form.explanation = data.explanation || ''
    form.subject = data.subject || ''
    form.difficulty = data.difficulty || ''
    form.is_active = data.is_active
    form.options = data.options.map((option) => ({ ...option }))
    ensureOptionCount()
  } catch (err) {
    error.value = 'Unable to load question.'
  }
}

const deleteQuestion = async (id: number) => {
  if (!confirm('Delete this question?')) return
  try {
    await http.delete(`/questions/${id}`)
    if (editingId.value === id) {
      resetForm()
    }
    await loadQuestions()
  } catch (err) {
    error.value = 'Delete failed.'
  }
}

loadQuestions()
</script>

<template>
  <section class="space-y-10">
    <header class="space-y-3">
      <div class="inline-flex items-center gap-2 rounded-full bg-slate-100 px-4 py-1 text-xs font-semibold uppercase tracking-widest text-slate-600">
        Question bank
      </div>
      <div class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h1 class="text-3xl font-semibold text-slate-900">Manage your question repository</h1>
          <p class="max-w-2xl text-sm text-slate-500">
            Add rich explanations, maintain difficulty balance, and ensure every mock test is accurate and up-to-date.
          </p>
        </div>
        <button
          class="inline-flex items-center justify-center rounded-full border border-slate-200 px-6 py-2.5 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:text-slate-900"
          type="button"
          @click="resetForm"
        >
          {{ editingId ? 'Cancel editing' : 'Reset form' }}
        </button>
      </div>
    </header>

    <div class="grid gap-5 lg:grid-cols-3">
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Total questions</p>
        <p class="mt-3 text-3xl font-semibold text-slate-900">{{ totalQuestions }}</p>
        <p class="mt-2 text-xs text-slate-500">Keep expanding coverage for every subject.</p>
      </article>
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Active items</p>
        <p class="mt-3 text-3xl font-semibold text-slate-900">{{ activeQuestions }}</p>
        <p class="mt-2 text-xs text-slate-500">Review inactive questions to ensure relevance.</p>
      </article>
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Avg. options</p>
        <p class="mt-3 text-3xl font-semibold text-slate-900">{{ averageOptions.toFixed(1) }}</p>
        <p class="mt-2 text-xs text-slate-500">Aim for four diverse answer choices.</p>
      </article>
    </div>

    <div class="grid gap-6 xl:grid-cols-[1.2fr,1fr] 2xl:grid-cols-[1.4fr,1fr]">
      <form class="space-y-5 rounded-3xl border border-slate-200 bg-white/90 p-6 shadow-lg backdrop-blur" @submit.prevent="submit">
        <header class="flex flex-col gap-1">
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">{{ editingId ? 'Update question' : 'New question' }}</p>
          <h2 class="text-xl font-semibold text-slate-900">{{ editingId ? 'Edit question' : 'Create question' }}</h2>
        </header>
        <div class="space-y-2">
          <label class="text-sm font-semibold text-slate-700" for="prompt">Prompt</label>
          <textarea
            id="prompt"
            v-model="form.prompt"
            class="min-h-[140px] w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200"
            placeholder="Enter the question stem"
            required
          ></textarea>
        </div>
        <div class="space-y-2">
          <label class="text-sm font-semibold text-slate-700" for="explanation">Explanation</label>
          <textarea
            id="explanation"
            v-model="form.explanation"
            class="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200"
            placeholder="Add reasoning or references (optional)"
          ></textarea>
        </div>
        <div class="grid gap-4 md:grid-cols-2">
          <div class="space-y-2">
            <label class="text-sm font-semibold text-slate-700" for="subject">Subject</label>
            <input
              id="subject"
              v-model="form.subject"
              class="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200"
              placeholder="General Knowledge"
            />
          </div>
          <div class="space-y-2">
            <label class="text-sm font-semibold text-slate-700" for="difficulty">Difficulty</label>
            <input
              id="difficulty"
              v-model="form.difficulty"
              class="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200"
              placeholder="Easy / Medium / Hard"
            />
          </div>
        </div>
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <p class="text-sm font-semibold text-slate-700">Options</p>
            <button
              class="inline-flex items-center rounded-full border border-slate-200 px-3 py-1 text-xs font-semibold text-slate-600 transition hover:border-slate-300 hover:text-slate-900"
              type="button"
              @click="addOption"
            >
              Add option
            </button>
          </div>
          <div class="space-y-3">
            <div
              v-for="(option, index) in form.options"
              :key="index"
              class="flex flex-col gap-2 rounded-2xl border border-slate-200 p-4 md:flex-row md:items-start md:gap-4"
            >
              <label class="flex items-center gap-2 text-xs font-semibold uppercase tracking-widest text-slate-500 md:w-32">
                <input
                  class="h-4 w-4 rounded border-slate-300 text-slate-900 focus:ring-slate-200"
                  name="correctOption"
                  type="radio"
                  :checked="option.is_correct"
                  @change="markCorrect(index)"
                />
                Correct
              </label>
              <textarea
                v-model="option.text"
                class="min-h-[80px] flex-1 rounded-2xl border border-slate-200 px-4 py-3 text-sm focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200"
                placeholder="Answer option"
                required
              ></textarea>
              <button
                class="self-end rounded-full border border-red-200 px-3 py-1 text-xs font-semibold text-red-500 transition hover:bg-red-50"
                type="button"
                @click="removeOption(index)"
              >
                Remove
              </button>
            </div>
          </div>
        </div>
        <label class="flex items-center gap-2 text-sm text-slate-600">
          <input id="is-active" v-model="form.is_active" type="checkbox" class="h-4 w-4 rounded border-slate-300 text-slate-900 focus:ring-slate-200" />
          Question is active and can be used in quizzes
        </label>
        <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
          <button
            class="inline-flex w-full items-center justify-center rounded-full bg-emerald-500 px-6 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-400 sm:w-auto"
            type="submit"
          >
            {{ editingId ? 'Update question' : 'Create question' }}
          </button>
          <button
            class="inline-flex w-full items-center justify-center rounded-full border border-slate-200 px-6 py-3 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:text-slate-900 sm:w-auto"
            type="button"
            @click="resetForm"
          >
            Clear form
          </button>
        </div>
        <p v-if="error" class="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">{{ error }}</p>
        <p v-if="success" class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-600">{{ success }}</p>
      </form>

      <div class="rounded-3xl border border-slate-200 bg-white/90 p-6 shadow-lg backdrop-blur">
        <header class="flex items-center justify-between">
          <div>
            <h2 class="text-lg font-semibold text-slate-900">Existing questions</h2>
            <p class="text-xs text-slate-500">{{ totalQuestions }} items</p>
          </div>
          <span v-if="loading" class="text-xs text-slate-400">Refreshing…</span>
        </header>
        <p v-if="loading" class="mt-6 text-sm text-slate-500">Loading question bank…</p>
        <p v-else-if="questions.length === 0" class="mt-6 text-sm text-slate-500">No questions yet. Start by creating your first prompt.</p>
        <ul v-else class="mt-6 space-y-4 text-sm">
          <li
            v-for="question in questions"
            :key="question.id"
            class="rounded-2xl border border-slate-200 p-4 shadow-sm"
          >
            <div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
              <div class="space-y-1">
                <p class="font-semibold text-slate-900">{{ question.prompt }}</p>
                <p class="text-xs text-slate-500">
                  {{ question.subject || 'General' }} • {{ question.difficulty || 'Unrated' }} • {{ question.option_count }} options
                </p>
                <span
                  class="inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-[11px] font-semibold"
                  :class="question.is_active ? 'bg-emerald-50 text-emerald-600' : 'bg-slate-100 text-slate-500'"
                >
                  <span class="inline-flex h-2 w-2 rounded-full" :class="question.is_active ? 'bg-emerald-500' : 'bg-slate-400'"></span>
                  {{ question.is_active ? 'Active' : 'Inactive' }}
                </span>
              </div>
              <div class="flex items-center gap-3">
                <button
                  class="rounded-full border border-slate-200 px-4 py-2 text-xs font-semibold text-slate-700 transition hover:border-slate-300 hover:text-slate-900"
                  type="button"
                  @click="editQuestion(question.id)"
                >
                  Edit
                </button>
                <button
                  class="rounded-full border border-red-200 px-4 py-2 text-xs font-semibold text-red-500 transition hover:bg-red-50"
                  type="button"
                  @click="deleteQuestion(question.id)"
                >
                  Delete
                </button>
              </div>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </section>
</template>
