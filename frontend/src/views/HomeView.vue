<template>
  <div>
    <div class="row mb-3">
      <div class="col-sm-12">
        <cluster-monitor></cluster-monitor>
      </div>
    </div>
    <div class="row mb-3">
      <div class="col-md-12">
        <sessions-list :size="5"></sessions-list>
      </div>
    </div>
  </div>
</template>
<script>
import ContentCard from '@/components/ContentCard.vue'
import ClusterMonitor from '@/components/ClusterMonitor.vue'
import SessionsList from '@/components/SessionsList.vue';

export default {
  components: {
    ContentCard,
    ClusterMonitor,
    SessionsList
  }
}
</script>
