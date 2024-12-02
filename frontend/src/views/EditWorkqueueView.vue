<template>
  <div>
    <content-card :title="contentCardTitle" class="mb-3">
      <template v-slot:header-right>
        <button @click="isEditing = true" class="btn btn-primary btn-sm" v-if="!isEditing && !showClearForm">
          <font-awesome-icon :icon="['fas', 'pencil-alt']" />
        </button>
        <button @click="showClearForm = true" class="btn btn-sm" v-if="!isEditing && !showClearForm">
          Clear Workqueue items
        </button>
      </template>
      <div class="card-body">
        <workqueue-info :workqueue="workqueue" v-if="workqueue && !isEditing && !showClearForm" />
        <workqueue-form :workqueue="workqueue" @save="saveWorkqueue" @cancel="cancelEdit"
          v-if="workqueue && isEditing" />
        <workqueue-clear-form v-if="showClearForm" :workqueue="workqueue" @clearWorkqueue="clearQueue" @back="showClearForm = false" />
      </div>
    </content-card>
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
import WorkqueueClearForm from '@/components/WorkqueueClearForm.vue'
const alertStore = useAlertStore()

export default {
  name: 'WorkqueueView',
  data: () => ({
    workqueue: null,
    isEditing: false,
    showClearForm: false
  }),
  components: {
    ContentCard,
    WorkqueueInfo,
    WorkqueueForm,
    WorkitemsTable,
    WorkqueueClearForm
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
    },
    async clearQueue(workqueueid, workitem_status, days_older_than) {
      try {
        console.log(workqueueid, workitem_status, days_older_than);  
        await workqueuesAPI.clearWorkqueue(workqueueid, workitem_status, days_older_than)
        alertStore.addAlert({
          type: 'success',
          message: "'" + this.workqueue.name + "' was cleared"
        })
      } catch (error) {
        alertStore.addAlert({ type: 'danger', message: error })
      }     
    },
  },
  computed: {
    // Compute the title based on either isEditing or showClearForm being true
    contentCardTitle() {
      if (this.isEditing) {
        return 'Edit workqueue'; // Title when editing
      } else if (this.showClearForm) {
        return 'Clear Workqueue'; // Title when clear form is shown
      }
      return 'Workqueue'; // Default title
    }
  }
}
</script>

<style scoped>
/* Your component styles here */
</style>
