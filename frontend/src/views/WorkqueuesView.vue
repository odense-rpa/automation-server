<template>
  <content-card title="Workqueues">
    <template v-slot:header-right>
      <div class="input-group">
        <span class="input-group-text"><i class="bi bi-search" /></span>
        <input
          type="text"
          v-model="searchTerm"
          class="form-control"
          placeholder="Search workqueues..."
        />
        <router-link :to="{ name: 'workqueue.create' }" class="btn btn-success">+</router-link>
      </div>
    </template>
    <workqueues-table :workqueues="filteredWorkqueues" />
  </content-card>
</template>

<script>
import { workqueuesAPI } from '@/services/automationserver.js'
import { useAlertStore } from '../stores/alertStore'
import ContentCard from '@/components/ContentCard.vue'
import WorkqueuesTable from '@/components/WorkqueuesTable.vue'

const alertStore = useAlertStore()

export default {
  name: 'WorkqueuesView',
  components: {
    ContentCard,
    WorkqueuesTable
  },
  data() {
    return {
      workqueues: [],
      searchTerm: ''
    }
  },
  computed: {
    filteredWorkqueues() {
      return this.workqueues.filter((workqueue) =>
        workqueue.name.toLowerCase().includes(this.searchTerm.toLowerCase())
      )
    }
  },
  // Load all workqueues on created
  async created() {
    try {
      this.workqueues = await workqueuesAPI.getWorkqueuesWithInformation(false)

      // Sort workqueues by name
      this.workqueues.sort((a, b) => a.name.localeCompare(b.name))
    } catch (error) {
      alertStore.addAlert({ type: 'danger', message: error })
    }
  }
}
</script>

<style scoped>
/* Your styles here */
</style>
