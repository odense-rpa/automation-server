<template>
    <div class="row" v-if="workqueue">
        <div class="col-6">
            <dl class="row">
                <dt class="col-5">Name:</dt>
                <dd class="col-7">{{ workqueue.name }}</dd>
                <dt class="col-5">Description:</dt>
                <dd class="col-7">{{ workqueue.description }}</dd>
            </dl>
        </div>
        <div class="col-6">
            <dl class="row">
                <dt class="col-5">Enabled:</dt>
                <dd class="col-7">{{ workqueue.enabled ? 'Yes' : 'No' }}</dd>
                <dt class="col-5">Last changed:</dt>
                <dd class="col-7">{{ $formatDateTime(workqueue.updated_at) }}</dd>
            </dl>
        </div>
    </div>
</template>
<script>

export default {
    name: 'WorkqueueInfo',
    props: {
        workqueue: {
            type: Object,
            required: true
        }
    }
}
</script>