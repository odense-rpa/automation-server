<template>
  <div>
    <content-card title="Workqueue" class="mb-3">
      <template v-slot:header-right>
        <button @click="$router.push({ name: 'workqueue.edit', params: { id: workqueue.id } })" class="btn btn-primary btn-sm" v-if="!showClearForm && workqueue">
          <font-awesome-icon :icon="['fas', 'pencil-alt']" /> Edit
        </button>
      </template>
      <div class="card-body">
        <workqueue-info :workqueue="workqueue" :information="information" v-if="workqueue && !showClearForm" />
        <workqueue-clear-form v-if="showClearForm" :workqueue="workqueue" @clearWorkqueue="clearQueue" @back="showClearForm = false" />
      </div>
    </content-card>
    <workitems-table :workqueue-id="workqueue.id" ref="workitemsTable" @clearWorkQueueItems="clearQueue" @workitems-refreshed="onWorkitemsRefreshed" :size="50" v-if="workqueue" />
  </div>
</template>

<script>
import { useAlertStore } from '../stores/alertStore'
import { workqueuesAPI } from '@/services/automationserver.js'
import ContentCard from '@/components/ContentCard.vue'
import WorkitemsTable from '@/components/WorkitemsTable.vue'
import WorkqueueInfo from '@/components/WorkqueueInfo.vue'
import WorkqueueClearForm from '@/components/WorkqueueClearForm.vue'
const alertStore = useAlertStore()

export default {
  name: 'WorkqueueView',
  data: () => ({
    workqueue: null,
    information: null,
    showClearForm: false
  }),
  components: {
    ContentCard,
    WorkqueueInfo,
    WorkitemsTable,
    WorkqueueClearForm
  },
  async created() {
    try {
      this.workqueue = await workqueuesAPI.getWorkqueue(this.$route.params.id)
      await this.fetchInformation()
    } catch (error) {
      alertStore.addAlert({ type: 'error', message: error })
    }
  },
  methods: {
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
    async fetchInformation() {
      try {
        this.information = await workqueuesAPI.getWorkqueueInformation(this.workqueue.id)
      } catch (error) {
        alertStore.addAlert({ type: 'error', message: error.message })
      }
    },
    onWorkitemsRefreshed() {
      if (this.workqueue) this.fetchInformation()
    }
  }
}
</script>

<style scoped>
</style>
