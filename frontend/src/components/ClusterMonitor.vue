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
import polling from '@/mixins/polling'

export default {
  name: 'ClusterMonitor',
  components: {
    ContentCard,
    ClusterItem,
    ClusterSessionItem,
    InstantSchedule
  },
  mixins: [polling],
  data() {
    return {
      resources: [],
      sessions: []
    }
  },

  created() {
    this.poll(() => this.refresh(), 5000)
    this.refresh()
  },
  computed: {
    sortedResources() {
      return this.resources.slice().sort((a, b) => a.name.localeCompare(b.name,"en"));
    }

  },
  methods: {
    async refresh() {
      try {
        // Resources too, so workers that come online show up without a reload
        const [resources, sessions] = await Promise.all([
          resourcesAPI.getResources(),
          sessionsAPI.getNewSessions()
        ])
        this.resources = resources
        // Queued sessions not yet assigned to a resource
        this.sessions = sessions.filter((session) => session.resource_id === null)
      } catch {
        // Keep the last state; the next refresh tries again
      }
    }
  }
}
</script>
