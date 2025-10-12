import { useState } from 'react'
import { PracticeQuestion } from '../types/practice'
import { clsx } from 'clsx'

interface Props {
  question: PracticeQuestion
}

export const QuestionCard = ({ question }: Props) => {
  const [selectedOption, setSelectedOption] = useState<number | null>(null)
  const [revealed, setRevealed] = useState(false)

  const handleReveal = () => setRevealed(true)

  return (
    <div className={clsx('surface-card')} style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem' }}>
        <div>
          <span className="badge" style={{ background: '#fee2e2', color: '#b91c1c' }}>
            {question.difficulty ?? 'General'}
          </span>
          <p style={{ margin: '0.75rem 0 0', fontWeight: 600 }}>{question.prompt}</p>
        </div>
      </div>
      <div style={{ display: 'grid', gap: '0.75rem' }}>
        {question.options.map((option) => {
          const isSelected = selectedOption === option.id
          const isCorrect = revealed && option.is_correct
          const isIncorrect = revealed && isSelected && !option.is_correct

          return (
            <button
              key={option.id}
              type="button"
              className="button outline"
              onClick={() => setSelectedOption(option.id)}
              style={{
                justifyContent: 'flex-start',
                borderColor: isCorrect ? '#16a34a' : isIncorrect ? '#dc2626' : undefined,
                backgroundColor: isCorrect ? 'rgba(34,197,94,0.1)' : isIncorrect ? 'rgba(220,38,38,0.08)' : undefined,
                color: isCorrect ? '#166534' : isIncorrect ? '#991b1b' : undefined,
              }}
            >
              {option.text}
            </button>
          )
        })}
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <button
          type="button"
          className="button primary"
          onClick={handleReveal}
          disabled={revealed}
          style={{ opacity: revealed ? 0.6 : 1 }}
        >
          Reveal answer
        </button>
        {revealed && question.explanation ? (
          <p style={{ margin: 0, color: '#334155' }}>{question.explanation}</p>
        ) : null}
      </div>
    </div>
  )
}
