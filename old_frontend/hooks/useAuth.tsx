"use client"

import { useState, useEffect, createContext, useContext, type ReactNode } from "react"
import { authService, type User } from "@/services/auth"
import { ApiError } from "@/lib/api"

interface AuthContextType {
  user: User | null
  loading: boolean
  error: string | null
  login: (email: string, password: string) => Promise<void>
  register: (name: string, email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  clearError: () => void
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Check authentication status on mount
  useEffect(() => {
    const checkAuth = async () => {
      if (authService.isAuthenticated()) {
        try {
          const userData = await authService.getProfile()
          setUser(userData)
        } catch (error) {
          // Token might be invalid, clear it
          await authService.logout()
        }
      }
      setLoading(false)
    }

    checkAuth()
  }, [])

  const login = async (email: string, password: string) => {
    try {
      setLoading(true)
      setError(null)
      const response = await authService.login({ email, password })
      setUser(response.user)
    } catch (error) {
      if (error instanceof ApiError) {
        setError(error.message)
      } else {
        setError("Login failed. Please try again.")
      }
      throw error
    } finally {
      setLoading(false)
    }
  }

  const register = async (name: string, email: string, password: string) => {
    try {
      setLoading(true)
      setError(null)

      const payload = {
        username: name,
        email: email,
        password1: password,
        password2: password,
      }

      const response = await authService.register(payload)
      setUser(response.user)
      return response
    } catch (err: any) {
      // Axios error
      if (err.response && err.response.data) {
        // Combine all field errors into a single string
        const messages = Object.values(err.response.data)
          .flat()
          .join(" ")
        setError(messages)
      } else {
        setError("Registration failed. Please try again.")
      }
      throw err
    } finally {
      setLoading(false)
    }
  }

  const logout = async () => {
    try {
      setLoading(true)
      await authService.logout()
      setUser(null)
    } catch (error) {
      console.error("Logout error:", error)
    } finally {
      setLoading(false)
    }
  }

  const clearError = () => setError(null)

  const value: AuthContextType = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    clearError,
    isAuthenticated: !!user,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
