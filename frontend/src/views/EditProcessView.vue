<template>
  <div class="grid grid-cols-1 lg:grid-cols-[60%,40%] gap-4">
    <!-- Left Column: 70% width -->
    <div>
      <content-card title="Process Information">
        <div class="p-4">
          <process-form :process="process" @save="saveProcess" @delete="deleteProcess" v-if="process" />
        </div>
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

const alertStore = useAlertStore()

export default {
  data() {
    return {
      process: null
    }
  },
  components: { ContentCard, ProcessForm, TriggerCard },
  methods: {
    async saveProcess(process) {
      try {
        await processesAPI.updateProcess(this.process.id, process)

        alertStore.addAlert({
          type: 'success',
          message: "'" + this.process.name + "' was saved"
        })
      } catch (error) {
        console.log(error)
        alertStore.addAlert({ type: 'error', message: error })
      }
      // Redirect to the overview
      this.$router.push({ name: 'process' })
    },

    async deleteProcess() {
      try {
        await processesAPI.deleteProcess(this.process.id)

        alertStore.addAlert({
          type: 'success',
          message: "'" + this.process.name + "' was deleted"
        })
      } catch (error) {
        alertStore.addAlert({ type: 'error', message: error })
      }
      // Redirect to the overview
      this.$router.push({ name: 'process' })
    },

    async fetchProcess(id) {
      try {
        this.process = await processesAPI.getProcess(id)
      } catch (error) {
        alertStore.addAlert({ type: 'error', message: 'Error fetching process:', error })
      }
    }
  },
  async mounted() {
    const processId = this.$route.params.id

    await this.fetchProcess(processId)
  }
}
</script>

<style scoped>
/* Add custom styles here */
</style>
