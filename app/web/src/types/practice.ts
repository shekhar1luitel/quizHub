export interface PracticeCategorySummary {
  slug: string
  name: string
  description: string | null
  icon: string | null
  total_questions: number
  difficulty: string
  difficulties: string[]
  quiz_id?: number | null
  organization_id?: number | null
}

export interface PracticeQuestionOption {
  id: number
  text: string
  is_correct: boolean
}

export interface PracticeQuestion {
  id: number
  prompt: string
  explanation: string | null
  difficulty: string | null
  options: PracticeQuestionOption[]
}

export interface PracticeCategoryDetail {
  slug: string
  name: string
  description: string | null
  icon: string | null
  total_questions: number
  difficulty: string
  questions: PracticeQuestion[]
  organization_id?: number | null
}
