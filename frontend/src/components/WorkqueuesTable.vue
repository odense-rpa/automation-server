<template>
  <table class="table w-full mb-3">
    <thead>
      <tr>
        <th>Name</th>
        <th class="text-center">Enabled</th>
        <th class="text-center">In progress</th>
        <th class="text-center">New</th>
        <th class="text-center">Pending user</th>
        <th class="text-center">Completed</th>
        <th class="text-center">Failed</th>
        <th class="text-center"></th>
      </tr>
    </thead>
    <tbody>
      <!-- Use v-for to loop through the workqueues and display the data -->
      <WorkqueueItem v-for="workqueue in workqueues" @clearWorkQueueItems="clearQueue" :key="workqueue.id" :workqueue="workqueue" />
    </tbody>
  </table>
</template>

<script>
import WorkqueueItem from '@/components/WorkqueueItem.vue'
import { useAlertStore } from '../stores/alertStore'
import { workqueuesAPI } from '@/services/automationserver.js'
const alertStore = useAlertStore()

export default {
  name: 'WorkqueuesTable',
  components: {
    WorkqueueItem   
  },
  props: {
    workqueues: {
      type: Array,
      required: true
    }
  },
  methods: {
    async clearQueue(workqueue, workitem_status, days_older_than) {
      console.log(workqueue, workitem_status, days_older_than);
      try {        
        await workqueuesAPI.clearWorkqueue(workqueue.id, workitem_status, days_older_than)
        let message = '';
        if (workitem_status == '') {
          message = "All items were cleared from '" + workqueue.name + "'";
        } else {
          message = workitem_status + " items were cleared from '" + workqueue.name + "'";
        }
        alertStore.addAlert({
          type: 'success',
          message: message
        });
        this.$emit('refresh', workqueue);
      } catch (error) {
        alertStore.addAlert({ type: 'error', message: error.message });
      }     
    },
  }
}
</script>

<style scoped>
/* Add custom styles for the table if needed */
</style>
