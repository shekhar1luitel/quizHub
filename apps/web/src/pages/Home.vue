<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()

const isAuthenticated = computed(() => auth.isAuthenticated)

const primaryCta = computed(() =>
  isAuthenticated.value
    ? { label: 'Go to Dashboard', to: { name: 'dashboard' } }
    : { label: 'Start Practicing', to: { name: 'register' } },
)

const secondaryCta = computed(() =>
  isAuthenticated.value
    ? { label: 'Browse Quizzes', to: { name: 'dashboard' } }
    : { label: 'Login to Continue', to: { name: 'login' } },
)

const features = [
  {
    title: 'Comprehensive Question Bank',
    description:
      'Access thousands of carefully curated questions across multiple categories and difficulty levels.',
    icon: 'book',
  },
  {
    title: 'Mock Tests',
    description:
      'Take timed mock tests that simulate real exam conditions to build confidence and speed.',
    icon: 'users',
  },
  {
    title: 'Performance Tracking',
    description:
      'Monitor your progress with detailed analytics and identify areas for improvement.',
    icon: 'trophy',
  },
  {
    title: 'Detailed Results',
    description:
      'Get instant feedback with comprehensive result analysis and performance insights.',
    icon: 'chart',
  },
]

const highlights = [
  { label: 'Students practicing', value: '10k+' },
  { label: 'Mock tests hosted', value: '320+' },
  { label: 'Average score boost', value: '18%' },
  { label: 'Success stories', value: '2.3k+' },
]
</script>

<template>
  <div class="min-h-screen bg-background text-foreground">
    <header class="border-b border-border bg-card">
      <div class="container mx-auto flex items-center justify-between px-4 py-4">
        <div class="flex items-center gap-2">
          <span class="inline-flex h-10 w-10 items-center justify-center rounded-md bg-secondary/20 text-secondary">
            <svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M3 5a2 2 0 0 1 2-2h6v16H5a2 2 0 0 0-2 2Z" />
              <path d="M21 5a2 2 0 0 0-2-2h-6v16h6a2 2 0 0 1 2 2Z" />
              <path d="M12 4v16" />
            </svg>
          </span>
          <RouterLink :to="{ name: 'home' }" class="text-2xl font-bold">
            QuizMaster
          </RouterLink>
        </div>
        <div class="flex gap-2">
          <RouterLink
            :to="{ name: isAuthenticated ? 'dashboard' : 'login' }"
            class="inline-flex items-center justify-center rounded-md border border-border px-4 py-2 text-sm font-medium transition hover:bg-muted"
          >
            {{ isAuthenticated ? 'Dashboard' : 'Login' }}
          </RouterLink>
          <RouterLink
            v-if="!isAuthenticated"
            :to="{ name: 'register' }"
            class="inline-flex items-center justify-center rounded-md bg-secondary px-4 py-2 text-sm font-medium text-secondary-foreground transition hover:bg-secondary/90"
          >
            Sign Up
          </RouterLink>
        </div>
      </div>
    </header>

    <main>
      <section class="bg-card py-20 px-4">
        <div class="container mx-auto grid max-w-6xl gap-12 lg:grid-cols-[3fr,2fr]">
          <div class="space-y-6 text-center lg:text-left">
            <h1 class="text-4xl font-bold leading-tight md:text-6xl">
              Master Your Competitive Exams
            </h1>
            <p class="text-lg text-muted-foreground">
              Practice with thousands of questions, track your progress, and ace your competitive exams with our comprehensive
              mock test platform.
            </p>
            <div class="flex flex-col items-center justify-center gap-4 sm:flex-row lg:justify-start">
              <RouterLink
                :to="primaryCta.to"
                class="inline-flex items-center justify-center rounded-md bg-secondary px-6 py-3 text-sm font-semibold text-secondary-foreground shadow-sm transition hover:bg-secondary/90"
              >
                {{ primaryCta.label }}
              </RouterLink>
              <RouterLink
                :to="secondaryCta.to"
                class="inline-flex items-center justify-center rounded-md border border-border px-6 py-3 text-sm font-semibold transition hover:bg-muted"
              >
                {{ secondaryCta.label }}
              </RouterLink>
            </div>
          </div>

          <dl class="grid grid-cols-2 gap-4">
            <div
              v-for="highlight in highlights"
              :key="highlight.label"
              class="rounded-lg border border-border bg-background/80 p-6 text-center shadow-sm backdrop-blur"
            >
              <dt class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                {{ highlight.label }}
              </dt>
              <dd class="mt-3 text-3xl font-bold">
                {{ highlight.value }}
              </dd>
            </div>
          </dl>
        </div>
      </section>

      <section class="py-16 px-4">
        <div class="container mx-auto max-w-6xl">
          <h2 class="text-3xl font-bold text-center">Why Choose QuizMaster?</h2>
          <p class="mt-4 text-center text-muted-foreground">
            Discover the tools that help thousands of aspirants study smarter every day.
          </p>
          <div class="mt-12 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            <article
              v-for="feature in features"
              :key="feature.title"
              class="flex flex-col gap-4 rounded-lg border border-border bg-card p-6 text-left shadow-sm transition hover:-translate-y-1 hover:shadow-lg"
            >
              <span class="inline-flex h-12 w-12 items-center justify-center rounded-full bg-secondary/15 text-secondary">
                <svg
                  v-if="feature.icon === 'book'"
                  class="h-7 w-7"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  aria-hidden="true"
                >
                  <path d="M3.5 5A2.5 2.5 0 0 1 6 2.5h6V19H6a2.5 2.5 0 0 0-2.5 2.5Z" />
                  <path d="M20.5 5A2.5 2.5 0 0 0 18 2.5h-6V19h6a2.5 2.5 0 0 1 2.5 2.5Z" />
                  <path d="M12 4v15" />
                </svg>
                <svg
                  v-else-if="feature.icon === 'users'"
                  class="h-7 w-7"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  aria-hidden="true"
                >
                  <path d="M17 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2" />
                  <circle cx="9" cy="7" r="4" />
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                  <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                </svg>
                <svg
                  v-else-if="feature.icon === 'trophy'"
                  class="h-7 w-7"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  aria-hidden="true"
                >
                  <path d="M8 21h8" />
                  <path d="M12 17a5 5 0 0 0 5-5V4H7v8a5 5 0 0 0 5 5Z" />
                  <path d="M8 4V2h8v2" />
                  <path d="M4 6h3v4a3 3 0 0 1-3-3Z" />
                  <path d="M20 6h-3v4a3 3 0 0 0 3-3Z" />
                </svg>
                <svg
                  v-else
                  class="h-7 w-7"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  aria-hidden="true"
                >
                  <path d="M3 3v18" />
                  <path d="M7 13v8" />
                  <path d="M11 9v12" />
                  <path d="M15 5v16" />
                  <path d="M19 11v10" />
                </svg>
              </span>
              <div>
                <h3 class="text-lg font-semibold">{{ feature.title }}</h3>
                <p class="mt-2 text-sm text-muted-foreground">{{ feature.description }}</p>
              </div>
            </article>
          </div>
        </div>
      </section>
    </main>

    <footer class="border-t border-border py-8 px-4">
      <div class="container mx-auto text-center text-sm text-muted-foreground">
        © 2024 QuizMaster. Built for competitive exam success.
      </div>
    </footer>
  </div>
</template>
