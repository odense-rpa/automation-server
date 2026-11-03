<!-- ProcessItem.vue -->
<template>
  <link-row :to="{ name: 'process.edit', params: { id: process.id } }">
    <td>
      <router-link :to="{ name: 'process.edit', params: { id: process.id } }" class="link link-hover">{{ process.name }}</router-link>
    </td>
    <td>{{ process.description }}</td>
    <td>{{ process.target_type }}</td>
    <td>{{ process.requirements }}</td>
  </link-row>
</template>

<script>
import LinkRow from '@/components/LinkRow.vue'

export default {
  name: 'ProcessItem',
  components: { LinkRow },
  props: {
    process: {
      type: Object,
      required: true
    }
  }
}
</script>
