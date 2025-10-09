<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import { http } from '../api/http'
import { useAuthStore } from '../stores/auth'

interface MemberResponse {
  total: number
}

interface CategorySummary {
  id: number
  name: string
  slug: string
  description?: string | null
  icon?: string | null
  organization_id?: number | null
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
  organization_id?: number | null
}

interface QuizSummary {
  id: number
  title: string
  description?: string | null
  is_active: boolean
  question_count: number
  organization_id?: number | null
}

const auth = useAuthStore()
const organization = computed(() => auth.user?.organization)

const loading = ref(true)
const error = ref('')

const memberCount = ref(0)
const categories = ref<CategorySummary[]>([])
const questions = ref<QuestionSummary[]>([])
const quizzes = ref<QuizSummary[]>([])

const activeQuizzes = computed(() => quizzes.value.filter((quiz) => quiz.is_active))
const inactiveQuizzes = computed(() => quizzes.value.filter((quiz) => !quiz.is_active))
const totalQuestions = computed(() => questions.value.length)
const totalActiveQuestions = computed(() => questions.value.filter((question) => question.is_active).length)

const orgName = computed(() => organization.value?.name ?? 'Your institution')
const orgSlug = computed(() => organization.value?.slug ?? '')

const loadSnapshot = async () => {
  if (!organization.value) {
    error.value = 'No organization assigned to this account.'
    loading.value = false
    return
  }

  loading.value = true
  error.value = ''
  const orgId = organization.value.id

  try {
    const [membersRes, categoriesRes, questionsRes, quizzesRes] = await Promise.all([
      http.get<MemberResponse>(`/organizations/${orgId}/members`, { params: { limit: 1 } }),
      http.get<CategorySummary[]>('/categories', { params: { organization_id: orgId } }),
      http.get<QuestionSummary[]>('/questions', { params: { organization_id: orgId } }),
      http.get<QuizSummary[]>('/quizzes', { params: { organization_id: orgId } }),
    ])

    memberCount.value = membersRes.data.total
    categories.value = categoriesRes.data
    questions.value = questionsRes.data
    quizzes.value = quizzesRes.data
  } catch (err) {
    console.error(err)
    error.value = 'Unable to load the institution dashboard right now.'
  } finally {
    loading.value = false
  }
}

onMounted(loadSnapshot)

const recentQuizzes = computed(() => quizzes.value.slice(0, 5))
const popularCategories = computed(() => categories.value.slice(0, 4))
</script>

