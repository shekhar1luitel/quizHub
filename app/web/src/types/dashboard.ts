export interface AttemptSummary {
  id: number
  quiz_id: number
  quiz_title: string
  score: number
  submitted_at: string
}

export interface CategoryAccuracy {
  category_id: number | null
  category_name: string
  attempts: number
  average_score: number
}

export interface WeeklyActivityEntry {
  label: string
  attempts: number
}

export interface DashboardSummary {
  total_attempts: number
  average_score: number
  total_correct_answers: number
  total_questions_answered: number
  recent_attempts: AttemptSummary[]
  streak: number
  category_accuracy: CategoryAccuracy[]
  weekly_activity: WeeklyActivityEntry[]
}
