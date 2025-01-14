<template>
    <span v-if="process">{{ process.name }}</span>
</template>

<script>
import { processesAPI } from '@/services/automationserver.js'

export default {
    name: 'ProcessLabel',
    props: {
        processId: {
            type: Number,
            required: true
        }
    },
    data() {
        return {
            process: {}
        }
    },
    async mounted() {
        try {
            this.process = await processesAPI.getProcess(this.processId);
        } catch (error) {
            // Set af deleted process with empty name AI!
        }
    }

}
</script>