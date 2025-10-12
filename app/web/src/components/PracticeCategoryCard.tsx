import { Link } from 'react-router-dom'
import { PracticeCategorySummary } from '../types/practice'
import { clsx } from 'clsx'

interface Props {
  category: PracticeCategorySummary
}

const iconFallbacks = ['📚', '🧠', '⚡️', '🎯', '📝', '🚀']

const pickIcon = (category: PracticeCategorySummary) => {
  if (category.icon) return category.icon
  const index = category.slug.charCodeAt(0) % iconFallbacks.length
  return iconFallbacks[index]
}

export const PracticeCategoryCard = ({ category }: Props) => {
  const icon = pickIcon(category)
  return (
    <Link
      to={`/practice/${category.slug}`}
      className={clsx('surface-card')}
      style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <span style={{ fontSize: '1.75rem' }}>{icon}</span>
        <div>
          <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700 }}>{category.name}</h3>
          <p style={{ margin: '0.2rem 0 0', color: '#475569', fontSize: '0.9rem' }}>
            {category.description || 'Sharpen your knowledge with curated practice questions.'}
          </p>
        </div>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: 'auto' }}>
        <span className="badge">{category.difficulty || 'Mixed'}</span>
        <span style={{ fontWeight: 600, color: '#2563eb' }}>{category.total_questions} questions</span>
      </div>
    </Link>
  )
}
