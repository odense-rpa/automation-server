// alertStore.js
import { defineStore } from 'pinia'

export const useAlertStore = defineStore({
  id: 'alert',
  state: () => ({
    alerts: []
  }),
  actions: {
    addAlert(alert) {
      this.alerts.push(alert)
      if (alert.type !== 'danger') {
        setTimeout(() => {
          this.removeAlert(alert)
        }, 2500) // Adjust the timeout as needed
      }
    },
    removeAlert(alert) {
      const index = this.alerts.indexOf(alert)
      if (index !== -1) {
        this.alerts.splice(index, 1)
      }
    }
  }
})
