<template>
  <div class="dropdown dropdown-bottom dropdown-end">
    <!-- Dropdown Toggle Button -->
     <slot>
      <button type="button" tabindex="0" class="btn btn-sm btn-accent-content m-1" :aria-label="label">
        <font-awesome-icon :icon="icon" />
      </button>
    </slot>
    
    <!-- Dropdown Menu -->
    <ul tabindex="0" class="dropdown-content menu bg-base-100 rounded-box z-[1] w-52 p-2 shadow">
      <li v-for="(item, index) in items" :key="index" :class="{ disabled: item.disabled }">
        <a href="#" :aria-disabled="item.disabled || null" @click.prevent="itemClicked(item)">
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
    icon: {
      type: Array,
      default: () => ['fas', 'ellipsis-v'], // Default icon
    },
    // Accessible name for the default (icon-only) button
    label: {
      type: String,
      default: 'Actions',
    },
  },
  emits: ['item-clicked'],
  methods: {
    itemClicked(item) {
      if (item.disabled) return;
      this.$emit('item-clicked', item.action, item); // Emit the item clicked event
      
      // Remove focus from the dropdown button (default or slotted) to close the dropdown
      const button = this.$el.querySelector('button');
      if (button) {
        button.focus();
        button.blur();
      }
    },
  },
};
</script>
