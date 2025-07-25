<template>
  <content-card title="Workitems">
    <template v-slot:header-right>
      <!-- Search Input Group -->
      <div class="join input-dropdown-container">
        <button class="join-item btn btn-square btn-sm">
          <font-awesome-icon :icon="['fas', 'search']" />
        </button>
        <input
          type="text"
          v-model="searchTerm"
          placeholder="Search workitems..."
          class="join-item input input-bordered input-sm w-full max-w-xs"
        />
      </div>
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
      <!-- Table -->
      <table class="table w-full table-auto mb-3 rounded-b-lg">
        <thead>
          <tr>
            <th class="text-center">Id</th>
            <th>&nbsp;</th>
            <th>Reference</th>
            <th>Message</th>
            <th>Data</th>
            <th class="text-center">Status</th>
            <th class="text-center">Created</th>
            <th class="text-center">Last change</th>
            <th>&nbsp;</th>
          </tr>
        </thead>
        
        <!-- Table Body with Workitems -->
        <tbody v-if="workitems.length > 0">
          <work-item-row
            v-for="workitem in workitems"
            :key="workitem.id"
            :workitem="workitem"
            @refresh="fetchWorkItems"
          />
        </tbody>
        
        <!-- No Workitems Found Message -->
        <tbody v-else>
          <tr>
            <td colspan="8" class="text-center text-gray-500">No workitems found</td>
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

  
  export default {
    name: "WorkitemsTable",
    components: {
      PageNavigation,
      ContentCard,
      WorkItemRow,
      DropdownButton
    },
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
    data() {
      return {
        workitems: [],
        page: 1,
        totalPages: 1,
        searchTerm: "",
        searchTimeout: null,
        refreshInterval: null,
        dropdownOpen: false   
      };
    },
    async created() {
      await this.fetchWorkItems();
    },
    watch: {
      searchTerm() {
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(async () => {
          this.page = 1; // Reset to first page when search term changes
          await this.fetchWorkItems();
        }, 300); // 300ms delay
      }
    },
    methods: {
      async fetchWorkItems() {
        const response = await workqueuesAPI.getWorkItems(
          this.workqueueId,
          this.page,
          this.size,
          this.searchTerm
        );
  
        if (response.total_pages === 0) {
          this.workitems = [];
          return;
        }
  
        this.workitems = response.items;
        this.totalPages = response.total_pages;
        if (this.page > this.totalPages) {
          this.page = this.totalPages;
          this.fetchWorkItems();
        }

        this.$emit('workitems-refreshed', this.workitems);
      },
      handlePageChange(newPage) {
        this.page = newPage;
        this.fetchWorkItems();
      },
      clearWorkQueueItems(action) {  
        if(action === '') {
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
  
  <style scoped>
  .input-dropdown-container {
    display: flex;
    align-items: center;
  }
  </style>