<template>
  <tr class="hover:bg-base-300">
    <td class="p-0">
      <router-link :to="{ name: 'workqueue.detail', params: { id: workqueue.id } }"
        class="block px-4 py-3 no-underline text-inherit">{{ workqueue.name }}</router-link>
    </td>
    <td class="text-center p-0">
      <router-link :to="{ name: 'workqueue.detail', params: { id: workqueue.id } }"
        class="block px-4 py-3 no-underline text-inherit">
        <font-awesome-icon :icon="['fas', 'circle-check']" v-if="workqueue.enabled" class="text-success" title="Enabled" />
        <font-awesome-icon :icon="['fas', 'xmark-circle']" v-else class="text-base-content/40" title="Disabled" />
      </router-link>
    </td>
    <td class="text-center p-0">
      <router-link :to="{ name: 'workqueue.detail', params: { id: workqueue.id } }"
        class="block px-4 py-3 no-underline text-inherit">
        <span v-if="workqueue.auto_clean_max_age_days != null" :title="`Completed and failed items older than ${workqueue.auto_clean_max_age_days} days are deleted automatically`">
          {{ workqueue.auto_clean_max_age_days }} days
        </span>
        <span v-else class="text-base-content/40" title="Auto-clean disabled">—</span>
      </router-link>
    </td>
    <td class="text-center p-0">
      <router-link :to="{ name: 'workqueue.detail', params: { id: workqueue.id } }"
        class="block px-4 py-3 no-underline text-inherit">{{ workqueue.in_progress }}</router-link>
    </td>
    <td class="text-center p-0">
      <router-link :to="{ name: 'workqueue.detail', params: { id: workqueue.id } }"
        class="block px-4 py-3 no-underline text-inherit">{{ workqueue.new }}</router-link>
    </td>
    <td class="text-center p-0">
      <router-link :to="{ name: 'workqueue.detail', params: { id: workqueue.id } }"
        class="block px-4 py-3 no-underline text-inherit">{{ workqueue.pending_user_action }}</router-link>
    </td>
    <td class="text-center p-0">
      <router-link :to="{ name: 'workqueue.detail', params: { id: workqueue.id } }"
        class="block px-4 py-3 no-underline text-inherit">{{ workqueue.completed }}</router-link>
    </td>
    <td class="text-center p-0">
      <router-link :to="{ name: 'workqueue.detail', params: { id: workqueue.id } }"
        class="block px-4 py-3 no-underline text-inherit">{{ workqueue.failed }}</router-link>
    </td>
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
        this.$router.push({ name: 'workqueue.detail', params: { id: this.workqueue.id } })
      }
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
