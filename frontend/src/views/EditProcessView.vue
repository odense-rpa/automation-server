<template>
  <item-load-error v-if="loadError" :message="loadError" @retry="fetchProcess($route.params.id)" />
  <div class="grid grid-cols-1 lg:grid-cols-[60%,40%] gap-4">
    <!-- Left Column: 70% width -->
    <div>
      <content-card title="Process Information">
        <process-form :process="process" @save="saveProcess" @delete="deleteProcess" v-if="process" />
      </content-card>
    </div>

    <!-- Right Column: 30% width -->
    <div class="space-y-4">
      <trigger-card :process-id="process.id" v-if="process" />
    </div>
  </div>
</template>


<script>
import { processesAPI } from '@/services/automationserver.js'

import { useAlertStore } from '../stores/alertStore'

import ContentCard from '@/components/ContentCard.vue'
import TriggerCard from '@/components/TriggerCard.vue'
import ProcessForm from '@/components/ProcessForm.vue'
import { useNameStore } from '@/stores/nameStore'
import ItemLoadError from '@/components/ItemLoadError.vue'
import itemPage from '@/mixins/itemPage'

const alertStore = useAlertStore()

export default {
  data() {
    return {
      process: null
    }
  },
  components: { ContentCard, ProcessForm, TriggerCard, ItemLoadError },
  mixins: [itemPage],
  methods: {
    async saveProcess(process) {
      try {
        await processesAPI.updateProcess(this.process.id, process)
        useNameStore().invalidate('processes')

        alertStore.addAlert({
          type: 'success',
          message: "'" + this.process.name + "' was saved"
        })
      } catch (error) {
        alertStore.addAlert({ type: 'error', message: error.message })
        return
      }
      // Redirect to the overview
      this.$router.push({ name: 'process' })
    },

    async deleteProcess() {
      const confirmed = confirm(`Are you sure you want to delete '${this.process.name}'?`)
      if (!confirmed) return

      try {
        await processesAPI.deleteProcess(this.process.id)
        useNameStore().invalidate('processes')

        alertStore.addAlert({
          type: 'success',
          message: "'" + this.process.name + "' was deleted"
        })
      } catch (error) {
        alertStore.addAlert({ type: 'error', message: error.message })
        return
      }
      // Redirect to the overview
      this.$router.push({ name: 'process' })
    },

    async fetchProcess(id) {
      this.process = await this.loadItem(() => processesAPI.getProcess(id), {
        what: `Process ${id}`,
        list: { name: 'process', label: 'Processes' }
      })
    }
  },
  async mounted() {
    const processId = this.$route.params.id

    await this.fetchProcess(processId)
  }
}
</script>
