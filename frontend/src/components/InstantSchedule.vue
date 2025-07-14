<template>
<div class="join">
    <!-- Select Dropdown -->
    <select v-model="selected" class="select select-sm select-bordered join-item">
      <option value="">Trigger process...</option>
      <option v-for="process in processes" :key="process.id" :value="process.id">
        {{ process.name }}
      </option>
    </select>

    <!-- Parameters Input (shown when process is selected) -->
    <transition name="parameter-expand">
      <input
        v-if="selected !== ''"
        type="text"
        class="input input-sm input-bordered join-item"
        v-model="parameters"
        placeholder="Parameters (optional)"
        title="Commandline parameters to pass to the process"
      />
    </transition>

    <!-- Button -->
    <button
      class="btn btn-sm btn-success join-item"
      :class="{ 'btn-disabled': selected === '' }"
      :disabled="selected === ''"
      @click.prevent="trigger()">
      <font-awesome-icon :icon="['fas', 'play']" />
    </button>
</div>
</template>
<script>
import { processesAPI, sessionsAPI } from '@/services/automationserver.js'
import { useAlertStore } from '../stores/alertStore'


export default {
    name: 'InstantSchedule',
    data() {
        return {
            processes: [],
            selected: "",
            parameters: ""
        }
    },
    async created() {
        this.processes = await processesAPI.getProcesses()
        if (this.processes.length > 0) {
             this.processes.sort((a, b) => a.name.localeCompare(b.name))
        }
    },
    methods: {
        async trigger() {
            try {
                // Basic validation for parameters if provided
                if (this.parameters && this.parameters.trim()) {
                    try {
                        JSON.parse(this.parameters)
                    } catch (e) {
                        // If it's not valid JSON, we'll still allow it as plain text parameters
                        // This maintains flexibility for simple command-line arguments
                    }
                }

                await sessionsAPI.createSession(this.selected, this.parameters || null)
                this.selected = ""
                this.parameters = ""

                useAlertStore().addAlert({
                    type: 'success',
                    message: 'Process was triggered'
                })
            } catch (error) {
                useAlertStore().addAlert({
                    type: 'error',
                    message: `Failed to trigger process: ${error.message}`
                })
            }
        }
    }
}

</script>

<style scoped>
/* Parameter input expand animation */
.parameter-expand-enter-active,
.parameter-expand-leave-active {
  transition: all 0.15s ease-out;
  overflow: hidden;
}

.parameter-expand-enter-from,
.parameter-expand-leave-to {
  width: 0;
  opacity: 0;
  padding-left: 0;
  padding-right: 0;
  margin-left: 0;
  margin-right: 0;
  border-left-width: 0;
  border-right-width: 0;
}
</style>