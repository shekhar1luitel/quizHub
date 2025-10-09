import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { pinia } from '../stores'

const routes = [
  { path: '/', name: 'home', component: () => import('../pages/Home.vue'), meta: { title: 'Home' } },
  { path: '/quiz/setup', name: 'quiz-setup', component: () => import('../pages/QuizSetup.vue'), meta: { requiresAuth: true, requiresLearner: true, title: 'Quiz Setup' } },
  { path: '/bookmarks', name: 'bookmarks', component: () => import('../pages/Bookmarks.vue'), meta: { requiresAuth: true, requiresLearner: true, title: 'Bookmarks' } },
  { path: '/categories', name: 'categories', component: () => import('../pages/Categories.vue'), meta: { title: 'Categories' } },
  { path: '/practice/:slug', name: 'practice', component: () => import('../pages/Practice.vue'), props: true, meta: { requiresAuth: true, requiresLearner: true, title: 'Practice' } },
  { path: '/quiz/:id', name: 'quiz', component: () => import('../pages/Quiz.vue'), props: true, meta: { requiresAuth: true, requiresLearner: true, title: 'Quiz' } },
  {
    path: '/notifications',
    name: 'notifications',
    component: () => import('../pages/Notifications.vue'),
    meta: { requiresAuth: true, title: 'Notifications' },
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('../pages/Settings.vue'),
    meta: { requiresAuth: true, title: 'Settings' },
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('../pages/Profile.vue'),
    meta: { requiresAuth: true, title: 'Profile' },
  },
  {
    path: '/results/:id',
    name: 'results',
    component: () => import('../pages/Results.vue'),
    meta: { requiresAuth: true, requiresLearner: true },
    props: true,
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('../pages/Dashboard.vue'),
    meta: { requiresAuth: true, requiresLearner: true, title: 'Dashboard' },
  },
  {
    path: '/org/dashboard',
    name: 'org-dashboard',
    component: () => import('../pages/OrgDashboard.vue'),
    meta: { requiresAuth: true, requiresOrgAdmin: true, title: 'Institution Dashboard' },
  },
  {
    path: '/history',
    name: 'history',
    component: () => import('../pages/History.vue'),
    meta: { requiresAuth: true, requiresLearner: true, title: 'History' },
  },
  {
    path: '/institutions/:slug',
    name: 'institution',
    component: () => import('../pages/Institution.vue'),
    props: true,
    meta: { requiresAuth: true, title: 'Institution Hub' },
  },
  {
    path: '/analytics',
    name: 'analytics',
    component: () => import('../pages/Analytics.vue'),
    meta: { requiresAuth: true, requiresLearner: true, title: 'Analytics' },
  },
  {
    path: '/admin',
    name: 'admin',
    component: () => import('../pages/admin/Admin.vue'),
    meta: { requiresAdmin: true, title: 'Admin Dashboard' },
  },
  {
    path: '/admin/questions',
    name: 'admin-questions',
    component: () => import('../pages/admin/QuestionsCRUD.vue'),
    meta: { requiresAdmin: true, title: 'Question Studio' },
  },
  {
    path: '/admin/questions/library',
    name: 'admin-question-library',
    component: () => import('../pages/admin/QuestionsLibrary.vue'),
    meta: { requiresAdmin: true, title: 'Question Library' },
  },
  {
    path: '/admin/quizzes',
    name: 'admin-quizzes',
    component: () => import('../pages/admin/QuizzesCRUD.vue'),
    meta: { requiresAdmin: true, title: 'Quiz Studio' },
  },
  {
    path: '/admin/quizzes/library',
    name: 'admin-quiz-library',
    component: () => import('../pages/admin/QuizzesLibrary.vue'),
    meta: { requiresAdmin: true, title: 'Quiz Library' },
  },
  {
    path: '/admin/categories',
    name: 'admin-categories',
    component: () => import('../pages/admin/CategoriesCRUD.vue'),
    meta: { requiresAdmin: true, title: 'Category Studio' },
  },
  {
    path: '/admin/categories/library',
    name: 'admin-category-library',
    component: () => import('../pages/admin/CategoriesLibrary.vue'),
    meta: { requiresAdmin: true, title: 'Category Library' },
  },
  {
    path: '/admin/users',
    name: 'admin-users',
    component: () => import('../pages/admin/UserManagement.vue'),
    meta: { requiresSuperuser: true, title: 'User Management' },
  },
  {
    path: '/admin/organizations',
    name: 'admin-organizations',
    component: () => import('../pages/admin/Organizations.vue'),
    meta: { requiresSuperuser: true, title: 'Organizations' },
  },
  {
    path: '/admin/settings/mail',
    name: 'admin-mail-config',
    component: () => import('../pages/admin/MailConfig.vue'),
    meta: { requiresSuperuser: true, title: 'Mail Delivery' },
  },
  {
    path: '/admin/organizations/:id/members',
    name: 'admin-organization-members',
    component: () => import('../pages/admin/OrganizationMembers.vue'),
    meta: { requiresAdmin: true, title: 'Organization Members' },
    props: true,
  },
  { path: '/login', name: 'login', component: () => import('../pages/auth/Login.vue'), meta: { title: 'Login' } },
  { path: '/register', name: 'register', component: () => import('../pages/auth/Register.vue'), meta: { title: 'Register' } },
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

  if (to.meta.requiresLearner && auth.isAuthenticated && !auth.isLearner) {
    return { name: 'home' }
  }

  if (to.meta.requiresOrgAdmin && auth.isAuthenticated && !auth.isOrgAdmin) {
    return { name: 'home' }
  }

  if (to.meta.requiresAdmin && !auth.isAdmin) {
    return { name: 'home' }
  }

  if (to.meta.requiresSuperuser && !auth.isSuperuser) {
    return { name: 'home' }
  }

  if (typeof to.meta.title === 'string') {
    document.title = `${to.meta.title} · QuizMaster`
  } else {
    document.title = 'QuizMaster'
  }

  return true
})

export default router
