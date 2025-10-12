import { clsx } from 'clsx'
import { PublicQuizSummary } from '../types/public'
import { formatDistanceToNow } from 'date-fns'

interface Props {
  quiz: PublicQuizSummary
}

export const QuizHighlightCard = ({ quiz }: Props) => {
  const createdAgo = formatDistanceToNow(new Date(quiz.created_at), { addSuffix: true })
  return (
    <div
      className={clsx('surface-card')}
      style={{
        padding: '1.5rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.75rem',
        background: 'linear-gradient(135deg, rgba(37, 99, 235, 0.07), rgba(59, 130, 246, 0.05))',
      }}
    >
      <div>
        <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 700 }}>{quiz.title}</h3>
        <p style={{ margin: '0.35rem 0 0', color: '#475569', fontSize: '0.95rem' }}>
          {quiz.description ?? 'Brush up essential concepts and test your progress.'}
        </p>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
        <span className="badge">{quiz.question_count} questions</span>
        <span className="badge" style={{ background: '#ede9fe', color: '#6d28d9' }}>
          {quiz.total_attempts} attempts
        </span>
        <span style={{ color: '#1d4ed8', fontWeight: 600 }}>Updated {createdAgo}</span>
      </div>
    </div>
  )
}
