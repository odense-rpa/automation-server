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
            <button class="btn btn-ghost btn-xs" @click="copyReference" :title="copiedReference ? 'Copied!' : 'Copy reference'">
              <font-awesome-icon :icon="['fas', copiedReference ? 'check' : 'copy']" />
            </button>
          </dd>
          <dt class="col-span-2 font-semibold mb-2">Message:</dt>
          <dd class="col-span-3 mb-2">{{ workitem.message }}</dd>
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
    <div class="p-2">
      <p class="font-semibold mb-2">Data:</p>
      <json-view :jsonData="workitem.data" :expanded="true" />
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
  },
  data() {
    return {
      copiedReference: false
    };
  },
  methods: {
    copyReference() {
      navigator.clipboard.writeText(this.workitem.reference);
      this.copiedReference = true;
      setTimeout(() => { this.copiedReference = false; }, 1500);
    }
  }
}
</script>
