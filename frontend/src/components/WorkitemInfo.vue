<template>
  <div v-if="workitem">
    <div class="flex flex-wrap">
      <div class="w-full lg:w-1/2 p-2">
        <dl class="grid grid-cols-5 gap-x-2">
          <dt class="col-span-2 font-semibold mb-2">ID:</dt>
          <dd class="col-span-3 mb-2">{{ workitem.id }} <font-awesome-icon :icon="['fas', 'lock']" v-if="workitem.locked" /></dd>
          <dt class="col-span-2 font-semibold mb-2">Reference:</dt>
          <dd class="col-span-3 mb-2 flex justify-between items-center">
            <span>{{ workitem.reference }}</span>
            <copy-button :text="workitem.reference || ''" label="Copy reference" />
          </dd>
          <dt class="col-span-2 font-semibold mb-2">Message:</dt>
          <dd class="col-span-3 mb-2">{{ workitem.message }}</dd>
        </dl>
      </div>
      <div class="w-full lg:w-1/2 p-2">
        <dl class="grid grid-cols-5 gap-x-2">
          <dt class="col-span-2 font-semibold mb-2">Status:</dt>
          <dd class="col-span-3 mb-2"><status-badge kind="workitem" :status="workitem.status" /></dd>
          <dt class="col-span-2 font-semibold mb-2">Created At:</dt>
          <dd class="col-span-3 mb-2">{{ $formatDateTime(workitem.created_at) }}</dd>
          <dt class="col-span-2 font-semibold mb-2">Updated At:</dt>
          <dd class="col-span-3 mb-2">{{ $formatDateTime(workitem.updated_at) }}</dd>
        </dl>
      </div>
    </div>
  </div>
</template>

<script>
import StatusBadge from '@/components/StatusBadge.vue'
import CopyButton from '@/components/CopyButton.vue'

export default {
  name: 'WorkitemInfo',
  components: { StatusBadge, CopyButton },
  props: {
    workitem: {
      type: Object,
      required: true
    }
  },
}
</script>
