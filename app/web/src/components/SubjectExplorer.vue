<template>
  <div class="explorer">
    <aside class="subject-panel">
      <header class="panel-header">
        <h2>Subjects</h2>
        <div class="search">
          <span class="search-icon" aria-hidden="true">🔍</span>
          <input
            v-model="search"
            type="search"
            placeholder="Search subjects"
            aria-label="Filter subjects"
          />
        </div>
      </header>

      <div class="subject-list" role="list">
        <button
          v-for="subject in filteredSubjects"
          :key="subject.id"
          :class="['subject-pill', { active: subject.id === activeSubjectId }]"
          type="button"
          @click="selectSubject(subject.id)"
        >
          <span class="pill-icon" aria-hidden="true">{{ subject.icon ?? '📘' }}</span>
          <div class="pill-content">
            <strong>{{ subject.name }}</strong>
            <small>{{ subject.description ?? 'No description yet' }}</small>
          </div>
          <span class="pill-meta">{{ subject.topics.length }} topics</span>
        </button>

        <p v-if="!loading && filteredSubjects.length === 0" class="empty">No subjects match your search.</p>
      </div>
    </aside>

    <section class="subject-detail" aria-live="polite">
      <div v-if="loading" class="state">
        <span class="spinner" aria-hidden="true"></span>
        <p>Loading subjects…</p>
      </div>
      <div v-else-if="error" class="state error">
        <h3>Unable to load subjects</h3>
        <p>{{ error }}</p>
        <button type="button" class="primary" @click="loadSubjects">Try again</button>
      </div>
      <div v-else-if="selectedSubject" class="detail-card">
        <header class="detail-header">
          <span class="detail-icon" aria-hidden="true">{{ selectedSubject.icon ?? '📘' }}</span>
          <div>
            <h2>{{ selectedSubject.name }}</h2>
            <p>{{ selectedSubject.description ?? 'Explore curated practice sets for this subject.' }}</p>
          </div>
        </header>

        <section class="topics">
          <header>
            <h3>Topics</h3>
            <span>{{ selectedSubject.topics.length }} available</span>
          </header>

          <div v-if="selectedSubject.topics.length > 0" class="topic-grid">
            <article v-for="topic in selectedSubject.topics" :key="topic.id" class="topic-card">
              <h4>{{ topic.name }}</h4>
              <p>{{ topic.description ?? 'Review questions and quizzes tailored to this topic.' }}</p>
              <div class="topic-actions">
                <a
                  class="secondary"
                  :href="getPracticeUrl(selectedSubject.slug, topic.slug)"
                >
                  Practice topic
                </a>
              </div>
            </article>
          </div>
          <p v-else class="empty">Topics have not been added for this subject yet.</p>
        </section>

        <footer class="detail-footer">
          <a class="primary" :href="getPracticeUrl(selectedSubject.slug)">
            Start practice set
          </a>
          <button type="button" class="ghost" @click="loadSubjects">Refresh</button>
        </footer>
      </div>
      <div v-else class="state">
        <h3>Select a subject to view topics</h3>
        <p>Subjects that appear here are available to your organization or globally.</p>
      </div>
    </section>
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

type Subject = {
  id: number
  slug: string
  name: string
  description?: string | null
  icon?: string | null
  organization_id: number | null
  topics: Topic[]
}

