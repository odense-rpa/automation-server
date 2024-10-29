<template>
  <tr>
    <td class="flex items-center space-x-2">
      <font-awesome-icon
        :icon="['fas', 'circle']"
        :class="{
          'text-gray-400': status === '',         // Equivalent to 'text-secondary'
          'text-blue-500': status === 'new',      // Equivalent to 'text-info'
          'text-green-500': status === 'in progress' // Equivalent to 'text-success'
        }"
      />
      <span>{{ resource.name }}</span>
    </td>
    
    <td>
      <span v-if="session"><process-label :process-id="session.process_id" /></span>
    </td>
    
    <td>
      <span v-if="session">{{ $formatDateTime(session?.dispatched_at) }}</span>
    </td>
    
    <td>{{ session?.status }}</td>
    
    <td>{{ resource.capabilities }}</td>
  </tr>
</template>
<script>
import { sessionsAPI } from '@/services/automationserver'
import ProcessLabel from '@/components/ProcessLabel.vue'

export default {
  name: 'ClusterItem',
  components: {
    ProcessLabel
  },
  props: {
    resource: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      session: null,
      status: '',
      timer: null
    }
  },
  async mounted() {
    await this.refresh()
    this.timer = setInterval(() => {
      this.refresh()
    }, 5000)
  },
  beforeUnmount() {
    clearInterval(this.timer)
  },
  methods: {
    async refresh() {
      this.session = await sessionsAPI.getByResourceId(this.resource.id)
      if (this.session) {
        this.status = this.session.status
      } else this.status = ''
    }
  }
}
</script>
