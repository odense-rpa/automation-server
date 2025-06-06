<template>
  <div class="json-view">
    <div v-if="showFullJson">
      <pre
        v-if="isValidJson"
        class="p-1 pointer border"
        @click="toggleView()"
        v-html="highlightedJson"
      ></pre>
      <pre v-if="!isValidJson" class="p-1 pointer text-danger border" @click="toggleView()">{{
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
    }
  },
  data() {
    return {
      showFullJson: false,
      isValidJson: true
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
