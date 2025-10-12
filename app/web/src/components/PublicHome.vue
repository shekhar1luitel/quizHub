<template>
  <div class="home">
    <section v-if="loading" class="state" aria-live="polite">
      <span class="spinner" aria-hidden="true"></span>
      <p>Loading QuizHub content…</p>
    </section>

    <section v-else-if="error" class="state error" aria-live="assertive">
      <h2>We couldn't load the latest content</h2>
      <p>{{ error }}</p>
      <button type="button" class="primary" @click="loadHome">Try again</button>
    </section>

    <template v-else>
      <section class="home-section">
        <header class="section-header">
          <div>
            <p class="eyebrow">Discover subjects</p>
            <h2>Featured categories</h2>
            <p class="subtitle">
              Browse categories curated by QuizHub and your organization. Each category
              includes active topics to help you focus your revision.
            </p>
          </div>
          <div class="section-tools">
            <label class="search" aria-label="Filter categories">
              <span class="search-icon" aria-hidden="true">🔍</span>
              <input v-model="search" type="search" placeholder="Search categories" />
            </label>
            <button type="button" class="ghost" @click="loadHome">
              Refresh
            </button>
          </div>
        </header>

        <div v-if="filteredCategories.length > 0" class="category-grid">
          <article
            v-for="category in filteredCategories"
            :key="category.slug"
            class="category-card"
          >
            <header class="category-header">
              <span class="category-icon" aria-hidden="true">{{ category.icon ?? '📚' }}</span>
              <div>
                <h3>{{ category.name }}</h3>
                <p>{{ category.description ?? 'A curated collection of practice material.' }}</p>
              </div>
            </header>

            <dl class="category-meta">
              <div>
                <dt>Difficulty</dt>
                <dd>{{ category.difficulty }}</dd>
              </div>
              <div>
                <dt>Questions</dt>
                <dd>{{ formatNumber(category.total_questions) }}</dd>
              </div>
              <div>
                <dt>Topics</dt>
                <dd>{{ category.topics.length }}</dd>
              </div>
            </dl>

            <section class="topic-preview">
              <h4>Focus areas</h4>
              <ul v-if="category.topics.length > 0">
                <li v-for="topic in getPreviewTopics(category.topics)" :key="topic.id">
                  <strong>{{ topic.name }}</strong>
                  <span>
                    {{ topic.description ?? 'Practice sessions tailored to this topic.' }}
                  </span>
                </li>
              </ul>
              <p v-else class="empty">Topics will be added soon.</p>
            </section>

            <footer class="category-actions">
              <a class="primary" :href="getPracticeUrl(category.slug)">Start practice</a>
              <a
                v-if="category.topics.length > 0"
                class="secondary"
                :href="getPracticeUrl(category.slug, category.topics[0].slug)"
              >
                Explore first topic
              </a>
            </footer>
          </article>
        </div>
        <p v-else class="empty">
          No categories match your search yet. Try a different keyword or refresh the list.
        </p>
      </section>

      <section class="home-section">
        <header class="section-header">
          <div>
            <p class="eyebrow">Join the buzz</p>
            <h2>Trending quizzes</h2>
            <p class="subtitle">
              Popular quizzes from across QuizHub. See what's helping other learners stay on
              track.
            </p>
          </div>
        </header>

        <div v-if="trendingQuizzes.length > 0" class="quiz-list">
          <article v-for="quiz in trendingQuizzes" :key="quiz.id" class="quiz-card">
            <header class="quiz-header">
              <h3>{{ quiz.title }}</h3>
              <span class="quiz-meta">{{ formatDate(quiz.created_at) }}</span>
            </header>
            <p>{{ quiz.description ?? 'Challenge yourself with this practice quiz.' }}</p>
            <dl class="quiz-stats">
              <div>
                <dt>Questions</dt>
                <dd>{{ quiz.question_count }}</dd>
              </div>
              <div>
                <dt>Attempts</dt>
                <dd>{{ formatNumber(quiz.total_attempts) }}</dd>
              </div>
            </dl>
            <footer class="quiz-actions">
              <a class="secondary" :href="getQuizUrl(quiz.id)">View quiz</a>
            </footer>
          </article>
        </div>
        <p v-else class="empty">No quizzes are trending yet. Check back soon!</p>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

