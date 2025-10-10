<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
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
      <div class="grid gap-4 md:grid-cols-3">
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

      <section class="space-y-4">
        <header class="flex items-center justify-between">
          <h2 class="text-lg font-semibold text-slate-900">Categories</h2>
          <p class="text-xs text-slate-500">{{ form.categories.length }} entries detected</p>
        </header>
        <div v-if="form.categories.length === 0" class="rounded-3xl border border-slate-200 bg-white p-6 text-sm text-slate-500">
          No categories were detected in this workbook.
        </div>
        <div v-else class="space-y-4">
          <article
            v-for="(category, index) in form.categories"
            :key="index"
            class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
          >
            <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">
                {{ preview.categories[index].action === 'create' ? 'Create' : 'Update' }} ·
                Row {{ preview.categories[index].source_row ?? '—' }}
              </p>
              <p v-if="preview.categories[index].errors.length" class="text-xs text-rose-500">
                {{ preview.categories[index].errors.join(' · ') }}
              </p>
            </div>
            <div class="mt-4 grid gap-4 md:grid-cols-3">
              <label class="flex flex-col gap-1 text-sm">
                <span class="font-medium text-slate-600">Name</span>
                <input v-model="category.name" type="text" class="rounded-2xl border border-slate-200 px-4 py-2 focus:border-slate-400 focus:outline-none" />
              </label>
              <label class="flex flex-col gap-1 text-sm md:col-span-2">
                <span class="font-medium text-slate-600">Description</span>
                <input v-model="category.description" type="text" class="rounded-2xl border border-slate-200 px-4 py-2 focus:border-slate-400 focus:outline-none" />
              </label>
              <label class="flex flex-col gap-1 text-sm">
                <span class="font-medium text-slate-600">Icon</span>
                <input v-model="category.icon" type="text" class="rounded-2xl border border-slate-200 px-4 py-2 focus:border-slate-400 focus:outline-none" />
              </label>
            </div>
          </article>
        </div>
      </section>

      <section class="space-y-4">
        <header class="flex items-center justify-between">
          <h2 class="text-lg font-semibold text-slate-900">Quizzes</h2>
          <p class="text-xs text-slate-500">{{ form.quizzes.length }} entries detected</p>
        </header>
        <div v-if="form.quizzes.length === 0" class="rounded-3xl border border-slate-200 bg-white p-6 text-sm text-slate-500">
          No quizzes were detected in this workbook.
        </div>
        <div v-else class="space-y-4">
          <article
            v-for="(quiz, index) in form.quizzes"
            :key="index"
            class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
          >
            <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">
                {{ preview.quizzes[index].action === 'create' ? 'Create' : 'Update' }} ·
                Row {{ preview.quizzes[index].source_row ?? '—' }}
              </p>
              <p v-if="preview.quizzes[index].errors.length" class="text-xs text-rose-500">
                {{ preview.quizzes[index].errors.join(' · ') }}
              </p>
            </div>
            <div class="mt-4 grid gap-4 md:grid-cols-2">
              <label class="flex flex-col gap-1 text-sm">
                <span class="font-medium text-slate-600">Title</span>
                <input v-model="quiz.title" type="text" class="rounded-2xl border border-slate-200 px-4 py-2 focus:border-slate-400 focus:outline-none" />
              </label>
              <label class="flex items-center gap-2 text-sm font-medium text-slate-600">
                <input v-model="quiz.is_active" type="checkbox" class="rounded border-slate-300 text-slate-900 focus:ring-slate-500" />
                Active
              </label>
              <label class="flex flex-col gap-1 text-sm md:col-span-2">
                <span class="font-medium text-slate-600">Description</span>
                <textarea v-model="quiz.description" rows="2" class="rounded-2xl border border-slate-200 px-4 py-2 focus:border-slate-400 focus:outline-none"></textarea>
              </label>
              <label class="flex flex-col gap-1 text-sm md:col-span-2">
                <span class="font-medium text-slate-600">Question prompts (comma separated)</span>
                <textarea v-model="quiz.questionPromptsText" rows="2" class="rounded-2xl border border-slate-200 px-4 py-2 focus:border-slate-400 focus:outline-none"></textarea>
              </label>
            </div>
          </article>
        </div>
      </section>

      <section class="space-y-4">
        <header class="flex items-center justify-between">
          <h2 class="text-lg font-semibold text-slate-900">Questions</h2>
          <p class="text-xs text-slate-500">{{ form.questions.length }} entries detected</p>
        </header>
        <div v-if="form.questions.length === 0" class="rounded-3xl border border-slate-200 bg-white p-6 text-sm text-slate-500">
          No questions were detected in this workbook.
        </div>
        <div v-else class="space-y-4">
          <article
            v-for="(question, index) in form.questions"
            :key="index"
            class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
          >
            <div class="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">
                {{ preview.questions[index].action === 'create' ? 'Create' : 'Update' }} ·
                Row {{ preview.questions[index].source_row ?? '—' }}
              </p>
              <p v-if="preview.questions[index].errors.length" class="text-xs text-rose-500">
                {{ preview.questions[index].errors.join(' · ') }}
              </p>
            </div>
            <div class="mt-4 grid gap-4 md:grid-cols-2">
              <label class="flex flex-col gap-1 text-sm md:col-span-2">
                <span class="font-medium text-slate-600">Prompt</span>
                <textarea v-model="question.prompt" rows="3" class="rounded-2xl border border-slate-200 px-4 py-2 focus:border-slate-400 focus:outline-none"></textarea>
              </label>
              <label class="flex flex-col gap-1 text-sm md:col-span-2">
                <span class="font-medium text-slate-600">Explanation</span>
                <textarea v-model="question.explanation" rows="3" class="rounded-2xl border border-slate-200 px-4 py-2 focus:border-slate-400 focus:outline-none"></textarea>
              </label>
              <label class="flex flex-col gap-1 text-sm">
                <span class="font-medium text-slate-600">Subject</span>
                <input v-model="question.subject" type="text" class="rounded-2xl border border-slate-200 px-4 py-2 focus:border-slate-400 focus:outline-none" />
              </label>
              <label class="flex flex-col gap-1 text-sm">
                <span class="font-medium text-slate-600">Difficulty</span>
                <input v-model="question.difficulty" type="text" class="rounded-2xl border border-slate-200 px-4 py-2 focus:border-slate-400 focus:outline-none" />
              </label>
              <label class="flex items-center gap-2 text-sm font-medium text-slate-600">
                <input v-model="question.is_active" type="checkbox" class="rounded border-slate-300 text-slate-900 focus:ring-slate-500" />
                Active
              </label>
              <label class="flex flex-col gap-1 text-sm">
                <span class="font-medium text-slate-600">Category</span>
                <input v-model="question.category_name" type="text" class="rounded-2xl border border-slate-200 px-4 py-2 focus:border-slate-400 focus:outline-none" />
              </label>
              <label class="flex flex-col gap-1 text-sm md:col-span-2">
                <span class="font-medium text-slate-600">Assign to quizzes (comma separated titles)</span>
                <textarea v-model="question.quizTitlesText" rows="2" class="rounded-2xl border border-slate-200 px-4 py-2 focus:border-slate-400 focus:outline-none"></textarea>
              </label>
            </div>
            <div class="mt-6 space-y-3">
              <h3 class="text-sm font-semibold text-slate-700">Answer options</h3>
              <div
                v-for="(option, optionIndex) in question.options"
                :key="optionIndex"
                class="flex flex-col gap-2 rounded-2xl border border-slate-200 p-4 md:flex-row md:items-center md:justify-between"
              >
                <div class="flex flex-1 flex-col gap-1 text-sm">
                  <span class="font-medium text-slate-600">Option {{ optionIndex + 1 }}</span>
                  <input v-model="option.text" type="text" class="rounded-2xl border border-slate-200 px-4 py-2 focus:border-slate-400 focus:outline-none" />
                </div>
                <div class="flex items-center gap-3 text-sm">
                  <label class="inline-flex items-center gap-2 font-medium text-slate-600">
                    <input
                      :name="`correct-${index}`"
                      type="radio"
                      :checked="option.is_correct"
                      @change="markCorrectOption(index, optionIndex)"
                      class="text-slate-900 focus:ring-slate-500"
                    />
                    Correct answer
                  </label>
                  <button
                    type="button"
                    class="rounded-full border border-slate-200 px-3 py-1 text-xs font-semibold text-slate-600 transition hover:border-slate-300 hover:text-slate-900"
                    @click="removeOption(index, optionIndex)"
                  >
                    Remove
                  </button>
                </div>
              </div>
              <button
                type="button"
                class="rounded-full border border-slate-200 px-4 py-1.5 text-xs font-semibold text-slate-600 transition hover:border-slate-300 hover:text-slate-900"
                @click="addOption(index)"
              >
                Add option
              </button>
            </div>
          </article>
        </div>
      </section>
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
  </section>
</template>
