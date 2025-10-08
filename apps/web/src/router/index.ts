import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', component: () => import('../pages/Home.vue') },
  { path: '/quiz', component: () => import('../pages/Quiz.vue') },
  { path: '/results/:id', component: () => import('../pages/Results.vue') },
  { path: '/dashboard', component: () => import('../pages/Dashboard.vue') },
  { path: '/admin', component: () => import('../pages/admin/Admin.vue') },
  { path: '/login', component: () => import('../pages/auth/Login.vue') },
  { path: '/register', component: () => import('../pages/auth/Register.vue') },
]

export default createRouter({ history: createWebHistory(), routes })
