<template>
  <div class="explorer">
    <header class="explorer-header">
      <div>
        <h2>API explorer</h2>
        <p>
          Interact with every QuizHub backend endpoint from a single interface. Configure path
          parameters, send requests, and inspect structured responses.
        </p>
      </div>
      <div class="base-url">
        <label class="field">
          <span>API base URL</span>
          <input
            v-model="baseUrl"
            type="url"
            placeholder="https://api.example.com"
            aria-label="API base URL"
          />
        </label>
      </div>
    </header>

    <section class="toolbar" aria-label="Endpoint filters">
      <label class="search field">
        <span class="sr-only">Search endpoints</span>
        <input
          v-model="search"
          type="search"
          placeholder="Search by path, module, or handler"
          aria-label="Search endpoints"
        />
      </label>

      <nav class="method-filter" aria-label="Filter by HTTP method">
        <button
          v-for="methodOption in methodOptions"
          :key="methodOption"
          type="button"
          :class="['method-chip', { active: methodFilter === methodOption }]"
          @click="toggleMethodFilter(methodOption)"
        >
          {{ methodOption }}
        </button>
      </nav>
    </section>

    <div class="layout">
      <aside class="endpoint-list" aria-label="Available endpoints">
        <template v-if="filteredEndpoints.length">
          <section
            v-for="group in groupedByModule"
            :key="group.module"
            v-show="group.endpoints.length"
            class="module-group"
          >
            <header class="module-header">
              <h3>{{ group.module }}</h3>
              <span>{{ group.endpoints.length }} endpoint{{ group.endpoints.length === 1 ? '' : 's' }}</span>
            </header>

            <ul>
              <li
                v-for="endpoint in group.endpoints"
                :key="endpoint.method + endpoint.path"
                :class="['endpoint-item', { active: isSelected(endpoint) }]"
              >
                <button type="button" @click="selectEndpoint(endpoint)">
                  <span class="endpoint-method" :data-method="endpoint.method">{{ endpoint.method }}</span>
                  <span class="endpoint-path">{{ endpoint.path }}</span>
                  <span class="endpoint-handler">{{ endpoint.handler }}</span>
                </button>
              </li>
            </ul>
          </section>
        </template>
        <p v-else class="empty-state">No endpoints match the current filters.</p>
      </aside>

      <section class="endpoint-panel" aria-live="polite">
        <template v-if="selected">
          <article class="endpoint-details">
            <header>
              <div class="endpoint-heading">
                <span class="badge" :data-method="selected.method">{{ selected.method }}</span>
                <h3>{{ selected.path }}</h3>
              </div>
              <dl class="meta">
                <div>
                  <dt>Module</dt>
                  <dd>{{ selected.module }}</dd>
                </div>
                <div>
                  <dt>Handler</dt>
                  <dd>{{ selected.handler }}</dd>
                </div>
              </dl>
              <p class="description">{{ selected.description }}</p>
            </header>

            <section class="request-config">
              <h4>Request configuration</h4>

              <div v-if="selected.pathParams.length" class="field-grid">
                <div v-for="param in selected.pathParams" :key="param" class="field">
                  <label :for="`param-${param}`">{{ param }}</label>
                  <input
                    :id="`param-${param}`"
                    v-model="pathParams[param]"
                    type="text"
                    :placeholder="`Enter ${param}`"
                  />
                </div>
              </div>

              <div class="field">
                <label for="query-string">Query string</label>
                <input
                  id="query-string"
                  v-model="queryString"
                  type="text"
                  placeholder="page=1&limit=20"
                />
              </div>

              <div class="field">
                <label for="headers-input">Headers (JSON)</label>
                <textarea
                  id="headers-input"
                  v-model="headersInput"
                  rows="4"
                  spellcheck="false"
                ></textarea>
              </div>

              <div class="field" v-if="supportsRequestBody">
                <label for="request-body">Request body (JSON)</label>
                <textarea
                  id="request-body"
                  v-model="requestBody"
                  rows="10"
                  spellcheck="false"
                ></textarea>
              </div>

              <footer class="actions">
                <button type="button" class="primary" :disabled="loading" @click="sendRequest">
                  <span v-if="loading" class="spinner" aria-hidden="true"></span>
                  <span>{{ loading ? 'Sending…' : 'Send request' }}</span>
                </button>
                <button type="button" class="ghost" :disabled="loading" @click="resetForm">
                  Reset
                </button>
              </footer>

              <p v-if="formError" class="form-error" role="alert">{{ formError }}</p>
            </section>

            <section class="response-panel">
              <header class="response-header">
                <h4>Response</h4>
                <div class="response-meta">
                  <span v-if="responseStatus" class="status">{{ responseStatus }}</span>
                  <span v-if="responseTime !== null" class="time">{{ responseTime }} ms</span>
                </div>
              </header>

              <details open>
                <summary>Headers</summary>
                <ul class="header-list" v-if="responseHeaders.length">
                  <li v-for="([key, value]) in responseHeaders" :key="key">
                    <strong>{{ key }}</strong>
                    <span>{{ value }}</span>
                  </li>
                </ul>
                <p v-else class="empty-state">No headers returned yet.</p>
              </details>

              <details open>
                <summary>Body</summary>
                <pre v-if="responseBody" class="response-body">{{ responseBody }}</pre>
                <p v-else class="empty-state">Send a request to view the response payload.</p>
              </details>
            </section>
          </article>
        </template>
        <div v-else class="placeholder">
          <h3>Select an endpoint to get started</h3>
          <p>
            Choose an endpoint from the list to configure a request. You'll be able to update path
            parameters, add headers, and send requests directly to the API.
          </p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'

