<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'

import { http } from '../../api/http'

interface AdminUser {
  id: number
  username: string
  email: string
  role: string
  status: string
  account_type: string
  organization_id: number | null
  created_at: string
}

interface AdminUserListResponse {
  items: AdminUser[]
  total: number
}

interface OrganizationItem {
  id: number
  name: string
  slug: string
  status: string
  logo_url: string | null
}

const users = ref<AdminUser[]>([])
const totalUsers = ref(0)
const loading = ref(false)
const error = ref('')
const success = ref('')

const organizations = ref<OrganizationItem[]>([])
const orgError = ref('')
const hasActiveOrganizations = computed(() => organizations.value.some((org) => org.status === 'active'))

const filters = reactive({
  role: '',
  status: '',
  organization_id: '',
  search: '',
})

const form = reactive({
  username: '',
  email: '',
  password: '',
  role: 'org_admin',
  organization_id: '',
  send_invite_email: false,
  send_notification: true,
})

const creating = ref(false)

const loadOrganizations = async () => {
  orgError.value = ''
  try {
    const { data } = await http.get<OrganizationItem[]>('/organizations', { params: { limit: 100 } })
    organizations.value = data
  } catch (err) {
    console.error(err)
    orgError.value = 'Unable to load organizations.'
  }
}

