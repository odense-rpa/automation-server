<!-- ProcessesView.vue -->
<template>
  <content-card title="Processes">
    <template v-slot:header-right>
      <div class="input-group">
        <span class="input-group-text"><i class="bi bi-search" /></span>
        <input
          type="text"
          v-model="searchTerm"
          class="form-control"
          placeholder="Search processes..."
        />
        <router-link :to="{ name: 'process.create' }" class="btn btn-success">+</router-link>
      </div>
    </template>

    <ProcessesTable :processes="filteredProcesses" />
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
      )
    }
  },
  async created() {
    const alertStore = useAlertStore()

    try {
      this.processes = await processesAPI.getProcesses()

      // Sort processes by name
      this.processes.sort((a, b) => a.name.localeCompare(b.name))
    } catch (error) {
      alertStore.addAlert({ type: 'danger', message: error })
    }
  }
}
</script>
<style></style>