type Endpoint = {
  method: string
  path: string
  module: string
  handler: string
  description: string
  pathParams: string[]
}

const endpoints: Endpoint[] = [
  { method: 'GET', path: '/api/health', module: 'health.py', handler: 'health', description: 'Service health check', pathParams: [] },
  { method: 'POST', path: '/api/admin/bulk-import/commit', module: 'admin.py', handler: 'commit_bulk_import', description: 'Commit an approved bulk import batch', pathParams: [] },
  { method: 'GET', path: '/api/admin/bulk-import/export', module: 'admin.py', handler: 'download_bulk_import_export', description: 'Download data prepared for bulk import', pathParams: [] },
  { method: 'POST', path: '/api/admin/bulk-import/preview', module: 'admin.py', handler: 'preview_bulk_import', description: 'Preview the results of a bulk import file', pathParams: [] },
  { method: 'GET', path: '/api/admin/bulk-import/template', module: 'admin.py', handler: 'download_bulk_import_template_route', description: 'Download a bulk import template file', pathParams: [] },
  { method: 'GET', path: '/api/admin/config/mail', module: 'admin.py', handler: 'get_mail_config', description: 'Retrieve the current mail configuration', pathParams: [] },
  { method: 'PUT', path: '/api/admin/config/mail', module: 'admin.py', handler: 'update_mail_config', description: 'Update the outbound mail configuration', pathParams: [] },
  { method: 'POST', path: '/api/admin/email/dispatch', module: 'admin.py', handler: 'dispatch_email_events', description: 'Dispatch queued admin email events', pathParams: [] },
  { method: 'POST', path: '/api/admin/notifications', module: 'admin.py', handler: 'create_admin_notification', description: 'Create a new admin notification', pathParams: [] },
  { method: 'GET', path: '/api/admin/overview', module: 'admin.py', handler: 'get_admin_overview', description: 'Retrieve metrics for the admin overview dashboard', pathParams: [] },
  { method: 'GET', path: '/api/admin/users', module: 'admin.py', handler: 'list_admin_users', description: 'List all admin users', pathParams: [] },
  { method: 'POST', path: '/api/admin/users', module: 'admin.py', handler: 'create_admin_user', description: 'Create a new admin user', pathParams: [] },
  { method: 'PUT', path: '/api/admin/users/{user_id}/status', module: 'admin.py', handler: 'update_admin_user_status', description: 'Update the status of an admin user', pathParams: ['user_id'] },
  { method: 'GET', path: '/api/analytics/overview', module: 'analytics.py', handler: 'get_analytics_overview', description: 'View aggregated analytics metrics', pathParams: [] },
  { method: 'POST', path: '/api/attempts/', module: 'attempts.py', handler: 'submit_attempt', description: 'Submit a quiz attempt', pathParams: [] },
  { method: 'GET', path: '/api/attempts/history', module: 'attempts.py', handler: 'list_attempt_history', description: 'List a user\'s attempt history', pathParams: [] },
  { method: 'GET', path: '/api/attempts/{attempt_id}', module: 'attempts.py', handler: 'get_attempt', description: 'Retrieve details for a specific attempt', pathParams: ['attempt_id'] },
  { method: 'POST', path: '/api/auth/login', module: 'auth.py', handler: 'login', description: 'Authenticate a user and issue tokens', pathParams: [] },
  { method: 'POST', path: '/api/auth/register', module: 'auth.py', handler: 'register', description: 'Register a new user account', pathParams: [] },
  { method: 'POST', path: '/api/auth/resend-verification', module: 'auth.py', handler: 'resend_verification', description: 'Resend the verification email', pathParams: [] },
  { method: 'POST', path: '/api/auth/verify-email', module: 'auth.py', handler: 'verify_email', description: 'Verify an email address using a token', pathParams: [] },
  { method: 'GET', path: '/api/bookmarks/', module: 'bookmarks.py', handler: 'list_bookmarks', description: 'List bookmarked questions for the current user', pathParams: [] },
  { method: 'POST', path: '/api/bookmarks/', module: 'bookmarks.py', handler: 'create_bookmark', description: 'Bookmark a question', pathParams: [] },
  { method: 'GET', path: '/api/bookmarks/ids', module: 'bookmarks.py', handler: 'list_bookmarked_question_ids', description: 'List IDs of bookmarked questions', pathParams: [] },
  { method: 'DELETE', path: '/api/bookmarks/{question_id}', module: 'bookmarks.py', handler: 'delete_bookmark', description: 'Remove a question bookmark', pathParams: ['question_id'] },
  { method: 'GET', path: '/api/categories/', module: 'categories.py', handler: 'list_categories', description: 'List all categories', pathParams: [] },
  { method: 'POST', path: '/api/categories/', module: 'categories.py', handler: 'create_category', description: 'Create a new category', pathParams: [] },
  { method: 'DELETE', path: '/api/categories/{category_id}', module: 'categories.py', handler: 'delete_category', description: 'Delete a category by ID', pathParams: ['category_id'] },
  { method: 'PUT', path: '/api/categories/{category_id}', module: 'categories.py', handler: 'update_category', description: 'Update category details', pathParams: ['category_id'] },
  { method: 'GET', path: '/api/dashboard/summary', module: 'dashboard.py', handler: 'get_dashboard_summary', description: 'Retrieve dashboard summary data', pathParams: [] },
  { method: 'GET', path: '/api/notifications', module: 'notifications.py', handler: 'list_notifications', description: 'List notifications for the current user', pathParams: [] },
  { method: 'POST', path: '/api/notifications/read-all', module: 'notifications.py', handler: 'mark_all_notifications_read', description: 'Mark every notification as read', pathParams: [] },
  { method: 'POST', path: '/api/notifications/{notification_id}/read', module: 'notifications.py', handler: 'mark_notification_read', description: 'Mark a specific notification as read', pathParams: ['notification_id'] },
  { method: 'GET', path: '/api/organizations', module: 'organizations.py', handler: 'list_organizations', description: 'List organizations visible to the user', pathParams: [] },
  { method: 'POST', path: '/api/organizations', module: 'organizations.py', handler: 'create_organization', description: 'Create a new organization', pathParams: [] },
  { method: 'POST', path: '/api/organizations/enroll', module: 'organizations.py', handler: 'enroll_current_user', description: 'Enroll the current user via token', pathParams: [] },
  { method: 'PATCH', path: '/api/organizations/{organization_id}', module: 'organizations.py', handler: 'update_organization', description: 'Update an organization profile', pathParams: ['organization_id'] },
  { method: 'POST', path: '/api/organizations/{organization_id}/enroll-tokens', module: 'organizations.py', handler: 'create_enroll_token', description: 'Create enrollment tokens for an organization', pathParams: ['organization_id'] },
  { method: 'GET', path: '/api/organizations/{organization_id}/members', module: 'organizations.py', handler: 'list_organization_members', description: 'List members of an organization', pathParams: ['organization_id'] },
  { method: 'GET', path: '/api/practice/bookmarks', module: 'practice.py', handler: 'get_bookmark_revision_set', description: 'Retrieve practice set based on bookmarks', pathParams: [] },
  { method: 'GET', path: '/api/practice/categories', module: 'practice.py', handler: 'list_practice_categories', description: 'List practice categories', pathParams: [] },
  { method: 'GET', path: '/api/practice/categories/{slug}', module: 'practice.py', handler: 'get_practice_category', description: 'Retrieve a practice category by slug', pathParams: ['slug'] },
  { method: 'GET', path: '/api/public/home', module: 'public.py', handler: 'get_public_home', description: 'Fetch featured categories and trending quizzes', pathParams: [] },
  { method: 'GET', path: '/api/questions/', module: 'questions.py', handler: 'list_questions', description: 'List all questions', pathParams: [] },
  { method: 'POST', path: '/api/questions/', module: 'questions.py', handler: 'create_question', description: 'Create a new question', pathParams: [] },
  { method: 'DELETE', path: '/api/questions/{question_id}', module: 'questions.py', handler: 'delete_question', description: 'Delete a question by ID', pathParams: ['question_id'] },
  { method: 'GET', path: '/api/questions/{question_id}', module: 'questions.py', handler: 'get_question', description: 'Retrieve a question by ID', pathParams: ['question_id'] },
  { method: 'PUT', path: '/api/questions/{question_id}', module: 'questions.py', handler: 'update_question', description: 'Update question details', pathParams: ['question_id'] },
  { method: 'GET', path: '/api/quizzes/', module: 'quizzes.py', handler: 'list_quizzes', description: 'List all quizzes', pathParams: [] },
  { method: 'POST', path: '/api/quizzes/', module: 'quizzes.py', handler: 'create_quiz', description: 'Create a new quiz', pathParams: [] },
  { method: 'DELETE', path: '/api/quizzes/{quiz_id}', module: 'quizzes.py', handler: 'delete_quiz', description: 'Delete a quiz by ID', pathParams: ['quiz_id'] },
  { method: 'GET', path: '/api/quizzes/{quiz_id}', module: 'quizzes.py', handler: 'get_quiz', description: 'Retrieve a quiz by ID', pathParams: ['quiz_id'] },
  { method: 'PUT', path: '/api/quizzes/{quiz_id}', module: 'quizzes.py', handler: 'update_quiz', description: 'Update quiz details', pathParams: ['quiz_id'] },
  { method: 'GET', path: '/api/subjects/', module: 'subjects.py', handler: 'list_subjects', description: 'List all subjects', pathParams: [] },
  { method: 'POST', path: '/api/subjects/', module: 'subjects.py', handler: 'create_subject', description: 'Create a new subject', pathParams: [] },
  { method: 'DELETE', path: '/api/subjects/{subject_id}', module: 'subjects.py', handler: 'delete_subject', description: 'Delete a subject by ID', pathParams: ['subject_id'] },
  { method: 'PUT', path: '/api/subjects/{subject_id}', module: 'subjects.py', handler: 'update_subject', description: 'Update subject details', pathParams: ['subject_id'] },
  { method: 'GET', path: '/api/subjects/{subject_id}/topics', module: 'subjects.py', handler: 'list_topics', description: 'List topics for a subject', pathParams: ['subject_id'] },
  { method: 'POST', path: '/api/subjects/{subject_id}/topics', module: 'subjects.py', handler: 'create_topic', description: 'Create a new topic within a subject', pathParams: ['subject_id'] },
  { method: 'DELETE', path: '/api/subjects/{subject_id}/topics/{topic_id}', module: 'subjects.py', handler: 'delete_topic', description: 'Delete a topic within a subject', pathParams: ['subject_id', 'topic_id'] },
  { method: 'PUT', path: '/api/subjects/{subject_id}/topics/{topic_id}', module: 'subjects.py', handler: 'update_topic', description: 'Update a topic within a subject', pathParams: ['subject_id', 'topic_id'] },
  { method: 'GET', path: '/api/users/me', module: 'users.py', handler: 'me', description: 'Retrieve the authenticated user profile', pathParams: [] },
  { method: 'PATCH', path: '/api/users/me', module: 'users.py', handler: 'update_me', description: 'Update the authenticated user profile', pathParams: [] }
]

