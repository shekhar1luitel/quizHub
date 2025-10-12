<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import { http } from '../../api/http'

interface AdminSubject {
  id: number
  name: string
  slug: string
  description?: string | null
  icon?: string | null
}

const router = useRouter()

const subjects = ref<AdminSubject[]>([])
const loading = ref(false)
const error = ref('')
const searchTerm = ref('')

const totalSubjects = computed(() => subjects.value.length)
const withDescriptions = computed(() =>
  subjects.value.filter((subject) => subject.description?.trim()).length
)

const filteredSubjects = computed(() => {
  const term = searchTerm.value.trim().toLowerCase()
  if (!term) return subjects.value
  return subjects.value.filter((subject) => {
    return (
      subject.name.toLowerCase().includes(term) ||
      subject.slug.toLowerCase().includes(term) ||
      (subject.description ?? '').toLowerCase().includes(term)
    )
  })
})

const loadSubjects = async () => {
  loading.value = true
  error.value = ''
  try {
    const { data } = await http.get<AdminSubject[]>('/subjects')
    subjects.value = data
  } catch (err) {
    error.value = 'Unable to load subjects.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const deleteSubject = async (id: number) => {
  if (!window.confirm('Delete this subject?')) return
  try {
    await http.delete(`/subjects/${id}`)
    await loadSubjects()
  } catch (err: any) {
    error.value = err?.response?.data?.detail || 'Unable to delete subject.'
  }
}

const editSubject = (id: number) => {
  router.push({ name: 'admin-subjects', query: { edit: id } })
}

loadSubjects()
</script>

<template>
  <section class="space-y-10">
    <header class="space-y-4">
      <div class="inline-flex items-center gap-2 rounded-full bg-slate-100 px-4 py-1 text-xs font-semibold uppercase tracking-widest text-slate-600">
        Subject library
      </div>
      <div class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h1 class="text-3xl font-semibold text-slate-900">Catalogue every subject</h1>
          <p class="max-w-2xl text-sm text-slate-500">
            Audit coverage, refine descriptions, and keep the taxonomy aligned with your syllabus.
          </p>
        </div>
        <div class="flex flex-wrap items-center gap-3">
          <RouterLink
            :to="{ name: 'admin-subjects' }"
            class="inline-flex items-center gap-2 rounded-full bg-brand-600 px-5 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-500"
          >
            Add new subject
          </RouterLink>
          <button
            class="inline-flex items-center gap-2 rounded-full border border-slate-200 px-5 py-2 text-sm font-semibold text-slate-700 transition hover:border-brand-300 hover:text-brand-600"
            type="button"
            @click="loadSubjects"
          >
            <svg class="h-4 w-4" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v4h4M16 16v-4h-4M5 15a7 7 0 0 0 10-10" />
            </svg>
            Refresh
          </button>
        </div>
      </div>
    </header>

    <div class="grid gap-5 md:grid-cols-3">
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">Total subjects</p>
        <p class="mt-3 text-3xl font-semibold text-slate-900">{{ totalSubjects }}</p>
        <p class="text-xs text-slate-500">All practice topics currently available.</p>
      </article>
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">With descriptions</p>
        <p class="mt-3 text-3xl font-semibold text-slate-900">{{ withDescriptions }}</p>
        <p class="text-xs text-slate-500">Context helps learners choose wisely.</p>
      </article>
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400">Icon coverage</p>
        <p class="mt-3 text-3xl font-semibold text-slate-900">
          {{ subjects.filter((subject) => subject.icon?.trim()).length }}
        </p>
        <p class="text-xs text-slate-500">Add visuals to guide at-a-glance scanning.</p>
      </article>
    </div>

    <div class="rounded-3xl border border-slate-200 bg-white/95 p-6 shadow-xl shadow-brand-900/5 backdrop-blur md:p-8">
      <header class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h2 class="text-lg font-semibold text-slate-900">Subject list</h2>
          <p class="text-xs text-slate-500">{{ filteredSubjects.length }} results</p>
        </div>
        <div class="relative flex-1 sm:w-80">
          <span class="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">
            <svg class="h-4 w-4" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="m13.5 13.5 3 3m-1.5-4.5A5.5 5.5 0 1 1 5 5a5.5 5.5 0 0 1 9.5 3.5Z" />
            </svg>
          </span>
          <input
            v-model="searchTerm"
            type="search"
            placeholder="Search by name, slug, or description"
            class="w-full rounded-2xl border border-slate-200 bg-white px-10 py-3 text-sm focus:border-brand-400 focus:outline-none focus:ring-4 focus:ring-brand-100"
          />
        </div>
      </header>

      <div class="mt-6 space-y-4 text-sm">
        <p v-if="loading" class="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-slate-500">Loading subjects…</p>
        <p v-else-if="error" class="rounded-2xl border border-red-200 bg-red-50 p-4 text-red-600">{{ error }}</p>
        <p v-else-if="filteredSubjects.length === 0" class="rounded-2xl border border-amber-200 bg-amber-50 p-6 text-center text-amber-800">
          No subjects match your search.
        </p>
        <ul v-else class="space-y-4">
          <li
            v-for="subject in filteredSubjects"
            :key="subject.id"
            class="rounded-2xl border border-slate-200 p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-brand-200 hover:shadow-lg"
          >
            <div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
              <div class="space-y-2">
                <div class="flex items-center gap-3">
                  <span class="text-3xl">{{ subject.icon || '📝' }}</span>
                  <div>
                    <p class="text-base font-semibold text-slate-900">{{ subject.name }}</p>
                    <p class="text-xs uppercase tracking-[0.25em] text-slate-400">{{ subject.slug }}</p>
                  </div>
                </div>
                <p class="text-sm leading-6 text-slate-600">{{ subject.description || 'No description yet.' }}</p>
              </div>
              <div class="flex items-center gap-2">
                <button
                  class="inline-flex items-center gap-2 rounded-full border border-slate-200 px-4 py-2 text-xs font-semibold text-slate-700 transition hover:border-brand-300 hover:text-brand-600"
                  type="button"
                  @click="editSubject(subject.id)"
                >
                  <svg class="h-4 w-4" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M4 13.5V16h2.5l8-8-2.5-2.5-8 8z" />
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12.5 5.5 14.5 3.5 16.5 5.5 14.5 7.5z" />
                  </svg>
                  Edit
                </button>
                <button
                  class="inline-flex items-center gap-2 rounded-full border border-rose-200 px-4 py-2 text-xs font-semibold text-rose-500 transition hover:bg-rose-50"
                  type="button"
                  @click="deleteSubject(subject.id)"
                >
                  <svg class="h-4 w-4" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 7h8m-6 2v5m4-5v5M5 7l1-2h8l1 2m-9 0h8l-.5 9h-7z" />
                  </svg>
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
