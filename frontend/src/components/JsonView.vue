<template>
  <div class="json-view">
    <div v-if="showFullJson">
      <pre v-if="isValidJson" class="p-1 pointer border" @click="toggleView()" v-html="highlightedJson"></pre>
      <pre v-if="!isValidJson" class="p-1 pointer text-danger border" @click="toggleView()">{{ jsonData }}</pre>
    </div>
    <div v-else>
      <p v-if="isValidJson"><a href="#" @click.prevent="toggleView()">{{ jsonPropertyCount }} properties</a></p>
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
      type: String,
      required: true
    }
  },
  data() {
    return {
      showFullJson: false,
      parsedJson: null,
      isValidJson: true
    };
  },
  computed: {
    formattedJson() {
      return JSON.stringify(this.parsedJson, null, 2);
    },
    jsonPropertyCount() {
      return this.parsedJson ? Object.keys(this.parsedJson).length : 0;
    },
    highlightedJson() {
      return this.isValidJson ? hljs.highlight('json', this.formattedJson).value : '';
    }
  },
  watch: {
    jsonData: {
      immediate: true,
      handler(newVal) {
        this.parseJson(newVal);
      }
    }
  },
  methods: {
    toggleView() {
      this.showFullJson = !this.showFullJson;
    },
    parseJson(jsonString) {
      try {
        this.parsedJson = JSON.parse(jsonString);
        this.isValidJson = true;
      } catch (e) {
        this.parsedJson = null;
        this.isValidJson = false;
      }
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