import { computed } from 'vue'
import { defineStore } from 'pinia'
import { http } from '../api/http'
import { useAuthStore } from './auth'

export interface BookmarkEntry {
  id: number
  question_id: number
  created_at: string
  prompt: string
  subject_label: string | null
  difficulty: string | null
  subject_id: number
  subject_name: string
}

interface BookmarkState {
  questionMap: Record<number, true>
  entries: BookmarkEntry[]
  idsFetched: boolean
  entriesFetched: boolean
  loadingIds: boolean
  loadingEntries: boolean
}

export const useBookmarkStore = defineStore('bookmarks', {
  state: (): BookmarkState => ({
    questionMap: {},
    entries: [],
    idsFetched: false,
    entriesFetched: false,
    loadingIds: false,
    loadingEntries: false,
  }),
  getters: {
    questionIds(state): number[] {
      return Object.keys(state.questionMap).map((id) => Number(id))
    },
    isBookmarked(state) {
      return (questionId: number) => Boolean(state.questionMap[questionId])
    },
  },
  actions: {
    reset() {
      this.questionMap = {}
      this.entries = []
      this.idsFetched = false
      this.entriesFetched = false
      this.loadingIds = false
      this.loadingEntries = false
    },
    async ensureQuestionIdsLoaded(force = false) {
      const auth = useAuthStore()
      if (!auth.isAuthenticated) {
        this.reset()
        return
      }
      if (this.loadingIds || (this.idsFetched && !force)) return
      this.loadingIds = true
      try {
        const { data } = await http.get<number[]>('/bookmarks/ids')
        const nextMap: Record<number, true> = {}
        for (const id of data) {
          nextMap[id] = true
        }
        this.questionMap = nextMap
        this.idsFetched = true
      } finally {
        this.loadingIds = false
      }
    },
    async ensureEntriesLoaded(force = false) {
      const auth = useAuthStore()
      if (!auth.isAuthenticated) {
        this.reset()
        return
      }
      if (this.loadingEntries || (this.entriesFetched && !force)) return
      this.loadingEntries = true
      try {
        const { data } = await http.get<BookmarkEntry[]>('/bookmarks')
        this.entries = data
        const nextMap: Record<number, true> = { ...this.questionMap }
        for (const entry of data) {
          nextMap[entry.question_id] = true
        }
        this.questionMap = nextMap
        this.entriesFetched = true
        this.idsFetched = true
      } finally {
        this.loadingEntries = false
      }
    },
    async addBookmark(questionId: number) {
      const auth = useAuthStore()
      if (!auth.isAuthenticated) {
        throw new Error('Login required')
      }
      const { data } = await http.post<BookmarkEntry>('/bookmarks', { question_id: questionId })
      this.questionMap = { ...this.questionMap, [questionId]: true }
      if (this.entriesFetched) {
        const exists = this.entries.some((entry) => entry.question_id === questionId)
        const updated = exists
          ? this.entries.map((entry) => (entry.question_id === questionId ? data : entry))
          : [data, ...this.entries]
        this.entries = updated
      }
      return data
    },
    async removeBookmark(questionId: number) {
      const auth = useAuthStore()
      if (!auth.isAuthenticated) {
        throw new Error('Login required')
      }
      await http.delete(`/bookmarks/${questionId}`)
      const nextMap = { ...this.questionMap }
      delete nextMap[questionId]
      this.questionMap = nextMap
      if (this.entriesFetched) {
        this.entries = this.entries.filter((entry) => entry.question_id !== questionId)
      }
    },
  },
})

export const useBookmarkHelpers = () => {
  const store = useBookmarkStore()
  const loading = computed(() => store.loadingEntries)
  const entries = computed(() => store.entries)
  return { store, loading, entries }
}
