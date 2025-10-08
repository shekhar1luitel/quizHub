"use client"

import { useState, useEffect } from "react"
import { ApiError } from "@/lib/api"

interface UseApiState<T> {
  data: T | null
  loading: boolean
  error: string | null
}

export function useApi<T>(
  apiCall: () => Promise<T>,
  dependencies: any[] = [],
): UseApiState<T> & { refetch: () => Promise<void> } {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: true,
    error: null,
  })

  const fetchData = async () => {
    try {
      setState((prev) => ({ ...prev, loading: true, error: null }))
      const data = await apiCall()
      setState({ data, loading: false, error: null })
    } catch (error) {
      const errorMessage = error instanceof ApiError ? error.message : "An unexpected error occurred"
      setState({ data: null, loading: false, error: errorMessage })
    }
  }

  useEffect(() => {
    fetchData()
  }, dependencies)

  return {
    ...state,
    refetch: fetchData,
  }
}

export function useApiMutation<T, P = any>(): {
  mutate: (params: P) => Promise<T>
  loading: boolean
  error: string | null
  data: T | null
  reset: () => void
} {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  })

  const mutate = async (apiCall: (params: P) => Promise<T>, params: P): Promise<T> => {
    try {
      setState((prev) => ({ ...prev, loading: true, error: null }))
      const data = await apiCall(params)
      setState({ data, loading: false, error: null })
      return data
    } catch (error) {
      const errorMessage = error instanceof ApiError ? error.message : "An unexpected error occurred"
      setState({ data: null, loading: false, error: errorMessage })
      throw error
    }
  }

  const reset = () => {
    setState({ data: null, loading: false, error: null })
  }

  return {
    mutate: (params: P) => mutate(() => Promise.resolve({} as T), params),
    ...state,
    reset,
  }
}
