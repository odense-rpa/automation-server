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
        this.process = await processesAPI.getProcess(this.processId);
    }

}
</script>