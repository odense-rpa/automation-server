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
          <input
            type="checkbox"
            class="checkbox checkbox-primary"
            v-model="editedWorkqueue.enabled"
            id="enabled"
          />
          <span>Enabled</span>
        </label>
      </div>
    </div>

    <!-- Auto-Clean -->
    <div class="flex items-center mb-3">
      <div class="w-1/5 lg:w-1/6"></div>
      <div class="w-full">
        <label class="cursor-pointer flex items-center space-x-2">
          <input
            type="checkbox"
            class="checkbox checkbox-primary"
            v-model="autoCleanEnabled"
            id="auto-clean"
          />
          <span>Auto-clean old items</span>
        </label>
      </div>
    </div>
    <div class="flex items-center mb-3" v-if="autoCleanEnabled">
      <label for="auto-clean-days" class="w-1/5 lg:w-1/6 font-semibold">Max age (days):</label>
      <div class="w-full">
        <input
          type="number"
          class="input input-bordered w-full"
          v-model.number="autoCleanDays"
          id="auto-clean-days"
          min="1"
          required
        />
        <p class="text-sm opacity-70 mt-1">
          Completed and failed items older than this are deleted automatically. New and in-progress
          items are never deleted.
        </p>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex justify-end space-x-2 mt-4">
      <button type="submit" class="btn btn-primary">Save</button>
      <button type="button" @click="cancelEdit" class="btn">Cancel</button>
      <button
        type="button"
        @click="deleteWorkqueue"
        class="btn btn-error"
        v-if="editedWorkqueue.id"
      >
        Delete
      </button>
    </div>
  </form>
</template>

<script>
export default {
  name: 'WorkqueueForm',
  components: {},
  props: {
    workqueue: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      editedWorkqueue: { ...this.workqueue },
      autoCleanEnabled: this.workqueue.auto_clean_max_age_days != null,
      autoCleanDays: this.workqueue.auto_clean_max_age_days ?? 30
    }
  },
  methods: {
    saveWorkqueue() {
      this.editedWorkqueue.auto_clean_max_age_days = this.autoCleanEnabled
        ? Number(this.autoCleanDays)
        : null
      this.$emit('save', this.editedWorkqueue)
    },
    cancelEdit() {
      this.$emit('cancel', this.editedWorkqueue)
      this.resetForm()
    },
    deleteWorkqueue() {
      this.$emit('delete', this.editedWorkqueue)
    },
    resetForm() {
      this.editedWorkqueue = { ...this.workqueue }
      this.autoCleanEnabled = this.workqueue.auto_clean_max_age_days != null
      this.autoCleanDays = this.workqueue.auto_clean_max_age_days ?? 30
    }
  },
  watch: {
    workqueue: {
      handler() {
        this.resetForm()
      },
      deep: true
    }
  }
}
</script>

<style scoped>
/* Your component styles go here */
</style>
