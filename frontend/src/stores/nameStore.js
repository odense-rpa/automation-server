import { defineStore } from 'pinia'
import { processesAPI, workqueuesAPI } from '@/services/automationserver'

// Names for process and workqueue ids, for labels in lists. One request per
// type (deleted ones included) instead of one request per label on screen.
// An id that isn't known yet (e.g. created after the last load) triggers a
// reload, at most once per RELOAD_MS.
const RELOAD_MS = 30000

const loaders = {
  processes: () => processesAPI.getProcesses(true),
  workqueues: () => workqueuesAPI.getWorkqueues(true)
}

// In-flight loads, shared by every label that asks at the same time
const pending = {}

export const useNameStore = defineStore('names', {
  state: () => ({
    processes: {},
    workqueues: {},
    loadedAt: { processes: 0, workqueues: 0 }
  }),
  actions: {
    async ensure(kind, id) {
      if (this[kind][id]) return
      if (!pending[kind] && Date.now() - this.loadedAt[kind] < RELOAD_MS) return
      await this.load(kind)
    },
    load(kind) {
      pending[kind] ??= loaders[kind]()
        .then((items) => {
          this[kind] = Object.fromEntries(
            items.map((item) => [item.id, { name: item.name, deleted: item.deleted }])
          )
          this.loadedAt[kind] = Date.now()
        })
        .catch(() => {
          // Labels stay empty; the next unknown id tries again after RELOAD_MS
          this.loadedAt[kind] = Date.now()
        })
        .finally(() => {
          delete pending[kind]
        })
      return pending[kind]
    },
    // Call after creating, renaming or deleting a process or workqueue
    invalidate(kind) {
      this.loadedAt[kind] = 0
      this[kind] = {}
    }
  }
})
