<template>
    <div class="flex flex-wrap" v-if="workqueue">
      <div class="w-full lg:w-1/2 p-2">
        <dl class="grid grid-cols-5 gap-x-2">
          <dt class="col-span-2 font-semibold mb-2">Name:</dt>
          <dd class="col-span-3 mb-2">{{ workqueue.name }}</dd>
          <dt class="col-span-2 font-semibold mb-2">Description:</dt>
          <dd class="col-span-3 mb-2">{{ workqueue.description }}</dd>
        </dl>
      </div>
      <div class="w-full lg:w-1/2 p-2">
        <dl class="grid grid-cols-5 gap-x-2">
          <dt class="col-span-2 font-semibold mb-2">Enabled:</dt>
          <dd class="col-span-3 mb-2">{{ workqueue.enabled ? 'Yes' : 'No' }}</dd>
          <dt class="col-span-2 font-semibold mb-2">Last changed:</dt>
          <dd class="col-span-3 mb-2">{{ $formatDateTime(workqueue.updated_at) }}</dd>
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