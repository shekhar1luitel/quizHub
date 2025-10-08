import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import { pinia } from '../stores'

const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export const http = axios.create({ baseURL })

http.interceptors.request.use((config) => {
  const auth = useAuthStore(pinia)
  if (auth.accessToken) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${auth.accessToken}`
  }
  return config
})

http.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const auth = useAuthStore(pinia)
      auth.logout()
    }
    return Promise.reject(error)
  }
)
