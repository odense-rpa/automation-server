<template>
  <tr v-if="session">
    <td>&nbsp;</td>
    <td><process-label :process-id="session.process_id" /></td>
    <td>&nbsp;</td>
    <td>&nbsp;</td>
    <td>{{ session.requirements }}</td>
  </tr>
</template>
<script>
import ProcessLabel from '@/components/ProcessLabel.vue'

export default {
  name: 'ClusterSessionItem',
  components: {
    ProcessLabel
  },
  props: {
    session: {
      type: Object,
      required: true
    }
  }
}
</script>
