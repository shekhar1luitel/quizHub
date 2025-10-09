import { defineStore } from 'pinia'

export interface UserProfile {
  name: string | null
  phone: string | null
  student_id: string | null
  qr_code_uri: string | null
  avatar_url: string | null
}

export interface OrganizationSummary {
  id: number
  name: string
  slug: string
  type: string | null
  logo_url: string | null
}

export interface OrgMembershipSummary {
  id: number
  org_role: string
  status: string
  organization: OrganizationSummary
}

export interface PlatformAccount {
  created_at: string
}

export interface OrganizationAccount {
  organization_id: number | null
  created_at: string
}

export interface LearnerAccount {
  primary_org_id: number | null
  created_at: string
}

export interface AuthUser {
  id: number
  username: string
  email: string
  role: string
  status: string
  account_type: string
  organization_id: number | null
  organization: OrganizationSummary | null
  profile: UserProfile | null
  memberships: OrgMembershipSummary[]
  platform_account: PlatformAccount | null
  organization_account: OrganizationAccount | null
  learner_account: LearnerAccount | null
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
    isOrgAdmin: (state) => state.user?.role === 'org_admin',
    isLearner: (state) => state.user?.role === 'user' && Boolean(state.user?.learner_account),
    isOrgManager: (state) => ['org_admin', 'admin', 'superuser'].includes(state.user?.role ?? ''),
    activeMemberships: (state) =>
      (state.user?.memberships ?? []).filter((membership) => membership.status === 'active'),
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
      if (user) {
        this.user = {
          ...user,
          memberships: user.memberships ?? [],
          platform_account: user.platform_account ?? null,
          organization_account: user.organization_account ?? null,
          learner_account: user.learner_account ?? null,
        }
      } else {
        this.user = null
      }
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
