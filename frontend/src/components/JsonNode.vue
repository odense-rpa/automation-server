<template>
  <!-- Object / array with children: native <details> for expand/collapse -->
  <details v-if="hasChildren" :open="isOpen" class="json-node" @toggle="isOpen = $event.target.open">
    <summary class="group flex items-center gap-1 cursor-pointer rounded hover:bg-base-200 pr-1">
      <font-awesome-icon :icon="['fas', isOpen ? 'caret-down' : 'caret-right']" class="w-3 text-base-content/50" />
      <span v-if="name !== null" class="font-semibold">{{ name }}:</span>
      <span class="text-base-content/50">{{ isOpen ? bracketOpen : summary }}</span>
      <copy-button
        :text="() => JSON.stringify(value, null, 2)"
        class="opacity-0 group-hover:opacity-100 focus:opacity-100 ml-auto"
      />
    </summary>
    <!-- Children are only rendered while open, keeping large payloads light -->
    <div v-if="isOpen" class="ml-1.5 pl-3 border-l border-base-300">
      <json-node
        v-for="entry in visibleEntries"
        :key="entry.key"
        :name="entry.key"
        :value="entry.value"
        :depth="depth + 1"
        :open-depth="openDepth"
      />
      <button
        v-if="hiddenCount > 0"
        type="button"
        class="btn btn-ghost btn-xs text-base-content/60"
        @click="limit += pageSize"
      >
        Show {{ Math.min(hiddenCount, pageSize) }} more ({{ hiddenCount }} hidden)
      </button>
    </div>
  </details>

  <!-- Leaf: scalar or empty container -->
  <!-- flex-wrap: on narrow screens a long value drops below its key instead of being squeezed -->
  <div v-else class="flex flex-wrap gap-x-1 pl-4 min-w-0">
    <span v-if="name !== null" class="font-semibold max-w-full [overflow-wrap:anywhere]">{{ name }}:</span>
    <pre
      v-if="isMultiline"
      class="whitespace-pre-wrap [overflow-wrap:anywhere] bg-base-200 rounded px-2 py-1 my-0.5 min-w-0 grow basis-64"
      :class="typeClass.string"
    >{{ value }}</pre>
    <span v-else class="[overflow-wrap:anywhere] min-w-0" :class="[leafClass, { 'grow basis-48': leafText.length > 40 }]">{{ leafText }}</span>
  </div>
</template>

<script>
import CopyButton from './CopyButton.vue'
import { jsonType, childCount, summarize, formatScalar, typeClass } from '@/utils/json.js'

const PAGE_SIZE = 20

export default {
  name: 'JsonNode',
  components: { CopyButton },
  props: {
    value: { default: null },
    name: { type: [String, Number], default: null },
    depth: { type: Number, default: 0 },
    openDepth: { type: Number, default: 2 }
  },
  data() {
    return {
      isOpen: this.depth < this.openDepth,
      limit: PAGE_SIZE,
      pageSize: PAGE_SIZE,
      typeClass
    }
  },
  computed: {
    type() {
      return jsonType(this.value)
    },
    hasChildren() {
      return childCount(this.value) > 0
    },
    entries() {
      if (this.type === 'array') return this.value.map((value, key) => ({ key, value }))
      return Object.entries(this.value).map(([key, value]) => ({ key, value }))
    },
    visibleEntries() {
      return this.entries.slice(0, this.limit)
    },
    hiddenCount() {
      return Math.max(0, this.entries.length - this.limit)
    },
    bracketOpen() {
      return this.type === 'array' ? `[${this.value.length}]` : `{${childCount(this.value)}}`
    },
    summary() {
      return summarize(this.value)
    },
    isMultiline() {
      return this.type === 'string' && this.value.includes('\n')
    },
    leafText() {
      if (this.type === 'array') return '[]'
      if (this.type === 'object') return '{}'
      return formatScalar(this.value)
    },
    leafClass() {
      return typeClass[this.type] || 'text-base-content/50'
    }
  },
}
</script>

<style scoped>
summary {
  list-style: none;
}
summary::-webkit-details-marker {
  display: none;
}
</style>
