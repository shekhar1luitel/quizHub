import { useAuth } from '../hooks/useAuth'

export const ProfilePage = () => {
  const { user } = useAuth()

  if (!user) {
    return null
  }

  return (
    <div className="main-container" style={{ paddingTop: '2.5rem', paddingBottom: '2.5rem' }}>
      <div className="surface-card" style={{ padding: '2.5rem' }}>
        <h1 className="page-title" style={{ marginTop: 0 }}>
          Profile
        </h1>
        <p className="page-subtitle">Keep your learner profile up to date.</p>
        <div style={{ display: 'grid', gap: '1rem', maxWidth: '480px' }}>
          <div>
            <span style={{ display: 'block', fontWeight: 600 }}>Username</span>
            <span style={{ color: '#475569' }}>{user.username}</span>
          </div>
          <div>
            <span style={{ display: 'block', fontWeight: 600 }}>Email</span>
            <span style={{ color: '#475569' }}>{user.email}</span>
          </div>
          <div>
            <span style={{ display: 'block', fontWeight: 600 }}>Role</span>
            <span style={{ color: '#475569', textTransform: 'capitalize' }}>{user.role}</span>
          </div>
          {user.organization ? (
            <div>
              <span style={{ display: 'block', fontWeight: 600 }}>Organization</span>
              <span style={{ color: '#475569' }}>{user.organization.name}</span>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  )
}
