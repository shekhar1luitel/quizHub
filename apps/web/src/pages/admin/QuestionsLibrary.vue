<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

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

const router = useRouter()

const questions = ref<QuestionSummary[]>([])
const loading = ref(false)
const error = ref('')
const searchTerm = ref('')

type StatusFilter = 'all' | 'active' | 'inactive'
const statusFilter = ref<StatusFilter>('all')
const statusOptions: StatusFilter[] = ['all', 'active', 'inactive']

const totalQuestions = computed(() => questions.value.length)
const activeQuestions = computed(() => questions.value.filter((item) => item.is_active).length)
const inactiveQuestions = computed(() => Math.max(totalQuestions.value - activeQuestions.value, 0))
const averageOptions = computed(() => {
  if (questions.value.length === 0) return 0
  const totalOptions = questions.value.reduce((acc, question) => acc + question.option_count, 0)
  return Math.round((totalOptions / questions.value.length) * 10) / 10
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

const clearFilters = () => {
  searchTerm.value = ''
  statusFilter.value = 'all'
}

const deleteQuestion = async (id: number) => {
  if (!window.confirm('Delete this question?')) return
  try {
    await http.delete(`/questions/${id}`)
    await loadQuestions()
  } catch (err: any) {
    error.value = err?.response?.data?.detail || 'Delete failed.'
  }
}

const editQuestion = (id: number) => {
  router.push({ name: 'admin-questions', query: { edit: id } })
}

loadQuestions()
</script>

<template>
  <section class="space-y-10">
    <header class="space-y-4">
      <div class="inline-flex items-center gap-2 rounded-full bg-slate-100 px-4 py-1 text-xs font-semibold uppercase tracking-widest text-slate-600">
        Question library
      </div>
      <div class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h1 class="text-3xl font-semibold text-slate-900">Explore every question</h1>
          <p class="max-w-2xl text-sm text-slate-500">
            Search, filter, and manage the full question bank. Use this view to audit quality and spot coverage gaps.
          </p>
        </div>
        <div class="flex flex-wrap items-center gap-3">
          <RouterLink
            :to="{ name: 'admin-questions' }"
            class="inline-flex items-center gap-2 rounded-full bg-brand-600 px-5 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-500"
          >
            Add new question
          </RouterLink>
          <button
            class="inline-flex items-center gap-2 rounded-full border border-slate-200 px-5 py-2 text-sm font-semibold text-slate-700 transition hover:border-brand-300 hover:text-brand-600"
            type="button"
            @click="loadQuestions"
          >
            <svg class="h-4 w-4" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v4h4M16 16v-4h-4M5 15a7 7 0 0 0 10-10" />
            </svg>
            Refresh
          </button>
        </div>
      </div>
    </header>

    <div class="grid gap-5 md:grid-cols-3">
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">Total questions</p>
        <p class="mt-3 text-3xl font-semibold text-slate-900">{{ totalQuestions }}</p>
        <p class="text-xs text-slate-500">All questions currently available in the bank.</p>
      </article>
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">Active</p>
        <p class="mt-3 text-3xl font-semibold text-slate-900">{{ activeQuestions }}</p>
        <p class="text-xs text-slate-500">Ready to be served in quizzes · {{ inactiveQuestions }} inactive</p>
      </article>
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">Average options</p>
        <p class="mt-3 text-3xl font-semibold text-slate-900">{{ averageOptions.toFixed(1) }}</p>
        <p class="text-xs text-slate-500">Maintain consistency for learner expectations.</p>
      </article>
    </div>

    <div class="rounded-3xl border border-slate-200 bg-white/95 p-6 shadow-xl shadow-brand-900/5 backdrop-blur md:p-8">
      <header class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h2 class="text-lg font-semibold text-slate-900">Question bank</h2>
          <p class="text-xs text-slate-500">
            {{ filteredQuestions.length }} results
            <span v-if="hasActiveFilters" class="text-slate-400"> · Filters active</span>
          </p>
        </div>
        <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
          <div class="relative flex-1 sm:w-72">
            <span class="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">
              <svg class="h-4 w-4" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="m13.5 13.5 3 3m-1.5-4.5A5.5 5.5 0 1 1 5 5a5.5 5.5 0 0 1 9.5 3.5Z" />
              </svg>
            </span>
            <input
              v-model="searchTerm"
              type="search"
              placeholder="Search text, subject, difficulty, or category"
              class="w-full rounded-2xl border border-slate-200 bg-white px-10 py-3 text-sm focus:border-brand-400 focus:outline-none focus:ring-4 focus:ring-brand-100"
            />
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-500">Status</span>
            <button
              v-for="option in statusOptions"
              :key="option"
              class="inline-flex items-center rounded-full px-4 py-2 text-xs font-semibold transition"
              :class="statusFilter === option ? 'bg-brand-600 text-white shadow-sm' : 'border border-slate-200 bg-white text-slate-600 hover:border-slate-300 hover:text-slate-900'"
              type="button"
              @click="statusFilter = option"
            >
              {{ option.charAt(0).toUpperCase() + option.slice(1) }}
            </button>
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
            Clear
          </button>
        </div>
      </header>

      <div class="mt-6 space-y-4 text-sm">
        <p v-if="loading" class="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-slate-500">Loading questions…</p>
        <p v-else-if="error" class="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-rose-600">{{ error }}</p>
        <p v-else-if="filteredQuestions.length === 0" class="rounded-2xl border border-amber-200 bg-amber-50 p-6 text-center text-amber-800">
          No questions match your filters yet.
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
  </section>
</template>
