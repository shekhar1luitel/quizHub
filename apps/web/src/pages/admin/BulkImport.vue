<script setup lang="ts">
import { computed, reactive, ref, type Ref } from 'vue'
import { http } from '../../api/http'

interface PreviewCategory {
  source_row: number | null
  name: string
  description: string | null
  icon: string | null
  slug: string
  action: 'create' | 'update'
  errors: string[]
}

interface PreviewQuiz {
  source_row: number | null
  title: string
  description: string | null
  is_active: boolean
  question_prompts: string[]
  action: 'create' | 'update'
  errors: string[]
}

interface PreviewQuestionOption {
  text: string
  is_correct: boolean
}

interface PreviewQuestion {
  source_row: number | null
  prompt: string
  explanation: string | null
  subject: string | null
  difficulty: string | null
  is_active: boolean
  category_name: string
  quiz_titles: string[]
  options: PreviewQuestionOption[]
  action: 'create' | 'update'
  errors: string[]
}

interface PreviewResponse {
  categories: PreviewCategory[]
  quizzes: PreviewQuiz[]
  questions: PreviewQuestion[]
  warnings: string[]
}

interface BulkImportResult {
  categories_created: number
  categories_updated: number
  quizzes_created: number
  quizzes_updated: number
  questions_created: number
  questions_updated: number
}

interface CategoryForm {
  name: string
  description: string
  icon: string
}

interface QuizForm {
  title: string
  description: string
  is_active: boolean
  questionPromptsText: string
}

interface QuestionOptionForm {
  text: string
  is_correct: boolean
}

interface QuestionForm {
  prompt: string
  explanation: string
  subject: string
  difficulty: string
  is_active: boolean
  category_name: string
  quizTitlesText: string
  options: QuestionOptionForm[]
}

const fileInput = ref<HTMLInputElement | null>(null)
const loading = ref(false)
const preview = ref<PreviewResponse | null>(null)
const form = reactive({
  categories: [] as CategoryForm[],
  quizzes: [] as QuizForm[],
  questions: [] as QuestionForm[],
})
const uploadError = ref('')
const commitError = ref('')
const commitSuccess = ref('')
const result = ref<BulkImportResult | null>(null)
const committing = ref(false)
const downloadError = ref('')
const downloadingTemplate = ref(false)
const downloadingExport = ref(false)

const hasPreview = computed(() => preview.value !== null)

const totalPendingCreates = computed(() => {
  if (!preview.value) return 0
  return [
    preview.value.categories.filter((category) => category.action === 'create').length,
    preview.value.quizzes.filter((quiz) => quiz.action === 'create').length,
    preview.value.questions.filter((question) => question.action === 'create').length,
  ].reduce((acc, count) => acc + count, 0)
})

const uploadHint = `Prepare a single Excel workbook (.xlsx) with sheets named “Categories”, “Quizzes”, and “Questions”.
Use headers “Name/Description/Icon” for categories, “Title/Description/Is Active/Questions” for quizzes, and include
columns for “Prompt, Explanation, Subject, Difficulty, Category, Option 1..n, Correct Option, Quizzes” for questions.`

const hasRowErrors = computed(() => {
  if (!preview.value) return false
  return (
    preview.value.categories.some((category) => category.errors.length > 0) ||
    preview.value.quizzes.some((quiz) => quiz.errors.length > 0) ||
    preview.value.questions.some((question) => question.errors.length > 0)
  )
})

const pickFile = () => {
  commitError.value = ''
  commitSuccess.value = ''
  result.value = null
  downloadError.value = ''
  fileInput.value?.click()
}

const formatWarnings = computed(() => preview.value?.warnings ?? [])

const resetForm = () => {
  form.categories = []
  form.quizzes = []
  form.questions = []
}

