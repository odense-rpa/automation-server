<template>
    <div class="input-group">
        <select v-model="selected" class="form-control">
            <option value="">Trigger process...</option>
            <option v-for="process in processes" :key="process.id" :value="process.id">
                {{ process.name }}
            </option>
        </select>
        <button class="btn btn-success" :class="{ 'disabled-class': selected === '' }" :disabled="selected === ''"
            @click.prevent="trigger()">+</button>
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
            selected: ""
        }
    },
    async created() {
        this.processes = await processesAPI.getProcesses()
    },
    methods: {
        async trigger() {
            await sessionsAPI.createSession(this.selected)
            this.selected = ""

            useAlertStore().addAlert({
                type: 'success',
                message: 'Process was triggered'
            })

        }
    }
}

</script>