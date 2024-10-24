<template>
    <content-card title="Workitems">
      <template v-slot:header-right>
        <div class="input-group">
          <span class="input-group-text"><i class="bi bi-search" /></span>
          <input type="text" v-model="searchTerm" class="form-control" placeholder="Search workitems..." />
        </div>
      </template>
      <div>
        <table class="table table-striped table-sm mb-3 rounded-bottom">
          <thead>
            <tr>
              <th class="text-center">Id</th>
              <th>Reference</th>
              <th>Message</th>
              <th>Data</th>
              <th class="text-center">Status</th>
              <th class="text-center">Created</th>
              <th class="text-center">Last change</th>
              <th>&nbsp;</th>
            </tr>
          </thead>
          <tbody v-if="workitems.length > 0">
            <work-item-row
              v-for="workitem in workitems"
              :key="workitem.id"
              :workitem="workitem"
              @refresh="fetchWorkItems"
            />
          </tbody>
          <tbody v-else>
            <tr>
              <td colspan="8" class="text-center">No workitems found</td>
            </tr>
          </tbody>
        </table>
        <div class="pr-4">
          <page-navigation :currentPage="page" :totalPages="totalPages" @change-page="handlePageChange"></page-navigation>
        </div>
      </div>
    </content-card>
  </template>
  
  <script>
  import ContentCard from "./ContentCard.vue";
  import PageNavigation from "@/components/PageNavigation.vue";
  import { workqueuesAPI } from "@/services/automationserver";
  import WorkItemRow from "./WorkItemRow.vue";
  
  export default {
    name: "WorkitemsTable",
    components: {
      PageNavigation,
      ContentCard,
      WorkItemRow
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
        refreshInterval: null
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
      },
      handlePageChange(newPage) {
        this.page = newPage;
        this.fetchWorkItems();
      }
    }
  };
  </script>
  
  <style scoped>
  /* Add any required styles here */
  </style>