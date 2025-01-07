<template>
  <form @submit.prevent="submitForm" class="space-y-4">
    <!-- Type Selector -->
    <div>
      <select class="select select-bordered w-full" v-model="editObject.type">
        <option value="cron">Cron</option>
        <option value="date">Date</option>
        <option value="workqueue">Workqueue</option>
      </select>
    </div>

    <!-- Cron Input Field -->
    <div v-if="editObject.type === 'cron'">
      <input type="text" class="input input-bordered w-full" id="cron" v-model="editObject.cron" required />
      <small class="text-gray-500 block mt-1">
        See <a href="https://crontab.guru/" target="_blank" class="link">crontab.guru</a> for help.
      </small>
    </div>

    <!-- Date Input Field -->
    <div v-if="editObject.type === 'date'">
      <input type="datetime-local" class="input input-bordered w-full" v-model="editObject.date" required />
    </div>

    <!-- Workqueue Fields -->
    <div v-if="editObject.type === 'workqueue'" class="space-y-2">
      <!-- Workqueue Selector -->
      <div>
        <select class="select select-bordered w-full" v-model="editObject.workqueue_id" required>
          <option v-for="workqueue in workqueues" :key="workqueue.id" :value="workqueue.id">
            {{ workqueue.name }}
          </option>
        </select>
      </div>

      <!-- Resource Limit Input -->
      <div>
        <small class="text-gray-500 block mb-1">How many resources can this workqueue consume</small>
        <input type="number" class="input input-bordered w-full" v-model="editObject.workqueue_resource_limit"
          placeholder="Set the resource limit" required />
      </div>

      <!-- Scale-up Threshold Input -->
      <div>
        <small class="text-gray-500 block mb-1">How many workitems must be present to scale up</small>
        <input type="number" class="input input-bordered w-full" v-model="editObject.workqueue_scale_up_threshold"
          placeholder="Set the scaling threshold" required />
      </div>
    </div>

    <div>
      <input type="text" class="input input-bordered w-full" id="cron" v-model="editObject.parameters" />
      <small class="text-gray-500 block mt-1">
        Commandline parameters to pass to the process
      </small>
    </div>

    <!-- Enabled Checkbox -->
    <div>
      <label class="flex items-center space-x-2">
        <input type="checkbox" class="checkbox checkbox-primary" id="enabled" v-model="editObject.enabled" />
        <span>Enabled</span>
      </label>
    </div>

    <!-- Action Buttons -->
    <div class="text-right space-x-2">
      <button type="submit" class="btn btn-primary btn-sm">
        <font-awesome-icon :icon="['fas', 'check']" />
      </button>
      <button class="btn btn-sm" @click.prevent="$emit('cancel')">
        <font-awesome-icon :icon="['fas', 'times']" />
      </button>
    </div>
  </form>
</template>

<script>
import { workqueuesAPI } from '@/services/automationserver.js'

export default {
  name: 'TriggerForm',
  props: {
    trigger: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      editObject: {},
      workqueues: []
    }
  },
  methods: {
    submitForm() {
      if (this.editObject.type == 'cron' || this.editObject.type == 'date') {
        this.editObject.workqueue_id = null;
        this.editObject.workqueue_resource_limit = 0;
        this.editObject.workqueue_scale_up_threshold = 0;
      }

      if (this.editObject.type == 'workqueue') {
        this.editObject.date = null;
        this.editObject.cron = "";
      }

      if (this.editObject.type == 'date') {
        this.editObject.cron = "";
      }

      if (this.editObject.type == 'cron') {
        this.editObject.date = null;
      }


      this.$emit('save', this.editObject)
    }
  },
  watch: {
    trigger: {
      handler() {
        this.editObject = { ...this.trigger }
      },
      immediate: true
    }
  },
  async mounted() {
    this.workqueues = await workqueuesAPI.getWorkqueues()
    this.workqueues.sort((a, b) => a.name.localeCompare(b.name))
  }
}

</script>