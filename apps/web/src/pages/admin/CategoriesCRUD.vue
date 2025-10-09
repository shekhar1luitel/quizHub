<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import { http } from '../../api/http'

interface AdminCategory {
  id: number
  name: string
  slug: string
  description?: string | null
  icon?: string | null
  organization_id?: number | null
}

const categories = ref<AdminCategory[]>([])
const loading = ref(false)
const formLoading = ref(false)
const error = ref('')
const formError = ref('')
const success = ref('')
const editingId = ref<number | null>(null)

const totalCategories = computed(() => categories.value.length)
const RECENT_LIMIT = 6
const recentCategories = computed(() => categories.value.slice(0, RECENT_LIMIT))
const hasMoreCategories = computed(() => categories.value.length > recentCategories.value.length)

const form = reactive({
  name: '',
  description: '',
  icon: '',
})

const route = useRoute()
const router = useRouter()
const pendingEditId = ref<number | null>(null)

const clearEditQuery = () => {
  if (!('edit' in route.query)) return
  const { edit, ...rest } = route.query
  router.replace({
    name: (route.name as string | undefined) ?? 'admin-categories',
    params: route.params,
    query: rest,
  })
}

const applyPendingCategoryEdit = () => {
  if (pendingEditId.value === null) return
  const target = categories.value.find((category) => category.id === pendingEditId.value)
  if (!target) return
  editCategory(target)
  pendingEditId.value = null
  clearEditQuery()
}

const resetForm = () => {
  form.name = ''
  form.description = ''
  form.icon = ''
  editingId.value = null
  formError.value = ''
  success.value = ''
}

