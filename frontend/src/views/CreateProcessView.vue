<template>
        <content-card title="Create process">
          <div class="card-body">
            <process-form :process="process" @save="saveProcess"></process-form>
          </div>
        </content-card>
</template>

<script>
import { processesAPI } from '@/services/automationserver.js'

import { useAlertStore } from '../stores/alertStore'

import ContentCard from '@/components/ContentCard.vue'
import ProcessForm from '@/components/ProcessForm.vue'

const alertStore = useAlertStore()

export default {
  data() {
    return {
      process: {
        name: '',
        description: '',
        target_type: 'python',
        target_source: '',
        target_credentials_id: 0,
        credentials_id: 0,
        workqueue_id: 0
      }
    }
  },
  components: { ContentCard, ProcessForm },

  methods: {
    async saveProcess(process) {
      try {
        await processesAPI.createProcess(process)

        alertStore.addAlert({
          type: 'success',
          message: "'" + process.name + "' was created"
        })
      } catch (error) {
        console.log(error)
        alertStore.addAlert({ type: 'error', message: error })
      }
      // Redirect to the overview
      this.$router.push({ name: 'process' })
    }
  }
}
</script>

<style scoped>
/* Add custom styles here */
</style>
