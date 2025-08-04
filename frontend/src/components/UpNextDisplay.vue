<template>
  <content-card title="Up Next">
    <template v-slot:header-right>
      <div class="join">
        <!-- Font Awesome Icon Button (Small) -->
        <button class="join-item btn btn-square btn-sm">
          <font-awesome-icon :icon="['fas', 'search']" />
        </button>

        <!-- Input Field (Small) -->
        <input type="text" v-model="searchTerm" placeholder="Search processes..."
            class="join-item input input-bordered input-sm w-full max-w-xs" />
      </div>
    </template>

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
    <div v-else-if="filteredExecutions.length === 0" class="text-center mb-4">
      <p class="secondary-content font-semibold">
        {{ searchTerm ? 'No executions found matching your search.' : 'No executions scheduled for the next 24 hours.' }}
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
            class="hover:bg-base-300 cursor-pointer"
            @click="navigateToProcess(execution.process_id)"
          >
            <td class="text-left">
              {{ execution.process_name }}
            </td>
            <td class="text-center">
              <span class="badge badge-sm badge-ghost">
                {{ execution.trigger_type }}
              </span>
            </td>
            <td class="text-center">{{ formatExecutionTime(execution.next_execution) }}</td>
            <td class="text-center">{{ formatRelativeTime(execution.next_execution) }}</td>
            <td class="text-left">
              <span v-if="execution.parameters" class="text-xs">{{ execution.parameters }}</span>
              <span v-else class="text-base-content/50">-</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </content-card>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { triggersAPI } from '@/services/automationserver'
import ContentCard from './ContentCard.vue'

export default {
  name: 'UpNextDisplay',
  components: {
    ContentCard
  },
  setup() {
    const router = useRouter()
    
    // Reactive state
    const executions = ref([])
    const isLoading = ref(false)
    const error = ref(null)
    const searchTerm = ref('')
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

    const navigateToProcess = (processId) => {
      router.push({ name: 'process.edit', params: { id: processId } })
    }



    const startAutoRefresh = () => {
      // Refresh every 1 minute
      refreshInterval.value = setInterval(refreshExecutions, 60000)
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
      filteredExecutions,
      refreshExecutions,
      formatExecutionTime,
      formatRelativeTime,
      navigateToProcess
    }
  }
}
</script>

<style scoped>
.transition-all {
  transition: all 0.3s ease;
}
</style>