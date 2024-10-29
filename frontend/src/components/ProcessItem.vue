<!-- ProcessItem.vue -->
<template>
  <tr class="hover:bg-base-300 cursor-pointer">
    <td @click="edit()">{{ process.name }}</td>
    <td @click="edit()">{{ process.description }}</td>
    <td @click="edit()">{{ process.target_type }}</td>
    <td @click="edit()">{{ process.requirements }}</td>
  </tr>
</template>

<script>
export default {
  name: 'ProcessItem',
  props: {
    process: {
      type: Object,
      required: true
    }
  },
  methods: {
    edit() {
      this.$router.push({ name: 'process.edit', params: { id: this.process.id } })
    }
  }
}
</script>
<style scoped>
td {
  cursor: pointer;
}
</style>