const prepareForm = (data: PreviewResponse) => {
  resetForm()
  form.categories = data.categories.map((category) => ({
    name: category.name,
    description: category.description ?? '',
    icon: category.icon ?? '',
  }))
  form.quizzes = data.quizzes.map((quiz) => ({
    title: quiz.title,
    description: quiz.description ?? '',
    is_active: quiz.is_active,
    questionPromptsText: quiz.question_prompts.join(', '),
  }))
  form.questions = data.questions.map((question) => ({
    prompt: question.prompt,
    explanation: question.explanation ?? '',
    subject: question.subject ?? '',
    difficulty: question.difficulty ?? '',
    is_active: question.is_active,
    category_name: question.category_name,
    quizTitlesText: question.quiz_titles.join(', '),
    options: question.options.map((option) => ({ ...option })),
  }))
}

const handleFileChange = async (event: Event) => {
  const target = event.target as HTMLInputElement | null
  if (!target?.files?.length) return
  const file = target.files[0]
  uploadError.value = ''
  commitError.value = ''
  commitSuccess.value = ''
  result.value = null

  const formData = new FormData()
  formData.append('file', file)

  loading.value = true
  try {
    const { data } = await http.post<PreviewResponse>('/admin/bulk-import/preview', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    preview.value = data
    prepareForm(data)
  } catch (error: any) {
    uploadError.value = error?.response?.data?.detail || 'Unable to read the workbook.'
    preview.value = null
    resetForm()
  } finally {
    loading.value = false
    if (target) {
      target.value = ''
    }
  }
}

const markCorrectOption = (questionIndex: number, optionIndex: number) => {
  const question = form.questions[questionIndex]
  question.options = question.options.map((option, index) => ({
    ...option,
    is_correct: index === optionIndex,
  }))
}

const addOption = (questionIndex: number) => {
  form.questions[questionIndex].options.push({ text: '', is_correct: false })
}

const removeOption = (questionIndex: number, optionIndex: number) => {
  const options = form.questions[questionIndex].options
  if (options.length <= 2) return
  options.splice(optionIndex, 1)
}

const splitList = (value: string) =>
  value
    .split(',')
    .map((item) => item.trim())
    .filter((item) => item.length > 0)

const commitImport = async () => {
  if (!preview.value) return
  committing.value = true
  commitError.value = ''
  commitSuccess.value = ''
  result.value = null

  const payload = {
    categories: form.categories.map((category) => ({
      name: category.name,
      description: category.description || null,
      icon: category.icon || null,
    })),
    quizzes: form.quizzes.map((quiz) => ({
      title: quiz.title,
      description: quiz.description || null,
      is_active: quiz.is_active,
      question_prompts: splitList(quiz.questionPromptsText),
    })),
    questions: form.questions.map((question) => ({
      prompt: question.prompt,
      explanation: question.explanation || null,
      subject: question.subject || null,
      difficulty: question.difficulty || null,
      is_active: question.is_active,
      category_name: question.category_name,
      quiz_titles: splitList(question.quizTitlesText),
      options: question.options.map((option) => ({
        text: option.text,
        is_correct: option.is_correct,
      })),
    })),
  }

  try {
    const { data } = await http.post<BulkImportResult>('/admin/bulk-import/commit', payload)
    result.value = data
    commitSuccess.value = `Import complete. ${data.questions_created + data.questions_updated} questions processed.`
  } catch (error: any) {
    commitError.value = error?.response?.data?.detail || 'Import failed. Review the data and try again.'
  } finally {
    committing.value = false
  }
}

const pendingSummary = computed(() => {
  if (!preview.value) return []
  return [
    {
      label: 'Categories',
      create: preview.value.categories.filter((item) => item.action === 'create').length,
      update: preview.value.categories.filter((item) => item.action === 'update').length,
    },
    {
      label: 'Quizzes',
      create: preview.value.quizzes.filter((item) => item.action === 'create').length,
      update: preview.value.quizzes.filter((item) => item.action === 'update').length,
    },
    {
      label: 'Questions',
      create: preview.value.questions.filter((item) => item.action === 'create').length,
      update: preview.value.questions.filter((item) => item.action === 'update').length,
    },
  ]
})

const hasData = computed(() =>
  form.categories.length + form.quizzes.length + form.questions.length > 0
)

const categoryEntries = computed(() =>
  form.categories.map((category, index) => ({
    form: category,
    meta: preview.value?.categories[index] ?? null,
    index,
  }))
)

const quizEntries = computed(() =>
  form.quizzes.map((quiz, index) => ({
    form: quiz,
    meta: preview.value?.quizzes[index] ?? null,
    index,
  }))
)

const questionEntries = computed(() =>
  form.questions.map((question, index) => ({
    form: question,
    meta: preview.value?.questions[index] ?? null,
    index,
  }))
)

const discardCategory = (index: number) => {
  form.categories.splice(index, 1)
  if (preview.value) {
    preview.value.categories.splice(index, 1)
  }
}

const discardQuiz = (index: number) => {
  form.quizzes.splice(index, 1)
  if (preview.value) {
    preview.value.quizzes.splice(index, 1)
  }
}

const discardQuestion = (index: number) => {
  form.questions.splice(index, 1)
  if (preview.value) {
    preview.value.questions.splice(index, 1)
  }
}

const downloadWorkbook = async (path: string, filename: string, state: Ref<boolean>) => {
  downloadError.value = ''
  state.value = true
  try {
    const { data } = await http.get(path, { responseType: 'blob' })
    const blobUrl = window.URL.createObjectURL(data as Blob)
    const link = document.createElement('a')
    link.href = blobUrl
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(blobUrl)
  } catch (error: any) {
    downloadError.value = error?.response?.data?.detail || 'Download failed. Please try again.'
  } finally {
    state.value = false
  }
}

const downloadTemplate = () =>
  downloadWorkbook('/admin/bulk-import/template', 'bulk-import-template.xlsx', downloadingTemplate)

const downloadExport = () =>
  downloadWorkbook('/admin/bulk-import/export', 'bulk-import-export.xlsx', downloadingExport)
</script>

<template>
  <section class="space-y-8">
    <header class="space-y-2">
      <h1 class="text-3xl font-semibold text-slate-900">Bulk content importer</h1>
      <p class="max-w-3xl text-sm text-slate-500">
        Upload a structured Excel workbook to create or update categories, questions, and quizzes in one
        step. Preview the detected changes, adjust the values inline, then publish everything together.
      </p>
    </header>

    <div class="grid gap-8 lg:grid-cols-[280px,1fr]">
      <aside class="space-y-4">
        <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 class="text-lg font-semibold text-slate-900">Import tools</h2>
          <p class="mt-2 text-sm text-slate-500">
            Download a starter workbook or export the latest library to make bulk edits in one place.
          </p>
          <div class="mt-4 space-y-3">
            <button
              type="button"
              class="w-full rounded-full border border-slate-200 px-5 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:text-slate-900 disabled:cursor-not-allowed disabled:border-slate-200 disabled:text-slate-400"
              :disabled="downloadingTemplate"
              @click="downloadTemplate"
            >
              {{ downloadingTemplate ? 'Preparing template…' : 'Download template' }}
            </button>
            <button
              type="button"
              class="w-full rounded-full border border-slate-200 px-5 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:text-slate-900 disabled:cursor-not-allowed disabled:border-slate-200 disabled:text-slate-400"
              :disabled="downloadingExport"
              @click="downloadExport"
            >
              {{ downloadingExport ? 'Collecting data…' : 'Download current data' }}
            </button>
          </div>
          <p v-if="downloadError" class="mt-4 rounded-2xl border border-rose-200 bg-rose-50 p-3 text-xs text-rose-600">
            {{ downloadError }}
          </p>
        </section>
        <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <h2 class="text-lg font-semibold text-slate-900">Workbook format</h2>
          <p class="mt-2 text-sm text-slate-500">Each sheet follows a simple column layout:</p>
          <ul class="mt-4 space-y-3 text-xs text-slate-600">
            <li class="rounded-2xl bg-slate-50 px-4 py-3">
              <p class="font-semibold text-slate-800">Categories</p>
              <p>Name · Description · Icon</p>
            </li>
            <li class="rounded-2xl bg-slate-50 px-4 py-3">
              <p class="font-semibold text-slate-800">Quizzes</p>
              <p>Title · Description · Is Active · Questions</p>
            </li>
            <li class="rounded-2xl bg-slate-50 px-4 py-3">
              <p class="font-semibold text-slate-800">Questions</p>
              <p>
                Prompt · Explanation · Subject · Difficulty · Is Active · Category · Option 1..n · Correct Option · Quizzes
              </p>
            </li>
          </ul>
        </section>
      </aside>

      <div class="space-y-8">
        <section class="rounded-3xl border border-dashed border-slate-300 bg-white/60 p-6">
          <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div class="space-y-2">
              <h2 class="text-lg font-semibold text-slate-900">Upload workbook</h2>
              <p class="text-sm text-slate-500">{{ uploadHint }}</p>
            </div>
            <div class="flex items-center gap-3">
              <button
                type="button"
                class="rounded-full border border-slate-200 px-5 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:text-slate-900"
                @click="pickFile"
              >
                Choose file
              </button>
              <input
                ref="fileInput"
                type="file"
                accept=".xlsx"
                class="hidden"
                @change="handleFileChange"
              />
            </div>
          </div>
          <p v-if="loading" class="mt-4 text-sm text-slate-500">Parsing workbook…</p>
          <p v-if="uploadError" class="mt-4 rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-600">
            {{ uploadError }}
          </p>
          <ul v-if="formatWarnings.length > 0" class="mt-4 space-y-2 text-sm text-amber-700">
            <li v-for="warning in formatWarnings" :key="warning" class="rounded-2xl bg-amber-50 px-4 py-2">
              {{ warning }}
            </li>
          </ul>
        </section>

        <section v-if="hasPreview && preview" class="space-y-6">
          <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            <article
              v-for="item in pendingSummary"
              :key="item.label"
              class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
            >
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">{{ item.label }}</p>
              <p class="mt-3 text-3xl font-semibold text-slate-900">{{ item.create }} new</p>
              <p class="text-xs text-slate-500">{{ item.update }} to update</p>
            </article>
          </div>
          <p v-if="hasRowErrors" class="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-700">
            Some rows contain validation issues. Adjust the values below or update the workbook and upload
            again. The API will perform final validation when you publish.
          </p>

          <div class="grid gap-6 lg:grid-cols-2 2xl:grid-cols-3">
            <section class="flex min-w-0 flex-col gap-4">
              <div class="flex items-center justify-between">
                <h2 class="text-lg font-semibold text-slate-900">Categories</h2>
                <p class="text-xs text-slate-500">{{ form.categories.length }} entries detected</p>
              </div>
              <div
                v-if="form.categories.length === 0"
                class="rounded-3xl border border-slate-200 bg-white p-6 text-sm text-slate-500"
              >
                No categories were detected in this workbook.
              </div>
              <div v-else class="space-y-4">
                <article
                  v-for="entry in categoryEntries"
                  :key="entry.meta?.source_row ?? `category-${entry.index}`"
                  class="relative min-w-0 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
                >
                  <button
                    type="button"
                    class="absolute -right-3 -top-3 inline-flex h-8 w-8 items-center justify-center rounded-full border border-slate-200 bg-white text-base font-semibold text-slate-400 shadow-sm transition hover:border-rose-200 hover:text-rose-500"
                    @click="discardCategory(entry.index)"
                    aria-label="Discard category"
                    title="Discard category"
                  >
                    <span aria-hidden="true">×</span>
                  </button>
                  <div class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                    <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">
                      {{ entry.meta?.action === 'create' ? 'Create' : entry.meta?.action === 'update' ? 'Update' : 'Entry' }} ·
                      Row {{ entry.meta?.source_row ?? '—' }}
                    </p>
                    <p v-if="entry.meta?.errors?.length" class="text-xs text-rose-500">
                      {{ entry.meta?.errors?.join(' · ') }}
                    </p>
                  </div>
                  <div class="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
                    <label class="flex flex-col gap-1 text-sm">
                      <span class="font-medium text-slate-600">Name</span>
                      <input v-model="entry.form.name" type="text" class="rounded-2xl border border-slate-200 px-4 py-2 focus:border-slate-400 focus:outline-none" />
                    </label>
                    <label class="flex flex-col gap-1 text-sm sm:col-span-2 xl:col-span-2">
                      <span class="font-medium text-slate-600">Description</span>
                      <input v-model="entry.form.description" type="text" class="rounded-2xl border border-slate-200 px-4 py-2 focus:border-slate-400 focus:outline-none" />
                    </label>
                    <label class="flex flex-col gap-1 text-sm">
                      <span class="font-medium text-slate-600">Icon</span>
                      <input v-model="entry.form.icon" type="text" class="rounded-2xl border border-slate-200 px-4 py-2 focus:border-slate-400 focus:outline-none" />
                    </label>
                  </div>
                </article>
              </div>
            </section>

            <section class="flex min-w-0 flex-col gap-4">
              <div class="flex items-center justify-between">
                <h2 class="text-lg font-semibold text-slate-900">Quizzes</h2>
                <p class="text-xs text-slate-500">{{ form.quizzes.length }} entries detected</p>
              </div>
              <div
                v-if="form.quizzes.length === 0"
                class="rounded-3xl border border-slate-200 bg-white p-6 text-sm text-slate-500"
              >
                No quizzes were detected in this workbook.
              </div>
              <div v-else class="space-y-4">
                <article
                  v-for="entry in quizEntries"
                  :key="entry.meta?.source_row ?? `quiz-${entry.index}`"
                  class="relative min-w-0 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
                >
                  <button
                    type="button"
                    class="absolute -right-3 -top-3 inline-flex h-8 w-8 items-center justify-center rounded-full border border-slate-200 bg-white text-base font-semibold text-slate-400 shadow-sm transition hover:border-rose-200 hover:text-rose-500"
                    @click="discardQuiz(entry.index)"
                    aria-label="Discard quiz"
                    title="Discard quiz"
                  >
                    <span aria-hidden="true">×</span>
                  </button>
                  <div class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                    <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">
                      {{ entry.meta?.action === 'create' ? 'Create' : entry.meta?.action === 'update' ? 'Update' : 'Entry' }} ·
                      Row {{ entry.meta?.source_row ?? '—' }}
                    </p>
                    <p v-if="entry.meta?.errors?.length" class="text-xs text-rose-500">
                      {{ entry.meta?.errors?.join(' · ') }}
                    </p>
                  </div>
                  <div class="mt-4 grid gap-4 sm:grid-cols-2">
                    <label class="flex flex-col gap-1 text-sm">
                      <span class="font-medium text-slate-600">Title</span>
                      <input v-model="entry.form.title" type="text" class="rounded-2xl border border-slate-200 px-4 py-2 focus:border-slate-400 focus:outline-none" />
                    </label>
                    <label class="flex items-center gap-2 text-sm font-medium text-slate-600">
                      <input v-model="entry.form.is_active" type="checkbox" class="rounded border-slate-300 text-slate-900 focus:ring-slate-500" />
                      Active
                    </label>
                    <label class="flex flex-col gap-1 text-sm sm:col-span-2">
                      <span class="font-medium text-slate-600">Description</span>
                      <textarea v-model="entry.form.description" rows="2" class="rounded-2xl border border-slate-200 px-4 py-2 focus:border-slate-400 focus:outline-none"></textarea>
                    </label>
                    <label class="flex flex-col gap-1 text-sm sm:col-span-2">
                      <span class="font-medium text-slate-600">Question prompts (comma separated)</span>
                      <textarea v-model="entry.form.questionPromptsText" rows="2" class="rounded-2xl border border-slate-200 px-4 py-2 focus:border-slate-400 focus:outline-none"></textarea>
                    </label>
                  </div>
                </article>
              </div>
            </section>

            <section class="flex min-w-0 flex-col gap-4">
              <div class="flex items-center justify-between">
                <h2 class="text-lg font-semibold text-slate-900">Questions</h2>
                <p class="text-xs text-slate-500">{{ form.questions.length }} entries detected</p>
              </div>
              <div
                v-if="form.questions.length === 0"
                class="rounded-3xl border border-slate-200 bg-white p-6 text-sm text-slate-500"
              >
                No questions were detected in this workbook.
              </div>
              <div v-else class="space-y-4">
                <article
                  v-for="entry in questionEntries"
                  :key="entry.meta?.source_row ?? `question-${entry.index}`"
                  class="relative min-w-0 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
                >
                  <button
                    type="button"
                    class="absolute -right-3 -top-3 inline-flex h-8 w-8 items-center justify-center rounded-full border border-slate-200 bg-white text-base font-semibold text-slate-400 shadow-sm transition hover:border-rose-200 hover:text-rose-500"
                    @click="discardQuestion(entry.index)"
                    aria-label="Discard question"
                    title="Discard question"
                  >
                    <span aria-hidden="true">×</span>
                  </button>
                  <div class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                    <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">
                      {{ entry.meta?.action === 'create' ? 'Create' : entry.meta?.action === 'update' ? 'Update' : 'Entry' }} ·
                      Row {{ entry.meta?.source_row ?? '—' }}
                    </p>
                    <p v-if="entry.meta?.errors?.length" class="text-xs text-rose-500">
                      {{ entry.meta?.errors?.join(' · ') }}
                    </p>
                  </div>
                  <div class="mt-4 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
                    <label class="flex flex-col gap-1 text-sm sm:col-span-2 xl:col-span-2">
                      <span class="font-medium text-slate-600">Prompt</span>
                      <textarea v-model="entry.form.prompt" rows="3" class="rounded-2xl border border-slate-200 px-4 py-2 focus:border-slate-400 focus:outline-none"></textarea>
                    </label>
                    <label class="flex items-center gap-2 text-sm font-medium text-slate-600">
                      <input v-model="entry.form.is_active" type="checkbox" class="rounded border-slate-300 text-slate-900 focus:ring-slate-500" />
                      Active
                    </label>
                    <label class="flex flex-col gap-1 text-sm sm:col-span-2 xl:col-span-2">
                      <span class="font-medium text-slate-600">Explanation</span>
                      <textarea v-model="entry.form.explanation" rows="3" class="rounded-2xl border border-slate-200 px-4 py-2 focus:border-slate-400 focus:outline-none"></textarea>
                    </label>
                    <label class="flex flex-col gap-1 text-sm">
                      <span class="font-medium text-slate-600">Subject</span>
                      <input v-model="entry.form.subject" type="text" class="rounded-2xl border border-slate-200 px-4 py-2 focus:border-slate-400 focus:outline-none" />
                    </label>
                    <label class="flex flex-col gap-1 text-sm">
                      <span class="font-medium text-slate-600">Difficulty</span>
                      <input v-model="entry.form.difficulty" type="text" class="rounded-2xl border border-slate-200 px-4 py-2 focus:border-slate-400 focus:outline-none" />
                    </label>
                    <label class="flex flex-col gap-1 text-sm">
                      <span class="font-medium text-slate-600">Category</span>
                      <input v-model="entry.form.category_name" type="text" class="rounded-2xl border border-slate-200 px-4 py-2 focus:border-slate-400 focus:outline-none" />
                    </label>
                    <label class="flex flex-col gap-1 text-sm sm:col-span-2 xl:col-span-2">
                      <span class="font-medium text-slate-600">Assign to quizzes (comma separated titles)</span>
                      <textarea v-model="entry.form.quizTitlesText" rows="2" class="rounded-2xl border border-slate-200 px-4 py-2 focus:border-slate-400 focus:outline-none"></textarea>
                    </label>
                  </div>
                  <div class="mt-6 space-y-3">
                    <h3 class="text-sm font-semibold text-slate-700">Answer options</h3>
                    <div
                      v-for="(option, optionIndex) in entry.form.options"
                      :key="optionIndex"
                      class="flex flex-col gap-2 rounded-2xl border border-slate-200 p-4 lg:flex-row lg:items-center lg:justify-between"
                    >
                      <div class="flex flex-1 flex-col gap-1 text-sm">
                        <span class="font-medium text-slate-600">Option {{ optionIndex + 1 }}</span>
                        <input v-model="option.text" type="text" class="rounded-2xl border border-slate-200 px-4 py-2 focus:border-slate-400 focus:outline-none" />
                      </div>
                      <div class="flex items-center gap-3 text-sm">
                        <label class="inline-flex items-center gap-2 font-medium text-slate-600">
                          <input
                            :name="`correct-${entry.index}`"
                            type="radio"
                            :checked="option.is_correct"
                            @change="markCorrectOption(entry.index, optionIndex)"
                            class="text-slate-900 focus:ring-slate-500"
                          />
                          Correct answer
                        </label>
                        <button
                          type="button"
                          class="rounded-full border border-slate-200 px-3 py-1 text-xs font-semibold text-slate-600 transition hover:border-slate-300 hover:text-slate-900"
                          @click="removeOption(entry.index, optionIndex)"
                        >
                          Remove
                        </button>
                      </div>
                    </div>
                    <button
                      type="button"
                      class="rounded-full border border-slate-200 px-4 py-1.5 text-xs font-semibold text-slate-600 transition hover:border-slate-300 hover:text-slate-900"
                      @click="addOption(entry.index)"
                    >
                      Add option
                    </button>
                  </div>
                </article>
              </div>
            </section>
          </div>
        </section>

        <section v-if="hasData" class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 class="text-lg font-semibold text-slate-900">Publish changes</h2>
              <p class="text-sm text-slate-500">
                Review the adjustments above. When you publish, the API will create new records and update any
                matching items.
              </p>
            </div>
            <button
              type="button"
              class="inline-flex items-center justify-center rounded-full bg-slate-900 px-6 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-400"
              :disabled="committing"
              @click="commitImport"
            >
              {{ committing ? 'Saving…' : 'Publish import' }}
            </button>
          </div>
          <p v-if="commitError" class="mt-4 rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-600">
            {{ commitError }}
          </p>
          <p v-if="commitSuccess" class="mt-4 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700">
            {{ commitSuccess }}
          </p>
          <div v-if="result" class="mt-4 grid gap-3 md:grid-cols-3">
            <div class="rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-600">
              <p class="font-semibold text-slate-900">Categories</p>
              <p>{{ result.categories_created }} created · {{ result.categories_updated }} updated</p>
            </div>
            <div class="rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-600">
              <p class="font-semibold text-slate-900">Quizzes</p>
              <p>{{ result.quizzes_created }} created · {{ result.quizzes_updated }} updated</p>
            </div>
            <div class="rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-600">
              <p class="font-semibold text-slate-900">Questions</p>
              <p>{{ result.questions_created }} created · {{ result.questions_updated }} updated</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  </section>
</template>
