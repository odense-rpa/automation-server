<template>
  <tr>
    <td class="text-center">{{ workitem.id }}</td>
    <td>{{ workitem.reference }}</td>
    <td>{{ workitem.message }}</td>
    <td><json-view :jsonData="workitem.data" /></td>
    <td class="text-center">{{ workitem.status }}</td>
    <td class="text-center">{{ $formatDateTime(workitem.created_at) }}</td>
    <td class="text-center">{{ $formatDateTime(workitem.updated_at) }}</td>
    <td>
      <dropdown-button
        :label="'Actions'"
        :items="[
          { text: 'Retry', icon: 'bi bi-arrow-clockwise', action: 'retry' },
          { text: 'Fail', icon: 'bi bi-trash', action: 'fail' },
          { text: 'Complete', icon: 'bi bi-check', action: 'complete' }
        ]"
        @item-clicked="triggerAction"
      />
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

      try {
        workitemsApi.updateWorkItemStatus(this.workitem.id, status);
        alertStore.addAlert({
          type: 'success',
          message: "Item status was updated"
        });
        
        // Emit an event to notify the parent component that the workitem status was updated
        this.$emit('refresh');

      } catch (error) {
        alertStore.addAlert({ type: 'danger', message: error });
      }
    }
  }
};
</script>

<style scoped>
/* Add any required styles here */
</style>