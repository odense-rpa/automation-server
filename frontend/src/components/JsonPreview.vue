<template>
  <span v-if="isEmpty" class="text-sm text-base-content/50">{}</span>

  <template v-else>
    <button
      type="button"
      class="block text-sm text-left truncate max-w-xs rounded px-1 hover:bg-base-300"
      title="Show data"
      @click="openModal"
    >{{ summary }}</button>

    <!-- Native <dialog> renders in the top layer, so no container can clip it.
         Only mounted while open, so tables with many rows stay light. -->
    <dialog v-if="isOpen" ref="dialog" class="modal" @close="isOpen = false">
      <!-- The box clips its rounded corners; only the body scrolls, so the
           scrollbar never cuts the corners and the heading stays visible -->
      <div class="modal-box w-11/12 max-w-4xl p-0 overflow-hidden flex flex-col">
        <div class="relative px-6 pt-5 pb-3">
          <form method="dialog">
            <button class="btn btn-sm btn-circle btn-ghost absolute right-3 top-3" aria-label="Close">
              <font-awesome-icon :icon="['fas', 'times']" />
            </button>
          </form>
          <h3 class="font-bold text-lg pr-8">{{ title }}</h3>
        </div>
        <div class="overflow-y-auto px-6 pb-6 min-h-0">
          <json-tree :data="data" />
        </div>
      </div>
      <form method="dialog" class="modal-backdrop">
        <button>close</button>
      </form>
    </dialog>
  </template>
</template>

<script>
import JsonTree from './JsonTree.vue'
import { childCount } from '@/utils/json.js'

export default {
  name: 'JsonPreview',
  components: { JsonTree },
  props: {
    data: { default: null },
    // Shown as the modal heading, e.g. "Work item 39"
    title: { type: String, default: 'Data' }
  },
  data() {
    return { isOpen: false }
  },
  computed: {
    isEmpty() {
      return this.data === null || this.data === undefined || childCount(this.data) === 0
    },
    summary() {
      const n = childCount(this.data)
      if (Array.isArray(this.data)) return `${n} ${n === 1 ? 'item' : 'items'}`
      return `${n} ${n === 1 ? 'property' : 'properties'}`
    }
  },
  methods: {
    async openModal() {
      this.isOpen = true
      await this.$nextTick()
      this.$refs.dialog.showModal()
    }
  }
}
</script>
