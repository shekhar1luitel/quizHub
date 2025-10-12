import { Link, NavLink, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useEffect } from 'react'

const navItems = [
  { to: '/', label: 'Home', protected: false },
  { to: '/dashboard', label: 'Dashboard', protected: true },
  { to: '/practice', label: 'Practice', protected: true },
]

export const Layout = () => {
  const { isAuthenticated, user, ensureInitialized, logout } = useAuth()
  const location = useLocation()

  useEffect(() => {
    ensureInitialized().catch((error) => {
      console.error('Failed to initialize auth', error)
    })
  }, [ensureInitialized])

  return (
    <div>
      <header className="navbar">
        <div className="main-container" style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontWeight: 700, fontSize: '1.1rem' }}>
            <span style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: '38px', height: '38px', borderRadius: '12px', background: 'linear-gradient(135deg, #2563eb, #3b82f6)', color: '#fff', fontWeight: 700 }}>
              QM
            </span>
            QuizMaster
          </Link>
          <nav style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', flex: 1 }}>
            {navItems
              .filter((item) => (item.protected ? isAuthenticated : true))
              .map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) => (isActive ? 'active' : undefined)}
                  style={{ padding: '0.5rem 0', position: 'relative' }}
                >
                  {item.label}
                  {location.pathname.startsWith(item.to) && item.to !== '/' ? (
                    <span
                      style={{
                        position: 'absolute',
                        left: 0,
                        bottom: '-0.4rem',
                        height: '3px',
                        width: '100%',
                        borderRadius: '999px',
                        background: 'linear-gradient(135deg, #2563eb, #3b82f6)',
                      }}
                    />
                  ) : null}
                </NavLink>
              ))}
          </nav>
          <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            {isAuthenticated && user ? (
              <>
                <Link to="/profile" style={{ fontWeight: 600, color: '#2563eb' }}>
                  {user.username}
                </Link>
                <button className="button outline" onClick={logout}>
                  Sign out
                </button>
              </>
            ) : (
              <Link to="/login" className="button primary">
                Sign in
              </Link>
            )}
          </div>
        </div>
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  )
}
