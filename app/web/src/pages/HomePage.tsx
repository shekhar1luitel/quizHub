import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiClient } from '../api/client'
import { PublicHomeResponse } from '../types/public'
import { PracticeCategoryCard } from '../components/PracticeCategoryCard'
import { QuizHighlightCard } from '../components/QuizHighlightCard'
import { useAuth } from '../hooks/useAuth'
import { PracticeCategorySummary } from '../types/practice'

export const HomePage = () => {
  const [data, setData] = useState<PublicHomeResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const { isAuthenticated } = useAuth()

  useEffect(() => {
    apiClient
      .get<PublicHomeResponse>('/public/home')
      .then((response) => setData(response.data))
      .catch((err) => {
        console.error(err)
        setError('Unable to load featured content at the moment.')
      })
  }, [])

  const categorySummaries = useMemo(() => {
    if (!data) return []
    return data.featured_categories.map(
      (category): PracticeCategorySummary => ({
        ...category,
        difficulties: [],
        quiz_id: null,
        organization_id: null,
      })
    )
  }, [data])

  return (
    <div>
      <section className="hero">
        <h1>Master Loksewa preparation with confident daily practice.</h1>
        <p>
          Track your progress, revisit bookmarked questions, and compete with yourself using
          intelligent analytics crafted for ambitious learners.
        </p>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          {isAuthenticated ? (
            <Link to="/dashboard" className="button primary">
              Go to dashboard
            </Link>
          ) : (
            <Link to="/login" className="button primary">
              Sign in to continue
            </Link>
          )}
          <Link to="/practice" className="button outline">
            Explore practice sets
          </Link>
        </div>
      </section>

      <section className="main-container">
        <div style={{ marginBottom: '2.5rem' }}>
          <h2 className="section-title">Popular categories</h2>
          <p className="section-subtitle">Carefully curated practice topics sourced from verified experts.</p>
          {error ? (
            <p style={{ color: '#dc2626' }}>{error}</p>
          ) : data ? (
            <div className="card-grid">
              {categorySummaries.map((category) => (
                <PracticeCategoryCard key={category.slug} category={category} />
              ))}
            </div>
          ) : (
            <p style={{ color: '#64748b' }}>Loading categories…</p>
          )}
        </div>

        <div style={{ marginBottom: '2.5rem' }}>
          <h2 className="section-title">Trending quizzes</h2>
          <p className="section-subtitle">Stay sharp with the most attempted quizzes from the community.</p>
          {error ? (
            <p style={{ color: '#dc2626' }}>{error}</p>
          ) : data ? (
            <div className="card-grid">
              {data.trending_quizzes.map((quiz) => (
                <QuizHighlightCard key={quiz.id} quiz={quiz} />
              ))}
            </div>
          ) : (
            <p style={{ color: '#64748b' }}>Crunching stats…</p>
          )}
        </div>
      </section>
    </div>
  )
}
