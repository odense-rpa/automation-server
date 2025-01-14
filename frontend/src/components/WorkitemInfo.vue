<template>
  <div class="flex flex-wrap" v-if="workitem">
    <div class="w-full lg:w-1/2 p-2">
      <dl class="grid grid-cols-5 gap-x-2">
        <dt class="col-span-2 font-semibold mb-2">ID:</dt>
        <dd class="col-span-3 mb-2">{{ workitem.id }}</dd>
        <dt class="col-span-2 font-semibold mb-2">Message:</dt>
        <dd class="col-span-3 mb-2">{{ workitem.message }}</dd>
        <dt class="col-span-2 font-semibold mb-2">Data:</dt>
        <dd class="col-span-3 mb-2"><json-view :jsonData="workitem.data" /></dd>
      </dl>
    </div>
    <div class="w-full lg:w-1/2 p-2">
      <dl class="grid grid-cols-5 gap-x-2">
        <dt class="col-span-2 font-semibold mb-2">Status:</dt>
        <dd class="col-span-3 mb-2"><font-awesome-icon :icon="['fas', 'triangle-exclamation']" v-if="workitem.status === 'failed'" /> {{ workitem.status }}</dd>
        <dt class="col-span-2 font-semibold mb-2">Created At:</dt>
        <dd class="col-span-3 mb-2">{{ $formatDateTime(workitem.created_at) }}</dd>
        <dt class="col-span-2 font-semibold mb-2">Updated At:</dt>
        <dd class="col-span-3 mb-2">{{ $formatDateTime(workitem.updated_at) }}</dd>
      </dl>
    </div>
  </div>
</template>

<script>
import JsonView from "./JsonView.vue";

export default {
  name: 'WorkitemInfo',
    components: {
        JsonView
    },
  props: {
    workitem: {
      type: Object,
      required: true
    }
  }
}
</script>
