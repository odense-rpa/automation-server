<template>
  <link-row :to="{ name: 'workqueue.item', params: { id: workitem.workqueue_id, itemId: workitem.id } }" :class="{
    'bg-error/30': workitem.status === 'failed',
    'bg-warning/30': workitem.status === 'pending user action'
  }">
    <td class="text-center">
      <router-link :to="{ name: 'workqueue.item', params: { id: workitem.workqueue_id, itemId: workitem.id } }" class="link link-hover">{{ workitem.id }}</router-link>
    </td>
    <td class="max-w-xs group/ref relative">
      <div class="truncate pr-6" :title="workitem.reference">{{ workitem.reference }}</div>
      <copy-button :text="workitem.reference || ''" label="Copy reference"
        class="absolute right-2 inset-y-0 my-auto opacity-0 group-hover/ref:opacity-100 focus:opacity-100 transition-opacity" />
    </td>
    <!-- max-w-0 lets the cell take the remaining width (w-full on its header) and still truncate -->
    <td class="max-w-0"><div class="truncate" :title="workitem.message">{{ workitem.message }}</div></td>
    <td class="whitespace-nowrap"><json-preview :data="workitem.data" :title="`Work item ${workitem.id}: ${workitem.reference}`" /></td>
    <td class="text-center">
      <status-badge kind="workitem" :status="workitem.status" compact />
      <font-awesome-icon v-if="workitem.locked" :icon="['fas', 'lock']" class="text-base-content/40 ml-1" title="Locked" />
    </td>
    <td class="text-center"><div class="xl:whitespace-nowrap">{{ $formatDateTime(workitem.created_at) }}</div></td>
    <td class="text-center"><div class="xl:whitespace-nowrap">{{ $formatDateTime(workitem.updated_at) }}</div></td>
    <td class="text-center">
      <dropdown-button :label="'Actions'" :items="[
        { text: 'Retry', icon: ['fas', 'redo'], action: 'retry' },
        { text: 'Fail', icon: ['fas', 'trash-alt'], action: 'fail' },
        { text: 'Complete', icon: ['fas', 'check'], action: 'complete' },
        { text: 'Details', icon: ['fas', 'info'], action: 'details' }
      ]" @item-clicked="triggerAction" />
    </td>
  </link-row>
</template>

<script>
import JsonPreview from "./JsonPreview.vue";
import DropdownButton from "./DropdownButton.vue";
import { workitemsApi } from "@/services/automationserver";
import { useAlertStore } from "@/stores/alertStore";
import StatusBadge from '@/components/StatusBadge.vue'
import CopyButton from '@/components/CopyButton.vue'
import LinkRow from '@/components/LinkRow.vue'

const alertStore = useAlertStore();

export default {
  name: "WorkItemRow",
  components: {
    JsonPreview,
    DropdownButton, StatusBadge, CopyButton, LinkRow
  },
  props: {
    workitem: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
    };
  },
  methods: {
    async triggerAction(action) {
      let status = '';
      if (action === 'retry') status = 'new';
      if (action === 'fail') status = 'failed';
      if (action === 'complete') status = 'completed';

      if (action === 'details') {
        this.$router.push({ name: 'workqueue.item', params: { id: this.workitem.workqueue_id, itemId: this.workitem.id } });
        return;
      }


      try {
        await workitemsApi.updateWorkItemStatus(this.workitem.id, status);
        alertStore.addAlert({
          type: 'success',
          message: "Item status was updated"
        });

        // Emit an event to notify the parent component that the workitem status was updated
        this.$emit('refresh');

      } catch (error) {
        alertStore.addAlert({ type: 'error', message: error.message });
      }
    }
  }
};
</script>
