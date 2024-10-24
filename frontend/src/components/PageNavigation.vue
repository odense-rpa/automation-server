<template>
  <nav class="d-flex justify-content-end me-2">
    <ul class="pagination" v-if="totalPages > 1">
      <li class="page-item" :class="{ disabled: currentPage === 1 }">
        <a class="page-link" href="#" @click.prevent="changePage(currentPage - 1)">
          <i class="bi bi-chevron-left"></i>
        </a>
      </li>
      <li v-if="totalPages > 1" class="page-item" :class="{ disabled: currentPage === 1 }">
        <a class="page-link" href="#" @click.prevent="changePage(1)">1</a>
      </li>
      <li v-if="startPage > 2" class="page-item disabled">
        <span class="page-link">...</span>
      </li>
      <li v-for="page in pages" :key="page" :class="{ active: page === currentPage }" class="page-item">
        <a class="page-link" href="#" @click.prevent="changePage(page)">{{ page }}</a>
      </li>
      <li v-if="endPage < totalPages - 1" class="page-item disabled">
        <span class="page-link">...</span>
      </li>
      <li v-if="totalPages > 1" class="page-item" :class="{ disabled: currentPage === totalPages }">
        <a class="page-link" href="#" @click.prevent="changePage(totalPages)">{{ totalPages }}</a>
      </li>
      <li class="page-item" :class="{ disabled: currentPage === totalPages }">
        <a class="page-link" href="#" @click.prevent="changePage(currentPage + 1)">
          <i class="bi bi-chevron-right"></i>
        </a>
      </li>
    </ul>
  </nav>
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
