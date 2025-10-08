import { defineStore } from 'pinia'
export const useQuizStore = defineStore('quiz', {
  state: () => ({ startedAt: 0, answers: {} as Record<number, number> }),
})
