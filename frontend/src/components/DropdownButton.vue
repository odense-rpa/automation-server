<template>
  <div class="dropdown dropdown-bottom dropdown-end">
    <!-- Dropdown Toggle Button -->
    <button ref="dropdownButton" tabindex="0" class="btn btn-sm btn-accent-content m-1">
      <font-awesome-icon :icon="['fas', 'ellipsis-v']" />
    </button>
    
    <!-- Dropdown Menu -->
    <ul tabindex="0" class="dropdown-content menu bg-base-100 rounded-box z-[1] w-52 p-2 shadow">
      <li v-for="(item, index) in items" :key="index">
        <a href="#" @click.prevent="itemClicked(item)">
          <font-awesome-icon :icon="item.icon" v-if="item.icon" />
          {{ item.text }}
        </a>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'DropdownButton',
  props: {
    items: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      dropdownButton: null,
    };
  },
  methods: {
    itemClicked(item) {
      this.$emit('item-clicked', item.action, item); // Emit the item clicked event
      
      // Remove focus from the dropdown button to close the dropdown
      if (this.dropdownButton) {
        this.dropdownButton.focus();
        this.dropdownButton.blur();
      }
    },
  },
  mounted() {
    // Ensure each instance has its own button reference
    this.dropdownButton = this.$el.querySelector('button');
  },
};
</script>
