<template>
  <div class="json-view">
    <div v-if="showFullJson" class="relative">
      <button class="absolute top-2 right-2 btn btn-ghost btn-xs" @click="copyJson" :title="copied ? 'Copied!' : 'Copy'">
        <font-awesome-icon :icon="['fas', copied ? 'check' : 'copy']" />
      </button>
      <pre
        v-if="isValidJson"
        :class="['p-1', 'border', { pointer: !expanded }]"
        @click="!expanded && toggleView()"
        v-html="highlightedJson"
      ></pre>
      <pre v-if="!isValidJson" :class="['p-1', 'text-danger', 'border', { pointer: !expanded }]" @click="!expanded && toggleView()">{{
        jsonData
      }}</pre>
    </div>
    <div v-else>
      <p v-if="isValidJson">
        <a href="#" @click.prevent="toggleView()">{{ jsonPropertyCount }} properties</a>
      </p>
      <p v-else class="text-danger" @click.prevent="toggleView()">Invalid JSON data</p>
    </div>
  </div>
</template>

<script>
import hljs from 'highlight.js';
import 'highlight.js/styles/tokyo-night-dark.css';

export default {
  name: 'JsonView',
  props: {
    jsonData: {
      type: Object,
      required: true
    },
    expanded: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      showFullJson: this.expanded,
      isValidJson: true,
      copied: false
    };
  },
  computed: {
    formattedJson() {
      return JSON.stringify(this.jsonData, null, 2);
    },
    jsonPropertyCount() {
      return this.jsonData ? Object.keys(this.jsonData).length : 0;
    },
    highlightedJson() {
      return this.isValidJson ? hljs.highlight('json', this.formattedJson).value : '';
    }
  },
  watch: {
    jsonData: {
      immediate: true,
      handler(newVal) {
        newVal;
      }
    }
  },
  methods: {
    toggleView() {
      this.showFullJson = !this.showFullJson;
    },
    copyJson() {
      navigator.clipboard.writeText(this.formattedJson);
      this.copied = true;
      setTimeout(() => { this.copied = false; }, 1500);
    }
  }
};
</script>

<style scoped>
.json-view {
  max-width: 100%;
  overflow-x: auto;
}

.pointer {
  cursor: pointer;
}
</style>
