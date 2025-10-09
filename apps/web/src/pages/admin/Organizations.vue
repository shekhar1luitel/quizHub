<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'

import { http } from '../../api/http'

interface OrganizationItem {
  id: number
  name: string
  slug: string
  type: string | null
  status: string
  created_at: string
  logo_url: string | null
}

const organizations = ref<OrganizationItem[]>([])
const loading = ref(false)
const error = ref('')
const success = ref('')

const creating = ref(false)
const createError = ref('')
const actionError = ref('')
const statusUpdating = ref<Record<number, boolean>>({})

const form = reactive({
  name: '',
  slug: '',
  type: '',
  logoUrl: '',
})

const slugTouched = ref(false)

const slugify = (value: string) =>
  value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 255)

watch(
  () => form.name,
  (value) => {
    if (!slugTouched.value) {
      form.slug = slugify(value)
    }
  },
)

const normalizeSlug = () => {
  slugTouched.value = true
  form.slug = slugify(form.slug)
}

const markSlugTouched = () => {
  slugTouched.value = true
}

const resetForm = () => {
  form.name = ''
  form.slug = ''
  form.type = ''
  form.logoUrl = ''
  slugTouched.value = false
}

const loadOrganizations = async () => {
  loading.value = true
  error.value = ''
  actionError.value = ''
  try {
    const { data } = await http.get<OrganizationItem[]>('/organizations', { params: { limit: 200 } })
    organizations.value = data
    statusUpdating.value = {}
  } catch (err) {
    console.error(err)
    error.value = 'Unable to load organizations right now.'
  } finally {
    loading.value = false
  }
}

const createOrganization = async () => {
  success.value = ''
  createError.value = ''

  if (!form.name.trim()) {
    createError.value = 'Enter an organization name.'
    return
  }

  if (!form.slug.trim()) {
    createError.value = 'Enter an organization slug.'
    return
  }

  creating.value = true
  try {
    const payload = {
      name: form.name.trim(),
      slug: form.slug.trim(),
      type: form.type.trim() || null,
      logo_url: form.logoUrl.trim() || null,
    }
    const { data } = await http.post<OrganizationItem>('/organizations', payload)
    success.value = `Created ${data.name}.`
    resetForm()
    await loadOrganizations()
  } catch (err: any) {
    console.error(err)
    const message = err?.response?.data?.detail
    createError.value = typeof message === 'string' ? message : 'Unable to create organization.'
  } finally {
    creating.value = false
  }
}

const setStatusUpdating = (id: number, value: boolean) => {
  statusUpdating.value = { ...statusUpdating.value, [id]: value }
}

const toggleStatus = async (organization: OrganizationItem) => {
  actionError.value = ''
  success.value = ''
  const nextStatus = organization.status === 'active' ? 'inactive' : 'active'
  setStatusUpdating(organization.id, true)
  try {
    const { data } = await http.patch<OrganizationItem>(`/organizations/${organization.id}`, { status: nextStatus })
    success.value =
      data.status === 'active'
        ? `${data.name} is active again. Learners can access their content.`
        : `${data.name} has been disabled. Their content is now hidden.`
    await loadOrganizations()
  } catch (err: any) {
    console.error(err)
    const message = err?.response?.data?.detail
    actionError.value = typeof message === 'string' ? message : 'Unable to update organization status.'
  } finally {
    const updated = { ...statusUpdating.value }
    delete updated[organization.id]
    statusUpdating.value = updated
  }
}

onMounted(() => {
  void loadOrganizations()
})
</script>

