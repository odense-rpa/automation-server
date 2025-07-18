<template>
  <div>
    <content-card :title="contentCardTitle" class="mb-3">
      <template v-slot:header-right>
        <button @click="isEditing = true" class="btn btn-primary btn-sm" v-if="!isEditing && !showClearForm">
          <font-awesome-icon :icon="['fas', 'pencil-alt']" /> Edit
        </button>
      </template>
      <div class="card-body">
        <workqueue-info :workqueue="workqueue" v-if="workqueue && !isEditing && !showClearForm" />
        <workqueue-form :workqueue="workqueue" @save="saveWorkqueue" @cancel="cancelEdit" @delete="deleteWorkqueue" 
          v-if="workqueue && isEditing" />          
        <workqueue-clear-form v-if="showClearForm" :workqueue="workqueue" @clearWorkqueue="clearQueue" @back="showClearForm = false" />
      </div>
    </content-card>
    <workitems-table :workqueue-id="workqueue.id" ref="workitemsTable" @clearWorkQueueItems="clearQueue"  @workitems-refreshed="onWorkitemsRefreshed" :size="50" v-if="workqueue" />  
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
      alertStore.addAlert({ type: 'error', message: error })
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
        alertStore.addAlert({ type: 'error', message: error })
      }
      // Redirect to the overview
      this.isEditing = false
    },
    async cancelEdit() {
      this.isEditing = false
    },
    async clearQueue(workqueueid, workitem_status, days_older_than) {
      try {        
        await workqueuesAPI.clearWorkqueue(workqueueid, workitem_status, days_older_than)
        let message = '';
        if (workitem_status == '') {
          message = "All items were cleared from '" + this.workqueue.name + "'";
        } else {
          message = workitem_status + " items were cleared from '" + this.workqueue.name + "'";
        }
        alertStore.addAlert({
          type: 'success',
          message: message
        });
        this.$refs.workitemsTable.fetchWorkItems();
      } catch (error) {
        alertStore.addAlert({ type: 'error', message: error.message });
      }     
    },
    async deleteWorkqueue(workqueue) {
      const confirmed = confirm(`Are you sure you want to delete '${workqueue.name}'?`)
        if (!confirmed) return
        
      try {
        await workqueuesAPI.deleteWorkqueue(workqueue.id)
        alertStore.addAlert({
          type: 'success',
          message: "'" + this.workqueue.name + "' was deleted"
        })
        // Redirect to the overview
        this.$router.push({ name: 'workqueues' })
      } catch (error) {
        alertStore.addAlert({ type: 'error', message: error })
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
