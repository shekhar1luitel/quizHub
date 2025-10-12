<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useBookmarkStore, type BookmarkEntry } from '../stores/bookmarks'

const router = useRouter()
const bookmarkStore = useBookmarkStore()
const authStore = useAuthStore()

const selectedSubject = ref('all')
const selectedDifficulty = ref('all')
const searchTerm = ref('')
const bookmarkBusy = ref<Record<number, boolean>>({})
const toastVisible = ref(false)
const toastMessage = ref('')
const toastVariant = ref<'success' | 'error'>('success')
let toastTimeout: number | null = null

const entries = computed<BookmarkEntry[]>(() => bookmarkStore.entries)
const isLoading = computed(() => bookmarkStore.loadingEntries && entries.value.length === 0)

const subjects = computed(() => {
  const names = new Set<string>()
  for (const entry of entries.value) {
    if (entry.subject_name) {
      names.add(entry.subject_name)
    }
  }
  return Array.from(names).sort((a, b) => a.localeCompare(b))
})

const difficulties = computed(() => {
  const levels = new Set<string>()
  for (const entry of entries.value) {
    if (entry.difficulty) {
      levels.add(entry.difficulty)
    }
  }
  return Array.from(levels).sort((a, b) => a.localeCompare(b))
})

const filteredEntries = computed(() => {
  return entries.value.filter((entry) => {
    const matchesSubject =
      selectedSubject.value === 'all' || entry.subject_name === selectedSubject.value
    const matchesDifficulty =
      selectedDifficulty.value === 'all' || entry.difficulty === selectedDifficulty.value
    const matchesSearch =
      searchTerm.value.trim().length === 0 ||
      entry.prompt.toLowerCase().includes(searchTerm.value.trim().toLowerCase())
    return matchesSubject && matchesDifficulty && matchesSearch
  })
})

const hasEntries = computed(() => entries.value.length > 0)
const hasFilteredResults = computed(() => filteredEntries.value.length > 0)
const hasActiveFilters = computed(
  () =>
    selectedSubject.value !== 'all' ||
    selectedDifficulty.value !== 'all' ||
    searchTerm.value.trim().length > 0
)

const showToast = (message: string, variant: 'success' | 'error') => {
  toastMessage.value = message
  toastVariant.value = variant
  toastVisible.value = true
  if (toastTimeout) {
    window.clearTimeout(toastTimeout)
  }
  toastTimeout = window.setTimeout(() => {
    toastVisible.value = false
    toastMessage.value = ''
  }, 3200)
}

const hideToast = () => {
  if (toastTimeout) {
    window.clearTimeout(toastTimeout)
    toastTimeout = null
  }
  toastVisible.value = false
  toastMessage.value = ''
}

const clearFilters = () => {
  selectedSubject.value = 'all'
  selectedDifficulty.value = 'all'
  searchTerm.value = ''
}

const removeBookmark = async (questionId: number) => {
  bookmarkBusy.value = { ...bookmarkBusy.value, [questionId]: true }
  try {
    await bookmarkStore.removeBookmark(questionId)
    showToast('Bookmark removed', 'success')
  } catch (err: any) {
    const detail = err?.response?.data?.detail || 'Unable to remove bookmark. Please try again.'
    showToast(detail, 'error')
  } finally {
    const updated = { ...bookmarkBusy.value }
    delete updated[questionId]
    bookmarkBusy.value = updated
  }
}

const isRemoving = (questionId: number) => Boolean(bookmarkBusy.value[questionId])

const practiceFromBookmarks = () => {
  router.push({ name: 'practice', params: { slug: 'bookmarks' } })
}

const formatTimestamp = (iso: string) => new Date(iso).toLocaleString()

onMounted(() => {
  void bookmarkStore.ensureEntriesLoaded(true)
})

onUnmounted(() => {
  hideToast()
})

watch(
  () => authStore.isAuthenticated,
  (isAuthenticated) => {
    if (isAuthenticated) {
      void bookmarkStore.ensureEntriesLoaded(true)
    } else {
      bookmarkStore.reset()
      clearFilters()
      hideToast()
    }
  }
)
</script>

