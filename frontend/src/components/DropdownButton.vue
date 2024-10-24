<template>
  <div class="btn-group">
    <button class="btn btn-sm btn-secondary dropdown-toggle" type="button" aria-expanded="false"
      @click="isOpen = !isOpen">
      <i class="bi bi-three-dots"></i>
    </button>
    <ul class="dropdown-menu" :class="{ show: isOpen }"
      style="position: absolute; transform: translate3d(0px, 35px, 0px); top: 0px; left: 0px; will-change: transform;">
      <li v-for="(item, index) in items" :key="index">
        <a class="dropdown-item" href="#" @click.prevent="itemClicked(item)"><i :class="item.icon" v-if="item.icon" />
          {{ item.text }}</a>
      </li>
    </ul>
  </div>
</template>

<script>
//import { onBeforeUnmount, onMounted } from 'vue';

export default {
  name: 'DropdownButton',
  props: {
    items: {
      type: Array,
      default: () => [],
    },
  },
  data: () => ({
    isOpen: false,
  }),
  methods: {
    itemClicked(item) {
      this.$emit('item-clicked', item.action, item);
      this.isOpen = false;
    }
  },

};
</script>

<style scoped>
/* Add any styles for your dropdown button here */
</style>