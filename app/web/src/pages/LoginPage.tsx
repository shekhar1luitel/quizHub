import type { FormEvent } from 'react'
import { useState } from 'react'
import { useLocation, useNavigate, type Location } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export const LoginPage = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { login } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const from = (location.state as { from?: Location })?.from?.pathname || '/dashboard'

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setLoading(true)
    setError(null)
    try {
      await login({ username, password })
      navigate(from, { replace: true })
    } catch (err) {
      console.error(err)
      setError('Invalid credentials or unverified account.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="main-container" style={{ maxWidth: '420px' }}>
      <div className="surface-card" style={{ padding: '2.5rem', marginTop: '4rem' }}>
        <h2 style={{ marginTop: 0, fontSize: '1.75rem', fontWeight: 700 }}>Sign in</h2>
        <p style={{ color: '#475569', marginBottom: '1.5rem' }}>
          Welcome back! Continue your preparation journey with fresh insights.
        </p>
        <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '1rem' }}>
          <div>
            <label htmlFor="username" style={{ display: 'block', marginBottom: '0.35rem', fontWeight: 600 }}>
              Username or email
            </label>
            <input
              id="username"
              className="input"
              placeholder="yourname"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              autoComplete="username"
              required
            />
          </div>
          <div>
            <label htmlFor="password" style={{ display: 'block', marginBottom: '0.35rem', fontWeight: 600 }}>
              Password
            </label>
            <input
              id="password"
              type="password"
              className="input"
              placeholder="••••••••"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              autoComplete="current-password"
              required
            />
          </div>
          {error ? <p style={{ color: '#dc2626', margin: 0 }}>{error}</p> : null}
          <button type="submit" className="button primary" disabled={loading}>
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  )
}
