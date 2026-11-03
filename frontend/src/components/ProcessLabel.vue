<template>
  <span v-if="entry">
    {{ entry.name }}<span v-if="entry.deleted" class="text-base-content/60"> (deleted)</span>
  </span>
  <span v-else-if="loaded" class="text-base-content/60">Unknown process #{{ processId }}</span>
</template>

<script>
import { useNameStore } from '@/stores/nameStore'

export default {
  name: 'ProcessLabel',
  props: {
    processId: {
      type: Number,
      required: true
    }
  },
  computed: {
    names() {
      return useNameStore()
    },
    entry() {
      return this.names.processes[this.processId]
    },
    loaded() {
      return this.names.loadedAt.processes > 0
    }
  },
  watch: {
    processId: {
      handler(id) {
        this.names.ensure('processes', id)
      },
      immediate: true
    }
  }
}
</script>
