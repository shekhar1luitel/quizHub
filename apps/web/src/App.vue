<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import type { RouteLocationRaw } from 'vue-router'

import { useAuthStore } from './stores/auth'

interface SidebarLink {
  label: string
  to: RouteLocationRaw
  icon: string
  badge?: string
}

interface SidebarSection {
  title: string
  items: SidebarLink[]
}

interface HeaderAction {
  label: string
  to: RouteLocationRaw
  icon: string
}

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const sidebarOpen = ref(false)

const logout = () => {
  auth.logout()
  router.push({ name: 'home' })
}

const isAdminRoute = computed(() => Boolean(route.meta.requiresAdmin))

const exploreLinks = computed<SidebarLink[]>(() => [
  {
    label: 'Home',
    to: { name: 'home' },
    icon: `
      <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12 11.204 3.045c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75V19.5A1.5 1.5 0 0 0 6 21h4.5v-5.25c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21H19.5a1.5 1.5 0 0 0 1.5-1.5V9.75" />
    `,
  },
  {
    label: 'Quiz setup',
    to: { name: 'quiz-setup' },
    icon: `
      <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 8.25h7.5M8.25 12h7.5M8.25 15.75h7.5M4.5 5.25h15v12H4.5z" />
    `,
  },
  {
    label: 'Categories',
    to: { name: 'categories' },
    icon: `
      <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 3.75h6.75v6.75H4.5zM12.75 13.5H19.5v6.75h-6.75zM12.75 3.75h6.75v6.75h-6.75zM4.5 13.5h6.75v6.75H4.5z" />
    `,
  },
  {
    label: 'Bookmarks',
    to: { name: 'bookmarks' },
    icon: `
      <path stroke-linecap="round" stroke-linejoin="round" d="M6.75 4.5h6.75L17.25 9v9l-6-3-6 3V6a1.5 1.5 0 0 1 1.5-1.5z" />
    `,
  },
])

const studyLinks = computed<SidebarLink[]>(() => {
  if (!auth.isAuthenticated) return []

  return [
    {
      label: 'Dashboard',
      to: { name: 'dashboard' },
      icon: `
        <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 3v16.5a1.5 1.5 0 0 0 1.5 1.5H18.75M7.5 14.25l3.75-3.75 2.25 2.25 3.75-3.75" />
      `,
      badge: 'Progress hub',
    },
    {
      label: 'Notifications',
      to: { name: 'notifications' },
      icon: `
        <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 8.25c0-4.556 3.694-8.25 8.25-8.25s8.25 3.694 8.25 8.25c0 3.464 1.636 5.932 2.327 6.857.36.486.071 1.143-.487 1.143H1.91c-.558 0-.847-.657-.487-1.143.69-.925 2.327-3.393 2.327-6.857Zm6 9.75a2.25 2.25 0 0 0 4.5 0" />
      `,
      badge: 'Updates',
    },
    {
      label: 'Analytics',
      to: { name: 'analytics' },
      icon: `
        <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 19.5h15M6.75 9.75v7.5M12 4.5v12.75M17.25 12.75v4.5" />
      `,
      badge: 'Insights',
    },
    {
      label: 'Results history',
      to: { name: 'history' },
      icon: `
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 8.25v4.5h3m6-.75a9 9 0 1 1-4.219-7.594" />
      `,
    },
  ]
})

const adminMenuLinks = computed<SidebarLink[]>(() => {
  if (!auth.isAdmin) return []

  return [
    {
      label: 'Overview',
      to: { name: 'admin' },
      badge: 'Live stats',
      icon: `
        <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75h3v7.5h-3zM10.5 8.25h3v12h-3zM16.5 4.5h3v15.75h-3z" />
      `,
    },
    {
      label: 'Question studio',
      to: { name: 'admin-questions' },
      badge: 'Compose & edit',
      icon: `
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v12M6 12h12" />
      `,
    },
    {
      label: 'Question library',
      to: { name: 'admin-question-library' },
      badge: 'Full bank',
      icon: `
        <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 5.25h15M4.5 12h15M4.5 18.75h15" />
      `,
    },
    {
      label: 'Quiz studio',
      to: { name: 'admin-quizzes' },
      badge: 'Assemble tests',
      icon: `
        <path stroke-linecap="round" stroke-linejoin="round" d="M5.25 5.25h13.5v5.25H5.25zM5.25 12.75h13.5v6H5.25zM12 12.75v6" />
      `,
    },
    {
      label: 'Quiz library',
      to: { name: 'admin-quiz-library' },
      badge: 'Published sets',
      icon: `
        <path stroke-linecap="round" stroke-linejoin="round" d="M5.25 6.75h13.5v10.5H5.25zM5.25 11.25h13.5" />
      `,
    },
    {
      label: 'Category studio',
      to: { name: 'admin-categories' },
      badge: 'Create topics',
      icon: `
        <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 6.75h6.75v6.75H4.5zM12.75 6.75H19.5v6.75h-6.75zM4.5 15.75h6.75v6.75H4.5zM12.75 15.75H19.5v6.75h-6.75z" />
      `,
    },
    {
      label: 'Category library',
      to: { name: 'admin-category-library' },
      badge: 'Browse taxonomy',
      icon: `
        <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 5.25h6v6h-6zM13.5 5.25h6v6h-6zM13.5 14.25h6v6h-6zM4.5 14.25h6v6h-6z" />
      `,
    },
  ]
})

