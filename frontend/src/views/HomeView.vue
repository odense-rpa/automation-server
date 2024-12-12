<template>
  <div>
    <cluster-monitor></cluster-monitor>
    <sessions-list :size="10"></sessions-list>
  </div>
</template>
<script>
import ClusterMonitor from '@/components/ClusterMonitor.vue'
import SessionsList from '@/components/SessionsList.vue';

export default {
  components: {

    ClusterMonitor,
    SessionsList
  }
}
</script>
