<template>
  <div class="flex justify-end me-2" v-if="totalPages > 1">
    <div class="join">
      <!-- Previous Page Button with Icon (Small) -->
      <button class="join-item btn btn-sm" :class="{ 'btn-disabled': currentPage === 1 }"
        @click.prevent="changePage(currentPage - 1)" :disabled="currentPage === 1">
        <font-awesome-icon :icon="['fas', 'chevron-left']" />
      </button>

      <!-- First Page Button (Small) -->
      <button class="join-item btn btn-sm" :class="{ 'btn-active': currentPage === 1 }" @click.prevent="changePage(1)">
        1
      </button>

      <!-- Ellipsis for skipped pages before startPage -->
      <button v-if="startPage > 2" class="join-item btn btn-sm btn-disabled">...</button>

      <!-- Page Buttons (Small) -->
      <button v-for="page in pages" :key="page" class="join-item btn btn-sm"
        :class="{ 'btn-active': page === currentPage }" @click.prevent="changePage(page)">
        {{ page }}
      </button>

      <!-- Ellipsis for skipped pages after endPage -->
      <button v-if="endPage < totalPages - 1" class="join-item btn btn-sm btn-disabled">...</button>

      <!-- Last Page Button (Small) -->
      <button class="join-item btn btn-sm" :class="{ 'btn-active': currentPage === totalPages }"
        @click.prevent="changePage(totalPages)">
        {{ totalPages }}
      </button>

      <!-- Next Page Button with Icon (Small) -->
      <button class="join-item btn btn-sm" :class="{ 'btn-disabled': currentPage === totalPages }"
        @click.prevent="changePage(currentPage + 1)" :disabled="currentPage === totalPages">
        <font-awesome-icon :icon="['fas', 'chevron-right']" />
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: "PageNavigation",
  props: {
    currentPage: {
      type: Number,
      required: true
    },
    totalPages: {
      type: Number,
      required: true
    }
  },
  computed: {
    startPage() {
      if (this.currentPage <= 6) {
        return 2;
      } else if (this.currentPage + 4 >= this.totalPages) {
        return Math.max(this.totalPages - 9, 2);
      } else {
        return this.currentPage - 4;
      }
    },
    endPage() {
      if (this.currentPage <= 6) {
        return Math.min(10, this.totalPages - 1);
      } else if (this.currentPage + 4 >= this.totalPages) {
        return this.totalPages - 1;
      } else {
        return this.currentPage + 4;
      }
    },
    pages() {
      let pages = [];
      for (let i = this.startPage; i <= this.endPage; i++) {
        pages.push(i);
      }
      return pages;
    }
  },
  methods: {
    changePage(page) {
      if (page > 0 && page <= this.totalPages && page !== this.currentPage) {
        this.$emit("change-page", page);
      }
    }
  }
};
</script>
