// Shared logic for server-paged lists with search.
//
// The component provides:
//   tableKey             computed or data: key in tableStateStore (search term and page
//                        survive navigation within the browser tab)
//   fetchPage(params)    method: ({ page, size, search }) => { items, total_pages }
//   refreshMs            optional data: refresh interval in ms
//   pageSize             optional computed: page size, defaults to the `size` prop
//   onPageLoaded(items)  optional method: called after each successful load
//
// It gets: items, totalPages, loading, loaded, error, searchTerm, page,
// refresh(), handlePageChange(page) and emptyText(text) for the empty state.
//
// Errors are shown inline (error), not as toasts, so a polling list doesn't
// stack up alerts while the backend is unreachable.
import { useTableStateStore } from '@/stores/tableStateStore'
import polling from './polling'

export default {
  mixins: [polling],
  data() {
    return {
      items: [],
      totalPages: 1,
      loading: false,
      loaded: false,
      error: null,
      searchTimeout: null
    }
  },
  computed: {
    // A computed rather than setup(): Vue doesn't merge setup() from mixins
    tableStateStore() {
      return useTableStateStore()
    },
    searchTerm: {
      get() {
        return this.tableStateStore.getSearchTerm(this.tableKey)
      },
      set(value) {
        this.tableStateStore.setSearchTerm(this.tableKey, value)
      }
    },
    page: {
      get() {
        return this.tableStateStore.getPage(this.tableKey)
      },
      set(value) {
        this.tableStateStore.setPage(this.tableKey, value)
      }
    },
    listSize() {
      return this.pageSize ?? this.size
    }
  },
  watch: {
    searchTerm() {
      clearTimeout(this.searchTimeout)
      // The store already resets the page to 1 when the search term changes
      this.searchTimeout = setTimeout(() => this.refresh(), 300)
    }
  },
  created() {
    if (this.refreshMs) {
      this.poll(() => this.refresh(), this.refreshMs)
    }
    this.refresh()
  },
  unmounted() {
    clearTimeout(this.searchTimeout)
  },
  methods: {
    async refresh() {
      this.loading = true
      try {
        const response = await this.fetchPage({
          page: this.page,
          size: this.listSize,
          search: this.searchTerm
        })
        this.items = response.items || []
        this.totalPages = response.total_pages || 1
        this.error = null
        this.loaded = true
        // The page can fall off the end (items removed, smaller page size)
        if (this.page > this.totalPages && this.totalPages > 0) {
          this.page = this.totalPages
          return this.refresh()
        }
        this.onPageLoaded?.(this.items)
      } catch (error) {
        this.error = error.message
      } finally {
        this.loading = false
      }
    },
    handlePageChange(newPage) {
      this.page = newPage
      this.refresh()
    },
    // Empty-state text: "Loading..." until the first load, then the given text
    emptyText(text) {
      if (this.loaded) return text
      return this.error ? '' : 'Loading...'
    }
  }
}
