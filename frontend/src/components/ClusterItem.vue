<template>
  <tr>
    <td>
      <i
        class="bi bi-circle-fill"
        :class="{
          'text-secondary': status === '',
          'text-info': status === 'new',
          'text-success': status === 'in progress'
        }"
      ></i>
      {{ resource.name }}
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
