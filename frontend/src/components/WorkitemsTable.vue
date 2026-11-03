<template>
  <content-card title="Workitems">
    <template v-slot:header-right>
      <search-input v-model="searchTerm" placeholder="Search workitems..." />
      <dropdown-button
          class="join-item"
          :items="[
            { text: 'Clear new', action: 'new' },           
            { text: 'Clear failed', action: 'failed'},
            { text: 'Clear completed', action: 'completed'},
            { text: 'Clear all', action: '' }
          ]"
          @item-clicked="clearWorkQueueItems">
          <button class="btn btn-sm flex items-center space-x-2">
            <font-awesome-icon :icon="['fas', 'broom']" />Clear  
          </button>
        </dropdown-button>
    </template>

    <div>
      <p v-if="error" class="text-error text-sm mb-2">{{ error }}</p>
      <!-- Table -->
      <table class="table w-full mb-3 rounded-b-lg">
        <thead>
          <tr>
            <th class="text-center whitespace-nowrap">Id</th>
            <th class="whitespace-nowrap">Reference</th>
            <th class="w-full">Message</th>
            <th class="whitespace-nowrap">Data</th>
            <th class="text-center whitespace-nowrap">Status</th>
            <th class="text-center whitespace-nowrap">Created</th>
            <th class="text-center whitespace-nowrap">Last change</th>
            <th class="whitespace-nowrap">&nbsp;</th>
          </tr>
        </thead>
        
        <!-- Table Body with Workitems -->
        <tbody v-if="workitems.length > 0">
          <work-item-row
            v-for="workitem in workitems"
            :key="workitem.id"
            :workitem="workitem"
            @refresh="refresh"
          />
        </tbody>
        
        <!-- No Workitems Found Message -->
        <tbody v-else>
          <tr>
            <td colspan="8" class="text-center text-base-content/60">{{ emptyText('No workitems found') }}</td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div class="pr-4">
        <page-navigation :currentPage="page" :totalPages="totalPages" @change-page="handlePageChange" />
      </div>
    </div>
  </content-card>
</template>
<script>
import ContentCard from "./ContentCard.vue";
import PageNavigation from "@/components/PageNavigation.vue";
import { workqueuesAPI } from "@/services/automationserver";
import WorkItemRow from "./WorkItemRow.vue";
import DropdownButton from "./DropdownButton.vue";
import SearchInput from "./SearchInput.vue";
import pagedList from "@/mixins/pagedList";

export default {
  name: "WorkitemsTable",
  components: {
    PageNavigation,
    ContentCard,
    WorkItemRow,
    DropdownButton,
    SearchInput
  },
  mixins: [pagedList],
  props: {
    size: {
      type: Number,
      default: 5
    },
    workqueueId: {
      type: Number,
      required: true
    }
  },
  emits: ['workitems-refreshed', 'clearWorkQueueItems'],
  computed: {
    tableKey() {
      return 'workitems-' + this.workqueueId;
    },
    workitems() {
      return this.items;
    }
  },
  methods: {
    fetchPage({ page, size, search }) {
      return workqueuesAPI.getWorkItems(this.workqueueId, page, size, search);
    },
    onPageLoaded(items) {
      this.$emit('workitems-refreshed', items);
    },
    clearWorkQueueItems(action) {
      if (action === '') {
        if (confirm(`Are you sure you want to clear all workitems?`)) {
          this.$emit("clearWorkQueueItems", this.workqueueId, action, 0);
        }
      } else if (confirm(`Are you sure you want to clear ${action} workitems?`)) {
        this.$emit("clearWorkQueueItems", this.workqueueId, action, 0);
      }
    },
  }
};
</script>