type Topic = {
  id: number
  slug: string
  name: string
  description?: string | null
  subject_id: number
}

type PublicCategorySummary = {
  slug: string
  name: string
  description?: string | null
  icon?: string | null
  total_questions: number
  difficulty: string
  topics: Topic[]
}

type PublicQuizSummary = {
  id: number
  title: string
  description?: string | null
  question_count: number
  total_attempts: number
  created_at: string
}

type PublicHomeResponse = {
  featured_categories: PublicCategorySummary[]
  trending_quizzes: PublicQuizSummary[]
}

const data = ref<PublicHomeResponse | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const search = ref('')

const categories = computed(() => data.value?.featured_categories ?? [])
const trendingQuizzes = computed(() => data.value?.trending_quizzes ?? [])

const filteredCategories = computed(() => {
  if (!search.value.trim()) {
    return categories.value
  }
  const term = search.value.toLowerCase()
  return categories.value.filter((category) => {
    const description = category.description ?? ''
    return (
      category.name.toLowerCase().includes(term) ||
      description.toLowerCase().includes(term) ||
      category.topics.some((topic) => topic.name.toLowerCase().includes(term))
    )
  })
})

function formatNumber(value: number): string {
  return new Intl.NumberFormat().format(value)
}

function formatDate(isoString: string): string {
  const date = new Date(isoString)
  return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium' }).format(date)
}

function getPracticeUrl(subjectSlug: string, topicSlug?: string): string {
  if (topicSlug) {
    return `/practice/categories/${subjectSlug}?topic=${encodeURIComponent(topicSlug)}`
  }
  return `/practice/categories/${subjectSlug}`
}

function getQuizUrl(quizId: number): string {
  return `/quizzes/${quizId}`
}

function getPreviewTopics(topics: Topic[]): Topic[] {
  if (topics.length <= 3) {
    return topics
  }
  return topics.slice(0, 3)
}

