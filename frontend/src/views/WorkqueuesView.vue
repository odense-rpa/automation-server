<template>
  <content-card title="Workqueues">
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
          placeholder="Search workqueues..."
          class="join-item input input-bordered input-sm w-full max-w-xs" 
        />

        <!-- Create New Workqueue Button -->
        <router-link :to="{ name: 'workqueue.create' }" class="join-item btn btn-success btn-sm">+</router-link>
      </div>
    </template>
    <div v-if="filteredWorkqueues.length === 0" class="text-center mb-4">
      <p class="secondary-content font-semibold">No workqueues found matching search.</p>
    </div>

    <workqueues-table :workqueues="filteredWorkqueues" @refresh="refreshWorkqueues" v-if="filteredWorkqueues.length !== 0"  />
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
    await this.refreshWorkqueues()
  },
  methods: {
    async refreshWorkqueues() {
      try {
        this.workqueues = await workqueuesAPI.getWorkqueuesWithInformation(false)

        // Sort workqueues by name
        this.workqueues.sort((a, b) => a.name.localeCompare(b.name))
      } catch (error) {
        alertStore.addAlert({ type: 'error', message: error })
      }
    }
  }
}
</script>

<style scoped>
/* Your styles here */
</style>
