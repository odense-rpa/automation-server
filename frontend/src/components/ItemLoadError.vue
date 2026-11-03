<template>
  <div role="alert" class="alert alert-warning mb-3 flex justify-between">
    <span>{{ message }}</span>
    <button type="button" class="btn btn-sm" @click="$emit('retry')">Try again</button>
  </div>
</template>

<script>
// Shown by single-item views when loading failed for a reason other than
// "not found" (server error, network): the item probably exists, so retry
export default {
  name: 'ItemLoadError',
  props: {
    message: { type: String, required: true }
  },
  emits: ['retry']
}
</script>