const methodOptions = ['ALL', 'GET', 'POST', 'PUT', 'PATCH', 'DELETE'] as const

type MethodOption = (typeof methodOptions)[number]

const baseUrl = ref(window.location.origin)
const search = ref('')
const methodFilter = ref<MethodOption>('ALL')
const selected = ref<Endpoint | null>(null)
const pathParams = reactive<Record<string, string>>({})
const queryString = ref('')
const headersInput = ref('{
  "Content-Type": "application/json"
}')
const requestBody = ref('{}')
const responseHeaders = ref<[string, string][]>([])
const responseBody = ref('')
const responseStatus = ref('')
const responseTime = ref<number | null>(null)
const loading = ref(false)
const formError = ref<string | null>(null)

const supportsRequestBody = computed(() => {
  if (!selected.value) return false
  return ['POST', 'PUT', 'PATCH'].includes(selected.value.method)
})

const filteredEndpoints = computed(() => {
  const term = search.value.trim().toLowerCase()
  return endpoints.filter((endpoint) => {
    const matchesMethod = methodFilter.value === 'ALL' || endpoint.method === methodFilter.value
    if (!matchesMethod) return false
    if (!term) return true
    return (
      endpoint.path.toLowerCase().includes(term) ||
      endpoint.module.toLowerCase().includes(term) ||
      endpoint.handler.toLowerCase().includes(term)
    )
  })
})

