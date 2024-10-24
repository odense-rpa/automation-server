<template>
      <form @submit.prevent="saveWorkqueue">
        <div class="row mb-3">
          <label class="col-sm-2" for="name">Name:</label>
          <div class="col">
            <input type="text" class="form-control" v-model="editedWorkqueue.name" id="name" required />
          </div>
        </div>
        <div class="row mb-3">
          <label for="description" class="col-sm-2">Description:</label>
          <div class="col">
            <textarea type="text" class="form-control" v-model="editedWorkqueue.description"
              id="description"></textarea>
          </div>
        </div>
        <div class="row mb-3">
          <div class="col-sm-2">&nbsp;</div>
          <div class="col">
            <div class="form-check">
              <input class="form-check-input" type="checkbox" v-model="editedWorkqueue.enabled" id="enabled" />
              <label class="form-check-label" for="enabled"> Enabled</label>
            </div>
          </div>
        </div>
        <div class="text-end">
          <button type="submit" class="btn btn-primary">Save</button>
          <button @click="cancelEdit" class="btn">Cancel</button>
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