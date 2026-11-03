<template>
  <form @submit.prevent="submit" class="space-y-4">
    <div class="flex items-center">
      <label for="datastore-name" class="w-1/5 font-semibold">Name</label>
      <div class="w-full">
        <input id="datastore-name" type="text" class="input input-bordered w-full" v-model="name" required />
        <p class="text-xs text-base-content/60 mt-1">
          Automations find the datastore by this name, so renaming it breaks those that use it.
        </p>
      </div>
    </div>

    <div class="flex items-center">
      <label for="datastore-description" class="w-1/5 font-semibold">Description</label>
      <div class="w-full">
        <input id="datastore-description" type="text" class="input input-bordered w-full" v-model="description" />
      </div>
    </div>

    <div class="flex">
      <label for="datastore-data" class="w-1/5 font-semibold pt-3">Document (JSON)</label>
      <div class="w-full">
        <textarea
          id="datastore-data"
          class="textarea textarea-bordered w-full h-96 font-mono text-sm"
          v-model="json"
          spellcheck="false"
        ></textarea>
        <p v-if="jsonError" class="text-error text-sm mt-1">{{ jsonError }}</p>
      </div>
    </div>

    <div class="flex justify-end gap-2">
      <button type="submit" class="btn btn-primary" :disabled="saving">{{ saving ? 'Saving…' : 'Save' }}</button>
      <button type="button" class="btn" @click="$emit('cancel')">Cancel</button>
    </div>
  </form>
</template>

<script>
export default {
  name: 'DatastoreForm',
  props: {
    // { name, description, data }
    datastore: { type: Object, required: true },
    saving: { type: Boolean, default: false }
  },
  emits: ['save', 'cancel'],
  data() {
    return {
      name: this.datastore.name || '',
      description: this.datastore.description || '',
      json: JSON.stringify(this.datastore.data ?? {}, null, 2),
      jsonError: ''
    }
  },
  methods: {
    submit() {
      let data
      try {
        data = JSON.parse(this.json)
      } catch (error) {
        this.jsonError = `Not valid JSON: ${error.message}`
        return
      }
      // A datastore holds one JSON object, not a list or a single value
      if (data === null || typeof data !== 'object' || Array.isArray(data)) {
        this.jsonError = 'The document must be a JSON object, like {"key": "value"}'
        return
      }
      this.jsonError = ''
      this.$emit('save', { name: this.name.trim(), description: this.description, data })
    }
  }
}
</script>
