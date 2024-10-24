<template>
  <form @submit.prevent="saveProcess" v-if="editedProcess">
    <div class="row mb-3">
      <label for="name" class="col-sm-2 col-form-label">Name</label>
      <div class="col-sm-10">
        <input type="text" class="form-control" v-model="editedProcess.name" id="name" required />
      </div>
    </div>
    <div class="row mb-3">
      <label for="description" class="col-sm-2 col-form-label">Description:</label>
      <div class="col-sm-10">
        <textarea
          type="text"
          class="form-control"
          v-model="editedProcess.description"
          id="description"
        ></textarea>
      </div>
    </div>

    <div class="row mb-3">
      <label for="workqueue_id" class="col-sm-2 col-form-label">Workqueue:</label>
      <div class="col-sm-10">
        <select
          name="target_type"
          v-model="editedProcess.workqueue_id"
          class="form-control"
          required
        >
          <option value="0">None</option>
          <option :value="queue.id" v-for="queue in workqueues" :key="queue.id">
            {{ queue.name }}
          </option>
        </select>
      </div>
    </div>

    <div class="row mb-3">
      <label for="target_type" class="col-sm-2 col-form-label">Platform:</label>
      <div class="col-sm-10">
        <select
          name="target_type"
          v-model="editedProcess.target_type"
          class="form-control"
          required
        >
          <option value="python">Python</option>
          <option value="blue_prism">Blue Prism</option>
          <option value="ui_path">UI Path</option>
          <option value="power_automate_desktop">Power Automate Desktop</option>
        </select>
      </div>
    </div>

    <div class="row mb-3" v-if="editedProcess.target_type == 'python'">
      <label for="target_source" class="col-sm-2 col-form-label">Git repo:</label>
      <div class="col-sm-10">
        <input
          type="text"
          class="form-control"
          v-model="editedProcess.target_source"
          id="target_source"
          required
        />
      </div>
    </div>

    <div class="row mb-3" v-if="editedProcess.target_type == 'python'">
      <label for="target_credentials_id" class="col-sm-2 col-form-label">Git credentials:</label>
      <div class="col-sm-10">
        <select
          name="target_credentials_id"
          v-model="editedProcess.target_credentials_id"
          class="form-control"
          required
        >
          <option value="0">None</option>
        </select>
      </div>
    </div>

    <div class="row mb-3" v-if="editedProcess.target_type != 'python'">
      <div class="col-sm-12">We are sorry but this platform is currently not supported</div>
    </div>

    <div class="row mb-3">
      <label for="requirements" class="col-sm-2 col-form-label">Requirements</label>
      <div class="col-sm-10">
        <input
          type="text"
          class="form-control"
          v-model="editedProcess.requirements"
          id="requirements"
        />
        <small class="form-text text-muted">Space separated list of required features</small>
      </div>
    </div>

    <div class="text-end">
      <button type="submit" class="btn btn-primary">Save</button>
      <router-link :to="{ name: 'process' }" class="btn">Cancel</router-link>
    </div>
  </form>
</template>
<script>
import { workqueuesAPI } from '@/services/automationserver.js'

export default {
  props: {
    process: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      editedProcess: { ...this.process },
      workqueues: []
    }
  },
  async mounted() {
    this.workqueues = await workqueuesAPI.getWorkqueues()
  },

  methods: {
    saveProcess() {
      this.$emit('save', this.editedProcess)
    }
  },

  //Detect change to process prop
  watch: {
    process: {
      handler() {
        this.editedProcess = { ...this.process }
      },
      deep: true
    }
  }
}
</script>