<template>
  <section class="space-y-8">
    <header class="space-y-3">
      <div class="inline-flex items-center gap-2 rounded-full bg-emerald-50 px-4 py-1 text-xs font-semibold uppercase tracking-[0.35em] text-emerald-600">
        Institution Dashboard
      </div>
      <div class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h1 class="text-3xl font-semibold text-slate-900">
            {{ orgName }} overview
          </h1>
          <p class="text-sm text-slate-500">
            Manage your learners, question bank, and quiz lineup from a single command center.
          </p>
        </div>
        <RouterLink
          :to="{ name: 'settings' }"
          class="inline-flex items-center justify-center rounded-full border border-emerald-200 bg-emerald-50 px-5 py-2 text-sm font-semibold text-emerald-700 transition hover:border-emerald-300 hover:text-emerald-800"
        >
          Generate enrollment invite
        </RouterLink>
      </div>
    </header>

    <div v-if="loading" class="grid gap-5 lg:grid-cols-4">
      <div v-for="n in 4" :key="`org-dashboard-skeleton-${n}`" class="h-32 animate-pulse rounded-3xl bg-white/70"></div>
    </div>

    <p v-else-if="error" class="rounded-3xl border border-amber-200 bg-amber-50 p-5 text-sm text-amber-800">{{ error }}</p>

    <template v-else>
      <div class="grid gap-5 lg:grid-cols-4">
        <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Learners</p>
          <p class="mt-3 text-3xl font-semibold text-slate-900">{{ memberCount }}</p>
          <p class="text-xs text-slate-500">Active members enrolled in {{ orgName }}</p>
        </article>
        <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Quizzes</p>
          <p class="mt-3 text-3xl font-semibold text-slate-900">{{ quizzes.length }}</p>
          <p class="text-xs text-slate-500">{{ activeQuizzes.length }} active · {{ inactiveQuizzes.length }} draft</p>
        </article>
        <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Questions</p>
          <p class="mt-3 text-3xl font-semibold text-slate-900">{{ totalQuestions }}</p>
          <p class="text-xs text-slate-500">{{ totalActiveQuestions }} ready for quizzes</p>
        </article>
        <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Categories</p>
          <p class="mt-3 text-3xl font-semibold text-slate-900">{{ categories.length }}</p>
          <p class="text-xs text-slate-500">Organize topics for easy discovery</p>
        </article>
      </div>

      <div class="grid gap-6 lg:grid-cols-[3fr,2fr]">
        <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <header class="flex items-center justify-between">
            <div>
              <h2 class="text-lg font-semibold text-slate-900">Recent quizzes</h2>
              <p class="text-xs text-slate-500">Activate new practice sets as soon as they’re ready.</p>
            </div>
            <RouterLink
              :to="{ name: 'admin-quizzes' }"
              class="inline-flex items-center justify-center rounded-full border border-slate-200 px-4 py-2 text-xs font-semibold uppercase tracking-[0.25em] text-slate-600 transition hover:border-slate-300 hover:text-slate-900"
            >
              Manage quizzes
            </RouterLink>
          </header>
          <div v-if="recentQuizzes.length === 0" class="mt-6 rounded-2xl border border-dashed border-slate-200 p-6 text-sm text-slate-500">
            No quizzes yet. Build your first mock test to get learners started.
          </div>
          <ul v-else class="mt-6 space-y-3">
            <li
              v-for="quiz in recentQuizzes"
              :key="quiz.id"
              class="flex items-center justify-between rounded-2xl border border-slate-200 px-4 py-3"
            >
              <div>
                <p class="font-semibold text-slate-900">{{ quiz.title }}</p>
                <p class="text-xs text-slate-500">{{ quiz.question_count }} questions · {{ quiz.is_active ? 'Active' : 'Draft' }}</p>
              </div>
              <RouterLink
                :to="{ name: 'quiz', params: { id: quiz.id } }"
                class="rounded-full bg-slate-900 px-3 py-1 text-xs font-semibold text-white shadow-sm transition hover:bg-slate-700"
              >
                Preview
              </RouterLink>
            </li>
          </ul>
        </section>

        <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <header class="flex items-center justify-between">
            <div>
              <h2 class="text-lg font-semibold text-slate-900">Team & enrollment</h2>
              <p class="text-xs text-slate-500">Invite instructors and track learner growth.</p>
            </div>
          </header>
          <div class="mt-4 space-y-3 text-sm text-slate-600">
            <p>Share your enrollment QR code or token from Settings to onboard new learners instantly.</p>
            <p>Encourage instructors to keep question banks fresh by rotating topics weekly.</p>
            <RouterLink
              :to="{ name: 'admin-organization-members', params: { id: organization?.id ?? 0 } }"
              class="inline-flex items-center justify-center rounded-full border border-slate-200 px-4 py-2 text-xs font-semibold uppercase tracking-[0.25em] text-slate-600 transition hover:border-slate-300 hover:text-slate-900"
            >
              View members
            </RouterLink>
          </div>
        </section>
      </div>

      <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <header class="flex items-center justify-between">
          <div>
            <h2 class="text-lg font-semibold text-slate-900">Categories at a glance</h2>
            <p class="text-xs text-slate-500">Highlight subjects to plan your next quiz.</p>
          </div>
          <RouterLink
            :to="{ name: 'admin-categories' }"
            class="inline-flex items-center justify-center rounded-full border border-slate-200 px-4 py-2 text-xs font-semibold uppercase tracking-[0.25em] text-slate-600 transition hover:border-slate-300 hover:text-slate-900"
          >
            Manage categories
          </RouterLink>
        </header>
        <div class="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <article
            v-for="category in popularCategories"
            :key="category.id"
            class="flex h-full flex-col justify-between rounded-2xl border border-slate-200 bg-slate-50/80 p-4"
          >
            <div class="space-y-1">
              <p class="text-sm font-semibold text-slate-900">{{ category.name }}</p>
              <p class="text-xs text-slate-500">{{ category.description || 'Add a description to inspire learners.' }}</p>
            </div>
            <RouterLink
              :to="{ name: 'admin-questions', query: { category: category.slug } }"
              class="mt-4 inline-flex items-center gap-2 text-xs font-semibold text-emerald-600 transition hover:text-emerald-500"
            >
              Add question
              <span aria-hidden="true">→</span>
            </RouterLink>
          </article>
          <div v-if="popularCategories.length === 0" class="col-span-full rounded-2xl border border-dashed border-slate-200 p-6 text-center text-sm text-slate-500">
            No categories yet. Create a subject track to get started.
          </div>
        </div>
      </section>
    </template>
  </section>
</template>
