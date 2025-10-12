import { useEffect, useState } from 'react'
import { apiClient } from '../api/client'
import { PracticeCategorySummary } from '../types/practice'
import { PracticeCategoryCard } from '../components/PracticeCategoryCard'
import { LoadingScreen } from '../components/Spinner'

export const PracticeCategoriesPage = () => {
  const [categories, setCategories] = useState<PracticeCategorySummary[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    apiClient
      .get<PracticeCategorySummary[]>('/practice/categories')
      .then((response) => setCategories(response.data))
      .catch((err) => {
        console.error(err)
        setError('Unable to load practice categories.')
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return <LoadingScreen />
  }

  return (
    <div className="main-container" style={{ paddingTop: '2.5rem', paddingBottom: '2.5rem' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 className="page-title">Practice library</h1>
        <p className="page-subtitle">Choose a category to start practicing with curated question sets.</p>
      </div>
      {error ? (
        <div className="surface-card" style={{ padding: '1.5rem' }}>
          <p style={{ color: '#dc2626', margin: 0 }}>{error}</p>
        </div>
      ) : (
        <div className="card-grid">
          {categories.map((category) => (
            <PracticeCategoryCard key={category.slug} category={category} />
          ))}
        </div>
      )}
    </div>
  )
}
