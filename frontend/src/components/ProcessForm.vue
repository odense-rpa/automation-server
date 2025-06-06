<template>
  <form @submit.prevent="saveProcess" v-if="editedProcess" class="space-y-4">
    <!-- Name Field -->
    <div class="flex items-center">
      <label for="name" class="w-1/5 font-semibold">Name</label>
      <div class="w-full">
        <input
          type="text"
          class="input input-bordered w-full"
          v-model="editedProcess.name"
          id="name"
          required
        />
      </div>
    </div>

    <!-- Description Field -->
    <div class="flex items-center">
      <label for="description" class="w-1/5 font-semibold">Description</label>
      <div class="w-full">
        <textarea
          class="textarea textarea-bordered w-full"
          v-model="editedProcess.description"
          id="description"
        ></textarea>
      </div>
    </div>

    <!-- Workqueue Field -->
    <div class="flex items-center">
      <label for="workqueue_id" class="w-1/5 font-semibold">Workqueue</label>
      <div class="w-full">
        <select
          v-model="editedProcess.workqueue_id"
          class="select select-bordered w-full"
          required
        >
          <option :value="null" :key="0">None</option>
          <option :value="queue.id" v-for="queue in workqueues" :key="queue.id">
            {{ queue.name }}
          </option>
        </select>
      </div>
    </div>

    <!-- Platform Field -->
    <div class="flex items-center">
      <label for="target_type" class="w-1/5 font-semibold">Platform</label>
      <div class="w-full">
        <select
          v-model="editedProcess.target_type"
          class="select select-bordered w-full"
          required
        >
          <option value="python">Python</option>
          <option value="blue_prism">Blue Prism</option>
          <option value="ui_path">UI Path</option>
          <option value="power_automate_desktop">Power Automate Desktop</option>
        </select>
      </div>
    </div>

    <!-- Git Repo Field (Python Only) -->
    <div class="flex items-center" v-if="editedProcess.target_type == 'python'">
      <label for="target_source" class="w-1/5 font-semibold">Git repo</label>
      <div class="w-full">
        <input
          type="text"
          class="input input-bordered w-full"
          v-model="editedProcess.target_source"
          id="target_source"
          required
        />
      </div>
    </div>

    <!-- Git Credentials Field (Python Only) -->
    <div class="flex items-center" v-if="editedProcess.target_type == 'python'">
      <label for="target_credentials_id" class="w-1/5 font-semibold">Git credentials</label>
      <div class="w-full">
        <select
          v-model="editedProcess.target_credentials_id"
          class="select select-bordered w-full"
        >
          <option :value="null" :key="0">None</option>
          <option :value="cred.id" v-for="cred in credentials" :key="cred.id">{{ cred.name }}</option>
        </select>
      </div>
    </div>

    <!-- Unsupported Platform Message -->
    <div class="text-center text-gray-500" v-if="editedProcess.target_type != 'python'">
      We are sorry, but this platform is currently not supported.
    </div>

    <!-- Requirements Field -->
    <div class="flex items-center">
      <label for="requirements" class="w-1/5 font-semibold">Requirements</label>
      <div class="w-full">
        <input
          type="text"
          class="input input-bordered w-full"
          v-model="editedProcess.requirements"
          id="requirements"
        />
        <small class="text-gray-500 block mt-1">Space separated list of required features</small>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="text-right space-x-2">
      <button type="submit" class="btn btn-primary">Save</button>
      <router-link :to="{ name: 'process' }" class="btn">Cancel</router-link>
      <button type="button" class="btn btn-error" @click="deleteProcess" v-if="this.process.id">Delete</button>
    </div>
  </form>
</template>

<script>
import { workqueuesAPI, credentialsAPI } from '@/services/automationserver.js'

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
      workqueues: [],
      credentials: []
    }
  },
  async mounted() {
    this.workqueues = await workqueuesAPI.getWorkqueues()
    this.credentials = await credentialsAPI.getCredentials()
  },

  methods: {
    saveProcess() {
      this.$emit('save', this.editedProcess)
    },
    deleteProcess() {
      this.$emit('delete', this.editedProcess)
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
