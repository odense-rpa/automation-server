import { defineStore } from 'pinia'

// Older versions persisted this store to localStorage by mistake (the plugin
// ignored the old config syntax), so filters survived browser restarts.
// Remove that leftover once; the store now lives in sessionStorage.
try {
  localStorage.removeItem('tableState')
} catch {
  // storage unavailable (private mode etc.): nothing to clean up
}

export const useTableStateStore = defineStore('tableState', {
  state: () => ({
    tables: {}
  }),
  // Per browser tab: search terms and pages reset when the tab is closed
  persist: {
    key: 'table-state',
    storage: sessionStorage
  },
  getters: {
    getSearchTerm: (state) => (viewId) => {
      return state.tables[viewId]?.searchTerm || ''
    },
    getPage: (state) => (viewId) => {
      return state.tables[viewId]?.page || 1
    },
    getOption: (state) => (viewId, key, defaultValue) => {
      return state.tables[viewId]?.options?.[key] ?? defaultValue
    }
  },
  actions: {
    setSearchTerm(viewId, value) {
      if (!this.tables[viewId]) {
        this.tables[viewId] = { searchTerm: '', page: 1 }
      }
      this.tables[viewId].searchTerm = value
      this.tables[viewId].page = 1
    },
    setPage(viewId, value) {
      if (!this.tables[viewId]) {
        this.tables[viewId] = { searchTerm: '', page: 1 }
      }
      this.tables[viewId].page = value
    },
    setOption(viewId, key, value) {
      if (!this.tables[viewId]) {
        this.tables[viewId] = { searchTerm: '', page: 1 }
      }
      if (!this.tables[viewId].options) {
        this.tables[viewId].options = {}
      }
      this.tables[viewId].options[key] = value
    },
    clearState(viewId) {
      delete this.tables[viewId]
    }
  }
})