async function loadHome(): Promise<void> {
  loading.value = true
  error.value = null
  try {
    const response = await fetch('/api/public/home?limit=6')
    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`)
    }
    const payload = (await response.json()) as PublicHomeResponse
    data.value = payload
  } catch (err) {
    console.error(err)
    error.value = err instanceof Error ? err.message : 'Unknown error'
  } finally {
    loading.value = false
  }
}

onMounted(loadHome)
</script>

<style scoped>
.home {
  display: grid;
  gap: clamp(2rem, 4vw, 3rem);
}

.home-section {
  background: white;
  border-radius: 1.5rem;
  padding: clamp(1.75rem, 4vw, 2.5rem);
  box-shadow: 0 25px 55px -35px rgba(30, 64, 175, 0.4);
  display: grid;
  gap: 2rem;
}

.section-header {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.section-header h2 {
  margin: 0;
  font-size: clamp(1.5rem, 2.8vw, 2.1rem);
}

.section-header .subtitle {
  margin: 0;
  color: #475569;
  max-width: 60ch;
}

.section-header .eyebrow {
  margin: 0;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #6366f1;
  font-weight: 600;
}

.section-tools {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  align-items: flex-start;
}

.search {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #f1f5f9;
  border-radius: 999px;
  padding: 0.4rem 1rem;
}

.search input {
  border: none;
  background: transparent;
  outline: none;
  font-size: 0.95rem;
  min-width: 220px;
}

.search-icon {
  opacity: 0.6;
}

.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.5rem;
}

.category-card {
  display: grid;
  gap: 1.5rem;
  padding: 1.5rem;
  background: #f8fafc;
  border-radius: 1.25rem;
  border: 1px solid rgba(148, 163, 184, 0.25);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.category-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 15px 40px -30px rgba(37, 99, 235, 0.6);
}

.category-header {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.category-header h3 {
  margin: 0 0 0.35rem;
  font-size: 1.25rem;
}

.category-header p {
  margin: 0;
  color: #475569;
  font-size: 0.95rem;
}

.category-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 3rem;
  height: 3rem;
  border-radius: 0.9rem;
  background: #e0e7ff;
  font-size: 1.6rem;
}

.category-meta {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
  margin: 0;
}

.category-meta dt {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #64748b;
}

.category-meta dd {
  margin: 0.15rem 0 0;
  font-weight: 600;
  font-size: 0.95rem;
}

.topic-preview h4 {
  margin: 0 0 0.75rem;
  font-size: 1rem;
}

.topic-preview ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.75rem;
}

.topic-preview li {
  background: white;
  border-radius: 0.9rem;
  padding: 0.85rem;
  border: 1px solid rgba(148, 163, 184, 0.18);
  display: grid;
  gap: 0.35rem;
}

.topic-preview strong {
  font-size: 0.95rem;
}

.topic-preview span {
  color: #475569;
  font-size: 0.85rem;
}

.category-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.primary,
.secondary,
.ghost {
  border-radius: 999px;
  padding: 0.65rem 1.2rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.primary {
  background: linear-gradient(135deg, #2563eb, #4f46e5);
  color: white;
  box-shadow: 0 12px 30px -22px rgba(37, 99, 235, 0.75);
}

.secondary {
  background: white;
  color: #2563eb;
  border: 1px solid rgba(37, 99, 235, 0.3);
}

.ghost {
  background: transparent;
  color: #1f2937;
  border: 1px solid rgba(148, 163, 184, 0.45);
}

.primary:hover,
.secondary:hover,
.ghost:hover {
  transform: translateY(-1px);
}

.quiz-list {
  display: grid;
  gap: 1rem;
}

.quiz-card {
  background: #f8fafc;
  border-radius: 1.1rem;
  padding: 1.35rem;
  border: 1px solid rgba(148, 163, 184, 0.25);
  display: grid;
  gap: 1rem;
}

.quiz-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 1rem;
}

.quiz-header h3 {
  margin: 0;
}

.quiz-header .quiz-meta {
  font-size: 0.85rem;
  color: #64748b;
}

.quiz-card p {
  margin: 0;
  color: #475569;
}

.quiz-stats {
  display: flex;
  gap: 2rem;
  margin: 0;
}

.quiz-stats dt {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #64748b;
}

.quiz-stats dd {
  margin: 0.25rem 0 0;
  font-weight: 600;
}

.quiz-actions {
  display: flex;
  justify-content: flex-end;
}

.state {
  background: white;
  border-radius: 1.5rem;
  padding: 2.25rem;
  text-align: center;
  display: grid;
  gap: 1rem;
  justify-items: center;
}

.state.error h2 {
  margin: 0;
}

.state.error p {
  color: #b91c1c;
}

.spinner {
  width: 2.6rem;
  height: 2.6rem;
  border-radius: 50%;
  border: 3px solid #dbeafe;
  border-top-color: #2563eb;
  animation: spin 1s linear infinite;
}

.empty {
  color: #64748b;
  font-size: 0.95rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (min-width: 960px) {
  .section-header {
    flex-direction: row;
    align-items: flex-end;
    justify-content: space-between;
  }

  .section-tools {
    align-items: flex-end;
  }
}

@media (max-width: 720px) {
  .search input {
    min-width: 0;
    width: 100%;
  }

  .category-meta {
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  }

  .quiz-stats {
    flex-direction: column;
    gap: 0.75rem;
    align-items: flex-start;
  }
}
</style>
