<template>
  <div>
    <cluster-monitor></cluster-monitor>
    <div class="mb-4">
      <up-next-display></up-next-display>
    </div>
    <sessions-list :size="10"></sessions-list>
  </div>
</template>
<script>
import ClusterMonitor from '@/components/ClusterMonitor.vue'
import SessionsList from '@/components/SessionsList.vue'
import UpNextDisplay from '@/components/UpNextDisplay.vue'

export default {
  components: {
    ClusterMonitor,
    SessionsList,
    UpNextDisplay
  }
}
</script>
