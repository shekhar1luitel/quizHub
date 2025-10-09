import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { pinia } from '../stores'

const routes = [
  { path: '/', name: 'home', component: () => import('../pages/Home.vue') },
  { path: '/categories', name: 'categories', component: () => import('../pages/Categories.vue') },
  { path: '/practice/:slug', name: 'practice', component: () => import('../pages/Practice.vue'), props: true },
  { path: '/quiz/:id', name: 'quiz', component: () => import('../pages/Quiz.vue'), props: true },
  {
    path: '/results/:id',
    name: 'results',
    component: () => import('../pages/Results.vue'),
    meta: { requiresAuth: true },
    props: true,
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('../pages/Dashboard.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/history',
    name: 'history',
    component: () => import('../pages/History.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/analytics',
    name: 'analytics',
    component: () => import('../pages/Analytics.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/admin',
    name: 'admin',
    component: () => import('../pages/admin/Admin.vue'),
    meta: { requiresAdmin: true },
  },
  {
    path: '/admin/questions',
    name: 'admin-questions',
    component: () => import('../pages/admin/QuestionsCRUD.vue'),
    meta: { requiresAdmin: true },
  },
  {
    path: '/admin/quizzes',
    name: 'admin-quizzes',
    component: () => import('../pages/admin/QuizzesCRUD.vue'),
    meta: { requiresAdmin: true },
  },
  {
    path: '/admin/categories',
    name: 'admin-categories',
    component: () => import('../pages/admin/CategoriesCRUD.vue'),
    meta: { requiresAdmin: true },
  },
  { path: '/login', name: 'login', component: () => import('../pages/auth/Login.vue') },
  { path: '/register', name: 'register', component: () => import('../pages/auth/Register.vue') },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach(async (to) => {
  const auth = useAuthStore(pinia)
  await auth.initialize()

  if ((to.name === 'login' || to.name === 'register') && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (to.meta.requiresAdmin && !auth.isAdmin) {
    return { name: 'home' }
  }

  return true
})

export default router
