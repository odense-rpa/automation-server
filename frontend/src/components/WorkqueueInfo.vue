<template>
    <div class="flex flex-wrap" v-if="workqueue">
      <div class="w-full lg:w-1/2 p-2">
        <dl class="grid grid-cols-5 gap-x-2">
          <dt class="col-span-2 font-semibold mb-2">Name:</dt>
          <dd class="col-span-3 mb-2">{{ workqueue.name }}</dd>
          <dt class="col-span-2 font-semibold mb-2">Description:</dt>
          <dd class="col-span-3 mb-2">{{ workqueue.description }}</dd>
          <template v-if="information">
            <dt class="col-span-2 font-semibold mb-2">Items:</dt>
            <dd class="col-span-3 mb-2 flex flex-wrap gap-1">
              <span v-for="stat in stats" :key="stat.key" class="badge badge-md badge-ghost whitespace-nowrap">
                {{ stat.label }}: <span class="font-semibold ml-1">{{ information[stat.key] }}</span>
              </span>
            </dd>
          </template>
        </dl>
      </div>
      <div class="w-full lg:w-1/2 p-2">
        <dl class="grid grid-cols-5 gap-x-2">
          <dt class="col-span-2 font-semibold mb-2">Enabled:</dt>
          <dd class="col-span-3 mb-2">{{ workqueue.enabled ? 'Yes' : 'No' }}</dd>
          <dt class="col-span-2 font-semibold mb-2">Auto-clean:</dt>
          <dd class="col-span-3 mb-2">
            <template v-if="workqueue.auto_clean_max_age_days != null">
              After {{ workqueue.auto_clean_max_age_days }} days
            </template>
            <template v-else>Disabled</template>
          </dd>
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
        },
        information: {
            type: Object,
            default: null
        }
    },
    data: () => ({
        stats: [
            { key: 'new', label: 'New' },
            { key: 'in_progress', label: 'In progress' },
            { key: 'pending_user_action', label: 'Pending user' },
            { key: 'completed', label: 'Completed' },
            { key: 'failed', label: 'Failed' }
        ]
    })
}
</script>