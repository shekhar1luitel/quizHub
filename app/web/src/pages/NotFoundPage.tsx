import { Link } from 'react-router-dom'

export const NotFoundPage = () => {
  return (
    <div className="main-container" style={{ paddingTop: '4rem', textAlign: 'center' }}>
      <div className="surface-card" style={{ padding: '3rem', maxWidth: '560px', margin: '0 auto' }}>
        <h1 style={{ fontSize: '3rem', margin: '0 0 1rem' }}>404</h1>
        <p style={{ color: '#475569', marginBottom: '2rem' }}>
          The page you are looking for might have been moved or removed.
        </p>
        <Link to="/" className="button primary">
          Back to home
        </Link>
      </div>
    </div>
  )
}
