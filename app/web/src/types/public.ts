export interface PublicCategorySummary {
  slug: string
  name: string
  description: string | null
  icon: string | null
  total_questions: number
  difficulty: string
}

export interface PublicQuizSummary {
  id: number
  title: string
  description: string | null
  question_count: number
  total_attempts: number
  created_at: string
}

export interface PublicHomeResponse {
  featured_categories: PublicCategorySummary[]
  trending_quizzes: PublicQuizSummary[]
}
