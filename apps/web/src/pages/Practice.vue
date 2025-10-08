<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, RouterLink } from 'vue-router'

type Difficulty = 'Easy' | 'Medium' | 'Hard'

type PracticeQuestion = {
  id: number
  question: string
  options: string[]
  correctAnswer: number
  explanation: string
  difficulty: Difficulty
}

const route = useRoute()
const categoryId = computed(() => Number(route.params.id))

const questions = ref<PracticeQuestion[]>([
  {
    id: 1,
    question: 'What is the capital of France?',
    options: ['London', 'Berlin', 'Paris', 'Madrid'],
    correctAnswer: 2,
    explanation: 'Paris is the capital and most populous city of France, located in the north-central part of the country.',
    difficulty: 'Easy',
  },
  {
    id: 2,
    question: 'Which planet is known as the Red Planet?',
    options: ['Venus', 'Mars', 'Jupiter', 'Saturn'],
    correctAnswer: 1,
    explanation: 'Mars gets its red colour from iron oxide, or rust, on its surface.',
    difficulty: 'Easy',
  },
  {
    id: 3,
    question: "Who wrote the play 'Romeo and Juliet'?",
    options: ['Charles Dickens', 'William Shakespeare', 'Jane Austen', 'Mark Twain'],
    correctAnswer: 1,
    explanation: "William Shakespeare wrote Romeo and Juliet, one of his most celebrated tragedies, around 1595.",
    difficulty: 'Medium',
  },
])

const currentIndex = ref(0)
const selectedAnswer = ref<number | null>(null)
const showResult = ref(false)
const showExplanation = ref(false)

const currentQuestion = computed(() => questions.value[currentIndex.value])

const selectAnswer = (optionIndex: number) => {
  if (showResult.value) return
  selectedAnswer.value = optionIndex
}

const submitAnswer = () => {
  if (selectedAnswer.value === null) return
  showResult.value = true
  showExplanation.value = true
}

const goNext = () => {
  if (currentIndex.value < questions.value.length - 1) {
    currentIndex.value += 1
    resetState()
  }
}

const goPrev = () => {
  if (currentIndex.value > 0) {
    currentIndex.value -= 1
    resetState()
  }
}

const retryQuestion = () => {
  showResult.value = false
  showExplanation.value = false
  selectedAnswer.value = null
}

const resetState = () => {
  selectedAnswer.value = null
  showResult.value = false
  showExplanation.value = false
}

const isCorrect = computed(
  () => selectedAnswer.value !== null && selectedAnswer.value === currentQuestion.value.correctAnswer
)

const difficultyBadge = (difficulty: Difficulty) => {
  switch (difficulty) {
    case 'Easy':
      return 'bg-emerald-100 text-emerald-800'
    case 'Medium':
      return 'bg-amber-100 text-amber-800'
    default:
      return 'bg-rose-100 text-rose-800'
  }
}
</script>

<template>
  <section class="space-y-8">
    <header class="flex items-start gap-4">
      <RouterLink
        :to="{ name: 'categories' }"
        class="inline-flex items-center gap-2 rounded-full border border-slate-200 px-4 py-2 text-xs font-semibold uppercase tracking-widest text-slate-600 transition hover:border-slate-300 hover:text-slate-900"
      >
        <span aria-hidden="true">←</span>
        Back to categories
      </RouterLink>
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">Practice</p>
        <h1 class="mt-2 text-3xl font-semibold text-slate-900">Reinforcement mode</h1>
        <p class="mt-2 text-sm text-slate-500">
          Category ID {{ categoryId || '—' }} · Question {{ currentIndex + 1 }} of {{ questions.length }}
        </p>
      </div>
    </header>

    <article class="space-y-6 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <header class="flex items-start justify-between gap-3">
        <div>
          <p class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">Question {{ currentIndex + 1 }}</p>
          <h2 class="mt-2 text-xl font-semibold text-slate-900">{{ currentQuestion.question }}</h2>
        </div>
        <span :class="['rounded-full px-3 py-1 text-xs font-semibold', difficultyBadge(currentQuestion.difficulty)]">
          {{ currentQuestion.difficulty }}
        </span>
      </header>

      <div class="space-y-3">
        <button
          v-for="(option, index) in currentQuestion.options"
          :key="option"
          class="w-full rounded-2xl border px-5 py-3 text-left text-sm transition"
          :class="[
            !showResult
              ? selectedAnswer === index
                ? 'border-slate-900 bg-slate-900/5 text-slate-900'
                : 'border-slate-200 hover:border-slate-300 hover:bg-slate-100'
              : index === currentQuestion.correctAnswer
                ? 'border-emerald-400 bg-emerald-50 text-emerald-700'
                : selectedAnswer === index
                  ? 'border-rose-400 bg-rose-50 text-rose-700'
                  : 'border-slate-200 text-slate-600'
          ]"
          :disabled="showResult"
          @click="selectAnswer(index)"
        >
          <span class="flex items-center gap-3">
            <span class="text-xs font-semibold text-slate-400">{{ String.fromCharCode(65 + index) }}.</span>
            <span class="flex-1">{{ option }}</span>
          </span>
        </button>
      </div>

      <div v-if="showResult" class="rounded-2xl border px-5 py-4" :class="isCorrect ? 'border-emerald-200 bg-emerald-50 text-emerald-700' : 'border-rose-200 bg-rose-50 text-rose-700'">
        <p class="text-sm font-semibold">{{ isCorrect ? 'Great job! That was correct.' : 'Not quite right this time.' }}</p>
      </div>

      <div v-if="showExplanation" class="rounded-2xl border border-slate-200 bg-slate-50 px-5 py-4 text-sm text-slate-600">
        <p class="font-semibold text-slate-900">Explanation</p>
        <p class="mt-2 leading-6">{{ currentQuestion.explanation }}</p>
      </div>

      <footer class="flex flex-col gap-3 border-t border-slate-200 pt-4 text-sm md:flex-row md:items-center md:justify-between">
        <div class="flex items-center gap-3">
          <button
            class="rounded-full border border-slate-200 px-4 py-2 font-semibold text-slate-600 transition hover:border-slate-300 hover:text-slate-900"
            :disabled="currentIndex === 0"
            @click="goPrev"
          >
            Previous
          </button>
          <button
            class="rounded-full border border-slate-200 px-4 py-2 font-semibold text-slate-600 transition hover:border-slate-300 hover:text-slate-900"
            :disabled="currentIndex >= questions.length - 1"
            @click="goNext"
          >
            Next
          </button>
        </div>
        <div class="flex items-center gap-3">
          <button
            v-if="showResult"
            class="rounded-full border border-slate-200 px-4 py-2 font-semibold text-slate-600 transition hover:border-slate-300 hover:text-slate-900"
            @click="retryQuestion"
          >
            Try again
          </button>
          <button
            v-else
            class="rounded-full bg-slate-900 px-5 py-2 font-semibold text-white transition hover:bg-slate-700 disabled:opacity-50"
            :disabled="selectedAnswer === null"
            @click="submitAnswer"
          >
            Check answer
          </button>
        </div>
      </footer>
    </article>
  </section>
</template>