const platformLinks = computed<SidebarLink[]>(() => {
  if (!auth.isSuperuser) return []

  return [
    {
      label: 'User management',
      to: { name: 'admin-users' },
      badge: 'Provision access',
      icon: `
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 6.75A2.25 2.25 0 1 0 12 2.25a2.25 2.25 0 0 0 0 4.5ZM4.125 8.25a2.625 2.625 0 1 0 0 5.25 2.625 2.625 0 0 0 0-5.25Zm15.75 0a2.625 2.625 0 1 0 0 5.25 2.625 2.625 0 0 0 0-5.25ZM4.125 15.75A3.375 3.375 0 0 0 .75 19.125v.375A.75.75 0 0 0 1.5 20.25h5.25a.75.75 0 0 0 .75-.75v-.375A3.375 3.375 0 0 0 4.125 15.75Zm7.875.75a3.375 3.375 0 0 0-3.375 3.375v.375a.75.75 0 0 0 .75.75h5.25a.75.75 0 0 0 .75-.75v-.375A3.375 3.375 0 0 0 12 16.5Zm7.875-.75a3.375 3.375 0 0 0-3.375 3.375v.375a.75.75 0 0 0 .75.75h5.25a.75.75 0 0 0 .75-.75v-.375A3.375 3.375 0 0 0 19.875 15.75Z" />
      `,
    },
    {
      label: 'Mail delivery',
      to: { name: 'admin-mail-config' },
      badge: 'SMTP settings',
      icon: `
        <path stroke-linecap="round" stroke-linejoin="round" d="M3 5.25h18V18a1.5 1.5 0 0 1-1.5 1.5H4.5A1.5 1.5 0 0 1 3 18V5.25zM3 5.25l9 6 9-6" />
      `,
    },
  ]
})

const navSections = computed<SidebarSection[]>(() => {
  const sections: SidebarSection[] = [
    { title: 'Explore', items: exploreLinks.value },
  ]

  if (studyLinks.value.length > 0) {
    sections.push({ title: 'Your prep', items: studyLinks.value })
  }

  if (adminMenuLinks.value.length > 0) {
    sections.push({ title: 'Admin', items: adminMenuLinks.value })
  }

  if (platformLinks.value.length > 0) {
    sections.push({ title: 'Platform', items: platformLinks.value })
  }

  return sections
})

const isLinkActive = (item: SidebarLink) => {
  const resolved = router.resolve(item.to)
  if (resolved.name && route.name) {
    return resolved.name === route.name
  }
  return resolved.href === route.href
}

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
}

const closeSidebar = () => {
  sidebarOpen.value = false
}

watch(
  () => route.fullPath,
  () => {
    sidebarOpen.value = false
  }
)

const pageTitle = computed(() => {
  if (typeof route.meta?.title === 'string') return route.meta.title
  if (typeof route.name === 'string') {
    return route.name
      .replace(/[-_]/g, ' ')
      .replace(/\b\w/g, (char) => char.toUpperCase())
  }
  return 'QuizMaster'
})

const headerContext = computed(() => (isAdminRoute.value ? 'Admin console' : 'QuizMaster'))

const headerAction = computed<HeaderAction | null>(() => {
  if (auth.isAdmin) {
    if (route.name === 'admin-quizzes') {
      return {
        label: 'Quiz library',
        to: { name: 'admin-quiz-library' },
        icon: `
          <path stroke-linecap="round" stroke-linejoin="round" d="M5.25 6.75h13.5v10.5H5.25zM5.25 11.25h13.5" />
        `,
      }
    }
    return {
      label: 'Build quiz',
      to: { name: 'admin-quizzes' },
      icon: `
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 5.25v13.5M5.25 12h13.5" />
      `,
    }
  }

  if (auth.isAuthenticated) {
    if (route.name === 'analytics') {
      return {
        label: 'View dashboard',
        to: { name: 'dashboard' },
        icon: `
          <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75h15M4.5 9h15M4.5 6h15" />
        `,
      }
    }

    return {
      label: 'View analytics',
      to: { name: 'analytics' },
      icon: `
        <path stroke-linecap="round" stroke-linejoin="round" d="M4.5 19.5h15M6.75 9.75v7.5M12 4.5v12.75M17.25 12.75v4.5" />
      `,
    }
  }

  return null
})

