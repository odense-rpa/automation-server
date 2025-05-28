<!-- ProcessesView.vue -->
<template>
  <content-card title="Processes">
    <template v-slot:header-right>
      <div class="join">
        <!-- Search Icon Button (Small) -->
        <button class="join-item btn btn-square btn-sm">
          <font-awesome-icon :icon="['fas', 'search']" />
        </button>

        <!-- Input Field (Small) -->
        <input
          type="text"
          v-model="searchTerm"
          placeholder="Search processes..."
          class="join-item input input-bordered input-sm w-full max-w-xs"
        />

        <!-- Create New Process Button -->
        <router-link :to="{ name: 'process.create' }" class="join-item btn btn-success btn-sm">+</router-link>
      </div>
    </template>
    <div v-if="filteredProcesses.length === 0" class="text-center mb-4">
      <p class="secondary-content font-semibold">No processes found matching search.</p>
    </div>

    <ProcessesTable :processes="filteredProcesses" v-if="filteredProcesses.length !== 0" />
  </content-card>
</template>

<script>
import { processesAPI } from '@/services/automationserver.js'
import ProcessesTable from '@/components/ProcessesTable.vue'
import ContentCard from '@/components/ContentCard.vue'

import { useAlertStore } from '../stores/alertStore'

export default {
  name: 'ProcessesView',
  components: {
    ProcessesTable,
    ContentCard
  },
  data() {
    return {
      processes: [],
      searchTerm: ''
    }
  },
  computed: {
    filteredProcesses() {
      return this.processes.filter((process) =>
        process.name.toLowerCase().includes(this.searchTerm.toLowerCase())
      ).sort((a, b) => a.name.localeCompare(b.name));
    }
  },
  async created() {
    const alertStore = useAlertStore()

    try {
      this.processes = await processesAPI.getProcesses()

      // Sort processes by name
      this.processes.sort((a, b) => a.name.localeCompare(b.name))
    } catch (error) {
      alertStore.addAlert({ type: 'error', message: error })
    }
  }
}
</script>
<style></style>
