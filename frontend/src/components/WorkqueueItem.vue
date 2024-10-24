<template>
  <tr>
    <td @click="edit()">{{ workqueue.name }}</td>
    <td @click="edit()" class="text-center">
      <i class="bi bi-check" v-if="workqueue.enabled"></i>
    </td>
    <td @click="edit()" class="text-center">{{ workqueue.in_progress }}</td>
    <td @click="edit()" class="text-center">{{ workqueue.new }}</td>
    <td @click="edit()" class="text-center">{{ workqueue.pending_user_action }}</td>
    <td @click="edit()" class="text-center">{{ workqueue.completed }}</td>
    <td @click="edit()" class="text-center">{{ workqueue.failed }}</td>
  </tr>
</template>

<script>

export default {
  props: {
    workqueue: {
      type: Object,
      required: true
    }
  },
  methods: {
    edit() {
      this.$router.push({ name: 'workqueue.edit', params: { id: this.workqueue.id } })
    }
  }
}
</script>
<style scoped>
td {
  cursor: pointer;
}
</style>
