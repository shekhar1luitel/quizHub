<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'

import { http } from '../../api/http'

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
  category_id: number
  category: {
    id: number
    name: string
    slug: string
  }
}

interface AdminCategory {
  id: number
  name: string
  slug: string
  description?: string | null
  icon?: string | null
}

const questions = ref<QuestionSummary[]>([])
const loading = ref(false)
const error = ref('')
const success = ref('')
const editingId = ref<number | null>(null)
const categories = ref<AdminCategory[]>([])
const categoriesLoading = ref(false)
const categoryError = ref('')
const searchTerm = ref('')

type StatusFilter = 'all' | 'active' | 'inactive'

const statusFilter = ref<StatusFilter>('all')
const statusOptions: Array<{ label: string; value: StatusFilter }> = [
  { label: 'All', value: 'all' },
  { label: 'Active', value: 'active' },
  { label: 'Inactive', value: 'inactive' },
]

const difficultyLevels = ['Easy', 'Medium', 'Hard'] as const
const difficultyLevelSet = new Set<string>(difficultyLevels)

const totalQuestions = computed(() => questions.value.length)
const activeQuestions = computed(() => questions.value.filter((question) => question.is_active).length)
const inactiveQuestions = computed(() => Math.max(totalQuestions.value - activeQuestions.value, 0))
const averageOptions = computed(() => {
  if (questions.value.length === 0) return 0
  const totalOptions = questions.value.reduce((acc, question) => acc + question.option_count, 0)
  return Math.round((totalOptions / questions.value.length) * 10) / 10
})
const usedCategoryCount = computed(() => new Set(questions.value.map((question) => question.category_id)).size)
const categoryCoveragePercent = computed(() => {
  if (categories.value.length === 0) return 0
  return Math.round((usedCategoryCount.value / categories.value.length) * 100)
})
const filteredQuestions = computed(() => {
  const term = searchTerm.value.trim().toLowerCase()
  return questions.value.filter((question) => {
    const matchesStatus =
      statusFilter.value === 'all' ||
      (statusFilter.value === 'active' && question.is_active) ||
      (statusFilter.value === 'inactive' && !question.is_active)
    const matchesSearch =
      !term ||
      question.prompt.toLowerCase().includes(term) ||
      question.category_name.toLowerCase().includes(term) ||
      question.subject?.toLowerCase().includes(term) ||
      question.difficulty?.toLowerCase().includes(term)
    return matchesStatus && matchesSearch
  })
})
const hasActiveFilters = computed(() => statusFilter.value !== 'all' || searchTerm.value.trim().length > 0)

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
  category_id: null as number | null,
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
  form.category_id = categories.value[0]?.id ?? null
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

