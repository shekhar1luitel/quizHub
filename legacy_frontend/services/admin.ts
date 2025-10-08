import { api } from "@/lib/api"
import type { User } from "./auth"
import type { Category, Question } from "./quiz"

export interface AdminStats {
  total_users: number
  active_users: number
  total_questions: number
  total_categories: number
  tests_today: number
  average_score: number
  system_health: number
  pending_reports: number
}

export interface UserWithStats extends User {
  total_attempts: number
  average_score: number
  last_active: string
  status: "active" | "inactive" | "banned"
}

export interface QuestionWithCategory extends Question {
  category_name: string
  created_at: string
  updated_at: string
  status: "active" | "inactive"
}

export const adminService = {
  // Get admin dashboard stats
  getStats: async (): Promise<AdminStats> => {
    return api.get<AdminStats>("/admin/stats")
  },

  // User management
  getUsers: async (
    page = 1,
    limit = 10,
    search?: string,
  ): Promise<{
    users: UserWithStats[]
    total: number
    page: number
    total_pages: number
  }> => {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      ...(search && { search }),
    })
    return api.get(`/admin/users?${params}`)
  },

  updateUserStatus: async (userId: number, status: "active" | "inactive" | "banned"): Promise<User> => {
    return api.put<User>(`/admin/users/${userId}/status`, { status })
  },

  deleteUser: async (userId: number): Promise<void> => {
    return api.delete(`/admin/users/${userId}`)
  },

  // Question management
  getQuestions: async (
    page = 1,
    limit = 10,
    categoryId?: number,
  ): Promise<{
    questions: QuestionWithCategory[]
    total: number
    page: number
    total_pages: number
  }> => {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      ...(categoryId && { category_id: categoryId.toString() }),
    })
    return api.get(`/admin/questions?${params}`)
  },

  createQuestion: async (questionData: {
    question: string
    options: string[]
    correct_answer: number
    explanation?: string
    category_id: number
    difficulty: string
  }): Promise<Question> => {
    return api.post<Question>("/admin/questions", questionData)
  },

  updateQuestion: async (questionId: number, questionData: Partial<Question>): Promise<Question> => {
    return api.put<Question>(`/admin/questions/${questionId}`, questionData)
  },

  deleteQuestion: async (questionId: number): Promise<void> => {
    return api.delete(`/admin/questions/${questionId}`)
  },

  // Category management
  createCategory: async (categoryData: {
    name: string
    description: string
    icon?: string
    difficulty: string
  }): Promise<Category> => {
    return api.post<Category>("/admin/categories", categoryData)
  },

  updateCategory: async (categoryId: number, categoryData: Partial<Category>): Promise<Category> => {
    return api.put<Category>(`/admin/categories/${categoryId}`, categoryData)
  },

  deleteCategory: async (categoryId: number): Promise<void> => {
    return api.delete(`/admin/categories/${categoryId}`)
  },

  // Reports and analytics
  getSystemReports: async (): Promise<{
    user_activity: Array<{
      date: string
      new_users: number
      active_users: number
      tests_taken: number
    }>
    category_performance: Array<{
      category: Category
      total_attempts: number
      average_score: number
    }>
    recent_activity: Array<{
      id: number
      user: string
      action: string
      score?: number
      timestamp: string
    }>
  }> => {
    return api.get("/admin/reports")
  },
}