const userRoleLabel = computed(() => {
  if (!auth.isAuthenticated) return ''
  if (auth.isSuperuser) return 'Superuser'
  return auth.isAdmin ? 'Admin' : 'Learner'
})

const currentYear = new Date().getFullYear()

onMounted(() => {
  auth.initialize()
})
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-slate-900 lg:flex">
    <transition name="fade">
      <div
        v-if="sidebarOpen"
        class="fixed inset-0 z-40 bg-slate-900/50 backdrop-blur-sm lg:hidden"
        @click="closeSidebar"
      ></div>
    </transition>

    <aside
      class="fixed inset-y-0 left-0 z-50 flex w-72 transform flex-col border-r border-slate-200 bg-white/95 shadow-xl shadow-slate-900/10 transition-transform duration-200 ease-out lg:sticky lg:top-0 lg:max-h-screen lg:translate-x-0 lg:border-r lg:shadow-none lg:overflow-y-auto"
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'"
    >
      <div class="flex h-full flex-col gap-6 overflow-y-auto pb-8">
        <div class="flex items-center justify-between px-6 pt-6">
          <RouterLink
            :to="{ name: 'home' }"
            class="flex items-center gap-3 text-base font-semibold text-slate-800 transition hover:text-brand-600"
            @click="closeSidebar"
          >
            <span
              class="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-500 via-sky-400 to-emerald-400 text-white shadow-lg shadow-brand-900/20"
              aria-hidden="true"
            >
              <span class="text-lg font-bold">Q</span>
            </span>
            <div class="flex flex-col leading-tight">
              <span class="text-xs font-semibold uppercase tracking-[0.35em] text-slate-400">
                QuizMaster
              </span>
              <span class="text-xs font-medium text-slate-500">Exam readiness suite</span>
            </div>
          </RouterLink>
          <button
            class="inline-flex items-center justify-center rounded-full border border-slate-200 bg-white p-2 text-slate-500 transition hover:border-slate-300 hover:text-slate-800 lg:hidden"
            type="button"
            @click="closeSidebar"
          >
            <svg class="h-4 w-4" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 6l8 8m0-8-8 8" />
            </svg>
          </button>
        </div>

        <nav class="flex-1 space-y-6 px-4">
          <div
            v-for="section in navSections"
            :key="section.title"
            class="space-y-3"
          >
            <p class="px-2 text-[11px] font-semibold uppercase tracking-[0.35em] text-slate-400">
              {{ section.title }}
            </p>
            <div class="space-y-1.5">
              <RouterLink
                v-for="item in section.items"
                :key="item.label"
                :to="item.to"
                class="group flex items-center gap-3 rounded-2xl px-3 py-2 transition"
                :class="isLinkActive(item)
                  ? 'bg-slate-900 text-white shadow-lg shadow-slate-900/20'
                  : 'text-slate-600 hover:bg-white/80 hover:text-slate-900'"
                @click="closeSidebar"
              >
                <span
                  class="inline-flex h-10 w-10 items-center justify-center rounded-2xl border border-slate-200/70 bg-white/70 text-slate-500 transition group-hover:border-brand-100 group-hover:bg-brand-50 group-hover:text-brand-600"
                  :class="isLinkActive(item) ? 'border-white/20 bg-white/10 text-white' : ''"
                >
                  <svg
                    class="h-5 w-5"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.5"
                    v-html="item.icon"
                  ></svg>
                </span>
                <div class="flex flex-1 flex-col">
                  <span class="font-semibold leading-tight">
                    {{ item.label }}
                  </span>
                  <span
                    v-if="item.badge"
                    class="text-[11px] font-medium uppercase tracking-[0.3em]"
                    :class="isLinkActive(item) ? 'text-white/70' : 'text-slate-400 group-hover:text-slate-500'"
                  >
                    {{ item.badge }}
                  </span>
                </div>
                <span
                  class="h-2 w-2 rounded-full transition"
                  :class="isLinkActive(item) ? 'bg-brand-400' : 'bg-transparent group-hover:bg-brand-200'"
                ></span>
              </RouterLink>
            </div>
          </div>
        </nav>

        <div
          v-if="auth.isAdmin"
          class="mx-4 mt-auto space-y-3 rounded-2xl border border-emerald-200 bg-emerald-50/70 p-4 text-xs text-emerald-700"
        >
          <p class="text-[11px] font-semibold uppercase tracking-[0.35em] text-emerald-500">
            Featured tip
          </p>
          <p>
            Only active quizzes appear to learners. Activate your latest set in Quiz Studio to replace the
            “Coming soon” banner on the homepage.
          </p>
          <RouterLink
            :to="{ name: 'admin-quizzes' }"
            class="inline-flex items-center gap-1 text-xs font-semibold text-emerald-700 transition hover:text-emerald-600"
            @click="closeSidebar"
          >
            Open Quiz Studio
            <span aria-hidden="true">→</span>
          </RouterLink>
        </div>
      </div>
    </aside>

    <div class="flex flex-1 flex-col">
      <header class="sticky top-0 z-30 border-b border-slate-200/70 bg-white/85 backdrop-blur">
        <div class="flex items-center justify-between gap-4 px-4 py-4 sm:px-6">
          <div class="flex items-center gap-3">
            <button
              class="inline-flex items-center justify-center rounded-full border border-slate-200 bg-white p-2 text-slate-500 transition hover:border-slate-300 hover:text-slate-800 lg:hidden"
              type="button"
              @click="toggleSidebar"
            >
              <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <div>
              <p class="text-[11px] font-semibold uppercase tracking-[0.35em] text-slate-400">
                {{ headerContext }}
              </p>
              <h1 class="text-xl font-semibold leading-tight text-slate-900 sm:text-2xl">
                {{ pageTitle }}
              </h1>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <RouterLink
              v-if="headerAction"
              :to="headerAction.to"
              class="hidden items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-brand-300 hover:text-brand-600 sm:inline-flex"
            >
              <svg class="h-4 w-4" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
                <g v-html="headerAction.icon"></g>
              </svg>
              {{ headerAction.label }}
            </RouterLink>
            <template v-if="!auth.isAuthenticated">
              <RouterLink
                :to="{ name: 'login' }"
                class="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 shadow-sm transition hover:border-brand-300 hover:text-brand-600"
              >
                Login
              </RouterLink>
              <RouterLink
                :to="{ name: 'register' }"
                class="inline-flex items-center gap-2 rounded-full bg-slate-900 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-slate-900/20 transition hover:bg-slate-700"
              >
                Get started
              </RouterLink>
            </template>
            <template v-else>
              <div class="hidden items-center gap-2 rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-500 sm:inline-flex">
                <span class="inline-flex h-2 w-2 rounded-full" :class="auth.isAdmin ? 'bg-emerald-500' : 'bg-brand-500'"></span>
                {{ auth.user?.email }}
                <span class="rounded-full bg-white/60 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-slate-500">
                  {{ userRoleLabel }}
                </span>
              </div>
              <button
                class="inline-flex items-center gap-2 rounded-full bg-slate-900 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-slate-900/20 transition hover:bg-slate-700"
                type="button"
                @click="logout"
              >
                <svg class="h-4 w-4" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M11 4h-1.5a3.5 3.5 0 0 0 0 7H11m0 0-2-2m2 2-2 2m4-9h1a3 3 0 0 1 3 3v6a3 3 0 0 1-3 3h-1" />
                </svg>
                Logout
              </button>
            </template>
          </div>
        </div>
      </header>

      <main class="flex-1">
        <div class="px-4 pb-16 pt-6 sm:px-8">
          <RouterView />
        </div>
      </main>

      <footer class="border-t border-slate-200/70 bg-white/80 py-6 text-sm text-slate-500 backdrop-blur">
        <div class="mx-auto flex w-full max-w-6xl flex-col items-center justify-between gap-4 px-4 text-xs font-semibold uppercase tracking-[0.3em] sm:flex-row sm:px-8 sm:text-[11px]">
          <p class="text-[11px] font-medium normal-case tracking-normal text-slate-400">
            © {{ currentYear }} QuizMaster · Crafted for exam success.
          </p>
          <div class="flex items-center gap-3 text-slate-400">
            <RouterLink :to="{ name: 'home' }" class="transition hover:text-brand-600">Home</RouterLink>
            <RouterLink
              :to="{ name: 'categories' }"
              class="transition hover:text-brand-600"
            >
              Categories
            </RouterLink>
            <RouterLink
              v-if="auth.isAuthenticated"
              :to="{ name: 'dashboard' }"
              class="transition hover:text-brand-600"
            >
              Dashboard
            </RouterLink>
            <RouterLink
              v-if="auth.isAdmin"
              :to="{ name: 'admin' }"
              class="transition hover:text-brand-600"
            >
              Admin
            </RouterLink>
          </div>
        </div>
      </footer>
    </div>
  </div>
</template>