const groupedByModule = computed(() => {
  const groups: { module: string; endpoints: Endpoint[] }[] = []
  const byModule = new Map<string, Endpoint[]>()
  for (const endpoint of filteredEndpoints.value) {
    if (!byModule.has(endpoint.module)) {
      byModule.set(endpoint.module, [])
    }
    byModule.get(endpoint.module)!.push(endpoint)
  }
  for (const [module, moduleEndpoints] of byModule.entries()) {
    groups.push({ module, endpoints: moduleEndpoints })
  }
  return groups.sort((a, b) => a.module.localeCompare(b.module))
})

watch(selected, (endpoint) => {
  Object.keys(pathParams).forEach((key) => delete pathParams[key])
  if (!endpoint) {
    requestBody.value = supportsRequestBody.value ? '{}' : ''
    responseHeaders.value = []
    responseBody.value = ''
    responseStatus.value = ''
    responseTime.value = null
    queryString.value = ''
    return
  }
  endpoint.pathParams.forEach((param) => {
    pathParams[param] = ''
  })
  requestBody.value = supportsRequestBody.value ? '{}' : ''
  queryString.value = ''
  responseHeaders.value = []
  responseBody.value = ''
  responseStatus.value = ''
  responseTime.value = null
  formError.value = null
})

function toggleMethodFilter(methodOption: MethodOption) {
  methodFilter.value = methodFilter.value === methodOption ? 'ALL' : methodOption
}

