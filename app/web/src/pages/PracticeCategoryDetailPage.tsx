import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { apiClient } from '../api/client'
import { PracticeCategoryDetail } from '../types/practice'
import { LoadingScreen } from '../components/Spinner'
import { QuestionCard } from '../components/QuestionCard'

export const PracticeCategoryDetailPage = () => {
  const { slug } = useParams<{ slug: string }>()
  const [category, setCategory] = useState<PracticeCategoryDetail | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!slug) return
    apiClient
      .get<PracticeCategoryDetail>(`/practice/categories/${slug}`)
      .then((response) => setCategory(response.data))
      .catch((err) => {
        console.error(err)
        setError('Unable to load questions for this category.')
      })
      .finally(() => setLoading(false))
  }, [slug])

  if (loading) {
    return <LoadingScreen />
  }

  if (error) {
    return (
      <div className="main-container" style={{ paddingTop: '2.5rem' }}>
        <div className="surface-card" style={{ padding: '2rem' }}>
          <h1 className="page-title">Practice</h1>
          <p style={{ color: '#dc2626' }}>{error}</p>
        </div>
      </div>
    )
  }

  if (!category) {
    return null
  }

  return (
    <div className="main-container" style={{ paddingTop: '2.5rem', paddingBottom: '2.5rem' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 className="page-title">{category.name}</h1>
        <p className="page-subtitle">
          {category.description || 'Work through the set and reveal answers when you are ready.'}
        </p>
      </div>
      <div style={{ display: 'grid', gap: '1.5rem' }}>
        {category.questions.map((question) => (
          <QuestionCard key={question.id} question={question} />
        ))}
      </div>
    </div>
  )
}
