<template>
  <div class="container">
    <div class="row">
      <div class="col-sm-7">
        <content-card title="Process information">
          <div class="card-body">
            <process-form :process="process" @save="saveProcess"></process-form>
          </div>
        </content-card>
      </div>
      <div class="col-sm-5">
        <trigger-card :process-id="process.id" v-if="process"></trigger-card>

        <content-card title="Recent sessions"></content-card>
      </div>
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
        alertStore.addAlert({ type: 'danger', message: error })
      }
      // Redirect to the overview
      this.$router.push({ name: 'process' })
    },

    async fetchProcess(id) {
      try {
        this.process = await processesAPI.getProcess(id)
      } catch (error) {
        alertStore.addAlert({ type: 'danger', message: 'Error fetching process:', error })
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
