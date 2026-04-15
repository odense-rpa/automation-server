<template>
  <tr :class="{
    'hover:bg-base-200': true,
    'bg-error/30': workitem.status === 'failed',
    'bg-warning/30': workitem.status === 'pending user action'
  }">
    <td class="text-center p-0">
      <router-link :to="{ name: 'workqueue.item', params: { id: workitem.workqueue_id, itemId: workitem.id } }"
        class="block px-4 py-3 no-underline text-inherit">{{ workitem.id }}</router-link>
    </td>
    <td class="p-0 max-w-xs">
      <router-link :to="{ name: 'workqueue.item', params: { id: workitem.workqueue_id, itemId: workitem.id } }"
        class="block px-4 py-3 no-underline text-inherit truncate" :title="workitem.reference">{{ workitem.reference }}</router-link>
    </td>
    <td class="p-0 max-w-xs">
      <router-link :to="{ name: 'workqueue.item', params: { id: workitem.workqueue_id, itemId: workitem.id } }"
        class="block px-4 py-3 no-underline text-inherit truncate" :title="workitem.message">{{ workitem.message }}</router-link>
    </td>
    <td><json-view :jsonData="workitem.data" /></td>
    <td class="text-center p-0">
      <router-link :to="{ name: 'workqueue.item', params: { id: workitem.workqueue_id, itemId: workitem.id } }"
        class="block px-4 py-3 no-underline text-inherit">
        <font-awesome-icon v-if="workitem.status === 'new'" :icon="['fas', 'circle']" class="text-info" :title="workitem.status" />
        <font-awesome-icon v-else-if="workitem.status === 'in progress'" :icon="['fas', 'spinner']" spin class="text-warning" :title="workitem.status" />
        <font-awesome-icon v-else-if="workitem.status === 'completed'" :icon="['fas', 'circle-check']" class="text-success" :title="workitem.status" />
        <font-awesome-icon v-else-if="workitem.status === 'failed'" :icon="['fas', 'triangle-exclamation']" class="text-error" :title="workitem.status" />
        <font-awesome-icon v-else-if="workitem.status === 'pending user action'" :icon="['fas', 'lock']" class="text-warning" :title="workitem.status" />
        <font-awesome-icon v-if="workitem.locked" :icon="['fas', 'lock']" class="text-base-content/40 ml-1" title="Locked" />
      </router-link>
    </td>
    <td class="text-center p-0">
      <router-link :to="{ name: 'workqueue.item', params: { id: workitem.workqueue_id, itemId: workitem.id } }"
        class="block px-4 py-3 no-underline text-inherit">{{ $formatDateTime(workitem.created_at) }}</router-link>
    </td>
    <td class="text-center p-0">
      <router-link :to="{ name: 'workqueue.item', params: { id: workitem.workqueue_id, itemId: workitem.id } }"
        class="block px-4 py-3 no-underline text-inherit">{{ $formatDateTime(workitem.updated_at) }}</router-link>
    </td>
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
