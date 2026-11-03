<template>
  <button
    type="button"
    class="btn btn-ghost btn-xs"
    :title="copied ? 'Copied!' : label"
    :aria-label="label"
    @click.stop.prevent="copy"
  >
    <font-awesome-icon :icon="['fas', copied ? 'check' : 'copy']" />
  </button>
</template>

<script>
import { useAlertStore } from '@/stores/alertStore'

export default {
  name: 'CopyButton',
  props: {
    // The text, or a function returning it (for values that are costly to build
    // and only needed when someone actually copies, like JSON of a large tree)
    text: { type: [String, Function], required: true },
    label: { type: String, default: 'Copy' }
  },
  emits: ['copied'],
  data() {
    return { copied: false, resetTimer: null }
  },
  beforeUnmount() {
    clearTimeout(this.resetTimer)
  },
  methods: {
    async copy() {
      const text = typeof this.text === 'function' ? this.text() : this.text
      try {
        await this.writeToClipboard(text)
        this.copied = true
        this.$emit('copied')
        clearTimeout(this.resetTimer)
        this.resetTimer = setTimeout(() => (this.copied = false), 1500)
      } catch {
        useAlertStore().addAlert({ type: 'error', message: 'Could not copy to the clipboard' })
      }
    },
    async writeToClipboard(text) {
      // navigator.clipboard only exists over HTTPS or on localhost
      if (navigator.clipboard?.writeText) {
        return navigator.clipboard.writeText(text)
      }
      // Fallback for plain-HTTP intranets. The helper textarea goes next to the
      // button: inside a modal <dialog> everything outside it is inert
      const area = document.createElement('textarea')
      area.value = text
      area.setAttribute('readonly', '')
      area.style.position = 'fixed'
      area.style.opacity = '0'
      this.$el.parentElement.appendChild(area)
      area.select()
      try {
        if (!document.execCommand('copy')) throw new Error('copy command failed')
      } finally {
        area.remove()
      }
    }
  }
}
</script>
