<template>
  <!-- Mouse users can click anywhere in the row; keyboard and screen-reader
       users get the one real link inside it (instead of one link per cell) -->
  <tr class="hover:bg-base-300 cursor-pointer" @click="onClick" @auxclick="onClick">
    <slot />
  </tr>
</template>

<script>
// Clicks on these are their own action (copy, actions menu, JSON modal, a
// different link), not "open the row"
const INTERACTIVE = 'a, button, input, select, textarea, label, summary, dialog, .dropdown'

export default {
  name: 'LinkRow',
  props: {
    to: { type: [String, Object], required: true }
  },
  methods: {
    onClick(event) {
      if (event.button > 1 || event.target.closest(INTERACTIVE)) return
      // Don't navigate when the user is selecting text in the row
      if (window.getSelection()?.toString()) return
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.button === 1) {
        window.open(this.$router.resolve(this.to).href, '_blank', 'noopener')
      } else {
        this.$router.push(this.to)
      }
    }
  }
}
</script>
