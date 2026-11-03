<template>
  <div class="json-tree font-mono text-sm min-w-0">
    <div class="flex items-center gap-1 mb-1">
      <template v-if="!raw && isContainerData">
        <button type="button" class="btn btn-ghost btn-xs" @click="setDepth(Infinity)">Expand all</button>
        <button type="button" class="btn btn-ghost btn-xs" @click="setDepth(0)">Collapse all</button>
      </template>
      <button type="button" class="btn btn-ghost btn-xs" @click="raw = !raw">{{ raw ? 'Tree' : 'Raw' }}</button>
      <button type="button" class="btn btn-ghost btn-xs ml-auto" :title="copied ? 'Copied!' : 'Copy'" @click="copy">
        <font-awesome-icon :icon="['fas', copied ? 'check' : 'copy']" />
      </button>
    </div>

    <pre v-if="raw" class="bg-base-200 rounded p-2 overflow-x-auto">{{ pretty }}</pre>

    <!-- Root container is shown as its children directly, without a root summary row -->
    <div v-else-if="isContainerData && hasEntries" :key="renderKey">
      <json-node
        v-for="entry in entries"
        :key="entry.key"
        :name="entry.key"
        :value="entry.value"
        :depth="0"
        :open-depth="depth"
      />
    </div>
    <json-node v-else :value="data" :open-depth="depth" />
  </div>
</template>

<script>
import JsonNode from './JsonNode.vue'
import { isContainer, childCount } from '@/utils/json.js'

export default {
  name: 'JsonTree',
  components: { JsonNode },
  props: {
    data: { default: null },
    // Levels open by default; deeper nodes start collapsed
    openDepth: { type: Number, default: 2 }
  },
  data() {
    return {
      depth: this.openDepth,
      renderKey: 0,
      raw: false,
      copied: false
    }
  },
  computed: {
    isContainerData() {
      return isContainer(this.data)
    },
    hasEntries() {
      return childCount(this.data) > 0
    },
    entries() {
      if (Array.isArray(this.data)) return this.data.map((value, key) => ({ key, value }))
      return Object.entries(this.data).map(([key, value]) => ({ key, value }))
    },
    pretty() {
      return JSON.stringify(this.data, null, 2)
    }
  },
  methods: {
    setDepth(depth) {
      this.depth = depth
      this.renderKey++ // re-create nodes so manual toggles reset
    },
    async copy() {
      await navigator.clipboard.writeText(this.pretty)
      this.copied = true
      setTimeout(() => { this.copied = false }, 1500)
    }
  }
}
</script>
