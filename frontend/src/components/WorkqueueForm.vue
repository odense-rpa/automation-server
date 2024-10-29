<template>
  <form @submit.prevent="saveWorkqueue">
    <!-- Name Field -->
    <div class="flex items-center mb-3">
      <label class="w-1/5 lg:w-1/6 font-semibold" for="name">Name:</label>
      <div class="w-full">
        <input
          type="text"
          class="input input-bordered w-full"
          v-model="editedWorkqueue.name"
          id="name"
          required
        />
      </div>
    </div>

    <!-- Description Field -->
    <div class="flex items-center mb-3">
      <label for="description" class="w-1/5 lg:w-1/6 font-semibold">Description:</label>
      <div class="w-full">
        <textarea
          type="text"
          class="textarea textarea-bordered w-full"
          v-model="editedWorkqueue.description"
          id="description"
        ></textarea>
      </div>
    </div>

    <!-- Enabled Checkbox -->
    <div class="flex items-center mb-3">
      <div class="w-1/5 lg:w-1/6"></div>
      <div class="w-full">
        <label class="cursor-pointer flex items-center space-x-2">
          <input type="checkbox" class="checkbox checkbox-primary" v-model="editedWorkqueue.enabled" id="enabled" />
          <span>Enabled</span>
        </label>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex justify-end space-x-2 mt-4">
      <button type="submit" class="btn btn-primary">Save</button>
      <button type="button" @click="cancelEdit" class="btn">Cancel</button>
    </div>
  </form>
</template>

<script>
export default {
  name: 'WorkqueueForm',
  components: {
  },
  props: {
    workqueue: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      editedWorkqueue: { ...this.workqueue },
    }
  },
  methods: {
    saveWorkqueue() {
      this.$emit('save', this.editedWorkqueue)
    },
    cancelEdit() {
      this.$emit('cancel', this.editedWorkqueue)
      this.editedWorkqueue = { ...this.workqueue }
    }
  },
  watch: {
    workqueue: {
      handler() {
        this.editedWorkqueue = { ...this.workqueue }
      },
      deep: true
    }
  }
}
</script>

<style scoped>
/* Your component styles go here */
</style>