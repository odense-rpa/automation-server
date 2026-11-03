<template>
  <content-card title="Up Next">
    <template v-slot:header-right>
      <search-input v-model="searchTerm" placeholder="Search processes..." />
      <select v-model="selectedHours" class="select select-sm select-bordered">
        <option :value="1">Next 1h</option>
        <option :value="3">Next 3h</option>
        <option :value="12">Next 12h</option>
        <option :value="24">Next 24h</option>
        <option :value="48">Next 48h</option>
        <option :value="72">Next 72h</option>
      </select>
    </template>

    <!-- Loading state -->
    <div v-if="isLoading" class="text-center py-4">
      <span class="loading loading-spinner loading-md"></span>
      <p class="mt-2">Loading upcoming executions...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="alert alert-error">
      <font-awesome-icon :icon="['fas', 'triangle-exclamation']" />
      <span>{{ error }}</span>
    </div>

    <!-- Empty state -->
    <div v-else-if="filteredExecutions.length === 0" class="text-center mb-4">
      <p class="text-base-content/60 font-semibold">
        {{ searchTerm ? 'No executions found matching your search.' : `No executions scheduled for the next ${selectedHours} hours.` }}
      </p>
    </div>

    <!-- Executions table -->
    <div v-else>
      <table class="table w-full mb-3">
        <thead>
          <tr>
            <th class="text-left">Process</th>
            <th class="text-center">Type</th>
            <th class="text-center">Next Execution</th>
            <th class="text-center">In</th>
            <th class="text-left">Parameters</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="execution in filteredExecutions"
            :key="`${execution.trigger_id}-${execution.next_execution}`"
            class="hover:bg-base-300"
          >
            <td class="text-left p-0">
              <router-link :to="{ name: 'process.edit', params: { id: execution.process_id } }"
                class="block px-4 py-3 no-underline text-inherit">{{ execution.process_name }}</router-link>
            </td>
            <td class="text-center p-0">
              <router-link :to="{ name: 'process.edit', params: { id: execution.process_id } }"
                class="block px-4 py-3 no-underline text-inherit">
                <span class="badge badge-sm badge-ghost">
                  {{ execution.trigger_type }}
                </span>
              </router-link>
            </td>
            <td class="text-center p-0">
              <router-link :to="{ name: 'process.edit', params: { id: execution.process_id } }"
                class="block px-4 py-3 no-underline text-inherit">{{ formatExecutionTime(execution.next_execution) }}</router-link>
            </td>
            <td class="text-center p-0">
              <router-link :to="{ name: 'process.edit', params: { id: execution.process_id } }"
                class="block px-4 py-3 no-underline text-inherit">{{ formatRelativeTime(execution.next_execution) }}</router-link>
            </td>
            <td class="text-left p-0">
              <router-link :to="{ name: 'process.edit', params: { id: execution.process_id } }"
                class="block px-4 py-3 no-underline text-inherit">
                <span v-if="execution.parameters" class="text-xs">{{ execution.parameters }}</span>
                <span v-else class="text-base-content/50">-</span>
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </content-card>
</template>

<script>
import { triggersAPI } from '@/services/automationserver'
import { useTableStateStore } from '@/stores/tableStateStore'
import ContentCard from './ContentCard.vue'
import SearchInput from './SearchInput.vue'

export default {
  name: 'UpNextDisplay',
  components: {
    ContentCard,
    SearchInput
  },
  setup() {
    return { tableStateStore: useTableStateStore() }
  },
  data() {
    return {
      executions: [],
      isLoading: false,
      hasLoaded: false,
      error: null,
      searchTerm: '',
      refreshInterval: null
    }
  },
  computed: {
    selectedHours: {
      get() {
        return this.tableStateStore.getOption('upNext', 'hours', 24)
      },
      set(value) {
        this.tableStateStore.setOption('upNext', 'hours', value)
      }
    },
    filteredExecutions() {
      if (!this.searchTerm) return this.executions

      const search = this.searchTerm.toLowerCase()
      return this.executions.filter(execution =>
        execution.process_name.toLowerCase().includes(search) ||
        execution.process_description?.toLowerCase().includes(search) ||
        execution.trigger_type.toLowerCase().includes(search)
      )
    }
  },
  watch: {
    selectedHours() {
      this.refreshExecutions()
    }
  },
  async created() {
    await this.refreshExecutions()
    this.refreshInterval = setInterval(this.refreshExecutions, 60000)
  },
  unmounted() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval)
    }
  },
  methods: {
    async refreshExecutions() {
      // Spinner only before the first load; refreshes keep the table on screen
      this.isLoading = !this.hasLoaded
      this.error = null

      try {
        this.executions = await triggersAPI.getUpcomingExecutions(this.selectedHours)
        this.hasLoaded = true
      } catch {
        this.error = 'Failed to load upcoming executions'
      } finally {
        this.isLoading = false
      }
    },
    formatExecutionTime(isoString) {
      const date = new Date(isoString)
      const now = new Date()
      const isToday = date.toDateString() === now.toDateString()
      const isTomorrow = date.toDateString() === new Date(now.getTime() + 24 * 60 * 60 * 1000).toDateString()

      const timeString = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

      if (isToday) return `Today ${timeString}`
      if (isTomorrow) return `Tomorrow ${timeString}`
      return `${date.toLocaleDateString()} ${timeString}`
    },
    formatRelativeTime(isoString) {
      const date = new Date(isoString)
      const now = new Date()
      const diffMs = date.getTime() - now.getTime()
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
      const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60))

      if (diffHours < 1) {
        return diffMinutes <= 1 ? 'in 1 minute' : `in ${diffMinutes} minutes`
      } else if (diffHours < 24) {
        return diffHours === 1 ? 'in 1 hour' : `in ${diffHours} hours`
      } else {
        const diffDays = Math.floor(diffHours / 24)
        return diffDays === 1 ? 'in 1 day' : `in ${diffDays} days`
      }
    }
  }
}
</script>

<style scoped>
.transition-all {
  transition: all 0.3s ease;
}
</style>
