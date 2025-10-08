import { api, setAuthToken, removeAuthToken } from "@/lib/api"

export interface User {
  id: number
  name: string
  email: string
  role?: string
  created_at?: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password1: string
  password2: string
}

export interface AuthResponse {
  user: User
  token: string
  message?: string
}

export const authService = {
  // Login user
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>("/auth/login/", credentials)

    if (response.token) {
      setAuthToken(response.token)
    }

    return response
  },

  // Register new user
  register: async (userData: RegisterRequest): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>("/auth/registration/", userData)
  
    if (response.token) {
      setAuthToken(response.token)
    }
  
    return response
  },

  // Logout user
  logout: async (): Promise<void> => {
    try {
      await api.post("/auth/logout")
    } catch (error) {
      // Continue with logout even if API call fails
      console.warn("Logout API call failed:", error)
    } finally {
      removeAuthToken()
    }
  },

  // Get current user profile
  getProfile: async (): Promise<User> => {
    return api.get<User>("/auth/profile")
  },

  // Update user profile
  updateProfile: async (userData: Partial<User>): Promise<User> => {
    return api.put<User>("/auth/profile", userData)
  },

  // Check if user is authenticated
  isAuthenticated: (): boolean => {
    if (typeof window === "undefined") return false
    return !!localStorage.getItem("auth_token")
  },
}
