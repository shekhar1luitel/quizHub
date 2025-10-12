import { useEffect, useState } from 'react'
import { apiClient } from '../api/client'
import { DashboardSummary } from '../types/dashboard'
import { MetricCard } from '../components/MetricCard'
import { format } from 'date-fns'
import { LoadingScreen } from '../components/Spinner'

export const DashboardPage = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    apiClient
      .get<DashboardSummary>('/dashboard/summary')
      .then((response) => setSummary(response.data))
      .catch((err) => {
        console.error(err)
        setError('Unable to load dashboard insights right now.')
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return <LoadingScreen />
  }

  if (error) {
    return (
      <div className="main-container">
        <div className="surface-card" style={{ padding: '2rem' }}>
          <h2 style={{ marginTop: 0 }}>Dashboard</h2>
          <p style={{ color: '#dc2626' }}>{error}</p>
        </div>
      </div>
    )
  }

  if (!summary) {
    return null
  }

  return (
    <div className="main-container" style={{ paddingTop: '2.5rem', paddingBottom: '2.5rem' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 className="page-title">Dashboard</h1>
        <p className="page-subtitle">Monitor your learning streak and discover where to focus next.</p>
      </div>

      <div className="metric-grid" style={{ marginBottom: '2rem' }}>
        <MetricCard label="Total attempts" value={summary.total_attempts} />
        <MetricCard label="Average score" value={`${summary.average_score.toFixed(1)}%`} accent="#7c3aed" />
        <MetricCard label="Correct answers" value={summary.total_correct_answers} accent="#16a34a" />
        <MetricCard label="Active streak" value={`${summary.streak} days`} accent="#f97316" />
      </div>

      <div className="surface-card table-card" style={{ marginBottom: '2rem' }}>
        <table>
          <thead>
            <tr>
              <th>Recent quizzes</th>
              <th>Score</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            {summary.recent_attempts.length === 0 ? (
              <tr>
                <td colSpan={3} style={{ textAlign: 'center', padding: '1.5rem', color: '#64748b' }}>
                  Complete a quiz to see it appear here.
                </td>
              </tr>
            ) : (
              summary.recent_attempts.map((attempt) => (
                <tr key={attempt.id}>
                  <td>{attempt.quiz_title}</td>
                  <td>{attempt.score.toFixed(1)}%</td>
                  <td>{format(new Date(attempt.submitted_at), 'dd MMM yyyy')}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="surface-card table-card">
        <table>
          <thead>
            <tr>
              <th>Category</th>
              <th>Attempts</th>
              <th>Average score</th>
            </tr>
          </thead>
          <tbody>
            {summary.category_accuracy.length === 0 ? (
              <tr>
                <td colSpan={3} style={{ textAlign: 'center', padding: '1.5rem', color: '#64748b' }}>
                  Start practicing to unlock accuracy breakdowns.
                </td>
              </tr>
            ) : (
              summary.category_accuracy.map((category) => (
                <tr key={`${category.category_id ?? 'general'}`}> 
                  <td>{category.category_name}</td>
                  <td>{category.attempts}</td>
                  <td>{category.average_score.toFixed(1)}%</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
