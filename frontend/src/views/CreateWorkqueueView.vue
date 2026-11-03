<template>
  <content-card title="Create workqueue" class="mb-4">
    <workqueue-form :workqueue="workqueue" @save="saveWorkqueue" @cancel="cancel" />
  </content-card>
</template>

<script>
import { useAlertStore } from '../stores/alertStore'
import { workqueuesAPI } from '@/services/automationserver.js'
import ContentCard from '@/components/ContentCard.vue'
import WorkqueueForm from '@/components/WorkqueueForm.vue'
import { useNameStore } from '@/stores/nameStore'

const alertStore = useAlertStore()

export default {
  name: 'CreateWorkqueueView',
  data: () => ({
    workqueue: null
  }),
  components: {
    ContentCard,
    WorkqueueForm
  },
  async created() {
    this.workqueue = {
      id: null,
      name: '',
      description: '',
      enabled: true
    }
  },
  methods: {
    async saveWorkqueue(workqueue) {
      try {
        await workqueuesAPI.createWorkqueue(workqueue)
        useNameStore().invalidate('workqueues')
        alertStore.addAlert({
          type: 'success',
          message: "'" + workqueue.name + "' was created"
        })
      } catch (error) {
        alertStore.addAlert({ type: 'error', message: error.message })
        return
      }
      // Redirect to the overview
      this.$router.push({ name: 'workqueues' })
    },
    cancel() {
      this.$router.push({ name: 'workqueues' })
    }
  }
}
</script>
