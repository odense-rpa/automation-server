<template>
    <span>{{ workqueue.name }}</span>
</template>

<script>
import { workqueuesAPI } from '@/services/automationserver.js'

export default {
    name: 'WorkqueueLabel',
    props: {
        workqueueId: {
            type: Number,
            required: true
        }
    },
    data() {
        return {
            workqueue: {}
        }
    },
    async mounted() {
        this.workqueue = await workqueuesAPI.getWorkqueue(this.workqueueId)
    }

}
</script>