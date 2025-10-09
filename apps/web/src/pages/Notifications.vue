<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { http } from '../api/http'

interface NotificationItem {
  id: number
  type: string
  title: string
  body: string
  meta?: Record<string, unknown> | null
  read_at?: string | null
  created_at: string
}

interface NotificationResponse {
  items: NotificationItem[]
  next_cursor: string | null
}

const notifications = ref<NotificationItem[]>([])
const loading = ref(false)
const loadingMore = ref(false)
const error = ref('')
const success = ref('')
const nextCursor = ref<string | null>(null)

const unreadCount = computed(() => notifications.value.filter((item) => !item.read_at).length)

const formatDate = (value: string) => new Date(value).toLocaleString()

const loadNotifications = async (reset = false) => {
  if (reset) {
    loading.value = true
    notifications.value = []
    nextCursor.value = null
  } else {
    loadingMore.value = true
  }
  error.value = ''
  success.value = ''

  try {
    const params: Record<string, string> = { limit: '20' }
    if (!reset && nextCursor.value) {
      params.cursor = nextCursor.value
    }
    const { data } = await http.get<NotificationResponse>('/notifications', { params })
    if (reset) {
      notifications.value = data.items
    } else {
      notifications.value = [...notifications.value, ...data.items]
    }
    nextCursor.value = data.next_cursor
  } catch (err) {
    console.error(err)
    error.value = 'Unable to load notifications. Please try again.'
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const markNotificationRead = async (id: number) => {
  try {
    await http.post(`/notifications/${id}/read`)
    notifications.value = notifications.value.map((item) =>
      item.id === id ? { ...item, read_at: new Date().toISOString() } : item,
    )
  } catch (err) {
    console.error(err)
    error.value = 'Unable to mark notification as read.'
  }
}

const markAllRead = async () => {
  try {
    const { data } = await http.post<{ marked: boolean; count?: number }>('/notifications/read-all')
    if (data.marked) {
      const timestamp = new Date().toISOString()
      notifications.value = notifications.value.map((item) => ({ ...item, read_at: timestamp }))
      success.value = data.count ? `Marked ${data.count} notifications as read.` : 'All notifications marked as read.'
    }
  } catch (err) {
    console.error(err)
    error.value = 'Unable to mark notifications as read.'
  }
}

onMounted(() => {
  void loadNotifications(true)
})
</script>

<template>
  <section class="space-y-6">
    <header class="space-y-2">
      <div class="inline-flex items-center gap-2 rounded-full bg-slate-100 px-4 py-1 text-xs font-semibold uppercase tracking-widest text-slate-600">
        Notifications
      </div>
      <div class="flex items-start justify-between gap-4">
        <div>
          <h1 class="text-3xl font-semibold text-slate-900">Stay on top of updates</h1>
          <p class="text-sm text-slate-500">
            System alerts, organization announcements, and important account notices appear here.
          </p>
        </div>
        <div class="flex flex-col items-end gap-3 sm:flex-row">
          <p class="text-xs font-semibold uppercase tracking-[0.35em] text-slate-400">
            {{ unreadCount }} unread
          </p>
          <button
            class="inline-flex items-center justify-center rounded-full border border-slate-200 px-4 py-2 text-xs font-semibold text-slate-700 transition hover:border-slate-300 hover:text-slate-900"
            type="button"
            @click="markAllRead"
          >
            Mark all as read
          </button>
        </div>
      </div>
    </header>

    <p v-if="error" class="rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">{{ error }}</p>
    <p v-if="success" class="rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">{{ success }}</p>

    <div v-if="loading" class="space-y-3">
      <div v-for="n in 4" :key="n" class="h-24 animate-pulse rounded-3xl bg-white"></div>
    </div>

    <ul v-else class="space-y-3">
      <li
        v-for="notification in notifications"
        :key="notification.id"
        class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm transition hover:border-slate-300"
      >
        <div class="flex items-start justify-between gap-4">
          <div class="space-y-1">
            <p class="text-xs font-semibold uppercase tracking-[0.35em] text-slate-400">{{ notification.type }}</p>
            <h2 class="text-lg font-semibold text-slate-900">{{ notification.title }}</h2>
            <p class="text-sm text-slate-600">{{ notification.body }}</p>
            <p class="text-xs text-slate-400">{{ formatDate(notification.created_at) }}</p>
          </div>
          <div class="flex flex-col items-end gap-2">
            <span
              class="inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-semibold"
              :class="notification.read_at ? 'bg-slate-100 text-slate-500' : 'bg-brand-100 text-brand-700'"
            >
              {{ notification.read_at ? 'Read' : 'Unread' }}
            </span>
            <button
              v-if="!notification.read_at"
              class="text-xs font-semibold text-brand-600 transition hover:text-brand-500"
              type="button"
              @click="markNotificationRead(notification.id)"
            >
              Mark as read
            </button>
          </div>
        </div>
      </li>
      <li v-if="!loading && notifications.length === 0" class="rounded-3xl border border-slate-200 bg-white p-6 text-sm text-slate-500">
        No notifications yet. Updates from your admins and the platform will appear here.
      </li>
    </ul>

    <div v-if="nextCursor" class="text-center">
      <button
        class="inline-flex items-center justify-center rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:text-slate-900"
        type="button"
        :disabled="loadingMore"
        @click="loadNotifications(false)"
      >
        <span v-if="loadingMore" class="animate-pulse">Loading…</span>
        <span v-else>Load older notifications</span>
      </button>
    </div>
  </section>
</template>