<template>
  <section class="space-y-8">
    <header class="space-y-2">
      <div class="inline-flex items-center gap-2 rounded-full bg-slate-100 px-4 py-1 text-xs font-semibold uppercase tracking-widest text-slate-600">
        Platform management
      </div>
      <div class="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 class="text-3xl font-semibold text-slate-900">Organization directory</h1>
          <p class="text-sm text-slate-500">
            Create new tenants, pause inactive ones, and keep track of who currently has access to their learning content.
          </p>
        </div>
        <div class="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-xs text-slate-500">
          <span class="font-semibold text-slate-900">{{ organizations.length }}</span>
          registered organizations
        </div>
      </div>
    </header>

    <p v-if="error" class="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">{{ error }}</p>

    <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <header class="flex flex-col gap-2">
        <h2 class="text-lg font-semibold text-slate-900">Create organization</h2>
        <p class="text-xs text-slate-500">Provision a new tenant so their admins can manage quizzes and learners.</p>
      </header>

      <form class="mt-6 grid gap-4 md:grid-cols-4" @submit.prevent="createOrganization">
        <label class="flex flex-col gap-1 text-sm text-slate-600 md:col-span-1">
          Organization name
          <input
            v-model="form.name"
            type="text"
            class="rounded-xl border border-slate-200 px-3 py-2 text-sm"
            placeholder="Acme Labs"
          />
        </label>
        <label class="flex flex-col gap-1 text-sm text-slate-600 md:col-span-1">
          Slug
          <input
            v-model="form.slug"
            type="text"
            class="rounded-xl border border-slate-200 px-3 py-2 text-sm"
            placeholder="acme-labs"
            @focus="markSlugTouched"
            @blur="normalizeSlug"
          />
        </label>
        <label class="flex flex-col gap-1 text-sm text-slate-600 md:col-span-1">
          Type
          <input
            v-model="form.type"
            type="text"
            class="rounded-xl border border-slate-200 px-3 py-2 text-sm"
            placeholder="bootcamp, university, corporate..."
          />
        </label>
        <label class="flex flex-col gap-1 text-sm text-slate-600 md:col-span-1">
          Logo URL
          <input
            v-model="form.logoUrl"
            type="url"
            class="rounded-xl border border-slate-200 px-3 py-2 text-sm"
            placeholder="https://cdn.example.com/logo.png"
          />
        </label>
        <div class="md:col-span-4">
          <button
            type="submit"
            class="inline-flex items-center gap-2 rounded-full bg-slate-900 px-5 py-2 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-400"
            :disabled="creating"
          >
            <svg
              v-if="creating"
              class="h-4 w-4 animate-spin text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path
                class="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 0 1 8-8v4a4 4 0 0 0-4 4H4z"
              />
            </svg>
            <span>{{ creating ? 'Creating...' : 'Create organization' }}</span>
          </button>
        </div>
      </form>

      <p v-if="createError" class="mt-3 rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs text-amber-800">
        {{ createError }}
      </p>
      <p v-if="success" class="mt-3 rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-xs text-emerald-800">
        {{ success }}
      </p>
    </section>

    <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <header class="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 class="text-lg font-semibold text-slate-900">Existing organizations</h2>
          <p class="text-xs text-slate-500">
            Track status, disable tenants when needed, and keep a record of who currently has platform access.
          </p>
        </div>
      </header>

      <div class="mt-5 overflow-x-auto">
        <p v-if="actionError" class="mb-3 rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs text-amber-800">
          {{ actionError }}
        </p>
        <table class="min-w-full text-left text-sm text-slate-600">
          <thead>
            <tr class="border-b border-slate-200 text-xs uppercase tracking-widest text-slate-400">
              <th class="py-2 pr-4">Name</th>
              <th class="py-2 pr-4">Logo</th>
              <th class="py-2 pr-4">Slug</th>
              <th class="py-2 pr-4">Type</th>
              <th class="py-2 pr-4">Status</th>
              <th class="py-2 pr-4">Created</th>
              <th class="py-2 pr-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loading">
              <td colspan="7" class="py-6 text-center text-xs text-slate-400">Loading organizations...</td>
            </tr>
            <tr v-else-if="organizations.length === 0">
              <td colspan="7" class="py-6 text-center text-xs text-slate-400">No organizations yet.</td>
            </tr>
            <tr
              v-for="organization in organizations"
              v-else
              :key="organization.id"
              :class="[
                'border-b border-slate-100 text-sm',
                organization.status === 'active' ? 'text-slate-600' : 'text-slate-500 bg-slate-50',
              ]"
            >
              <td class="py-3 pr-4">
                <div
                  class="font-semibold"
                  :class="organization.status === 'active' ? 'text-slate-900' : 'text-slate-700'"
                >
                  {{ organization.name }}
                </div>
                <p v-if="organization.status !== 'active'" class="text-xs text-amber-600">Disabled tenant</p>
              </td>
              <td class="py-3 pr-4">
                <div class="h-10 w-10 overflow-hidden rounded-xl border border-slate-200 bg-slate-50">
                  <img
                    v-if="organization.logo_url"
                    :src="organization.logo_url"
                    :alt="`${organization.name} logo`"
                    class="h-full w-full object-contain p-1.5"
                  />
                  <div
                    v-else
                    class="flex h-full w-full items-center justify-center text-xs font-semibold uppercase tracking-[0.25em] text-slate-400"
                  >
                    {{ organization.name.charAt(0) }}
                  </div>
                </div>
              </td>
              <td class="py-3 pr-4 text-xs text-slate-500">{{ organization.slug }}</td>
              <td class="py-3 pr-4 capitalize">{{ organization.type || '—' }}</td>
              <td class="py-3 pr-4">
                <span
                  class="inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-semibold"
                  :class="organization.status === 'active' ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'"
                >
                  <span
                    class="h-2 w-2 rounded-full"
                    :class="organization.status === 'active' ? 'bg-emerald-500' : 'bg-slate-400'"
                  ></span>
                  {{ organization.status }}
                </span>
              </td>
              <td class="py-3 pr-4 text-xs text-slate-500">
                {{ new Date(organization.created_at).toLocaleDateString() }}
              </td>
              <td class="py-3 pr-4 text-right">
                <button
                  class="inline-flex items-center gap-2 rounded-full px-4 py-1.5 text-xs font-semibold transition disabled:cursor-not-allowed disabled:opacity-60"
                  :class="
                    organization.status === 'active'
                      ? 'bg-rose-600 text-white hover:bg-rose-500'
                      : 'bg-emerald-600 text-white hover:bg-emerald-500'
                  "
                  type="button"
                  :disabled="statusUpdating[organization.id]"
                  @click="toggleStatus(organization)"
                >
                  <svg
                    v-if="statusUpdating[organization.id]"
                    class="h-4 w-4 animate-spin text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                    <path
                      class="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 0 1 8-8v4a4 4 0 0 0-4 4H4z"
                    />
                  </svg>
                  <span>
                    {{ organization.status === 'active' ? 'Disable' : 'Enable' }}
                  </span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </section>
</template>
