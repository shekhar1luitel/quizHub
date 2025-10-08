import { api } from "@/lib/api"

export interface Category {
  id: number
  name: string
  description: string
  icon?: string
  total_questions: number
  completed_questions?: number
  difficulty: "Easy" | "Medium" | "Hard" | "Mixed"
  subcategories?: string[]
}

export interface Question {
  id: number
  question: string
  options: string[]
  correct_answer: number
  explanation?: string
  category_id: number
  difficulty: string
}

export interface Quiz {
  id: number
  title: string
  description: string
  category_id: number
  questions: Question[]
  time_limit: number // in minutes
  total_questions: number
}

export interface QuizAttempt {
  id: number
  quiz_id: number
  user_id: number
  answers: { [questionId: number]: number }
  score: number
  total_questions: number
  time_spent: number // in seconds
  completed_at: string
}

export interface QuizResult {
  attempt: QuizAttempt
  correct_answers: number
  incorrect_answers: number
  percentage: number
  questions_with_answers: Array<{
    question: Question
    user_answer: number
    is_correct: boolean
  }>
}

export const quizService = {
  // Get all categories
  getCategories: async (): Promise<Category[]> => {
    return api.get<Category[]>("/categories")
  },

  // Get category by ID
  getCategory: async (categoryId: number): Promise<Category> => {
    return api.get<Category>(`/categories/${categoryId}`)
  },

  // Get quiz for category
  getQuiz: async (categoryId: number, type: "practice" | "quiz" = "quiz"): Promise<Quiz> => {
    return api.get<Quiz>(`/categories/${categoryId}/${type}`)
  },

  // Submit quiz answers
  submitQuiz: async (
    quizId: number,
    answers: { [questionId: number]: number },
    timeSpent: number,
  ): Promise<QuizResult> => {
    return api.post<QuizResult>(`/quiz/${quizId}/submit`, {
      answers,
      time_spent: timeSpent,
    })
  },

  // Get quiz result
  getQuizResult: async (attemptId: number): Promise<QuizResult> => {
    return api.get<QuizResult>(`/quiz/results/${attemptId}`)
  },

  // Get user's quiz history
  getQuizHistory: async (
    page = 1,
    limit = 10,
  ): Promise<{
    attempts: QuizAttempt[]
    total: number
    page: number
    total_pages: number
  }> => {
    return api.get(`/quiz/history?page=${page}&limit=${limit}`)
  },

  // Get user analytics
  getUserAnalytics: async (): Promise<{
    total_attempts: number
    average_score: number
    category_performance: Array<{
      category: Category
      attempts: number
      average_score: number
      best_score: number
    }>
    recent_performance: Array<{
      date: string
      score: number
    }>
  }> => {
    return api.get("/quiz/analytics")
  },
}
