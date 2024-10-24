<template>
  <div>
    <content-card :title="!isEditing ? 'Workqueue' : 'Edit workqueue'">
      <template v-slot:header-right>
        <button @click="isEditing = true" class="btn btn-primary btn-sm" v-if="!isEditing"><i
            class="bi bi-pencil"></i></button>
      </template>
      <div class="card-body">
        <workqueue-info :workqueue="workqueue" v-if="workqueue && !isEditing" />
        <workqueue-form :workqueue="workqueue" @save="saveWorkqueue" @cancel="cancelEdit" v-if="workqueue && isEditing" />
      </div>
    </content-card>
    <hr />
    <workitems-table :workqueue-id="workqueue.id" :size="50" v-if="workqueue" />
  </div>
</template>

<script>
import { useAlertStore } from '../stores/alertStore'
import { workqueuesAPI } from '@/services/automationserver.js'
import ContentCard from '@/components/ContentCard.vue'
import WorkqueueForm from '@/components/WorkqueueForm.vue'
import WorkitemsTable from '@/components/WorkitemsTable.vue'
import WorkqueueInfo from '@/components/WorkqueueInfo.vue'
const alertStore = useAlertStore()

export default {
  name: 'WorkqueueView',
  data: () => ({
    workqueue: null,
    isEditing: false
  }),
  components: {
    ContentCard,
    WorkqueueInfo,
    WorkqueueForm,
    WorkitemsTable
  },
  async created() {
    //Load workqueue from id
    try {
      this.workqueue = await workqueuesAPI.getWorkqueue(this.$route.params.id)
    } catch (error) {
      alertStore.addAlert({ type: 'danger', message: error })
    }
  },
  methods: {
    async saveWorkqueue(workqueue) {
      try {
        this.workqueue = await workqueuesAPI.updateWorkqueue(this.workqueue.id, workqueue)
        alertStore.addAlert({
          type: 'success',
          message: "'" + this.workqueue.name + "' was saved"
        })
      } catch (error) {
        alertStore.addAlert({ type: 'danger', message: error })
      }
      // Redirect to the overview
      this.isEditing = false
    },
    async cancelEdit() {
      this.isEditing = false
    }
  }
}
</script>

<style scoped>
/* Your component styles here */
</style>
