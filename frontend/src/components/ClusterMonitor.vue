<template>
  <content-card title="Cluster" class="mb-4">
    <template v-slot:header-right>
      <instant-schedule></instant-schedule>
    </template>
    <table class="table w-full mb-3">
      <thead>
        <tr>
          <th>Resource</th>
          <th>Process</th>
          <th>Dispatched</th>
          <th>Status</th>
          <th>Supports</th>
        </tr>
      </thead>
      <tbody>
        <cluster-item
          v-for="resource in sortedResources"
          :key="resource.id"
          :resource="resource"
        ></cluster-item>
        <cluster-session-item
          v-for="session in sessions"
          :key="session.id"
          :session="session"
        ></cluster-session-item>
      </tbody>
    </table>
  </content-card>
</template>
<script>
import ContentCard from '@/components/ContentCard.vue'
import ClusterItem from '@/components/ClusterItem.vue'
import ClusterSessionItem from './ClusterSessionItem.vue'
import InstantSchedule from './InstantSchedule.vue'
import { resourcesAPI, sessionsAPI } from '@/services/automationserver'

export default {
  name: 'ClusterMonitor',
  components: {
    ContentCard,
    ClusterItem,
    ClusterSessionItem,
    InstantSchedule
  },
  data() {
    return {
      resources: [],
      sessions: [],
      timer: null
    }
  },

  async mounted() {
    this.resources = await resourcesAPI.getResources()
    this.timer = setInterval(this.updateSessions, 5000)
    this.sessions = await sessionsAPI.getNewSessions()
  },
  beforeUnmount() {
    clearInterval(this.timer)
  },
  computed: {
    sortedResources() {
      return this.resources.slice().sort((a, b) => a.name.localeCompare(b.name,"en"));
    }

  },
  methods: {
    async updateSessions() {
      var sessions = await sessionsAPI.getNewSessions()
      this.sessions = sessions.filter((session) => session.resource_id === null)
    }
  }
}
</script>
