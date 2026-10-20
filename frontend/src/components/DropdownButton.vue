<template>
  <div class="inline-block" ref="root">
    <!-- Dropdown Toggle Button -->
    <span @click="toggle">
      <slot>
        <button ref="dropdownButton" class="btn btn-sm btn-accent-content m-1">
          <font-awesome-icon :icon="icon" />
        </button>
      </slot>
    </span>

    <!-- Dropdown Menu: teleported to body so cards with overflow-hidden cannot clip it -->
    <Teleport to="body">
      <ul
        v-if="open"
        ref="menu"
        :style="menuStyle"
        class="menu bg-base-100 rounded-box z-[1000] w-52 p-2 shadow fixed"
      >
        <li v-for="(item, index) in items" :key="index">
          <a href="#" @click.prevent="itemClicked(item)">
            <font-awesome-icon :icon="item.icon" v-if="item.icon" />
            {{ item.text }}
          </a>
        </li>
      </ul>
    </Teleport>
  </div>
</template>

<script>
const MENU_WIDTH = 208; // w-52
const MARGIN = 8;

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
  },
  data() {
    return {
      open: false,
      menuStyle: {},
    };
  },
  methods: {
    toggle() {
      if (this.open) {
        this.close();
        return;
      }
      this.position();
      this.open = true;
      // Defer so the click that opened the menu does not immediately close it
      setTimeout(() => {
        document.addEventListener('click', this.onOutsideClick);
        document.addEventListener('keydown', this.onKeydown);
        window.addEventListener('resize', this.close);
        window.addEventListener('scroll', this.close, true);
      });
    },
    close() {
      this.open = false;
      document.removeEventListener('click', this.onOutsideClick);
      document.removeEventListener('keydown', this.onKeydown);
      window.removeEventListener('resize', this.close);
      window.removeEventListener('scroll', this.close, true);
    },
    // Right-align under the trigger; flip above it if there is no room below
    position() {
      const trigger = this.$refs.root.getBoundingClientRect();
      const menuHeight = this.items.length * 40 + 16;
      const opensUp =
        window.innerHeight - trigger.bottom < menuHeight + MARGIN && trigger.top > menuHeight + MARGIN;
      const left = Math.max(MARGIN, Math.min(trigger.right - MENU_WIDTH, window.innerWidth - MENU_WIDTH - MARGIN));
      this.menuStyle = opensUp
        ? { left: `${left}px`, bottom: `${window.innerHeight - trigger.top + 4}px` }
        : { left: `${left}px`, top: `${trigger.bottom + 4}px` };
    },
    onOutsideClick(event) {
      if (this.$refs.menu && !this.$refs.menu.contains(event.target)) this.close();
    },
    onKeydown(event) {
      if (event.key === 'Escape') this.close();
    },
    itemClicked(item) {
      this.close();
      this.$emit('item-clicked', item.action, item); // Emit the item clicked event
    },
  },
  beforeUnmount() {
    this.close();
  },
};
</script>
