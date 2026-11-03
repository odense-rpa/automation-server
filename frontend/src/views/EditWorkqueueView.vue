<template>
  <div>
    <content-card title="Edit workqueue" class="mb-3">
      <workqueue-form :workqueue="workqueue" @save="saveWorkqueue" @cancel="cancelEdit" @delete="deleteWorkqueue"
        v-if="workqueue" />
    </content-card>
  </div>
</template>

<script>
import { useAlertStore } from '../stores/alertStore'
import { workqueuesAPI } from '@/services/automationserver.js'
import ContentCard from '@/components/ContentCard.vue'
import WorkqueueForm from '@/components/WorkqueueForm.vue'
import { useNameStore } from '@/stores/nameStore'
const alertStore = useAlertStore()

export default {
  name: 'EditWorkqueueView',
  data: () => ({
    workqueue: null
  }),
  components: {
    ContentCard,
    WorkqueueForm
  },
  async created() {
    try {
      this.workqueue = await workqueuesAPI.getWorkqueue(this.$route.params.id)
    } catch (error) {
      alertStore.addAlert({ type: 'error', message: error.message })
    }
  },
  methods: {
    async saveWorkqueue(workqueue) {
      try {
        this.workqueue = await workqueuesAPI.updateWorkqueue(this.workqueue.id, workqueue)
        useNameStore().invalidate('workqueues')
        alertStore.addAlert({
          type: 'success',
          message: "'" + this.workqueue.name + "' was saved"
        })
      } catch (error) {
        alertStore.addAlert({ type: 'error', message: error.message })
        return
      }
      this.$router.push({ name: 'workqueue.detail', params: { id: this.workqueue.id } })
    },
    async cancelEdit() {
      this.$router.push({ name: 'workqueue.detail', params: { id: this.workqueue.id } })
    },
    async deleteWorkqueue(workqueue) {
      const confirmed = confirm(`Are you sure you want to delete '${workqueue.name}'?`)
      if (!confirmed) return

      try {
        await workqueuesAPI.deleteWorkqueue(workqueue.id)
        useNameStore().invalidate('workqueues')
        alertStore.addAlert({
          type: 'success',
          message: "'" + this.workqueue.name + "' was deleted"
        })
        this.$router.push({ name: 'workqueues' })
      } catch (error) {
        alertStore.addAlert({ type: 'error', message: error.message })
      }
    }
  }
}
</script>
