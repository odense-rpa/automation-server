<template>
  <span v-if="entry">
    {{ entry.name }}<span v-if="entry.deleted" class="text-base-content/60"> (deleted)</span>
  </span>
  <span v-else-if="loaded" class="text-base-content/60">Unknown workqueue #{{ workqueueId }}</span>
</template>

<script>
import { useNameStore } from '@/stores/nameStore'

export default {
  name: 'WorkqueueLabel',
  props: {
    workqueueId: {
      type: Number,
      required: true
    }
  },
  computed: {
    names() {
      return useNameStore()
    },
    entry() {
      return this.names.workqueues[this.workqueueId]
    },
    loaded() {
      return this.names.loadedAt.workqueues > 0
    }
  },
  watch: {
    workqueueId: {
      handler(id) {
        this.names.ensure('workqueues', id)
      },
      immediate: true
    }
  }
}
</script>
