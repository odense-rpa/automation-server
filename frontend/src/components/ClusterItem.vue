<template>
  <tr>
    <td class="flex items-center space-x-2">
      <font-awesome-icon
        :icon="['fas', 'circle']"
        :class="{
          'text-base-content/40': status === '',
          'text-info': status === 'new',
          'text-success': status === 'in progress',
        }"
        :title="status || 'idle'"
      />
      <span>{{ resource.name }}</span>
    </td>
    
    <td>
      <span v-if="session"><process-label :process-id="session.process_id" /></span>
    </td>
    
    <td>
      <span v-if="session">{{ $formatDateTime(session?.dispatched_at) }}</span>
    </td>
    
    <td>
      <status-badge v-if="session" kind="session" :status="session.status" />
      <span v-else class="text-base-content/60">Idle</span>
    </td>
    
    <td>{{ resource.capabilities }}</td>
  </tr>
</template>
<script>
import { sessionsAPI } from '@/services/automationserver'
import ProcessLabel from '@/components/ProcessLabel.vue'
import polling from '@/mixins/polling'
import StatusBadge from '@/components/StatusBadge.vue'

export default {
  name: 'ClusterItem',
  components: {
    ProcessLabel, StatusBadge
  },
  mixins: [polling],
  props: {
    resource: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      session: null,
      status: ''
    }
  },
  created() {
    this.poll(() => this.refresh(), 5000)
    this.refresh()
  },
  methods: {
    async refresh() {
      try {
        this.session = await sessionsAPI.getByResourceId(this.resource.id)
        this.status = this.session ? this.session.status : ''
      } catch {
        // Keep the last state; the next refresh tries again
      }
    }
  }
}
</script>
