import { useCallback } from 'react'
import { useAuthContext } from '../contexts/AuthContext'

export const useAuth = () => {
  const context = useAuthContext()

  const ensureInitialized = useCallback(() => context.ensureInitialized(), [context])

  return {
    ...context,
    ensureInitialized,
  }
}
