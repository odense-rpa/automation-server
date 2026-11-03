<template>
  <content-card title="Workqueues">
    <template v-slot:header-right>
      <search-input v-model="searchTerm" placeholder="Search workqueues..." />
      <router-link :to="{ name: 'workqueue.create' }" class="btn btn-primary btn-sm">+ Create</router-link>
    </template>
    <div v-if="loading" class="text-center mb-4">
      <p class="text-base-content/60 font-semibold">Loading workqueues...</p>
    </div>
    <div v-else-if="filteredWorkqueues.length === 0" class="text-center mb-4">
      <p class="text-base-content/60 font-semibold">No workqueues found matching search.</p>
    </div>

    <workqueues-table :workqueues="filteredWorkqueues" @refresh="refreshWorkqueues" v-if="filteredWorkqueues.length !== 0"  />
  </content-card>
</template>

<script>
import { workqueuesAPI } from '@/services/automationserver.js'
import { useAlertStore } from '../stores/alertStore'
import { useTableStateStore } from '../stores/tableStateStore'
import ContentCard from '@/components/ContentCard.vue'
import WorkqueuesTable from '@/components/WorkqueuesTable.vue'
import SearchInput from '@/components/SearchInput.vue'

const alertStore = useAlertStore()

export default {
  name: 'WorkqueuesView',
  components: {
    ContentCard,
    WorkqueuesTable,
    SearchInput
  },
  setup() {
    const tableStateStore = useTableStateStore()
    return { tableStateStore }
  },
  data() {
    return {
      workqueues: [],
      loading: true,
    }
  },
  computed: {
    searchTerm: {
      get() {
        return this.tableStateStore.getSearchTerm('workqueues')
      },
      set(value) {
        this.tableStateStore.setSearchTerm('workqueues', value)
      }
    },
    filteredWorkqueues() {
      return this.workqueues.filter((workqueue) =>
        workqueue.name.toLowerCase().includes(this.searchTerm.toLowerCase())
      ).sort((a, b) => a.name.localeCompare(b.name));
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
      } catch (error) {
        alertStore.addAlert({ type: 'error', message: error.message })
      }
      finally {
        this.loading = false;
      }
    }
  }
}
</script>
