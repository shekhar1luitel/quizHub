<script setup lang="ts">
import { reactive, ref } from 'vue'
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
  <section class="space-y-6">
    <header>
      <h2 class="text-xl font-semibold text-gray-900">Question bank</h2>
      <p class="text-sm text-gray-500">Add rich explanations and manage answer keys for each prompt.</p>
    </header>

    <div class="grid gap-6 lg:grid-cols-2">
      <form class="space-y-4 rounded-lg border border-gray-200 bg-white p-5 shadow-sm" @submit.prevent="submit">
        <h3 class="text-lg font-semibold text-gray-900">{{ editingId ? 'Edit question' : 'Create question' }}</h3>
        <div class="space-y-1">
          <label class="text-sm font-medium text-gray-700" for="prompt">Prompt</label>
          <textarea
            id="prompt"
            v-model="form.prompt"
            class="min-h-[120px] w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-gray-500 focus:outline-none"
            placeholder="Enter the question stem"
            required
          ></textarea>
        </div>
        <div class="space-y-1">
          <label class="text-sm font-medium text-gray-700" for="explanation">Explanation</label>
          <textarea
            id="explanation"
            v-model="form.explanation"
            class="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-gray-500 focus:outline-none"
            placeholder="Add reasoning or references (optional)"
          ></textarea>
        </div>
        <div class="grid gap-4 md:grid-cols-2">
          <div class="space-y-1">
            <label class="text-sm font-medium text-gray-700" for="subject">Subject</label>
            <input
              id="subject"
              v-model="form.subject"
              class="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-gray-500 focus:outline-none"
              placeholder="General Knowledge"
            />
          </div>
          <div class="space-y-1">
            <label class="text-sm font-medium text-gray-700" for="difficulty">Difficulty</label>
            <input
              id="difficulty"
              v-model="form.difficulty"
              class="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-gray-500 focus:outline-none"
              placeholder="Easy / Medium / Hard"
            />
          </div>
        </div>
        <div class="space-y-2">
          <p class="text-sm font-medium text-gray-700">Options</p>
          <div v-for="(option, index) in form.options" :key="index" class="flex items-start gap-3">
            <input
              class="mt-2"
              name="correctOption"
              type="radio"
              :checked="option.is_correct"
              @change="markCorrect(index)"
            />
            <textarea
              v-model="option.text"
              class="min-h-[60px] flex-1 rounded border border-gray-300 px-3 py-2 text-sm focus:border-gray-500 focus:outline-none"
              placeholder="Answer option"
              required
            ></textarea>
            <button
              class="mt-1 rounded border border-red-200 px-2 py-1 text-xs text-red-600 hover:bg-red-50"
              type="button"
              @click="removeOption(index)"
            >
              Remove
            </button>
          </div>
          <button
            class="rounded border border-dashed border-gray-300 px-3 py-2 text-xs font-medium text-gray-600 hover:bg-gray-50"
            type="button"
            @click="addOption"
          >
            Add option
          </button>
        </div>
        <div class="flex items-center gap-2">
          <input id="is-active" v-model="form.is_active" type="checkbox" class="h-4 w-4" />
          <label class="text-sm text-gray-700" for="is-active">Question is active</label>
        </div>
        <div class="flex items-center gap-3">
          <button
            class="rounded bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-500"
            type="submit"
          >
            {{ editingId ? 'Update question' : 'Create question' }}
          </button>
          <button
            class="text-sm text-gray-500 hover:underline"
            type="button"
            @click="resetForm"
          >
            Clear form
          </button>
        </div>
        <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
        <p v-if="success" class="text-sm text-emerald-600">{{ success }}</p>
      </form>

      <div class="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
        <header class="flex items-center justify-between">
          <h3 class="text-lg font-semibold text-gray-900">Existing questions</h3>
          <span class="text-xs text-gray-500">{{ questions.length }} items</span>
        </header>
        <p v-if="loading" class="mt-4 text-sm text-gray-500">Loading…</p>
        <p v-else-if="questions.length === 0" class="mt-4 text-sm text-gray-500">No questions yet.</p>
        <ul v-else class="mt-4 space-y-3 text-sm">
          <li v-for="question in questions" :key="question.id" class="rounded border border-gray-200 p-3">
            <div class="flex items-center justify-between gap-3">
              <div>
                <p class="font-medium text-gray-900">{{ question.prompt }}</p>
                <p class="text-xs text-gray-500">
                  {{ question.subject || '—' }} • {{ question.difficulty || '—' }} •
                  {{ question.option_count }} options
                </p>
              </div>
              <div class="flex gap-2">
                <button class="text-xs font-semibold text-gray-600 hover:underline" type="button" @click="editQuestion(question.id)">
                  Edit
                </button>
                <button class="text-xs font-semibold text-red-600 hover:underline" type="button" @click="deleteQuestion(question.id)">
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
