// For views that show one item (a process, workqueue, session, ...).
//
// this.loadItem(load, { what, list }) runs the load function and handles the
// failures:
//   404 / 410  -> the not-found page, in place (the URL stays), saying what
//                 is missing or deleted and linking back to its list
//   otherwise  -> this.loadError is set; show <item-load-error> with a retry
//
//   what: 'Process 12'                      (shown to the user)
//   list: { name: 'process', label: 'Processes' }   (route name + button text;
//         optional params, e.g. { name: 'workqueue.detail', params: { id: 3 }, ... })
export default {
  data() {
    return { loadError: null }
  },
  methods: {
    async loadItem(load, { what, list }) {
      this.loadError = null
      try {
        return await load()
      } catch (error) {
        const status = error?.cause?.response?.status
        if (status === 404 || status === 410) {
          this.$router.replace({
            name: 'not-found',
            params: { pathMatch: this.$route.path.substring(1).split('/') },
            query: this.$route.query,
            hash: this.$route.hash,
            // History state must be plain data: no route objects or functions
            state: { notFound: { what, deleted: status === 410, list } }
          })
        } else {
          this.loadError = error.message
        }
        return null
      }
    }
  }
}
