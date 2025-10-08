import axios from 'axios'

const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export const http = axios.create({ baseURL })

http.interceptors.response.use(
  (r) => r,
  async (error) => {
    // handle refresh flow later
    return Promise.reject(error)
  }
)
