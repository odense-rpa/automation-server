// alertStore.js
import { defineStore } from 'pinia'

let nextId = 0

export const useAlertStore = defineStore({
  id: 'alert',
  state: () => ({
    alerts: []
  }),
  actions: {
    addAlert(alert) {
      // A stable id keys the list, so transitions animate the right alert
      const entry = { id: ++nextId, ...alert }
      this.alerts.push(entry)
      // Errors stay until dismissed; everything else fades out
      if (entry.type !== 'error') {
        setTimeout(() => this.removeAlert(entry), 2500)
      }
    },
    removeAlert(alert) {
      this.alerts = this.alerts.filter((a) => a.id !== alert.id)
    }
  }
})
