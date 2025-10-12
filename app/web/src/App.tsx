import { Navigate, Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { ProtectedRoute } from './components/ProtectedRoute'
import { DashboardPage } from './pages/DashboardPage'
import { LoginPage } from './pages/LoginPage'
import { PracticeCategoriesPage } from './pages/PracticeCategoriesPage'
import { PracticeCategoryDetailPage } from './pages/PracticeCategoryDetailPage'
import { ProfilePage } from './pages/ProfilePage'
import { NotFoundPage } from './pages/NotFoundPage'
import { HomePage } from './pages/HomePage'

const App = () => {
  return (
    <Routes>
      <Route element={<Layout />}> 
        <Route index element={<HomePage />} />
        <Route
          path="dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="practice"
          element={
            <ProtectedRoute>
              <PracticeCategoriesPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="practice/:slug"
          element={
            <ProtectedRoute>
              <PracticeCategoryDetailPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="profile"
          element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          }
        />
        <Route path="login" element={<LoginPage />} />
        <Route path="logout" element={<Navigate to="/login" replace />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  )
}

export default App
