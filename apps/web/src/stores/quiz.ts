import { defineStore } from 'pinia'

export const useQuizStore = defineStore('quiz', {
  state: () => ({
    currentQuizId: null as number | null,
    startedAt: 0,
    durationSeconds: 0,
    answers: {} as Record<number, number | null>,
  }),
  actions: {
    start(quizId: number) {
      this.currentQuizId = quizId
      this.startedAt = Date.now()
      this.durationSeconds = 0
      this.answers = {}
    },
    recordDuration(seconds: number) {
      this.durationSeconds = seconds
    },
    selectAnswer(questionId: number, optionId: number | null) {
      this.answers = { ...this.answers, [questionId]: optionId }
    },
    reset() {
      this.currentQuizId = null
      this.startedAt = 0
      this.durationSeconds = 0
      this.answers = {}
    },
  },
})
