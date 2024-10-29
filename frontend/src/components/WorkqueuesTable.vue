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
      </tr>
    </thead>
    <tbody>
      <!-- Use v-for to loop through the workqueues and display the data -->
      <WorkqueueItem v-for="workqueue in workqueues" :key="workqueue.id" :workqueue="workqueue" />
    </tbody>
  </table>
</template>

<script>
import WorkqueueItem from '@/components/WorkqueueItem.vue'

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
  }
}
</script>

<style scoped>
/* Add custom styles for the table if needed */
</style>
