import { defineStore } from 'pinia'
export const useAuthStore = defineStore('auth', {
  state: () => ({ accessToken: '', refreshToken: '' }),
  actions: {
    setAccessToken(t: string) { this.accessToken = t },
    logout() { this.accessToken = ''; this.refreshToken = '' }
  }
})
