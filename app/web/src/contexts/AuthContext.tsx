import {
  ReactNode,
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react'
import { apiClient, registerUnauthorizedHandler, setAccessToken } from '../api/client'
import { AuthUser, LoginPayload, TokenResponse } from '../types/auth'

interface AuthContextValue {
  user: AuthUser | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (payload: LoginPayload) => Promise<void>
  logout: () => void
  ensureInitialized: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

const ACCESS_TOKEN_KEY = 'quizmaster_access_token'

const readInitialToken = () => {
  if (typeof window === 'undefined') return null
  return window.localStorage.getItem(ACCESS_TOKEN_KEY)
}

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [token, setToken] = useState<string | null>(() => readInitialToken())
  const [user, setUser] = useState<AuthUser | null>(null)
  const [initialized, setInitialized] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setAccessToken(token)
    if (typeof window !== 'undefined') {
      if (token) {
        window.localStorage.setItem(ACCESS_TOKEN_KEY, token)
      } else {
        window.localStorage.removeItem(ACCESS_TOKEN_KEY)
      }
    }
  }, [token])

  const fetchUser = useCallback(async () => {
    if (!token) {
      setUser(null)
      return
    }
    setLoading(true)
    try {
      const { data } = await apiClient.get<AuthUser>('/users/me')
      setUser(data)
    } catch (error) {
      console.error('Failed to load current user', error)
      setToken(null)
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [token])

  useEffect(() => {
    registerUnauthorizedHandler(() => {
      setToken(null)
      setUser(null)
    })
  }, [])

  const ensureInitialized = useCallback(async () => {
    if (initialized) return
    setInitialized(true)
    if (token && !user) {
      await fetchUser()
    }
  }, [initialized, token, user, fetchUser])

  const login = useCallback(
    async (payload: LoginPayload) => {
      const { data } = await apiClient.post<TokenResponse>('/auth/login', payload)
      setToken(data.access_token)
      setAccessToken(data.access_token)
      const profile = await apiClient.get<AuthUser>('/users/me')
      setUser(profile.data)
    },
    []
  )

  const logout = useCallback(() => {
    setToken(null)
    setUser(null)
  }, [])

  const value = useMemo(
    () => ({
      user,
      token,
      isAuthenticated: Boolean(token),
      isLoading: loading && Boolean(token),
      login,
      logout,
      ensureInitialized,
    }),
    [user, token, loading, login, logout, ensureInitialized]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuthContext = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuthContext must be used within AuthProvider')
  }
  return context
}
