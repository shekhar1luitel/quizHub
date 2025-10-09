import { defineStore } from 'pinia'

export interface AuthUser {
  id: number
  username: string
  email: string
  role: string
  status: string
  account_type: string
  organization_id: number | null
}

const ACCESS_TOKEN_KEY = 'lqh_access_token'

const getInitialToken = () => {
  if (typeof window === 'undefined') return ''
  return window.localStorage.getItem(ACCESS_TOKEN_KEY) || ''
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: getInitialToken(),
    user: null as AuthUser | null,
    initialized: false,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.accessToken),
    isAdmin: (state) => state.user?.role === 'admin' || state.user?.role === 'superuser',
    isSuperuser: (state) => state.user?.role === 'superuser',
  },
  actions: {
    setAccessToken(token: string) {
      this.accessToken = token
      if (typeof window !== 'undefined') {
        if (token) {
          window.localStorage.setItem(ACCESS_TOKEN_KEY, token)
        } else {
          window.localStorage.removeItem(ACCESS_TOKEN_KEY)
        }
      }
    },
    setUser(user: AuthUser | null) {
      this.user = user
    },
    async fetchCurrentUser() {
      if (!this.accessToken) {
        this.setUser(null)
        return null
      }
      try {
        const { http } = await import('../api/http')
        const { data } = await http.get<AuthUser>('/users/me')
        this.setUser(data)
        return data
      } catch (error) {
        this.logout()
        throw error
      }
    },
    async initialize() {
      if (this.initialized) return
      this.initialized = true
      if (this.accessToken) {
        try {
          await this.fetchCurrentUser()
        } catch (error) {
          console.error(error)
        }
      }
    },
    logout() {
      this.setAccessToken('')
      this.setUser(null)
      void import('./bookmarks').then(({ useBookmarkStore }) => {
        const bookmarks = useBookmarkStore()
        bookmarks.reset()
      })
    },
  },
})