<template>
  <section class="mx-auto max-w-5xl space-y-6">
    <div
      v-if="toastVisible"
      class="flex items-center justify-between gap-3 rounded-full border px-4 py-2 text-sm font-semibold shadow-sm"
      :class="
        toastVariant === 'success'
          ? 'border-emerald-200 bg-emerald-50 text-emerald-700'
          : 'border-red-200 bg-red-50 text-red-700'
      "
      role="status"
    >
      <span>{{ toastMessage }}</span>
      <button
        class="text-xs font-semibold uppercase tracking-wide text-current/70 transition hover:text-current"
        type="button"
        @click="hideToast"
      >
        Dismiss
      </button>
    </div>

    <header class="space-y-2 rounded-3xl border border-slate-200 bg-white/95 p-6 shadow-lg shadow-brand-900/10">
      <p class="text-[11px] font-semibold uppercase tracking-[0.35em] text-slate-400">Bookmarks</p>
      <h1 class="text-2xl font-semibold text-slate-900">Saved questions for quick review</h1>
      <p class="text-sm text-slate-500">
        Revisit questions you have flagged during practice or full-length quizzes. Use filters to find the right topic and
        jump back into focused practice.
      </p>
      <div class="flex flex-wrap items-center justify-between gap-3 pt-2 text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">
        <span>Total saved: {{ entries.length }}</span>
        <button
          class="inline-flex items-center gap-2 rounded-full bg-slate-900 px-4 py-2 text-xs font-semibold text-white shadow-lg shadow-slate-900/20 transition hover:bg-slate-700"
          type="button"
          :disabled="!hasEntries"
          @click="practiceFromBookmarks"
        >
          Practice from bookmarks
        </button>
      </div>
    </header>

    <div class="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm">
      <div class="grid gap-3 sm:grid-cols-3">
        <label class="flex flex-col gap-1 text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">
          Subject
          <select
            v-model="selectedSubject"
            class="w-full rounded-2xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 focus:border-brand-300 focus:outline-none focus:ring-2 focus:ring-brand-200"
          >
            <option value="all">All</option>
            <option v-for="subject in subjects" :key="subject" :value="subject">{{ subject }}</option>
          </select>
        </label>
        <label class="flex flex-col gap-1 text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">
          Difficulty
          <select
            v-model="selectedDifficulty"
            class="w-full rounded-2xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 focus:border-brand-300 focus:outline-none focus:ring-2 focus:ring-brand-200"
          >
            <option value="all">All</option>
            <option v-for="difficulty in difficulties" :key="difficulty" :value="difficulty">{{ difficulty }}</option>
          </select>
        </label>
        <label class="flex flex-col gap-1 text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">
          Search
          <input
            v-model="searchTerm"
            class="w-full rounded-2xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 focus:border-brand-300 focus:outline-none focus:ring-2 focus:ring-brand-200"
            placeholder="Find a question"
            type="search"
          />
        </label>
      </div>
      <div class="mt-3 flex flex-wrap items-center justify-between gap-2 text-[11px] font-semibold uppercase tracking-[0.3em] text-slate-400">
        <span>{{ filteredEntries.length }} shown</span>
        <button
          v-if="hasActiveFilters"
          class="inline-flex items-center gap-1 rounded-full border border-slate-200 px-3 py-1 text-[11px] font-semibold text-slate-500 transition hover:border-brand-200 hover:text-brand-600"
          type="button"
          @click="clearFilters"
        >
          Clear filters
        </button>
      </div>
    </div>

    <div v-if="isLoading" class="space-y-4">
      <div v-for="n in 4" :key="`bookmark-skeleton-${n}`" class="h-28 animate-pulse rounded-3xl border border-slate-200 bg-slate-100"></div>
    </div>

    <div v-else-if="hasFilteredResults" class="space-y-4">
      <article
        v-for="entry in filteredEntries"
        :key="entry.id"
        class="space-y-3 rounded-3xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg"
      >
        <header class="flex flex-wrap items-center justify-between gap-3">
          <div class="space-y-1">
            <p class="text-xs font-semibold uppercase tracking-[0.3em] text-brand-500">{{ entry.subject_name }}</p>
            <h2 class="text-base font-semibold text-slate-900">{{ entry.prompt }}</h2>
          </div>
          <div class="flex items-center gap-2 text-xs text-slate-500">
            <span v-if="entry.difficulty">Difficulty: {{ entry.difficulty }}</span>
            <span class="hidden h-1 w-1 rounded-full bg-slate-300 md:inline"></span>
            <span>Saved {{ formatTimestamp(entry.created_at) }}</span>
          </div>
        </header>
        <div class="flex flex-wrap items-center justify-between gap-3 text-xs text-slate-500">
          <span>Subject: {{ entry.subject_label || '—' }}</span>
          <button
            class="inline-flex items-center gap-2 rounded-full border border-slate-200 px-4 py-1.5 text-xs font-semibold text-slate-600 transition hover:border-red-200 hover:bg-red-50 hover:text-red-600"
            type="button"
            :disabled="isRemoving(entry.question_id)"
            @click="removeBookmark(entry.question_id)"
          >
            <svg
              v-if="!isRemoving(entry.question_id)"
              class="h-4 w-4"
              viewBox="0 0 20 20"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
              aria-hidden="true"
            >
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 6l8 8m0-8-8 8" />
            </svg>
            <svg
              v-else
              class="h-4 w-4 animate-spin text-red-500"
              viewBox="0 0 20 20"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
              aria-hidden="true"
            >
              <path d="M10 3.75a6.25 6.25 0 1 1-4.42 10.67" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            Remove
          </button>
        </div>
      </article>
    </div>

    <div
      v-else
      class="rounded-3xl border border-slate-200 bg-white p-6 text-sm text-slate-500"
    >
      <p v-if="hasEntries">No bookmarks match the selected filters. Adjust filters to see more saved questions.</p>
      <p v-else>You have not bookmarked any questions yet. As you practice, look for the bookmark button to save questions for later.</p>
    </div>
  </section>
</template>
