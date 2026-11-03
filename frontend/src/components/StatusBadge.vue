<template>
  <!-- Compact: just the icon, for status columns in tables. The label is still
       there as a tooltip and for screen readers -->
  <span v-if="compact" :title="label">
    <font-awesome-icon :icon="['fas', look.icon]" :spin="look.spin" :class="look.color" />
    <span class="sr-only">{{ label }}</span>
  </span>
  <span v-else class="badge badge-ghost gap-1.5 whitespace-nowrap" :title="label">
    <font-awesome-icon :icon="['fas', look.icon]" :spin="look.spin" :class="look.color" />
    {{ label }}
  </span>
</template>

<script>
// One place for how statuses look. "new" differs per kind: a new session or
// work item is just waiting, a new incident needs attention.
const LOOKS = {
  session: {
    new: { icon: 'circle', color: 'text-info', label: 'New' },
    'in progress': { icon: 'spinner', spin: true, color: 'text-warning', label: 'In progress' },
    completed: { icon: 'circle-check', color: 'text-success', label: 'Completed' },
    failed: { icon: 'triangle-exclamation', color: 'text-error', label: 'Failed' }
  },
  workitem: {
    new: { icon: 'circle', color: 'text-info', label: 'New' },
    'in progress': { icon: 'spinner', spin: true, color: 'text-warning', label: 'In progress' },
    completed: { icon: 'circle-check', color: 'text-success', label: 'Completed' },
    failed: { icon: 'triangle-exclamation', color: 'text-error', label: 'Failed' },
    'pending user action': { icon: 'lock', color: 'text-warning', label: 'Pending user' }
  },
  incident: {
    new: { icon: 'triangle-exclamation', color: 'text-error', label: 'Open' },
    dismissed: { icon: 'check', color: 'text-base-content/60', label: 'Dismissed' },
    rescheduled: { icon: 'redo', color: 'text-success', label: 'Rescheduled' }
  }
}

export default {
  name: 'StatusBadge',
  props: {
    status: { type: String, default: '' },
    kind: {
      type: String,
      required: true,
      validator: (value) => Object.keys(LOOKS).includes(value)
    },
    // Icon only (with tooltip and screen-reader text), for table columns
    compact: { type: Boolean, default: false }
  },
  computed: {
    look() {
      // Unknown statuses still render, so a new backend status isn't hidden
      return LOOKS[this.kind][this.status] || { icon: 'circle', color: 'text-base-content/40' }
    },
    label() {
      return this.look.label || this.status
    }
  }
}
</script>