function isSelected(endpoint: Endpoint) {
  return selected.value?.method === endpoint.method && selected.value?.path === endpoint.path
}

function selectEndpoint(endpoint: Endpoint) {
  selected.value = endpoint
}

function resetForm() {
  if (!selected.value) {
    return
  }
  selected.value.pathParams.forEach((param) => {
    pathParams[param] = ''
  })
  queryString.value = ''
  headersInput.value = '{\n  "Content-Type": "application/json"\n}'
  requestBody.value = supportsRequestBody.value ? '{}' : ''
  responseHeaders.value = []
  responseBody.value = ''
  responseStatus.value = ''
  responseTime.value = null
  formError.value = null
}

function buildUrl(endpoint: Endpoint): string | null {
  let resolvedPath = endpoint.path
  for (const param of endpoint.pathParams) {
    const value = pathParams[param]
    if (!value) {
      formError.value = `Missing required path parameter: ${param}`
      return null
    }
    resolvedPath = resolvedPath.replace(`{${param}}`, encodeURIComponent(value))
  }

  const trimmedBase = baseUrl.value.replace(/\/$/, '')
  const finalPath = queryString.value
    ? `${resolvedPath}${resolvedPath.includes('?') ? '&' : '?'}${queryString.value}`
    : resolvedPath

  return `${trimmedBase}${finalPath}`
}

