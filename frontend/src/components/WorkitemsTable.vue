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
      <!-- Table -->
      <table class="table w-full mb-3 rounded-b-lg">
        <thead>
          <tr>
            <th class="text-center whitespace-nowrap">Id</th>
            <th class="whitespace-nowrap">Reference</th>
            <th class="whitespace-nowrap">Message</th>
            <th class="w-full">Data</th>
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
            @refresh="fetchWorkItems"
          />
        </tbody>
        
        <!-- No Workitems Found Message -->
        <tbody v-else>
          <tr>
            <td colspan="7" class="text-center text-base-content/60">No workitems found</td>
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
  import { useTableStateStore } from "@/stores/tableStateStore";


  export default {
    name: "WorkitemsTable",
    components: {
      PageNavigation,
      ContentCard,
      WorkItemRow,
      DropdownButton,
      SearchInput
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
        totalPages: 1,
        searchTimeout: null,
        refreshInterval: null,
        dropdownOpen: false
      };
    },
    setup() {
      const tableStateStore = useTableStateStore();
      return { tableStateStore };
    },
    computed: {
      searchTerm: {
        get() {
          return this.tableStateStore.getSearchTerm('workitems-' + this.workqueueId);
        },
        set(value) {
          this.tableStateStore.setSearchTerm('workitems-' + this.workqueueId, value);
        }
      },
      page: {
        get() {
          return this.tableStateStore.getPage('workitems-' + this.workqueueId);
        },
        set(value) {
          this.tableStateStore.setPage('workitems-' + this.workqueueId, value);
        }
      }
    },
    async created() {
      await this.fetchWorkItems();
    },
    watch: {
      searchTerm() {
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(async () => {
          // The store already resets page to 1 when search term changes
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
  
        this.workitems = response.items || [];
        this.totalPages = response.total_pages || 1;
        if (this.page > this.totalPages && this.totalPages > 0) {
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
  </style>