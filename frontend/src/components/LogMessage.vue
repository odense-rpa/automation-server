<template>
  <div>
    <div ref="text" class="whitespace-pre-wrap [overflow-wrap:anywhere]" :style="expanded ? null : clampStyle">{{ message }}</div>
    <button
      v-if="overflowing || expanded"
      type="button"
      class="btn btn-link btn-xs px-0 h-auto min-h-0 no-underline"
      @click.stop="expanded = !expanded"
    >
      {{ expanded ? 'Show less' : 'Show more' }}
    </button>
  </div>
</template>

<script>
export default {
  name: 'LogMessage',
  props: {
    message: { type: String, default: '' },
    // Lines shown before the message is clamped
    lines: { type: Number, default: 3 }
  },
  data() {
    return {
      expanded: false,
      overflowing: false
    }
  },
  computed: {
    clampStyle() {
      return {
        display: '-webkit-box',
        WebkitBoxOrient: 'vertical',
        WebkitLineClamp: this.lines,
        overflow: 'hidden'
      }
    }
  },
  watch: {
    message() {
      this.expanded = false
      this.$nextTick(this.measure)
    }
  },
  mounted() {
    // Re-measure when the column width changes (window resize, sidebar toggle)
    this.observer = new ResizeObserver(() => this.measure())
    this.observer.observe(this.$refs.text)
  },
  beforeUnmount() {
    this.observer?.disconnect()
  },
  methods: {
    measure() {
      if (this.expanded) return
      const el = this.$refs.text
      this.overflowing = el.scrollHeight > el.clientHeight + 1
    }
  }
}
</script>