function parseHeaders(): HeadersInit | null {
  if (!headersInput.value.trim()) return {}
  try {
    const parsed = JSON.parse(headersInput.value)
    if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
      return parsed as Record<string, string>
    }
    formError.value = 'Headers must be a JSON object.'
    return null
  } catch (error) {
    formError.value = error instanceof Error ? error.message : 'Unable to parse headers JSON.'
    return null
  }
}

async function sendRequest() {
  if (!selected.value) return
  formError.value = null

  const url = buildUrl(selected.value)
  if (!url) {
    return
  }

  const headers = parseHeaders()
  if (headers === null) {
    return
  }

  const options: RequestInit = {
    method: selected.value.method,
    headers
  }

  if (supportsRequestBody.value && requestBody.value.trim()) {
    options.body = requestBody.value
  }

  loading.value = true
  responseHeaders.value = []
  responseBody.value = ''
  responseStatus.value = ''
  responseTime.value = null

  const start = performance.now()
  try {
    const res = await fetch(url, options)
    const elapsed = Math.round(performance.now() - start)
    responseTime.value = elapsed
    responseStatus.value = `${res.status} ${res.statusText}`
    responseHeaders.value = Array.from(res.headers.entries())
    const text = await res.text()
    responseBody.value = formatBody(text)
  } catch (error) {
    responseTime.value = null
    responseStatus.value = 'Request failed'
    responseBody.value = error instanceof Error ? error.message : 'Unknown network error'
  } finally {
    loading.value = false
  }
}

function formatBody(text: string): string {
  if (!text) return ''
  try {
    const parsed = JSON.parse(text)
    return JSON.stringify(parsed, null, 2)
  } catch (error) {
    return text
  }
}
</script>

<style scoped>
.explorer {
  display: grid;
  gap: 2rem;
}

.explorer-header {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: clamp(1.75rem, 4vw, 2.5rem);
  background: white;
  border-radius: 1.5rem;
  box-shadow: 0 18px 45px -26px rgba(37, 99, 235, 0.3);
}

.explorer-header h2 {
  margin: 0;
  font-size: clamp(1.8rem, 3vw, 2.4rem);
}

.explorer-header p {
  margin: 0;
  color: #475569;
  max-width: 60ch;
}

.base-url {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
}

.field {
  display: grid;
  gap: 0.45rem;
}

.field label span,
.field > span {
  font-size: 0.85rem;
  font-weight: 600;
  color: #475569;
}

.field input,
.field textarea {
  border-radius: 0.9rem;
  border: 1px solid rgba(148, 163, 184, 0.45);
  padding: 0.65rem 0.9rem;
  font: inherit;
  background: white;
  color: inherit;
  box-shadow: inset 0 1px 0 rgba(148, 163, 184, 0.15);
}

.field textarea {
  resize: vertical;
}

.search input {
  min-width: min(320px, 100%);
}

