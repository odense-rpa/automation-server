<template>
  <tr :class="{
    'hover:bg-base-200': true,
    'bg-red-400': workitem.status === 'failed',
    'bg-yellow-300': workitem.status === 'pending user action'
  }">
    <td class="text-center">{{ workitem.id }}</td>
    <td class="text-center">
      <font-awesome-icon :icon="['fas', 'triangle-exclamation']" v-if="workitem.status === 'failed'" />
    </td>
    <td>{{ workitem.reference }}</td>
    <td>{{ workitem.message }}</td>
    <td><json-view :jsonData="workitem.data" /></td>
    <td class="text-center">{{ workitem.status }}</td>
    <td class="text-center">{{ $formatDateTime(workitem.created_at) }}</td>
    <td class="text-center">{{ $formatDateTime(workitem.updated_at) }}</td>
    <td class="text-center">
      <dropdown-button :label="'Actions'" :items="[
        { text: 'Retry', icon: 'fas fa-redo', action: 'retry' },
        { text: 'Fail', icon: 'fas fa-trash-alt', action: 'fail' },
        { text: 'Complete', icon: 'fas fa-check', action: 'complete' },
        { text: 'Details', icon: 'fas fa-info', action: 'details' }
      ]" @item-clicked="triggerAction" />
    </td>
  </tr>
</template>

<script>
import JsonView from "./JsonView.vue";
import DropdownButton from "./DropdownButton.vue";
import { workitemsApi } from "@/services/automationserver";
import { useAlertStore } from "@/stores/alertStore";

const alertStore = useAlertStore();

export default {
  name: "WorkItemRow",
  components: {
    JsonView,
    DropdownButton
  },
  props: {
    workitem: {
      type: Object,
      required: true
    }
  },
  methods: {
    triggerAction(action) {
      let status = '';
      if (action === 'retry') status = 'new';
      if (action === 'fail') status = 'failed';
      if (action === 'complete') status = 'completed';

      if (action === 'details') {
        this.$router.push({ name: 'workqueue.item', params: { id: this.workitem.workqueue_id, itemId: this.workitem.id } });
        return;
      }


      try {
        workitemsApi.updateWorkItemStatus(this.workitem.id, status);
        alertStore.addAlert({
          type: 'success',
          message: "Item status was updated"
        });

        // Emit an event to notify the parent component that the workitem status was updated
        this.$emit('refresh');

      } catch (error) {
        alertStore.addAlert({ type: 'error', message: error });
      }
    }
  }
};
</script>

<style scoped>
/* Add any required styles here */
</style>