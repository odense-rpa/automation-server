import { defineStore } from 'pinia'

export const useSettingsStore = defineStore('settings', {
  state: () => ({
    apiUrl: import.meta.env.VITE_ATS_API_BASE_URL || '/api/',
    token: ''
  }),
  persist: {
    key: 'settings',
    storage: localStorage
  },
  actions: {
    setApiUrl(url) {
      this.apiUrl = url
    },
    setToken(token) {
      this.token = token
    }
  }
})
