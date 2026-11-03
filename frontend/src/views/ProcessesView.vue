<!-- ProcessesView.vue -->
<template>
  <content-card title="Processes">
    <template v-slot:header-right>
      <search-input v-model="searchTerm" placeholder="Search processes..." />
      
      <router-link :to="{ name: 'process.create' }" class="btn btn-primary btn-sm">+ Create</router-link>      
    </template>
    <div v-if="filteredProcesses.length === 0" class="text-center mb-4">
      <p class="text-base-content/60 font-semibold">No processes found matching search.</p>
    </div>

    <ProcessesTable :processes="filteredProcesses" v-if="filteredProcesses.length !== 0" />
  </content-card>
</template>

<script>
import { processesAPI } from '@/services/automationserver.js'
import ProcessesTable from '@/components/ProcessesTable.vue'
import ContentCard from '@/components/ContentCard.vue'
import SearchInput from '@/components/SearchInput.vue'

import { useAlertStore } from '../stores/alertStore'
import { useTableStateStore } from '../stores/tableStateStore'

export default {
  name: 'ProcessesView',
  components: {
    ProcessesTable,
    ContentCard,
    SearchInput
  },
  setup() {
    const tableStateStore = useTableStateStore()
    return { tableStateStore }
  },
  data() {
    return {
      processes: []
    }
  },
  computed: {
    searchTerm: {
      get() {
        return this.tableStateStore.getSearchTerm('processes')
      },
      set(value) {
        this.tableStateStore.setSearchTerm('processes', value)
      }
    },
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
    } catch (error) {
      alertStore.addAlert({ type: 'error', message: error.message })
    }
  }
}
</script>