const loadUsers = async () => {
  loading.value = true
  error.value = ''
  try {
    const params: Record<string, string> = { limit: '50' }
    if (filters.role) params.role = filters.role
    if (filters.status) params.status = filters.status
    if (filters.organization_id) params.organization_id = filters.organization_id
    if (filters.search) params.search = filters.search
    const { data } = await http.get<AdminUserListResponse>('/admin/users', { params })
    users.value = data.items
    totalUsers.value = data.total
  } catch (err) {
    console.error(err)
    error.value = 'Unable to load users.'
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.username = ''
  form.email = ''
  form.password = ''
  form.role = 'org_admin'
  form.organization_id = ''
  form.send_invite_email = false
  form.send_notification = true
}

const createUser = async () => {
  success.value = ''
  error.value = ''

  if (!form.username.trim()) {
    error.value = 'Enter a username for the new user.'
    return
  }
  if (!form.email.trim()) {
    error.value = 'Enter an email address.'
    return
  }
  if (form.password.length < 8) {
    error.value = 'Password must be at least 8 characters.'
    return
  }
  if (form.role === 'org_admin') {
    if (!hasActiveOrganizations.value) {
      error.value = 'No active organizations are available. Enable or create one before assigning admins.'
      return
    }
    if (!form.organization_id) {
      error.value = 'Select an organization for the admin user.'
      return
    }
  }

  creating.value = true
  try {
    const payload = {
      username: form.username,
      email: form.email,
      password: form.password,
      role: form.role,
      organization_id: form.role === 'org_admin' ? Number(form.organization_id) : null,
      send_invite_email: form.send_invite_email,
      send_notification: form.send_notification,
    }
    await http.post('/admin/users', payload)
    success.value = 'User created successfully.'
    resetForm()
    await loadUsers()
  } catch (err: any) {
    console.error(err)
    error.value = err?.response?.data?.detail || 'Unable to create user.'
  } finally {
    creating.value = false
  }
}

const toggleStatus = async (user: AdminUser) => {
  try {
    const nextStatus = user.status === 'active' ? 'inactive' : 'active'
    await http.put(`/admin/users/${user.id}/status`, { status: nextStatus })
    await loadUsers()
  } catch (err) {
    console.error(err)
    error.value = 'Unable to update user status.'
  }
}

onMounted(() => {
  void loadOrganizations()
  void loadUsers()
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
          <h1 class="text-3xl font-semibold text-slate-900">User access control</h1>
          <p class="text-sm text-slate-500">
            Provision superusers, organization admins, and support staff. Keep accounts tidy as your customer base grows.
          </p>
        </div>
        <div class="rounded-2xl border border-slate-200 bg-white px-4 py-2 text-xs text-slate-500">
          <span class="font-semibold text-slate-900">{{ totalUsers }}</span>
          total accounts
        </div>
      </div>
    </header>

    <p v-if="error" class="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">{{ error }}</p>
    <p v-if="success" class="rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">{{ success }}</p>

    <section class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <form class="grid gap-4 md:grid-cols-4" @submit.prevent="loadUsers">
        <label class="flex flex-col gap-1 text-sm text-slate-600">
          Role
          <select v-model="filters.role" class="rounded-xl border border-slate-200 px-3 py-2 text-sm">
            <option value="">All roles</option>
            <option value="superuser">Superuser</option>
            <option value="admin">Admin</option>
            <option value="org_admin">Org Admin</option>
            <option value="user">Learner</option>
          </select>
        </label>
        <label class="flex flex-col gap-1 text-sm text-slate-600">
          Status
          <select v-model="filters.status" class="rounded-xl border border-slate-200 px-3 py-2 text-sm">
            <option value="">Any status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </label>
        <label class="flex flex-col gap-1 text-sm text-slate-600">
          Organization
          <select v-model="filters.organization_id" class="rounded-xl border border-slate-200 px-3 py-2 text-sm">
            <option value="">All</option>
            <option v-for="org in organizations" :key="org.id" :value="String(org.id)">
              {{ org.name }}{{ org.status !== 'active' ? ' (disabled)' : '' }}
            </option>
          </select>
        </label>
        <label class="flex flex-col gap-1 text-sm text-slate-600 md:col-span-2">
          Search
          <input
            v-model="filters.search"
            class="rounded-xl border border-slate-200 px-3 py-2 text-sm"
            placeholder="Search by username or email"
            type="text"
          />
        </label>
        <div class="md:col-span-2 md:text-right">
          <button
            class="inline-flex items-center justify-center rounded-full bg-slate-900 px-5 py-2 text-sm font-semibold text-white transition hover:bg-slate-700"
            type="submit"
          >
            Apply filters
          </button>
        </div>
      </form>
      <p v-if="orgError" class="mt-3 text-xs text-amber-600">{{ orgError }}</p>
    </section>

    <section class="grid gap-6 lg:grid-cols-[2fr,3fr]">
      <form class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm" @submit.prevent="createUser">
        <h2 class="text-lg font-semibold text-slate-900">Create elevated user</h2>
        <p class="mt-1 text-xs text-slate-500">
          Superusers oversee the whole platform. Organization admins manage their own tenant data.
        </p>

        <div class="mt-4 space-y-4">
          <label class="flex flex-col gap-1 text-sm text-slate-600">
            Username
            <input v-model="form.username" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="e.g. campusadmin" type="text" />
          </label>
          <label class="flex flex-col gap-1 text-sm text-slate-600">
            Email
            <input v-model="form.email" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="name@example.com" type="email" />
          </label>
          <label class="flex flex-col gap-1 text-sm text-slate-600">
            Temporary password
            <input v-model="form.password" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="At least 8 characters" type="password" />
          </label>
          <label class="flex flex-col gap-1 text-sm text-slate-600">
            Role
            <select v-model="form.role" class="rounded-xl border border-slate-200 px-3 py-2 text-sm">
              <option value="org_admin">Organization admin</option>
              <option value="admin">Platform admin</option>
              <option value="superuser">Superuser</option>
            </select>
          </label>
          <label v-if="form.role === 'org_admin'" class="flex flex-col gap-1 text-sm text-slate-600">
            Organization
            <select v-model="form.organization_id" class="rounded-xl border border-slate-200 px-3 py-2 text-sm">
              <option value="">Select organization</option>
              <option
                v-for="org in organizations"
                :key="org.id"
                :disabled="org.status !== 'active'"
                :value="String(org.id)"
              >
                {{ org.name }}{{ org.status !== 'active' ? ' (disabled)' : '' }}
              </option>
            </select>
          </label>
          <p
            v-if="form.role === 'org_admin' && !hasActiveOrganizations"
            class="text-xs text-amber-600"
          >
            No active organizations available. Create or enable one before adding an org admin.
          </p>
          <label class="flex items-center gap-2 text-xs text-slate-600">
            <input v-model="form.send_notification" type="checkbox" class="h-4 w-4 rounded border-slate-200 text-brand-600" />
            Send in-app notification
          </label>
          <label class="flex items-center gap-2 text-xs text-slate-600">
            <input v-model="form.send_invite_email" type="checkbox" class="h-4 w-4 rounded border-slate-200 text-brand-600" />
            Queue invite email (requires SMTP)
          </label>
        </div>

        <button
          class="mt-6 inline-flex items-center justify-center rounded-full bg-slate-900 px-5 py-2 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:opacity-50"
          type="submit"
          :disabled="creating"
        >
          {{ creating ? 'Creating…' : 'Create user' }}
        </button>
      </form>

      <div class="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold text-slate-900">Existing accounts</h2>
          <span class="text-xs text-slate-400">{{ users.length }} shown</span>
        </div>
        <div class="mt-4 overflow-x-auto">
          <table class="min-w-full text-left text-sm">
            <thead class="text-xs uppercase tracking-wider text-slate-400">
              <tr>
                <th class="pb-2 pr-4">User</th>
                <th class="pb-2 pr-4">Role</th>
                <th class="pb-2 pr-4">Account type</th>
                <th class="pb-2 pr-4">Organization</th>
                <th class="pb-2">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="user in users" :key="user.id" class="text-slate-600">
                <td class="py-3 pr-4">
                  <div class="font-semibold text-slate-900">{{ user.username }}</div>
                  <div class="text-xs text-slate-500">{{ user.email }}</div>
                </td>
                <td class="py-3 pr-4 text-xs uppercase tracking-[0.25em]">{{ user.role }}</td>
                <td class="py-3 pr-4 text-xs uppercase tracking-[0.25em]">{{ user.account_type }}</td>
                <td class="py-3 pr-4 text-xs text-slate-500">
                  <span v-if="user.organization_id">Org #{{ user.organization_id }}</span>
                  <span v-else>—</span>
                </td>
                <td class="py-3 text-xs">
                  <button
                    class="rounded-full px-3 py-1 font-semibold"
                    :class="user.status === 'active' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-600'"
                    type="button"
                    @click="toggleStatus(user)"
                  >
                    {{ user.status === 'active' ? 'Active' : 'Inactive' }}
                  </button>
                </td>
              </tr>
              <tr v-if="!loading && users.length === 0">
                <td colspan="5" class="py-6 text-center text-sm text-slate-500">No users match the filters.</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p v-if="loading" class="mt-3 text-xs text-slate-400">Loading users…</p>
      </div>
    </section>
  </section>
</template>