.method-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.method-chip {
  border-radius: 999px;
  border: 1px solid rgba(99, 102, 241, 0.4);
  background: white;
  color: #4c1d95;
  padding: 0.45rem 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.method-chip.active {
  background: linear-gradient(135deg, #6366f1, #4f46e5);
  color: white;
  border-color: transparent;
  box-shadow: 0 10px 25px -20px rgba(79, 70, 229, 0.8);
}

.layout {
  display: grid;
  gap: 1.5rem;
  grid-template-columns: minmax(260px, 0.75fr) minmax(0, 2fr);
}

.endpoint-list {
  background: white;
  border-radius: 1.5rem;
  padding: 1.5rem;
  box-shadow: 0 20px 45px -35px rgba(30, 64, 175, 0.35);
  display: grid;
  gap: 1.25rem;
  max-height: 70vh;
  overflow: auto;
}

.module-group {
  display: grid;
  gap: 0.85rem;
}

.module-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
  font-weight: 600;
  color: #334155;
}

.module-header span {
  font-size: 0.75rem;
  color: #64748b;
}

.endpoint-item {
  list-style: none;
}

.endpoint-item button {
  width: 100%;
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.75rem;
  align-items: center;
  padding: 0.65rem;
  border-radius: 0.9rem;
  border: 1px solid transparent;
  background: transparent;
  cursor: pointer;
  text-align: left;
}

.endpoint-item button:hover {
  background: #eef2ff;
}

.endpoint-item.active button {
  background: #ede9fe;
  border-color: rgba(99, 102, 241, 0.45);
}

.endpoint-method {
  font-size: 0.8rem;
  font-weight: 700;
  padding: 0.35rem 0.6rem;
  border-radius: 0.6rem;
  text-transform: uppercase;
  justify-self: flex-start;
}

.endpoint-path {
  font-family: 'JetBrains Mono', 'Fira Code', ui-monospace, SFMono-Regular, Menlo, Monaco,
    Consolas, 'Liberation Mono', 'Courier New', monospace;
  font-size: 0.85rem;
}

.endpoint-handler {
  font-size: 0.75rem;
  color: #64748b;
  grid-column: span 2;
}

.endpoint-panel {
  background: white;
  border-radius: 1.5rem;
  padding: clamp(1.5rem, 3vw, 2rem);
  box-shadow: 0 20px 55px -40px rgba(59, 130, 246, 0.45);
  min-height: 60vh;
  display: grid;
}

.endpoint-details {
  display: grid;
  gap: 2rem;
}

.endpoint-heading {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.75rem;
}

.badge {
  border-radius: 999px;
  padding: 0.4rem 0.9rem;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  background: #e0e7ff;
  color: #312e81;
}

.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  margin: 0;
}

.meta dt {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #64748b;
}

.meta dd {
  margin: 0.2rem 0 0;
  font-weight: 600;
}

.description {
  margin: 0;
  color: #475569;
}

.field-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
}

.actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.primary,
.ghost {
  border-radius: 999px;
  padding: 0.65rem 1.35rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.primary {
  background: linear-gradient(135deg, #2563eb, #4f46e5);
  color: white;
  box-shadow: 0 15px 30px -22px rgba(37, 99, 235, 0.8);
}

.primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.ghost {
  background: transparent;
  color: #1f2937;
  border: 1px solid rgba(148, 163, 184, 0.55);
}

.primary:hover:not(:disabled),
.ghost:hover:not(:disabled) {
  transform: translateY(-1px);
}

.spinner {
  width: 1rem;
  height: 1rem;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.6);
  border-top-color: white;
  animation: spin 1s linear infinite;
}

.form-error {
  margin: 0;
  color: #b91c1c;
  font-weight: 600;
}

.response-panel {
  display: grid;
  gap: 1rem;
}

.response-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.response-meta {
  display: flex;
  gap: 0.75rem;
  font-size: 0.85rem;
  color: #475569;
}

.status {
  font-weight: 600;
}

.header-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 0.5rem;
}

.header-list li {
  display: flex;
  gap: 0.75rem;
  font-size: 0.9rem;
}

.header-list strong {
  min-width: 160px;
  color: #475569;
}

.response-body {
  margin: 0;
  background: #0f172a;
  color: #e2e8f0;
  border-radius: 1rem;
  padding: 1rem;
  overflow: auto;
  max-height: 320px;
}

.placeholder {
  display: grid;
  gap: 0.75rem;
  justify-items: start;
}

.empty-state {
  color: #64748b;
  font-size: 0.95rem;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}

[data-method='GET'] {
  background: #dcfce7;
  color: #166534;
}

[data-method='POST'] {
  background: #dbeafe;
  color: #1d4ed8;
}

[data-method='PUT'] {
  background: #fef3c7;
  color: #92400e;
}

[data-method='PATCH'] {
  background: #f3e8ff;
  color: #6b21a8;
}

[data-method='DELETE'] {
  background: #fee2e2;
  color: #b91c1c;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 1080px) {
  .layout {
    grid-template-columns: 1fr;
  }

  .endpoint-list {
    max-height: unset;
  }
}
</style>