const loadCategories = async () => {
  categoriesLoading.value = true
  categoryError.value = ''
  try {
    const { data } = await http.get<AdminCategory[]>('/categories')
    categories.value = data
    if (!form.category_id && data.length > 0) {
      form.category_id = data[0].id
    }
  } catch (err) {
    categoryError.value = 'Unable to load categories.'
    console.error(err)
  } finally {
    categoriesLoading.value = false
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
  if (!form.category_id) {
    error.value = 'Select a category for this question.'
    return
  }

  const payload = {
    prompt: form.prompt,
    explanation: form.explanation || null,
    subject: form.subject || null,
    difficulty: form.difficulty || null,
    is_active: form.is_active,
    options: trimmedOptions,
    category_id: form.category_id,
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
    form.category_id = data.category.id
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

const clearFilters = () => {
  searchTerm.value = ''
  statusFilter.value = 'all'
}

loadCategories().finally(() => {
  loadQuestions()
})
</script>

<template>
  <section class="space-y-10">
    <div class="relative overflow-hidden rounded-3xl border border-slate-200 bg-white text-slate-900 shadow-glow">
      <div class="absolute -top-20 right-12 h-48 w-48 rounded-full bg-brand-200/50 blur-3xl"></div>
      <div class="absolute -bottom-24 left-14 h-52 w-52 rounded-full bg-emerald-200/40 blur-3xl"></div>
      <div class="relative flex flex-col gap-6 px-8 py-10 lg:flex-row lg:items-center lg:justify-between">
        <div class="max-w-2xl space-y-4">
          <span class="inline-flex items-center gap-2 rounded-full bg-brand-50 px-4 py-1 text-xs font-semibold uppercase tracking-[0.35em] text-brand-600">
            Question studio
          </span>
          <div class="space-y-3">
            <h1 class="text-3xl font-semibold leading-snug md:text-4xl">Curate and polish your question bank</h1>
            <p class="text-sm text-slate-600">
              Manage prompts, refine explanations, and keep every quiz aligned with your latest syllabus updates.
            </p>
          </div>
        </div>
        <div class="flex flex-wrap items-center gap-3">
          <RouterLink
            :to="{ name: 'admin-categories' }"
            class="inline-flex items-center gap-2 rounded-full bg-brand-600 px-5 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-500"
          >
            <svg class="h-4 w-4" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3.5 4.5h13M4 10h12M5.5 15.5h9" />
            </svg>
            Manage categories
          </RouterLink>
          <button
            class="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-5 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-brand-300 hover:text-brand-600"
            type="button"
            @click="resetForm"
          >
            <svg class="h-4 w-4" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="M10 4.5v-2m0 2a5.5 5.5 0 1 1-5.5 5.5H2.5m15 0H15.5m0 0A5.5 5.5 0 1 1 10 4.5" />
            </svg>
            {{ editingId ? 'Cancel editing' : 'Reset form' }}
          </button>
        </div>
      </div>
    </div>

    <div class="grid gap-5 md:grid-cols-2 2xl:grid-cols-4">
      <article class="relative overflow-hidden rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200/70 transition hover:-translate-y-0.5 hover:shadow-lg">
        <div class="absolute -right-6 -top-6 h-20 w-20 rounded-full bg-brand-100/60 blur-2xl"></div>
        <div class="relative space-y-4">
          <div class="inline-flex items-center gap-3">
            <span class="inline-flex h-10 w-10 items-center justify-center rounded-2xl bg-brand-50 text-brand-600">
              <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4 7h16M4 12h10M4 17h7" />
              </svg>
            </span>
            <p class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">Total questions</p>
          </div>
          <p class="text-3xl font-semibold text-slate-900">{{ totalQuestions }}</p>
          <p class="text-xs text-slate-500">Expand coverage across every subject area.</p>
        </div>
      </article>
      <article class="relative overflow-hidden rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200/70 transition hover:-translate-y-0.5 hover:shadow-lg">
        <div class="absolute -right-6 -top-6 h-20 w-20 rounded-full bg-emerald-200/60 blur-2xl"></div>
        <div class="relative space-y-4">
          <div class="inline-flex items-center gap-3">
            <span class="inline-flex h-10 w-10 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600">
              <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </span>
            <p class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">Active questions</p>
          </div>
          <p class="text-3xl font-semibold text-slate-900">{{ activeQuestions }}</p>
          <p class="text-xs text-slate-500">Ready to appear in quizzes immediately.</p>
        </div>
      </article>
      <article class="relative overflow-hidden rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200/70 transition hover:-translate-y-0.5 hover:shadow-lg">
        <div class="absolute -right-6 -top-6 h-20 w-20 rounded-full bg-rose-200/50 blur-2xl"></div>
        <div class="relative space-y-4">
          <div class="inline-flex items-center gap-3">
            <span class="inline-flex h-10 w-10 items-center justify-center rounded-2xl bg-rose-50 text-rose-500">
              <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18l12-12M6 6l12 12" />
              </svg>
            </span>
            <p class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">Needs review</p>
          </div>
          <p class="text-3xl font-semibold text-slate-900">{{ inactiveQuestions }}</p>
          <p class="text-xs text-slate-500">Polish these drafts and publish when ready.</p>
        </div>
      </article>
      <article class="relative overflow-hidden rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-200/70 transition hover:-translate-y-0.5 hover:shadow-lg">
        <div class="absolute -right-6 -top-6 h-20 w-20 rounded-full bg-sky-200/60 blur-2xl"></div>
        <div class="relative space-y-4">
          <div class="inline-flex items-center gap-3">
            <span class="inline-flex h-10 w-10 items-center justify-center rounded-2xl bg-sky-50 text-sky-600">
              <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v4m0 10v4m7-7h-4M9 12H5m11.657-6.657l-2.829 2.829M9.172 14.828l-2.829 2.829M9.172 7.172 6.343 4.343m11.314 15.314-2.829-2.829" />
              </svg>
            </span>
            <p class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">Category coverage</p>
          </div>
          <p class="text-3xl font-semibold text-slate-900">{{ usedCategoryCount }}</p>
          <p class="text-xs text-slate-500">
            {{ categories.length ? `${categoryCoveragePercent}% of ${categories.length} categories` : 'Create a category to get started.' }}
          </p>
        </div>
      </article>
    </div>

    <div class="grid gap-6 xl:grid-cols-[1.3fr,1fr] 2xl:grid-cols-[1.5fr,1fr]">
      <form class="space-y-6 rounded-3xl border border-slate-200/80 bg-white/95 p-6 shadow-xl shadow-brand-900/5 backdrop-blur md:p-8" @submit.prevent="submit">
        <header class="space-y-1">
          <p class="text-xs font-semibold uppercase tracking-[0.35em] text-slate-400">{{ editingId ? 'Update question' : 'New question' }}</p>
          <h2 class="text-xl font-semibold text-slate-900">{{ editingId ? 'Edit question' : 'Create question' }}</h2>
          <p class="text-xs text-slate-500">
            Craft a clear prompt, highlight the right answer, and optionally add an explanation to reinforce learning.
          </p>
        </header>

        <div class="space-y-2">
          <label class="text-sm font-semibold text-slate-700" for="prompt">Prompt</label>
          <textarea
            id="prompt"
            v-model="form.prompt"
            class="min-h-[140px] w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm shadow-inner focus:border-brand-400 focus:outline-none focus:ring-4 focus:ring-brand-100"
            placeholder="Enter the question stem"
            required
          ></textarea>
        </div>

        <div class="space-y-2">
          <label class="text-sm font-semibold text-slate-700" for="explanation">Explanation</label>
          <textarea
            id="explanation"
            v-model="form.explanation"
            class="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm shadow-inner focus:border-brand-400 focus:outline-none focus:ring-4 focus:ring-brand-100"
            placeholder="Add reasoning or references (optional)"
          ></textarea>
        </div>

        <div class="space-y-3">
          <div class="flex items-center justify-between gap-3">
            <label class="text-sm font-semibold text-slate-700" for="category">Category</label>
            <RouterLink
              :to="{ name: 'admin-categories' }"
              class="text-xs font-semibold uppercase tracking-[0.3em] text-brand-600 transition hover:text-brand-500"
            >
              Manage
            </RouterLink>
          </div>
          <select
            id="category"
            v-model.number="form.category_id"
            :disabled="categoriesLoading || categories.length === 0"
            class="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm focus:border-brand-400 focus:outline-none focus:ring-4 focus:ring-brand-100 disabled:cursor-not-allowed disabled:opacity-60"
            required
          >
            <option value="" disabled>Select a category</option>
            <option v-for="category in categories" :key="category.id" :value="category.id">
              {{ category.name }}
            </option>
          </select>
          <p v-if="categoriesLoading" class="text-xs text-slate-400">Loading categories…</p>
          <p v-else-if="categoryError" class="text-xs text-rose-500">{{ categoryError }}</p>
          <p v-else-if="categories.length === 0" class="text-xs text-slate-500">
            Create a category before adding questions.
          </p>
        </div>

        <div class="grid gap-4 md:grid-cols-2">
          <div class="space-y-2">
            <label class="text-sm font-semibold text-slate-700" for="subject">Subject</label>
            <input
              id="subject"
              v-model="form.subject"
              class="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm focus:border-brand-400 focus:outline-none focus:ring-4 focus:ring-brand-100"
              placeholder="General Knowledge"
            />
          </div>
          <div class="space-y-2">
            <label class="text-sm font-semibold text-slate-700" for="difficulty">Difficulty</label>
            <select
              id="difficulty"
              v-model="form.difficulty"
              class="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm focus:border-brand-400 focus:outline-none focus:ring-4 focus:ring-brand-100"
            >
              <option value="">Not set</option>
              <option v-for="level in difficultyLevels" :key="level" :value="level">
                {{ level }}
              </option>
              <option v-if="form.difficulty && !difficultyLevelSet.has(form.difficulty)" :value="form.difficulty">
                {{ form.difficulty }}
              </option>
            </select>
          </div>
        </div>

        <div class="space-y-4">
          <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <p class="text-sm font-semibold text-slate-700">Options</p>
            <button
              class="inline-flex items-center gap-2 rounded-full bg-brand-50 px-4 py-2 text-xs font-semibold text-brand-600 transition hover:bg-brand-100"
              type="button"
              @click="addOption"
            >
              <svg class="h-4 w-4" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M10 4v12m6-6H4" />
              </svg>
              Add option
            </button>
          </div>
          <div class="space-y-3">
            <div
              v-for="(option, index) in form.options"
              :key="index"
              class="flex flex-col gap-3 rounded-2xl border border-slate-200 p-4 shadow-sm transition hover:border-brand-200 md:flex-row md:items-start md:gap-4"
            >
              <label class="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.35em] text-slate-500 md:w-32">
                <input
                  class="h-4 w-4 rounded border-slate-300 text-brand-600 focus:ring-brand-200"
                  name="correctOption"
                  type="radio"
                  :checked="option.is_correct"
                  @change="markCorrect(index)"
                />
                Correct
              </label>
              <textarea
                v-model="option.text"
                class="min-h-[80px] flex-1 rounded-2xl border border-slate-200 px-4 py-3 text-sm focus:border-brand-400 focus:outline-none focus:ring-4 focus:ring-brand-100"
                placeholder="Answer option"
                required
              ></textarea>
              <button
                class="self-end rounded-full border border-rose-200 px-4 py-2 text-xs font-semibold text-rose-500 transition hover:bg-rose-50"
                type="button"
                @click="removeOption(index)"
              >
                Remove
              </button>
            </div>
          </div>
        </div>

        <label class="flex items-center gap-3 rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-600">
          <input id="is-active" v-model="form.is_active" type="checkbox" class="h-4 w-4 rounded border-slate-300 text-brand-600 focus:ring-brand-200" />
          Question is active and can be used in quizzes
        </label>

        <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
          <button
            class="inline-flex w-full items-center justify-center rounded-full bg-brand-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-brand-900/20 transition hover:bg-brand-500 sm:w-auto"
            :class="{ 'cursor-not-allowed opacity-60': categories.length === 0 }"
            :disabled="categories.length === 0"
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

        <p v-if="error" class="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-600">{{ error }}</p>
        <p v-if="success" class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-600">{{ success }}</p>
      </form>

      <div class="rounded-3xl border border-slate-200/80 bg-white/95 p-6 shadow-xl shadow-brand-900/5 backdrop-blur md:p-7">
        <header class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 class="text-lg font-semibold text-slate-900">Question library</h2>
            <p class="text-xs text-slate-500">
              Showing {{ filteredQuestions.length }} of {{ totalQuestions }} questions • Avg options {{ averageOptions.toFixed(1) }}
            </p>
          </div>
          <span v-if="loading" class="inline-flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1 text-[11px] font-semibold text-slate-500">
            <span class="h-2 w-2 animate-pulse rounded-full bg-brand-500"></span>
            Syncing
          </span>
        </header>

        <div class="mt-5 space-y-4">
          <div class="flex flex-col gap-3 lg:flex-row lg:items-center">
            <div class="relative flex-1">
              <span class="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">
                <svg class="h-4 w-4" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" d="m13.5 13.5 3 3m-1.5-4.5A5.5 5.5 0 1 1 5 5a5.5 5.5 0 0 1 9.5 3.5Z" />
                </svg>
              </span>
              <input
                v-model="searchTerm"
                type="search"
                placeholder="Search question text, subject, or category…"
                class="w-full rounded-2xl border border-slate-200 bg-white px-10 py-3 text-sm focus:border-brand-400 focus:outline-none focus:ring-4 focus:ring-brand-100"
              />
            </div>
            <div class="flex flex-wrap items-center gap-2">
              <span class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-500">Status</span>
              <button
                v-for="option in statusOptions"
                :key="option.value"
                class="inline-flex items-center rounded-full px-4 py-2 text-xs font-semibold transition"
                :class="statusFilter === option.value ? 'bg-brand-600 text-white shadow-sm' : 'border border-slate-200 bg-white text-slate-600 hover:border-slate-300 hover:text-slate-900'"
                type="button"
                @click="statusFilter = option.value"
              >
                {{ option.label }}
              </button>
            </div>
          </div>
          <button
            v-if="hasActiveFilters"
            class="inline-flex items-center gap-2 rounded-full border border-slate-200 px-4 py-2 text-xs font-semibold text-slate-600 transition hover:border-slate-300 hover:text-slate-900"
            type="button"
            @click="clearFilters"
          >
            <svg class="h-4 w-4" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 6l8 8m0-8-8 8" />
            </svg>
            Clear filters
          </button>
        </div>

        <div class="mt-6 space-y-4 text-sm">
          <p v-if="loading" class="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-slate-500">Loading question bank…</p>
          <p
            v-else-if="questions.length === 0"
            class="rounded-2xl border border-slate-200 bg-slate-50 p-6 text-center text-slate-500"
          >
            No questions yet. Start by creating your first prompt on the left.
          </p>
          <p
            v-else-if="filteredQuestions.length === 0"
            class="rounded-2xl border border-amber-200 bg-amber-50 p-6 text-center text-amber-800"
          >
            Nothing matches your filters. Try adjusting the search or status.
          </p>
          <ul v-else class="space-y-4">
            <li
              v-for="question in filteredQuestions"
              :key="question.id"
              class="rounded-2xl border border-slate-200 p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-brand-200 hover:shadow-lg"
            >
              <div class="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                <div class="space-y-3">
                  <div class="flex flex-wrap items-center gap-2 text-xs">
                    <span class="inline-flex items-center gap-1 rounded-full bg-brand-50 px-3 py-1 font-semibold text-brand-600">
                      {{ question.category_name }}
                    </span>
                    <span class="inline-flex items-center gap-1 rounded-full bg-slate-100 px-3 py-1 font-semibold text-slate-600">
                      {{ question.subject || 'General' }}
                    </span>
                    <span class="inline-flex items-center gap-1 rounded-full bg-slate-100 px-3 py-1 font-semibold text-slate-600">
                      {{ question.difficulty || 'Unrated' }}
                    </span>
                  </div>
                  <p class="text-base font-semibold text-slate-900">{{ question.prompt }}</p>
                  <div class="flex flex-wrap items-center gap-2 text-xs text-slate-500">
                    <span class="inline-flex items-center gap-1 rounded-full bg-slate-100 px-3 py-1 font-medium">
                      <svg class="h-3.5 w-3.5" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M4 10h12m-6-6v12" />
                      </svg>
                      {{ question.option_count }} options
                    </span>
                    <span class="inline-flex items-center gap-1 rounded-full bg-slate-100 px-3 py-1 font-medium text-slate-500">
                      ID #{{ question.id }}
                    </span>
                  </div>
                </div>
                <div class="flex flex-col items-end gap-3">
                  <span
                    class="inline-flex items-center gap-2 rounded-full px-3 py-1 text-[11px] font-semibold"
                    :class="question.is_active ? 'bg-emerald-50 text-emerald-600' : 'bg-slate-100 text-slate-500'"
                  >
                    <span class="h-2 w-2 rounded-full" :class="question.is_active ? 'bg-emerald-500' : 'bg-slate-400'"></span>
                    {{ question.is_active ? 'Active' : 'Inactive' }}
                  </span>
                  <div class="flex items-center gap-2">
                    <button
                      class="inline-flex items-center gap-2 rounded-full border border-slate-200 px-4 py-2 text-xs font-semibold text-slate-700 transition hover:border-brand-300 hover:text-brand-600"
                      type="button"
                      @click="editQuestion(question.id)"
                    >
                      <svg class="h-4 w-4" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M4 13.5V16h2.5l8-8-2.5-2.5-8 8z" />
                        <path stroke-linecap="round" stroke-linejoin="round" d="M12.5 5.5 14.5 3.5 16.5 5.5 14.5 7.5z" />
                      </svg>
                      Edit
                    </button>
                    <button
                      class="inline-flex items-center gap-2 rounded-full border border-rose-200 px-4 py-2 text-xs font-semibold text-rose-500 transition hover:bg-rose-50"
                      type="button"
                      @click="deleteQuestion(question.id)"
                    >
                      <svg class="h-4 w-4" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M6 7h8m-6 2v5m4-5v5M5 7l1-2h8l1 2m-9 0h8l-.5 9h-7z" />
                      </svg>
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </section>
</template>
