import { defineStore } from 'pinia'

export const useSettingsStore = defineStore('settings', {
  state: () => ({
    apiUrl: import.meta.env.VITE_ATS_API_BASE_URL || '/api/',
    token: ''
  }),
  persist: {
    enabled: true,
    strategies: [
      {
        key: 'settings', // name for the storage item
        storage: localStorage // can also use sessionStorage here
      }
    ]
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
