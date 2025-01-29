<template>
  <tr class="hover:bg-base-300 cursor-pointer">
    <td @click="edit()">{{ workqueue.name }}</td>
    <td @click="edit()" class="text-center">
      <font-awesome-icon :icon="['fas', 'check']" v-if="workqueue.enabled" />
    </td>
    <td @click="edit()" class="text-center">{{ workqueue.in_progress }}</td>
    <td @click="edit()" class="text-center">{{ workqueue.new }}</td>
    <td @click="edit()" class="text-center">{{ workqueue.pending_user_action }}</td>
    <td @click="edit()" class="text-center">{{ workqueue.completed }}</td>
    <td @click="edit()" class="text-center">{{ workqueue.failed }}</td>
    <td class="text-center">  
      <dropdown-button
        :items="[
          { text: 'Details', icon: ['fas', 'info'], action: 'Details' },
          { text: 'Clear new', icon: ['fas', 'broom'], action: 'new' },
          { text: 'Clear failed', icon: ['fas', 'broom'], action: 'failed' },
          { text: 'Clear completed', icon: ['fas', 'broom'], action: 'completed' },
          { text: 'Clear all', icon: ['fas', 'broom'], action: '' }
        ]" 
        @item-clicked="handleItemClick"
      />
    </td>
  </tr>
</template>

<script>
 import DropdownButton from "./DropdownButton.vue";

export default {
  name: 'WorkqueueItem',
  components: {
    DropdownButton
  },
  props: {
    workqueue: {
      type: Object,
      required: true
    }
  },
  methods: {
    handleItemClick(action) {
      if (action !== 'Details') {
        this.clearWorkQueueItems(action);
      }else{
        this.edit();
      }
    },
    edit() {
      this.$router.push({ name: 'workqueue.edit', params: { id: this.workqueue.id } })
    },
    clearWorkQueueItems(action) {
      if(action === '') 
        {
          if (confirm(`Are you sure you want to clear all workitems?`)) {
            this.$emit("clearWorkQueueItems", this.workqueue, action, 0);
          }
        } 
        else if (confirm(`Are you sure you want to clear ${action} workitems?`)) 
        {
          this.$emit("clearWorkQueueItems", this.workqueue, action, 0);
        }
    }
  }
}
</script>
<style scoped>
td {
  cursor: pointer;
}
</style>