const loadCategories = async () => {
  loading.value = true
  error.value = ''
  try {
    const { data } = await http.get<AdminCategory[]>('/categories')
    categories.value = data
    applyPendingCategoryEdit()
  } catch (err) {
    error.value = 'Unable to load categories.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const submit = async () => {
  formError.value = ''
  success.value = ''

  const payload = {
    name: form.name.trim(),
    description: form.description.trim() ? form.description.trim() : null,
    icon: form.icon.trim() ? form.icon.trim() : null,
  }

  if (!payload.name) {
    formError.value = 'Provide a category name.'
    return
  }

  formLoading.value = true
  try {
    if (editingId.value) {
      await http.put(`/categories/${editingId.value}`, payload)
      success.value = 'Category updated.'
    } else {
      await http.post('/categories', payload)
      success.value = 'Category created.'
    }
    await loadCategories()
    resetForm()
  } catch (err: any) {
    formError.value = err?.response?.data?.detail || 'Save failed.'
  } finally {
    formLoading.value = false
  }
}

const editCategory = (category: AdminCategory) => {
  form.name = category.name
  form.description = category.description || ''
  form.icon = category.icon || ''
  editingId.value = category.id
  formError.value = ''
  success.value = ''
}

const deleteCategory = async (id: number) => {
  if (!confirm('Delete this category?')) return
  formError.value = ''
  success.value = ''
  try {
    await http.delete(`/categories/${id}`)
    if (editingId.value === id) {
      resetForm()
    }
    await loadCategories()
    success.value = 'Category removed.'
  } catch (err: any) {
    formError.value = err?.response?.data?.detail || 'Unable to delete category.'
  }
}

loadCategories()

watch(
  () => route.query.edit,
  (value) => {
    if (!value && pendingEditId.value === null) return
    if (!value) {
      pendingEditId.value = null
      return
    }
    const id = Number(value)
    if (Number.isNaN(id)) return
    pendingEditId.value = id
    applyPendingCategoryEdit()
  },
  { immediate: true }
)
</script>

<template>
  <section class="space-y-10">
    <header class="space-y-4">
      <div class="inline-flex items-center gap-2 rounded-full bg-slate-100 px-4 py-1 text-xs font-semibold uppercase tracking-widest text-slate-600">
        Category library
      </div>
      <div class="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h1 class="text-3xl font-semibold text-slate-900">Organize practice categories</h1>
          <p class="max-w-2xl text-sm text-slate-500">
            Create topics, assign icons, and keep descriptions up to date so learners always know what they are practicing.
          </p>
        </div>
        <div class="flex flex-wrap items-center gap-3">
          <RouterLink
            :to="{ name: 'admin-category-library' }"
            class="inline-flex items-center justify-center rounded-full border border-slate-200 px-6 py-2.5 text-sm font-semibold text-slate-700 transition hover:border-brand-300 hover:text-brand-600"
          >
            View all categories
          </RouterLink>
          <button
            class="inline-flex items-center justify-center rounded-full border border-slate-200 px-6 py-2.5 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:text-slate-900"
            type="button"
            @click="resetForm"
          >
            {{ editingId ? 'Cancel editing' : 'Reset form' }}
          </button>
        </div>
      </div>
    </header>

    <div class="grid gap-5 lg:grid-cols-3">
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Total categories</p>
        <p class="mt-3 text-3xl font-semibold text-slate-900">{{ totalCategories }}</p>
        <p class="mt-2 text-xs text-slate-500">Keep practice organized with clear topic areas.</p>
      </article>
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Featured icon</p>
        <p class="mt-3 text-3xl font-semibold text-slate-900">
          {{ categories[0]?.icon || '✨' }}
        </p>
        <p class="mt-2 text-xs text-slate-500">Use emoji to make categories instantly recognizable.</p>
      </article>
      <article class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Descriptions</p>
        <p class="mt-3 text-3xl font-semibold text-slate-900">
          {{ categories.filter((category) => category.description?.length).length }}
        </p>
        <p class="mt-2 text-xs text-slate-500">Add context so learners choose the right focus area.</p>
      </article>
    </div>

    <div class="grid gap-6 lg:grid-cols-[1.1fr,1fr]">
      <form class="space-y-5 rounded-3xl border border-slate-200 bg-white/90 p-6 shadow-lg backdrop-blur" @submit.prevent="submit">
        <header class="flex flex-col gap-1">
          <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">{{ editingId ? 'Update category' : 'New category' }}</p>
          <h2 class="text-xl font-semibold text-slate-900">{{ editingId ? 'Edit category' : 'Create category' }}</h2>
        </header>
        <div class="space-y-2">
          <label class="text-sm font-semibold text-slate-700" for="name">Name</label>
          <input
            id="name"
            v-model="form.name"
            class="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200"
            placeholder="General Knowledge"
            required
          />
        </div>
        <div class="space-y-2">
          <label class="text-sm font-semibold text-slate-700" for="icon">Icon (emoji)</label>
          <input
            id="icon"
            v-model="form.icon"
            class="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200"
            placeholder="🌍"
            maxlength="16"
          />
          <p class="text-xs text-slate-500">Pick a single emoji or short symbol.</p>
        </div>
        <div class="space-y-2">
          <label class="text-sm font-semibold text-slate-700" for="description">Description</label>
          <textarea
            id="description"
            v-model="form.description"
            class="min-h-[120px] w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-200"
            placeholder="Add context about what this category covers"
          ></textarea>
        </div>
        <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
          <button
            class="inline-flex w-full items-center justify-center rounded-full bg-slate-900 px-6 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-700 sm:w-auto"
            :class="{ 'cursor-not-allowed opacity-60': formLoading }"
            :disabled="formLoading"
            type="submit"
          >
            {{ editingId ? 'Update category' : 'Create category' }}
          </button>
          <button
            class="inline-flex w-full items-center justify-center rounded-full border border-slate-200 px-6 py-3 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:text-slate-900 sm:w-auto"
            type="button"
            @click="resetForm"
          >
            Clear form
          </button>
        </div>
        <p v-if="formError" class="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">{{ formError }}</p>
        <p v-if="success" class="rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-600">{{ success }}</p>
      </form>

      <div class="space-y-4">
        <div class="rounded-3xl border border-slate-200 bg-white/90 p-6 shadow-lg backdrop-blur">
          <header class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <h2 class="text-lg font-semibold text-slate-900">Recent categories</h2>
              <p class="text-xs text-slate-500">
                <span v-if="totalCategories === 0">No categories created yet.</span>
                <span v-else>Showing {{ recentCategories.length }} of {{ totalCategories }} categories</span>
              </p>
            </div>
            <RouterLink
              :to="{ name: 'admin-category-library' }"
              class="inline-flex items-center justify-center rounded-full border border-slate-200 px-4 py-2 text-xs font-semibold text-slate-700 transition hover:border-brand-300 hover:text-brand-600"
            >
              Open category library
              <span aria-hidden="true">→</span>
            </RouterLink>
          </header>
          <p v-if="loading" class="mt-6 text-sm text-slate-500">Loading categories…</p>
          <p v-else-if="error" class="mt-6 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">{{ error }}</p>
          <p v-else-if="recentCategories.length === 0" class="mt-6 text-sm text-slate-500">No categories yet. Create your first topic on the left.</p>
          <ul v-else class="mt-6 space-y-4 text-sm">
            <li
              v-for="category in recentCategories"
              :key="category.id"
              class="rounded-2xl border border-slate-200 p-4 shadow-sm"
            >
              <div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                <div class="space-y-2">
                  <div class="flex items-center gap-3">
                    <span class="text-2xl">{{ category.icon || '📝' }}</span>
                    <div>
                      <p class="text-base font-semibold text-slate-900">{{ category.name }}</p>
                      <p class="text-xs uppercase tracking-[0.25em] text-slate-400">{{ category.slug }}</p>
                    </div>
                  </div>
                  <p class="text-sm leading-6 text-slate-600">{{ category.description || 'No description yet.' }}</p>
                </div>
                <div class="flex items-center gap-3">
                  <button
                    class="rounded-full border border-slate-200 px-4 py-2 text-xs font-semibold text-slate-700 transition hover:border-slate-300 hover:text-slate-900"
                    type="button"
                    @click="editCategory(category)"
                  >
                    Edit
                  </button>
                  <button
                    class="rounded-full border border-red-200 px-4 py-2 text-xs font-semibold text-red-500 transition hover:bg-red-50"
                    type="button"
                    @click="deleteCategory(category.id)"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </li>
          </ul>
          <p
            v-if="hasMoreCategories && !loading"
            class="mt-6 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-xs text-slate-500"
          >
            Showing the latest {{ recentCategories.length }} categories. Visit the
            <RouterLink :to="{ name: 'admin-category-library' }" class="font-semibold text-brand-600 hover:text-brand-500">
              full category library
            </RouterLink>
            for complete management.
          </p>
        </div>
      </div>
    </div>
  </section>
</template>
