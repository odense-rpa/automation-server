<template>
  <div class="card bg-base-100 shadow-xl card-bordered card-compact">
    <div class="card-body">
      <!-- Header with title and controls -->
      <div class="flex items-center justify-between">
        <h2 class="card-title">
          <font-awesome-icon :icon="['fas', 'clock']" class="mr-2"/>
          Up Next ({{ filteredExecutions.length }})
        </h2>
        <div class="card-actions">
          <div class="join">
            <!-- Search input -->
            <input 
              type="text" 
              v-model="searchTerm" 
              placeholder="Search processes..."
              class="join-item input input-bordered input-sm w-full max-w-xs" 
            />
            <!-- Collapse toggle button -->
            <button 
              @click="isCollapsed = !isCollapsed"
              class="join-item btn btn-square btn-sm"
              :class="{ 'btn-active': !isCollapsed }"
            >
              <font-awesome-icon :icon="['fas', isCollapsed ? 'chevron-down' : 'chevron-up']" />
            </button>
          </div>
        </div>
      </div>

      <!-- Collapsible content -->
      <div v-if="!isCollapsed" class="transition-all duration-300">
        <!-- Loading state -->
        <div v-if="isLoading" class="text-center py-4">
          <span class="loading loading-spinner loading-md"></span>
          <p class="mt-2">Loading upcoming executions...</p>
        </div>

        <!-- Error state -->
        <div v-else-if="error" class="alert alert-error">
          <font-awesome-icon :icon="['fas', 'exclamation-triangle']" />
          <span>{{ error }}</span>
        </div>

        <!-- Empty state -->
        <div v-else-if="filteredExecutions.length === 0" class="text-center py-4">
          <font-awesome-icon :icon="['fas', 'calendar-check']" class="text-4xl text-base-300 mb-2" />
          <p class="text-base-content/70">
            {{ searchTerm ? 'No executions found matching your search.' : 'No executions scheduled for the next 24 hours.' }}
          </p>
        </div>

        <!-- Executions list -->
        <div v-else class="space-y-3">
          <div 
            v-for="execution in filteredExecutions" 
            :key="`${execution.trigger_id}-${execution.next_execution}`"
            class="flex items-center justify-between p-3 bg-base-200 rounded-lg hover:bg-base-300 transition-colors"
          >
            <!-- Execution info -->
            <div class="flex-1">
              <div class="flex items-center gap-2">
                <span class="font-semibold text-primary">{{ execution.process_name }}</span>
                <span class="badge badge-sm" :class="getTriggerTypeClass(execution.trigger_type)">
                  {{ execution.trigger_type }}
                </span>
              </div>
              <div class="text-sm text-base-content/70 mt-1">
                {{ execution.process_description }}
              </div>
              <div v-if="execution.parameters" class="text-xs text-base-content/50 mt-1">
                Parameters: {{ execution.parameters }}
              </div>
            </div>

            <!-- Time info -->
            <div class="text-right">
              <div class="font-medium">{{ formatExecutionTime(execution.next_execution) }}</div>
              <div class="text-sm text-base-content/70">{{ formatRelativeTime(execution.next_execution) }}</div>
            </div>
          </div>
        </div>

        <!-- Refresh info -->
        <div v-if="!isLoading && !error" class="text-center mt-4 text-xs text-base-content/50">
          Last updated: {{ formatDateTime(lastUpdated) }}
          <button @click="refreshExecutions" class="btn btn-ghost btn-xs ml-2">
            <font-awesome-icon :icon="['fas', 'refresh']" />
            Refresh
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { triggersAPI } from '@/services/automationserver'

export default {
  name: 'UpNextDisplay',
  setup() {
    // Reactive state
    const executions = ref([])
    const isLoading = ref(false)
    const error = ref(null)
    const searchTerm = ref('')
    const isCollapsed = ref(false)
    const lastUpdated = ref(null)
    const refreshInterval = ref(null)

    // Computed properties
    const filteredExecutions = computed(() => {
      if (!searchTerm.value) return executions.value
      
      const search = searchTerm.value.toLowerCase()
      return executions.value.filter(execution => 
        execution.process_name.toLowerCase().includes(search) ||
        execution.process_description?.toLowerCase().includes(search) ||
        execution.trigger_type.toLowerCase().includes(search)
      )
    })

    // Methods
    const refreshExecutions = async () => {
      isLoading.value = true
      error.value = null
      
      try {
        const data = await triggersAPI.getUpcomingExecutions()
        executions.value = data
        lastUpdated.value = new Date()
      } catch (err) {
        error.value = 'Failed to load upcoming executions'
        console.error('Error loading upcoming executions:', err)
      } finally {
        isLoading.value = false
      }
    }

    const formatExecutionTime = (isoString) => {
      const date = new Date(isoString)
      const now = new Date()
      const isToday = date.toDateString() === now.toDateString()
      const isTomorrow = date.toDateString() === new Date(now.getTime() + 24 * 60 * 60 * 1000).toDateString()
      
      const timeString = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      
      if (isToday) return `Today ${timeString}`
      if (isTomorrow) return `Tomorrow ${timeString}`
      return `${date.toLocaleDateString()} ${timeString}`
    }

    const formatRelativeTime = (isoString) => {
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

    const formatDateTime = (date) => {
      if (!date) return ''
      return date.toLocaleString()
    }

    const getTriggerTypeClass = (type) => {
      switch (type) {
        case 'cron':
          return 'badge-primary'
        case 'date':
          return 'badge-secondary'
        case 'workqueue':
          return 'badge-accent'
        default:
          return 'badge-neutral'
      }
    }

    const startAutoRefresh = () => {
      // Refresh every 30 seconds
      refreshInterval.value = setInterval(refreshExecutions, 30000)
    }

    const stopAutoRefresh = () => {
      if (refreshInterval.value) {
        clearInterval(refreshInterval.value)
        refreshInterval.value = null
      }
    }

    // Lifecycle hooks
    onMounted(() => {
      refreshExecutions()
      startAutoRefresh()
    })

    onUnmounted(() => {
      stopAutoRefresh()
    })

    return {
      executions,
      isLoading,
      error,
      searchTerm,
      isCollapsed,
      lastUpdated,
      filteredExecutions,
      refreshExecutions,
      formatExecutionTime,
      formatRelativeTime,
      formatDateTime,
      getTriggerTypeClass
    }
  }
}
</script>

<style scoped>
.transition-all {
  transition: all 0.3s ease;
}
</style>