const subjects = ref<Subject[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const activeSubjectId = ref<number | null>(null)
const search = ref('')

const filteredSubjects = computed(() => {
  if (!search.value.trim()) {
    return subjects.value
  }
  const value = search.value.toLowerCase()
  return subjects.value.filter((subject) =>
    subject.name.toLowerCase().includes(value) ||
    (subject.description ?? '').toLowerCase().includes(value)
  )
})

const selectedSubject = computed(() =>
  subjects.value.find((subject) => subject.id === activeSubjectId.value) ?? null
)

async function loadSubjects() {
  loading.value = true
  error.value = null
  try {
    const response = await fetch('/api/subjects')
    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`)
    }
    const payload = (await response.json()) as Subject[]
    subjects.value = payload
    if (payload.length > 0) {
      activeSubjectId.value ??= payload[0].id
    } else {
      activeSubjectId.value = null
    }
  } catch (err) {
    console.error(err)
    error.value = err instanceof Error ? err.message : 'Unknown error'
  } finally {
    loading.value = false
  }
}

function selectSubject(id: number) {
  activeSubjectId.value = id
}

function getPracticeUrl(subjectSlug: string, topicSlug?: string) {
  if (topicSlug) {
    return `/practice/categories/${subjectSlug}?topic=${encodeURIComponent(topicSlug)}`
  }
  return `/practice/categories/${subjectSlug}`
}

onMounted(loadSubjects)
</script>

<style scoped>
.explorer {
  display: grid;
  grid-template-columns: minmax(280px, 320px) 1fr;
  gap: 2rem;
  align-items: stretch;
}

.subject-panel {
  background: white;
  border-radius: 1.25rem;
  padding: 1.5rem;
  box-shadow: 0 18px 45px -28px rgba(15, 23, 42, 0.35);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.panel-header {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.panel-header h2 {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 600;
}

.search {
  display: flex;
  align-items: center;
  background: #f1f5f9;
  border-radius: 999px;
  padding: 0.25rem 0.75rem;
  gap: 0.5rem;
}


.search-icon {
  font-size: 1rem;
  opacity: 0.6;
}

.search input {
  border: none;
  background: transparent;
  outline: none;
  flex: 1;
  font-size: 0.95rem;
}

.subject-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-height: min(60vh, 540px);
  overflow-y: auto;
  padding-right: 0.25rem;
}

.subject-pill {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 1rem;
  border: 1px solid transparent;
  background: #f8fafc;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s ease;
}

.subject-pill:hover {
  transform: translateY(-1px);
  background: #f1f5f9;
}

.subject-pill.active {
  border-color: #2563eb;
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.12), rgba(79, 70, 229, 0.12));
}

.pill-icon {
  font-size: 1.6rem;
}

.pill-content strong {
  display: block;
  font-size: 1rem;
  margin-bottom: 0.15rem;
}

.pill-content small {
  color: #475569;
  font-size: 0.85rem;
}

.pill-meta {
  font-size: 0.8rem;
  color: #475569;
  font-weight: 600;
}

.subject-detail {
  background: white;
  border-radius: 1.25rem;
  padding: clamp(1.5rem, 3vw, 2.25rem);
  box-shadow: 0 18px 45px -30px rgba(15, 23, 42, 0.4);
  min-height: 420px;
  display: flex;
  flex-direction: column;
}

.detail-card {
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
  height: 100%;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.detail-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #eef2ff;
  color: #4338ca;
  border-radius: 1rem;
  font-size: 2rem;
  width: 3.5rem;
  height: 3.5rem;
}

.detail-header h2 {
  margin: 0;
  font-size: 1.75rem;
}

.detail-header p {
  margin: 0.25rem 0 0;
  color: #475569;
  max-width: 45ch;
}

.topics header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.topics h3 {
  margin: 0;
  font-size: 1.2rem;
}

.topics header span {
  color: #475569;
  font-size: 0.9rem;
}

.topic-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

.topic-card {
  background: #f8fafc;
  border-radius: 1rem;
  padding: 1.1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  border: 1px solid rgba(148, 163, 184, 0.2);
}

.topic-card h4 {
  margin: 0;
  font-size: 1.05rem;
  color: #1f2937;
}

.topic-card p {
  margin: 0;
  color: #4b5563;
  font-size: 0.9rem;
  flex: 1;
}

.topic-actions {
  display: flex;
  justify-content: flex-end;
}

.state {
  margin: auto;
  text-align: center;
  max-width: 26rem;
  display: grid;
  gap: 0.75rem;
  justify-items: center;
}

.state.error h3 {
  margin: 0;
}

.state.error p {
  color: #b91c1c;
}

.spinner {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  border: 3px solid #dbeafe;
  border-top-color: #2563eb;
  animation: spin 1s linear infinite;
}

.detail-footer {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.primary,
.secondary,
.ghost {
  border-radius: 999px;
  padding: 0.6rem 1.1rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.primary {
  background: linear-gradient(135deg, #2563eb, #4f46e5);
  color: white;
  box-shadow: 0 10px 25px -18px rgba(37, 99, 235, 0.75);
}

.secondary {
  background: white;
  color: #2563eb;
  border: 1px solid rgba(37, 99, 235, 0.25);
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

.empty {
  color: #64748b;
  font-size: 0.95rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 960px) {
  .explorer {
    grid-template-columns: 1fr;
  }

  .subject-panel {
    order: 2;
  }

  .subject-detail {
    order: 1;
  }
}
</style>
