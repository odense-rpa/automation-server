<template>
  <div>
    <item-load-error v-if="loadError" :message="loadError" @retry="fetchWorkqueue" />
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
import ItemLoadError from '@/components/ItemLoadError.vue'
import itemPage from '@/mixins/itemPage'
const alertStore = useAlertStore()

export default {
  name: 'EditWorkqueueView',
  data: () => ({
    workqueue: null
  }),
  components: {
    ContentCard,
    WorkqueueForm,
    ItemLoadError
  },
  mixins: [itemPage],
  created() {
    this.fetchWorkqueue()
  },
  methods: {
    async fetchWorkqueue() {
      this.workqueue = await this.loadItem(() => workqueuesAPI.getWorkqueue(this.$route.params.id), {
        what: `Workqueue ${this.$route.params.id}`,
        list: { name: 'workqueues', label: 'Workqueues' }
      })
    },
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
