<template>
        <content-card title="Create process">
          <process-form :process="process" @save="saveProcess"></process-form>
        </content-card>
</template>

<script>
import { processesAPI } from '@/services/automationserver.js'

import { useAlertStore } from '../stores/alertStore'

import ContentCard from '@/components/ContentCard.vue'
import ProcessForm from '@/components/ProcessForm.vue'
import { useNameStore } from '@/stores/nameStore'

const alertStore = useAlertStore()

export default {
  data() {
    return {
      process: {
        name: '',
        description: '',
        target_type: 'python',
        target_source: '',
        git_options: '',
        target_credentials_id: null,
        credentials_id: null,
        workqueue_id: null,
        requirements: 'python'
      }
    }
  },
  components: { ContentCard, ProcessForm },

  methods: {
    async saveProcess(process) {
      try {
        process = await processesAPI.createProcess(process)
        useNameStore().invalidate('processes')

        alertStore.addAlert({
          type: 'success',
          message: "'" + process.name + "' was created"
        })
      } catch (error) {
        alertStore.addAlert({ type: 'error', message: error.message })
        return
      }
      // Redirect to the edit form
      this.$router.push({ name: 'process.edit', params: { id: process.id } })
    }
  }
}
</script>
