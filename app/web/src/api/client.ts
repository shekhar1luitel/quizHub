import axios from 'axios'

const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

let accessToken: string | null = null
let unauthorizedHandler: (() => void) | null = null

export const setAccessToken = (token: string | null) => {
  accessToken = token
}

export const registerUnauthorizedHandler = (handler: () => void) => {
  unauthorizedHandler = handler
}

export const apiClient = axios.create({ baseURL })

apiClient.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${accessToken}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && unauthorizedHandler) {
      unauthorizedHandler()
    }
    return Promise.reject(error)
  }
)
