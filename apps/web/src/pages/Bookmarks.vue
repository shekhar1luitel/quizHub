<script setup lang="ts">
// TODO: Replace with real bookmark data once backend endpoints are available.
import { computed, ref } from 'vue'

interface BookmarkEntry {
  id: number
  prompt: string
  difficulty: string
  source: string
}

const entries = ref<BookmarkEntry[]>([])

const hasEntries = computed(() => entries.value.length > 0)
</script>

<template>
  <section class="mx-auto max-w-3xl space-y-6">
    <header class="space-y-2 rounded-3xl border border-slate-200 bg-white/95 p-6 shadow-lg shadow-brand-900/10">
      <p class="text-[11px] font-semibold uppercase tracking-[0.35em] text-slate-400">Bookmarks</p>
      <h1 class="text-2xl font-semibold text-slate-900">Saved questions for quick review</h1>
      <p class="text-sm text-slate-500">
        Revisit questions you have flagged during practice or full-length quizzes. This view will grow as bookmarking
        support lands in the quiz and results experience.
      </p>
    </header>

    <div v-if="hasEntries" class="space-y-4">
      <article
        v-for="entry in entries"
        :key="entry.id"
        class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm"
      >
        <p class="text-sm font-semibold text-slate-900">{{ entry.prompt }}</p>
        <div class="mt-2 flex items-center justify-between text-xs text-slate-500">
          <span>{{ entry.difficulty }}</span>
          <span>{{ entry.source }}</span>
        </div>
      </article>
    </div>

    <div
      v-else
      class="rounded-3xl border border-slate-200 bg-white p-6 text-sm text-slate-500"
    >
      You have not bookmarked any questions yet. As you practice, look for the bookmark button to save questions for
      later.
    </div>
  </section>
</template>
